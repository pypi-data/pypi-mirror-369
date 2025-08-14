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
        """
        self.tile_size = self._validate_size(tile_size, "tile_size")
        self.overlap = self._validate_size(overlap, "overlap")
        self.chunk_size = self._validate_size(chunk_size, "chunk_size") if chunk_size else None
        self.chunk_overlap = self._validate_size(chunk_overlap, "chunk_overlap")
        self.name = name

        # Validate overlap against tile size
        validate_overlap(self.overlap, self.tile_size)
        if self.chunk_size:
            validate_overlap(self.chunk_overlap, self.chunk_size)

        self._processor: Callable[[np.ndarray, TileSpec], np.ndarray] | None = None
        self._chunk_processor: Callable[[list[np.ndarray], TileSpec], list[np.ndarray]] | None = None
        self._configured = False

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

    def configure(
        self,
        function: Callable[[np.ndarray, TileSpec], np.ndarray],
        chunk_function: Callable[[list[np.ndarray], TileSpec], list[np.ndarray]] | None = None,
    ) -> None:
        """Configure the processor with processing functions.

        Parameters
        ----------
        function : Callable[[np.ndarray, TileSpec], np.ndarray]
            Function to apply to each tile. Receives tile data and tile specification.
        chunk_function : Callable[[list[np.ndarray], TileSpec], list[np.ndarray]], optional
            Function to apply to reconstructed chunks. Receives chunk output and chunk specification.
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
    ) -> np.ndarray | list[ProcessedTile]:
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
        np.ndarray | list[ProcessedTile]
            Processed result or individual tiles
        """
        if not self._configured:
            raise RuntimeError(
                f"Processor '{self.name}' must be configured before use. Call processor.configure(function=fn)"
            )

        streamable = as_streamable(data)

        # Validate configuration against actual data (spatial dimensions only)
        spatial_shape = streamable.shape[-2:] if len(streamable.shape) >= 2 else streamable.shape
        validate_tile_size(self.tile_size, spatial_shape)

        # Create unified callback interface
        callback = CompositeCallback(callbacks or [])

        # Initialize processing statistics
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
                chunk_specs = list(chunk_grid_spec.build_grid(spatial_shape))
                stats.total_chunks = len(chunk_specs)
                # Estimate total tiles (will be updated during processing)
                stats.total_tiles = len(chunk_specs) * 10  # Rough estimate
            else:
                tile_specs = list(grid_spec.build_grid(spatial_shape))
                stats.total_tiles = len(tile_specs)

            # Start processing
            callback.on_processing_start(stats)

            if self.chunk_size is not None:
                result = self._process_chunked(streamable, spatial_shape, callback, return_tiles, stats)
            else:
                result = self._process_direct(streamable, spatial_shape, callback, return_tiles, stats)

            # Update final statistics
            stats.output_shape = result.shape if hasattr(result, "shape") else None
            callback.on_processing_end(stats)

            return result

        except Exception as e:
            callback.on_processing_error(e, stats)
            raise

    def _process_direct(
        self,
        streamable: Streamable,
        spatial_shape: tuple[int, int],
        callback: CompositeCallback,
        return_tiles: bool = False,
        stats: ProcessingStats | None = None,
    ) -> np.ndarray | list[ProcessedTile]:
        """Process with direct tiling (no chunking)."""
        grid_spec = GridSpec(size=self.tile_size, overlap=self.overlap)
        tiles: list[ProcessedTile] = []

        tile_specs = list(grid_spec.build_grid(spatial_shape))
        total_tiles = len(tile_specs)

        if stats:
            stats.total_tiles = total_tiles

        for i, tile_spec in enumerate(tile_specs):
            # Create temporary tile for start event
            temp_tile = ProcessedTile(tile_spec=tile_spec, image_data=[])
            callback.on_tile_start(temp_tile, i, total_tiles)

            halo_slices = tile_spec.get_halo_slices()
            # For multi-dimensional arrays, prepend slice(None) for extra dimensions
            if len(streamable.shape) > 2:
                full_slices = tuple([slice(None)] * (len(streamable.shape) - 2) + list(halo_slices))
            else:
                full_slices = halo_slices
            tile_data = streamable[full_slices]
            tile_output = self._processor(tile_data, tile_spec)
            processed_tile = ProcessedTile(tile_spec=tile_spec, image_data=tile_output)

            callback.on_tile_end(processed_tile, i, total_tiles)
            tiles.append(processed_tile)

            if stats:
                stats.processed_tiles = i + 1

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
    ) -> np.ndarray | list[ProcessedTile]:
        """Process with chunking for large images."""
        chunk_grid_spec = GridSpec(size=self.chunk_size, overlap=self.chunk_overlap)
        tiles: list[ProcessedTile] = []

        chunk_specs = list(chunk_grid_spec.build_grid(spatial_shape))
        total_chunks = len(chunk_specs)

        if stats:
            stats.total_chunks = total_chunks

        for i, chunk_spec in enumerate(chunk_specs):
            chunk_shape = chunk_spec.geometry.halo.shape
            callback.on_chunk_start(i, total_chunks, chunk_shape)

            halo_slices = chunk_spec.get_halo_slices()
            # For multi-dimensional arrays, prepend slice(None) for extra dimensions
            if len(streamable.shape) > 2:
                full_slices = tuple([slice(None)] * (len(streamable.shape) - 2) + list(halo_slices))
            else:
                full_slices = halo_slices
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

            processed_tile = ProcessedTile(tile_spec=chunk_spec, image_data=chunk_output)
            callback.on_chunk_end(i, total_chunks, chunk_shape)

            if stats:
                stats.processed_chunks = i + 1

            tiles.append(processed_tile)

        if return_tiles:
            return tiles

        reconstructed = reconstruct(tiles)
        # Return single array if only one channel, otherwise return list
        return reconstructed[0] if len(reconstructed) == 1 else reconstructed

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
        print(f"Configured:     {self._configured}")
        if self._configured:
            print(
                f"Function:       {self._processor.__name__ if hasattr(self._processor, '__name__') else 'Custom function'}"
            )
        print("=" * 50)
