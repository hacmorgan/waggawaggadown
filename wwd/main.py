#!/usr/bin/env python3


"""
Main game logic
"""


import sys

from wwd.game import Game


def main() -> int:
    """
    Main game logic

    Returns:
        Exit status
    """
    Game().main_loop()

    return 0


if __name__ == "__main__":
    sys.exit(main())
