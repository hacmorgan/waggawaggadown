#!/usr/bin/env python3


"""
Download tiles from google maps
"""


import functools
import subprocess
import sys

import numpy as np


URL_TEMPLATE = "https://www.google.com/maps/@{lat},{lon},300m/data=!3m1!1e3"

START_LAT = -35.1372994
START_LON = 147.3403537

STOP_LAT = -35.1176863
STOP_LON = 147.3656834

STEP_LAT = 0.0023
STEP_LON = 0.0075


MAP_X = 100
MAP_Y = 260
MAP_WIDTH = 1600
MAP_HEIGHT = 650
SCREENSHOT_CMD_TEMPLATE = f"scrot --autoselect {MAP_X},{MAP_Y},{MAP_WIDTH},{MAP_HEIGHT}"


sh_run = functools.partial(subprocess.run, shell=True, check=True)


def main() -> int:
    """
    Main logic
    """
    for lat in np.arange(START_LAT, STOP_LAT, STEP_LAT):
        for lon in np.arange(START_LON, STOP_LON, STEP_LON):
            sh_run("firefox " + URL_TEMPLATE.format(lat=lat, lon=lon))
            input()
            sh_run(SCREENSHOT_CMD_TEMPLATE + f" --exec 'mv -v $f ./{lat}_{lon}.png'")

    return 0


if __name__ == "__main__":
    sys.exit(main())
