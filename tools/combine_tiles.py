#!/usr/bin/env python3


"""
Combine tiles from google maps into a large raster
"""


import functools
import subprocess
import sys

from pathlib import Path

import numpy as np
import PIL.Image


OUTPUT_SHAPE = (5326, 6400, 3)
Y_STEP, X_STEP = 334, 960
TILE_SHAPE_Y, TILE_SHAPE_X = 650, 1600
TILE_ORIGIN_Y, TILE_ORIGIN_X = (OUTPUT_SHAPE[0] - TILE_SHAPE_Y, 0)

sh_run = functools.partial(subprocess.run, shell=True, check=True)


def main() -> int:
    """
    Main logic
    """
    output_raster = np.zeros(OUTPUT_SHAPE, dtype=np.uint8)

    input_paths = list(
        path
        for path in Path("../assets/backgrounds").iterdir()
        if path.suffix == ".png"
    )

    # Find all latitudes and longitudes
    longitudes, latitudes = set(), set()
    for path in input_paths:
        lon, lat = path.stem.strip().split("_")
        longitudes.add(lon)
        latitudes.add(lat)

    # Create mapping from lat/lon to position index of tile
    longitudes = {lon: idx for idx, lon in enumerate(sorted(longitudes, reverse=True))}
    latitudes = {lat: idx for idx, lat in enumerate(sorted(latitudes))}

    for path in input_paths:
        lon, lat = path.stem.strip().split("_")
        lon_idx, lat_idx = longitudes[lon], latitudes[lat]
        tile_y = TILE_ORIGIN_Y - lon_idx * Y_STEP
        tile_x = TILE_ORIGIN_X + lat_idx * X_STEP
        output_raster[
            tile_y : tile_y + TILE_SHAPE_Y, tile_x : tile_x + TILE_SHAPE_X, :
        ] = np.array(PIL.Image.open(path))

    PIL.Image.fromarray(output_raster).save("../assets/combined_bg.png")

    return 0


if __name__ == "__main__":
    sys.exit(main())
