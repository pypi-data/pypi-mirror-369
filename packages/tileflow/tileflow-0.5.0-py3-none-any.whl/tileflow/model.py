"""High-performance tile-based image processing engine.

This module implements TileFlow's main processing pipeline:
- TileFlow: Main processor class with configure/run interface
- Direct tiling: Process images tile by tile
- Hierarchical chunking: Handle massive images through chunk → tile processing
- Memory optimization: Minimal footprint through lazy evaluation
- Multi-dimensional support: Handle CHW, CHWD, and arbitrary array shapes

The processor supports both simple workflows and complex multi-stage pipelines
for scientific imaging and computer vision applications.
"""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
import os
from typing import Any

import numpy as np

from tileflow.backends import Streamable, as_streamable
from tileflow.callback import CompositeCallback, ProcessingStats, TileFlowCallback
from tileflow.core import ProcessedTile, TileSpec
from tileflow.reconstruction import reconstruct
from tileflow.tiling import GridSpec
from tileflow.utils import validate_overlap, validate_tile_size


class TileFlow:
    """High-performance tile-based image processor.

    Processes large images through intelligent tiling with configurable overlap
    and reconstruction. Supports both direct tiling and hierarchical chunking
    for memory-efficient processing of massive datasets.

    Examples
    --------
    >>> processor = TileFlow(tile_size=(128, 128), overlap=(8, 8))
    >>> processor.configure(function=my_function)
    >>> result = processor.run(image)

    >>> # For very large images, use chunking
    >>> processor = TileFlow(tile_size=(128, 128), overlap=(8, 8), chunk_size=(512, 512))
    >>> processor.configure(function=my_function)
    >>> result = processor.run(large_image)
    """

    def __init__(
        self,
        tile_size: tuple[int, int],
        overlap: tuple[int, int] = (0, 0),
        chunk_size: tuple[int, int] | None = None,
        chunk_overlap: tuple[int, int] = (16, 16),
        name: str = "TileFlow",
        n_workers: int = 1,
        enable_optimization: bool = True,
        use_memmap: bool = False,
        memmap_threshold_mb: float = 100.0,
    ) -> None:
        """Initialize TileFlow processor.

        Parameters
        ----------
        tile_size : tuple[int, int]
            Size of each tile (height, width)
        overlap : tuple[int, int], default=(0, 0)
            Overlap between tiles (height, width)
        chunk_size : tuple[int, int], optional
            If provided, process large images in chunks of this size
        chunk_overlap : tuple[int, int], default=(16, 16)
            Overlap between chunks when using chunked processing
        name : str, default="TileFlow"
            Name of the processor for logging/debugging
        n_workers : int, default=1
            Number of parallel workers for tile processing. Set to > 1 to enable
            parallel processing. Use -1 to auto-detect CPU cores.
        enable_optimization : bool, default=True
            Enable performance optimizations (caching, lazy evaluation)
        use_memmap : bool, default=False
            Use memory-mapped arrays for large intermediate results
        memmap_threshold_mb : float, default=100.0
            Size threshold (MB) above which to use memory mapping
        """
        self.tile_size = self._validate_size(tile_size, "tile_size")
        self.overlap = self._validate_size(overlap, "overlap")
        self.chunk_size = self._validate_size(chunk_size, "chunk_size") if chunk_size else None
        self.chunk_overlap = self._validate_size(chunk_overlap, "chunk_overlap")
        self.name = name
        self.enable_optimization = enable_optimization
        self.use_memmap = use_memmap
        self.memmap_threshold_mb = memmap_threshold_mb

        # Handle n_workers parameter
        if n_workers == -1:
            self.n_workers = os.cpu_count() or 1
        elif n_workers < 1:
            raise ValueError(f"n_workers must be >= 1 or -1, got {n_workers}")
        else:
            self.n_workers = n_workers

        # Validate overlap against tile size
        validate_overlap(self.overlap, self.tile_size)
        if self.chunk_size:
            validate_overlap(self.chunk_overlap, self.chunk_size)

        self._processor: (
            Callable[[np.ndarray], np.ndarray]
            | Callable[[np.ndarray, TileSpec], np.ndarray]
            | None
        ) = None
        self._chunk_processor: (
            Callable[[list[np.ndarray], TileSpec], list[np.ndarray]] | None
        ) = None
        self._configured = False
        self._slice_prefix_cache: dict[int, tuple] = {}
        # NumPy optimizations
        self._enable_numpy_optimizations = enable_optimization
        self._array_pool: dict[tuple, list[np.ndarray]] = {}  # (shape, dtype) -> [arrays]

    @staticmethod
    def _validate_size(size: tuple[int, int], param_name: str) -> tuple[int, int]:
        """Validate size parameters."""
        if not isinstance(size, (tuple, list)) or len(size) != 2:
            raise ValueError(f"{param_name} must be a tuple of 2 integers")
        h, w = size
        if not isinstance(h, int) or not isinstance(w, int):
            raise ValueError(f"{param_name} must contain integers")
        if h < 0 or w < 0:
            raise ValueError(f"{param_name} must be non-negative, got {size}")
        if "size" in param_name and (h == 0 or w == 0):
            raise ValueError(f"{param_name} must be positive, got {size}")
        return (h, w)

    def _get_slice_prefix(self, ndim: int) -> tuple:
        """Get cached slice prefix for multi-dimensional arrays."""
        if not self.enable_optimization:
            return tuple([slice(None)] * (ndim - 2)) if ndim > 2 else ()

        if ndim not in self._slice_prefix_cache:
            self._slice_prefix_cache[ndim] = (
                tuple([slice(None)] * (ndim - 2)) if ndim > 2 else ()
            )
        return self._slice_prefix_cache[ndim]
    
    def _get_pooled_array(self, shape: tuple[int, ...], dtype: np.dtype) -> np.ndarray:
        """Get a reusable array from the pool or create new one."""
        if not self._enable_numpy_optimizations:
            return np.empty(shape, dtype=dtype, order='C')
            
        key = (shape, dtype)
        if key in self._array_pool and self._array_pool[key]:
            return self._array_pool[key].pop()
        else:
            return np.empty(shape, dtype=dtype, order='C')
    
    def _return_pooled_array(self, array: np.ndarray) -> None:
        """Return an array to the pool for reuse."""
        if not self._enable_numpy_optimizations:
            return
            
        key = (array.shape, array.dtype)
        if key not in self._array_pool:
            self._array_pool[key] = []
        
        # Limit pool size to prevent excessive memory usage
        if len(self._array_pool[key]) < 10:
            self._array_pool[key].append(array)
    
    def _should_use_memmap(self, shape: tuple[int, ...], dtype: np.dtype) -> bool:
        """Check if array should use memory mapping based on size."""
        if not self.use_memmap:
            return False
        
        size_bytes = np.prod(shape) * dtype.itemsize
        size_mb = size_bytes / (1024 * 1024)
        return size_mb > self.memmap_threshold_mb
    
    def _create_optimized_array(self, shape: tuple[int, ...], dtype: np.dtype) -> np.ndarray:
        """Create array with optimal allocation strategy."""
        if self._should_use_memmap(shape, dtype):
            # Use memory-mapped temporary file for large arrays
            import tempfile
            return np.memmap(
                tempfile.NamedTemporaryFile().name,
                dtype=dtype,
                mode='w+',
                shape=shape,
                order='C'
            )
        else:
            return self._get_pooled_array(shape, dtype)
    
    def _apply_numpy_optimizations(self, array: np.ndarray) -> np.ndarray:
        """Apply NumPy-specific optimizations to array operations."""
        if not self._enable_numpy_optimizations:
            return array
            
        # Ensure C-contiguous layout for better cache performance
        if not array.flags['C_CONTIGUOUS']:
            array = np.ascontiguousarray(array)
            
        # Use optimized data types if beneficial
        if array.dtype == np.float64 and array.size > 1000:
            # Convert to float32 if precision loss is acceptable for large arrays
            # This provides 2x memory savings and often faster SIMD operations
            return array.astype(np.float32, copy=False)
            
        return array

    def _process_single_tile(
        self, streamable: Streamable, tile_spec: TileSpec, slice_prefix: tuple
    ) -> ProcessedTile:
        """Process a single tile - used for both serial and parallel processing."""
        halo_slices = tile_spec.get_halo_slices()
        full_slices = slice_prefix + halo_slices if slice_prefix else halo_slices
        tile_data = streamable[full_slices]

        # Apply NumPy optimizations to input data
        if self._enable_numpy_optimizations:
            tile_data = self._apply_numpy_optimizations(tile_data)

        # Try calling with both arguments first, fall back to single argument for compatibility
        try:
            tile_output = self._processor(tile_data, tile_spec)
        except TypeError:
            # Fall back to single argument for backward compatibility
            tile_output = self._processor(tile_data)

        # Apply optimizations to output if it's a numpy array
        if self._enable_numpy_optimizations and isinstance(tile_output, np.ndarray):
            tile_output = self._apply_numpy_optimizations(tile_output)

        return ProcessedTile(tile_spec=tile_spec, image_data=tile_output)

    def _process_tiles_parallel(
        self,
        streamable: Streamable,
        tile_specs: list[TileSpec],
        slice_prefix: tuple,
        callback: CompositeCallback,
        stats: ProcessingStats | None = None,
    ) -> list[ProcessedTile]:
        """Process tiles in parallel using ThreadPoolExecutor."""
        total_tiles = len(tile_specs)
        tiles: list[ProcessedTile] = []

        def process_tile_with_callback(i_and_spec):
            i, tile_spec = i_and_spec
            # Only create temp tiles and call callbacks if there are listeners
            if callback.has_tile_listeners():
                temp_tile = ProcessedTile(tile_spec=tile_spec, image_data=[])
                callback.on_tile_start(temp_tile, i, total_tiles)

            processed_tile = self._process_single_tile(streamable, tile_spec, slice_prefix)
            
            if callback.has_tile_listeners():
                callback.on_tile_end(processed_tile, i, total_tiles)
            return processed_tile

        with ThreadPoolExecutor(max_workers=self.n_workers) as executor:
            futures = [
                executor.submit(process_tile_with_callback, (i, spec))
                for i, spec in enumerate(tile_specs)
            ]

            for i, future in enumerate(futures):
                processed_tile = future.result()
                tiles.append(processed_tile)
                if stats:
                    stats.processed_tiles = i + 1

        return tiles

    def _process_tiles_serial(
        self,
        streamable: Streamable,
        tile_specs_iter,
        slice_prefix: tuple,
        callback: CompositeCallback,
        stats: ProcessingStats | None = None,
    ) -> list[ProcessedTile]:
        """Process tiles serially with optimized callbacks."""
        tiles: list[ProcessedTile] = []

        for i, tile_spec in enumerate(tile_specs_iter):
            # Only create temp tiles and call callbacks if there are listeners
            if callback.has_tile_listeners():
                temp_tile = ProcessedTile(tile_spec=tile_spec, image_data=[])
                callback.on_tile_start(temp_tile, i, stats.total_tiles if stats else 0)

            processed_tile = self._process_single_tile(streamable, tile_spec, slice_prefix)
            
            if callback.has_tile_listeners():
                callback.on_tile_end(processed_tile, i, stats.total_tiles if stats else 0)
            tiles.append(processed_tile)

            if stats:
                stats.processed_tiles = i + 1

        return tiles

    def configure(
        self,
        function: Callable[[np.ndarray], np.ndarray] | Callable[[np.ndarray, TileSpec], np.ndarray],
        chunk_function: Callable[[list[np.ndarray], TileSpec], list[np.ndarray]] | None = None,
    ) -> None:
        """Configure the processor with processing functions.

        Parameters
        ----------
        function : Callable[[np.ndarray], np.ndarray] | Callable[[np.ndarray, TileSpec], np.ndarray]
            Function to apply to each tile. Can receive just tile data or both tile data and
            tile specification.
        chunk_function : Callable[[list[np.ndarray], TileSpec], list[np.ndarray]], optional
            Function to apply to reconstructed chunks. Receives chunk output and
            chunk specification.
        """
        if not callable(function):
            raise TypeError("function must be callable")
        if chunk_function is not None and not callable(chunk_function):
            raise TypeError("chunk_function must be callable")

        self._processor = function
        self._chunk_processor = chunk_function
        self._configured = True

    def run(
        self,
        data: Any,
        callbacks: list[TileFlowCallback] | None = None,
        return_tiles: bool = False,
    ) -> np.ndarray | list[ProcessedTile] | None:
        """Run processing pipeline on input data.

        Parameters
        ----------
        data : Any
            Input data (np.ndarray or other supported types)
        callbacks : list[TileFlowCallback], optional
            Callbacks for progress tracking
        return_tiles : bool, default=False
            Return individual tiles instead of reconstructed image

        Returns
        -------
        np.ndarray | list[ProcessedTile] | None
            Processed result, individual tiles, or None for chunked processing of massive images
        """
        if not self._configured:
            raise RuntimeError(
                f"Processor '{self.name}' must be configured before use. "
                f"Call processor.configure(function=fn)"
            )

        streamable = as_streamable(data)

        # Validate configuration against actual data (spatial dimensions only)
        spatial_shape = streamable.shape[-2:] if len(streamable.shape) >= 2 else streamable.shape
        validate_tile_size(self.tile_size, spatial_shape)

        # Create unified callback interface
        callback = CompositeCallback(callbacks or [])

        # Only initialize statistics if callbacks need them or optimization is disabled
        stats = None
        if callbacks or not self.enable_optimization:
            stats = ProcessingStats()
            stats.input_shape = streamable.shape
            stats.tile_size = self.tile_size
            stats.overlap = self.overlap
            stats.chunk_size = self.chunk_size

        try:
            # Calculate total tiles for progress tracking
            grid_spec = GridSpec(size=self.tile_size, overlap=self.overlap)
            if self.chunk_size is not None:
                validate_tile_size(self.chunk_size, spatial_shape)
                chunk_grid_spec = GridSpec(size=self.chunk_size, overlap=self.chunk_overlap)
                if self.enable_optimization and stats is None:
                    # Pure lazy evaluation - no stats needed
                    chunk_specs_iter = chunk_grid_spec.build_grid(spatial_shape)
                elif self.enable_optimization:
                    # Lazy evaluation - only calculate total if needed for stats
                    grid_shape = chunk_grid_spec.grid_shape(spatial_shape)
                    stats.total_chunks = grid_shape[0] * grid_shape[1]
                    # Better estimate for total tiles
                    stats.total_tiles = stats.total_chunks * 4  # More accurate estimate
                    chunk_specs_iter = chunk_grid_spec.build_grid(spatial_shape)
                else:
                    chunk_specs = list(chunk_grid_spec.build_grid(spatial_shape))
                    if stats:
                        stats.total_chunks = len(chunk_specs)
                        stats.total_tiles = len(chunk_specs) * 10  # Rough estimate
                    chunk_specs_iter = iter(chunk_specs)
            elif self.enable_optimization and stats is None:
                # Pure lazy evaluation - no stats needed
                tile_specs_iter = grid_spec.build_grid(spatial_shape)
            elif self.enable_optimization:
                # Lazy evaluation - only calculate total if needed for stats
                grid_shape = grid_spec.grid_shape(spatial_shape)
                stats.total_tiles = grid_shape[0] * grid_shape[1]
                tile_specs_iter = grid_spec.build_grid(spatial_shape)
            else:
                tile_specs = list(grid_spec.build_grid(spatial_shape))
                if stats:
                    stats.total_tiles = len(tile_specs)
                tile_specs_iter = iter(tile_specs)

            # Start processing (create dummy stats if needed for callbacks)
            callback_stats = stats or ProcessingStats()
            callback.on_processing_start(callback_stats)

            if self.chunk_size is not None:
                result = self._process_chunked(
                    streamable, spatial_shape, callback, return_tiles, stats, chunk_specs_iter
                )
            else:
                result = self._process_direct(
                    streamable, spatial_shape, callback, return_tiles, stats, tile_specs_iter
                )

            # Update final statistics
            if stats:
                stats.output_shape = (
                    result.shape if result is not None and hasattr(result, "shape") else None
                )
            callback.on_processing_end(callback_stats)

            return result

        except Exception as e:
            callback.on_processing_error(e, callback_stats)
            raise

    def _process_direct(
        self,
        streamable: Streamable,
        spatial_shape: tuple[int, int],
        callback: CompositeCallback,
        return_tiles: bool = False,
        stats: ProcessingStats | None = None,
        tile_specs_iter=None,
    ) -> np.ndarray | list[ProcessedTile]:
        """Process with direct tiling (no chunking)."""
        # Use provided iterator or create new one
        if tile_specs_iter is None:
            grid_spec = GridSpec(size=self.tile_size, overlap=self.overlap)
            tile_specs_iter = grid_spec.build_grid(spatial_shape)

        # Pre-compute slice prefix for optimization
        slice_prefix = self._get_slice_prefix(len(streamable.shape))

        # Convert to list for parallel processing or keep as iterator
        if self.n_workers > 1:
            tile_specs = list(tile_specs_iter)
            total_tiles = len(tile_specs)
            if stats:
                stats.total_tiles = total_tiles
            tiles = self._process_tiles_parallel(
                streamable, tile_specs, slice_prefix, callback, stats
            )
        else:
            tiles = self._process_tiles_serial(
                streamable, tile_specs_iter, slice_prefix, callback, stats
            )

        if return_tiles:
            return tiles

        reconstructed = reconstruct(tiles)
        # Return single array if only one channel, otherwise return list
        return reconstructed[0] if len(reconstructed) == 1 else reconstructed

    def _process_chunked(
        self,
        streamable: Streamable,
        spatial_shape: tuple[int, int],
        callback: CompositeCallback,
        return_tiles: bool = False,
        stats: ProcessingStats | None = None,
        chunk_specs_iter=None,
    ) -> None:
        """Process with chunking for large images."""
        # Use provided iterator or create new one
        if chunk_specs_iter is None:
            chunk_grid_spec = GridSpec(size=self.chunk_size, overlap=self.chunk_overlap)
            chunk_specs_iter = chunk_grid_spec.build_grid(spatial_shape)

        # Pre-compute slice prefix for optimization
        slice_prefix = self._get_slice_prefix(len(streamable.shape))

        for i, chunk_spec in enumerate(chunk_specs_iter):
            # Use dynamic total calculation for optimized mode
            total_chunks = stats.total_chunks if stats else 0
            
            # Only call chunk callbacks if there are listeners
            if callback.has_chunk_listeners():
                chunk_shape = chunk_spec.geometry.halo.shape
                callback.on_chunk_start(i, total_chunks, chunk_shape)

            # Use optimized slice computation
            halo_slices = chunk_spec.get_halo_slices()
            full_slices = slice_prefix + halo_slices if slice_prefix else halo_slices
            chunk_data = streamable[full_slices]

            # Process chunk with tiles (pass None for callbacks to avoid double-counting)
            chunk_streamable = as_streamable(chunk_data)
            chunk_spatial_shape = (
                chunk_data.shape[-2:] if len(chunk_data.shape) >= 2 else chunk_data.shape
            )
            chunk_output = self._process_direct(
                chunk_streamable, chunk_spatial_shape, callback, return_tiles=False, stats=None
            )

            # Apply chunk processor if provided
            if self._chunk_processor:
                chunk_output = self._chunk_processor(chunk_output, chunk_spec)

            if callback.has_chunk_listeners():
                chunk_shape = chunk_spec.geometry.halo.shape
                callback.on_chunk_end(i, total_chunks, chunk_shape)

            if stats:
                stats.processed_chunks = i + 1

        # For massive images, we don't return anything to save memory

    def summary(self) -> None:
        """Print processor configuration summary."""
        print(f"TileFlow Processor: {self.name}")
        print("=" * 50)
        print(f"Tile size:      {self.tile_size}")
        print(f"Tile overlap:   {self.overlap}")
        if self.chunk_size:
            print(f"Chunk size:     {self.chunk_size}")
            print(f"Chunk overlap:  {self.chunk_overlap}")
            print("Mode:           Hierarchical (chunks → tiles)")
        else:
            print("Mode:           Direct tiling")
        print(f"Workers:        {self.n_workers}")
        print(f"Optimizations:  {'Enabled' if self.enable_optimization else 'Disabled'}")
        if self.enable_optimization:
            print(f"NumPy optimizations: {'Enabled' if self._enable_numpy_optimizations else 'Disabled'}")
            if self.use_memmap:
                print(f"Memory mapping: Enabled (>{self.memmap_threshold_mb} MB)")
            print(f"Array pooling: {'Enabled' if self._enable_numpy_optimizations else 'Disabled'}")
        print(f"Configured:     {self._configured}")
        if self._configured:
            print(
                f"Function:       {
                    self._processor.__name__
                    if hasattr(self._processor, '__name__')
                    else 'Custom function'
                }"
            )
        if self._chunk_processor:
            print(
                f"Chunk function: {
                    self._chunk_processor.__name__
                    if hasattr(self._chunk_processor, '__name__')
                    else 'Custom chunk function'
                }"
            )
        print("=" * 50)
