"""
Wagga Wagga Down character classes
"""


from enum import Enum
from typing import Dict

import pygame


class SpriteFrame(Enum):
    """
    Defined frames of animation
    """

    FORWARD = "FORWARD"
    FORWARD_LEFT_STEP = "FORWARD_LEFT_STEP"
    FORWARD_RIGHT_STEP = "FORWARD_RIGHT_STEP"
    LEFT = "LEFT"
    LEFT_LEFT_STEP = "LEFT_LEFT_STEP"
    LEFT_RIGHT_STEP = "LEFT_RIGHT_STEP"
    RIGHT = "RIGHT"
    RIGHT_LEFT_STEP = "RIGHT_LEFT_STEP"
    RIGHT_RIGHT_STEP = "RIGHT_RIGHT_STEP"
    BACK = "BACK"
    BACK_LEFT_STEP = "BACK_LEFT_STEP"
    BACK_RIGHT_STEP = "BACK_RIGHT_STEP"


class Character:
    """
    Base class for all characters
    """

    def __init__(self, sprites: Dict[SpriteFrame, pygame.Surface], max_health: float):
        """
        Construct the character object
        """
        self.sprites = sprites
        self.health = max_health

    def draw(self) -> None:
        """
        Draw the character and recursively draw any extras (e.g. weapons, pets)
        """


class Player(Character):
    """
    Class for player character
    """


class Enemy(Character):
    """
    Class for enemy NPCs
    """


class Pet(Character):
    """
    Class for friendly pets
    """
