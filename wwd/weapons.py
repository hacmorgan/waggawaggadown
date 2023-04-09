"""
Wagga Wagga Down character classes
"""


from enum import Enum
from typing import Dict

import pygame

from wwd.characters import CollisionsDict


RANGED_SCALE_FACTOR = 1.0
MEELEE_SCALE_FACTOR = 1.0

MACHETE_DAMAGE = 50
ARROW_DAMAGE = 50


class Weapon(pygame.sprite.Sprite):
    """
    Base class for all weapons
    """

    def __init__(
        self,
        pos: pygame.Vector2,
        image: pygame.Surface,
        damage: float,
        single_use: bool,
    ):
        """
        Construct the weapon object

        Args:
            damage: Amount of damage inflicted by weapon
            single_use: Weapon dies after making contact if True
        """
        super().__init__()
        self.pos = pos
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.damage = damage
        self.single_use = single_use

    def update(
        self,
        weapon_enemy_collisions: CollisionsDict,
    ) -> None:
        """
        Update enemy state
        """
        if self in weapon_enemy_collisions:
            for enemy in weapon_enemy_collisions[self]:
                enemy.health -= self.damage
                if self.single_use:
                    self.kill()
                    return


class MeeleeWeapon(Weapon):
    """
    Handheld weapons
    """

    def __init__(
        self,
        pos: pygame.Vector2,
    ):
        """
        Construct the character object

        Args:
            damage: Amount of damage inflicted by weapon
            single_use: Weapon dies after making contact if True
        """
        img = pygame.transform.smoothscale_by(
            pygame.image.load("../assets/sprites/weapons/machete.png").convert_alpha(),
            MEELEE_SCALE_FACTOR,
        )
        super().__init__(pos=pos, image=img, damage=MACHETE_DAMAGE, single_use=False)

    def update(
        self,
        scroll_delta: pygame.Vector2,
        weapon_enemy_collisions: CollisionsDict,
    ) -> None:
        """
        Update enemy state
        """
        super().update(weapon_enemy_collisions=weapon_enemy_collisions)


class RangedWeapon(Weapon):
    """
    HandheldRanged weapons
    """

    def __init__(
        self,
        pos: pygame.Vector2,
    ):
        """
        Construct the character object

        Args:
            damage: Amount of damage inflicted by weapon
            single_use: Weapon dies after making contact if True
        """
        img = pygame.transform.smoothscale_by(
            pygame.image.load("../assets/sprites/weapons/arrow.png").convert_alpha(),
            RANGED_SCALE_FACTOR,
        )
        super().__init__(pos=pos, image=img, damage=ARROW_DAMAGE, single_use=True)

    def update(
        self,
        scroll_delta: pygame.Vector2,
        weapon_enemy_collisions: CollisionsDict,
    ) -> None:
        """
        Update enemy state
        """
        self.pos += scroll_delta
        self.rect.center = self.pos
        super().update(weapon_enemy_collisions=weapon_enemy_collisions)
