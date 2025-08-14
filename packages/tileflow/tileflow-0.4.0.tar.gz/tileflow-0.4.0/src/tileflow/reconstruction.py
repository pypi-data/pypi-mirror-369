"""Image reconstruction from processed tiles."""

import numpy as np

from tileflow.core import Image2D, ProcessedTile, new_image2d


def reconstruct(tiles: list[ProcessedTile]) -> list[Image2D]:
    """Reconstruct a full image from a list of processed tiles.

    Parameters
    ----------
    tiles : list[ProcessedTile]
        List of processed tiles to reconstruct the image from

    Returns
    -------
    list[ImageData]
        List of reconstructed images, one per channel

    Raises
    ------
    ValueError
        If tiles don't form a valid reconstruction grid
    """
    last_tile = tiles[-1]
    if not last_tile.tile_spec.position.edges.right:
        raise ValueError("Last tile must have a right edge to determine full image size.")
    if not last_tile.tile_spec.position.edges.bottom:
        raise ValueError("Last tile must have a bottom edge to determine full image size.")

    if last_tile.image_data is None:
        raise ValueError("Last tile must have valid image data to determine output structure.")

    # Get output dimensions from the last tile's region bounds (core area)
    width_reconstructed = last_tile.tile_spec.geometry.core.x1
    height_reconstructed = last_tile.tile_spec.geometry.core.y1

    # Handle both single array and list of arrays
    if isinstance(last_tile.image_data, list):
        sample_data = last_tile.image_data
    else:
        sample_data = [last_tile.image_data]

    # Determine output shape from processed data
    # For multi-dimensional output, preserve the shape structure
    sample_shape = sample_data[0].shape
    if len(sample_shape) >= 3:  # Multi-channel output (C, H, W)
        output_channels = sample_shape[0]
        output_shape = (output_channels, height_reconstructed, width_reconstructed)
    else:  # 2D output (H, W)
        output_shape = (height_reconstructed, width_reconstructed)

    # Create output arrays matching the processor output structure
    if len(sample_shape) >= 3:
        # Multi-channel: create single array
        reconstructed = [np.zeros(output_shape, dtype=sample_data[0].dtype)]
    else:
        # Single channel or traditional list approach
        reconstructed = [
            new_image2d(
                (height_reconstructed, width_reconstructed),
                dtype=data.dtype,
            )
            for data in sample_data
        ]

    # Fill in data from each tile
    for tile in tiles:
        if tile.image_data is None:
            continue

        region_bbox = tile.tile_spec.geometry.core
        region_images = tile.only_core_image()

        if region_images is None:
            continue

        # Handle different output formats
        if len(sample_shape) >= 3:
            # Multi-channel processor output - place directly
            region_data = region_images[0] if isinstance(region_images, list) else region_images
            reconstructed[0][
                :, region_bbox.y0 : region_bbox.y1, region_bbox.x0 : region_bbox.x1
            ] = region_data
        else:
            # Traditional channel-wise reconstruction
            for i, region_img in enumerate(region_images):
                reconstructed[i][
                    region_bbox.y0 : region_bbox.y1, region_bbox.x0 : region_bbox.x1
                ] = region_img

    return reconstructed
