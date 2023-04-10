"""
Wagga Wagga Down character classes
"""


from enum import Enum
from math import sin, cos, radians
from pathlib import Path
from typing import Dict

import pygame

from wwd.constants import CollisionsDict


RANGED_SCALE_FACTOR = 1.0
MEELEE_SCALE_FACTOR = 1.5

MACHETE_DAMAGE = 50
MACHETE_ANGULAR_VELOCITY = 800
ARROW_DAMAGE = 50


class Weapon(pygame.sprite.Sprite):
    """
    Base class for all weapons
    """

    def __init__(
        self,
        pos: pygame.Vector2,
        weapons_group: pygame.sprite.Group,
        player_center: pygame.Vector2,
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
        self.player_center = player_center
        self.weapons_group = weapons_group
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.damage = damage
        self.single_use = single_use
        self.is_attacking = False
        self.kill_next_time = False

    def update(
        self,
        weapon_enemy_collisions: CollisionsDict,
    ) -> None:
        """
        Update enemy state
        """
        # Check if we were killed last time
        if self.kill_next_time:
            self.kill()
            self.kill_next_time = False

        # Ensure is_attacking is unset when the sprite is killed
        if not self.alive():
            self.is_attacking = False

        # Check collisions with enemies
        if self in weapon_enemy_collisions and self.is_attacking:
            for enemy in weapon_enemy_collisions[self]:
                enemy.health -= self.damage
                if self.single_use:
                    self.kill_next_time = True
                    return

    def attack(self) -> None:
        """
        Execute weapon attack
        """
        self.is_attacking = True
        self.add(self.weapons_group)


class MeeleeWeapon(Weapon):
    """
    Handheld weapons
    """

    def __init__(
        self,
        pos: pygame.Vector2,
        weapons_group: pygame.sprite.Group,
        player_center: pygame.Vector2,
    ):
        """
        Construct the character object

        Args:
            damage: Amount of damage inflicted by weapon
            single_use: Weapon dies after making contact if True
        """
        img = pygame.transform.smoothscale_by(
            pygame.image.load(
                Path("../assets/sprites/weapons/machete.png")
            ).convert_alpha(),
            MEELEE_SCALE_FACTOR,
        )
        super().__init__(
            pos=pos,
            weapons_group=weapons_group,
            player_center=player_center,
            image=img,
            damage=MACHETE_DAMAGE,
            single_use=True,
        )
        self.angle = 0
        self.swing_radius = self.rect.height / 2
        self.original_image = img

    def update(
        self,
        scroll_delta: pygame.Vector2,
        dt: float,
        weapon_enemy_collisions: CollisionsDict,
    ) -> None:
        """
        Update enemy state
        """
        super().update(weapon_enemy_collisions=weapon_enemy_collisions)

        # Update animation if currently attacking
        if self.is_attacking:

            # Check if we have completed a full revolution
            self.angle += MACHETE_ANGULAR_VELOCITY * dt
            if self.angle > 360:
                self.is_attacking = False
                self.kill()
            self.image = pygame.transform.rotate(self.original_image, self.angle)

            # Compute new center
            self.pos.x = (
                self.player_center.x
                - self.rect.width / 4
                - self.swing_radius * sin(radians(self.angle))
            )
            self.pos.y = self.player_center.y - self.swing_radius * cos(
                radians(self.angle)
            )
            self.rect.center = self.pos

    def attack(self) -> None:
        """
        Execute weapon attack
        """
        super().attack()
        self.angle = 0


class RangedWeapon(Weapon):
    """
    HandheldRanged weapons
    """

    def __init__(
        self,
        pos: pygame.Vector2,
        weapons_group: pygame.sprite.Group,
        player_center: pygame.Vector2,
    ):
        """
        Construct the character object

        Args:
            damage: Amount of damage inflicted by weapon
            single_use: Weapon dies after making contact if True
        """
        img = pygame.transform.smoothscale_by(
            pygame.image.load(
                Path("../assets/sprites/weapons/arrow.png")
            ).convert_alpha(),
            RANGED_SCALE_FACTOR,
        )
        super().__init__(
            pos=pos,
            weapons_group=weapons_group,
            player_center=player_center,
            image=img,
            damage=ARROW_DAMAGE,
            single_use=True,
        )
        self.direction = None

    def update(
        self,
        scroll_delta: pygame.Vector2,
        dt: float,
        weapon_enemy_collisions: CollisionsDict,
    ) -> None:
        """
        Update enemy state
        """
        self.pos += scroll_delta
        self.rect.center = self.pos
        super().update(weapon_enemy_collisions=weapon_enemy_collisions)

        # Update animation if currently attacking
        if self.is_attacking:

            # Check if we have completed a full revolution
            self.pos += self.direction * MACHETE_ANGULAR_VELOCITY * dt
            if self.angle > 360:
                self.is_attacking = False
                self.kill()
            self.image = pygame.transform.rotate(self.original_image, self.angle)

            # Compute new center
            self.pos.x = (
                self.player_center.x
                - self.rect.width / 4
                - self.swing_radius * sin(radians(self.angle))
            )
            self.pos.y = self.player_center.y - self.swing_radius * cos(
                radians(self.angle)
            )
            self.rect.center = self.pos
