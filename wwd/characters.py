"""
Wagga Wagga Down character classes
"""


from enum import Enum
from pathlib import Path
from typing import Dict, Iterator, Tuple

import pygame

from wwd.constants import CollisionsDict
from wwd.weapons import MeeleeWeapon, RangedWeapon


# Scaling factors for sprites
PLAYER_SCALE_FACTOR = 2.5
ENEMY_SCALE_FACTOR = 1.0

# Movement and following
ENEMY_FOLLOW_DIST = 800
ENEMY_MOVE_SPEED = 100
PANKO_MOVEMENT_SPEED = 200

# Enemy starting health
ENEMY_HEALTH = 49

# Rate of player health regeneration
HEALTH_REGEN_RATE = 5

# Damage done to player by enemy contact
ENEMY_COLLISION_DAMAGE = 20
WEAPON_COLLISION_DAMAGE = 50
PANKO_BITE_DAMAGE = 30


class AnimationFrame(Enum):
    """
    Walk animation frames
    """

    REGULAR = "FORWARD"
    LEFT_STEP = "LEFT_STEP"
    RIGHT_STEP = "RIGHT_STEP"


class MouseButton(Enum):
    """
    Mouse button indices to pygame mouse return tuple
    """

    LEFT = 0
    RIGHT = 1
    MIDDLE = 2


MOUSE_BUTTONS = {"LEFT": idx for idx, mouse_button in enumerate(MouseButton)}


class Character(pygame.sprite.Sprite):
    """
    Base class for all characters
    """

    def __init__(
        self,
        pos: pygame.Vector2,
        sprites: Dict[AnimationFrame, pygame.Surface],
        max_health: float,
        screen: pygame.Surface,
    ):
        """
        Construct the character object
        """
        super().__init__()
        self.image = sprites[AnimationFrame.REGULAR]
        self.pos = pos
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.max_health = max_health
        self.health = self.max_health
        self.screen = screen

    def animation_frames(self) -> Iterator[pygame.Surface]:
        """
        Yield
        """
        # Only do walk animations if all required frames are present
        if all(frame in self.sprites for frame in AnimationFrame):
            frames = (
                AnimationFrame.REGULAR,
                AnimationFrame.LEFT_STEP,
                AnimationFrame.REGULAR,
                AnimationFrame.RIGHT_STEP,
            )
        else:
            frames = (AnimationFrame.REGULAR,)

        # Infinitely yield frames
        while True:
            yield from frames

    def update(self) -> None:
        """
        Update charcter state
        """
        if self.health < 0:
            self.kill()

        # Draw health bar
        health_bar_left = self.pos.copy() - pygame.Vector2(
            self.rect.width / 2, 10 + self.rect.height / 2
        )
        health_bar_inflection_point = health_bar_left.copy()
        health_bar_inflection_point.x = (
            health_bar_left.x + self.health / self.max_health * self.rect.width
        )
        health_bar_right = health_bar_left.copy()
        health_bar_right.x = health_bar_left.x + self.rect.width
        pygame.draw.line(
            self.screen, "green", health_bar_left, health_bar_inflection_point, width=2
        )
        pygame.draw.line(
            self.screen, "red", health_bar_inflection_point, health_bar_right, width=2
        )

    def regenerate_health(self, dt: float) -> None:
        """
        Regenrate character health
        """
        if self.health < self.max_health:
            self.health = min(self.max_health, self.health + HEALTH_REGEN_RATE * dt)


class Player(Character):
    """
    Class for player character
    """

    def __init__(
        self,
        pos: pygame.Vector2,
        meelee_weapon: MeeleeWeapon,
        ranged_weapon: RangedWeapon,
        screen: pygame.Surface,
    ):
        """
        Construct the player
        """
        fwd_image = pygame.transform.smoothscale_by(
            pygame.image.load(
                Path("../assets/sprites/player/forward/regular.png")
            ).convert_alpha(),
            PLAYER_SCALE_FACTOR,
        )
        super().__init__(
            pos=pos,
            sprites={AnimationFrame.REGULAR: fwd_image},
            max_health=100,
            screen=screen,
        )
        self.meelee_weapon = meelee_weapon
        self.ranged_weapon = ranged_weapon
        self.active_weapon = self.meelee_weapon

    def update(
        self,
        scroll_delta: pygame.Vector2,
        dt: float,
        player_enemy_collisions: CollisionsDict,
        mouse_buttons: Tuple[bool],
        scroll_wheel: bool,
        keys: Tuple[bool],
    ) -> None:
        """
        Update player
        """
        # Check collisions
        if self in player_enemy_collisions:
            for _ in player_enemy_collisions[self]:
                self.health -= ENEMY_COLLISION_DAMAGE * dt

        # Check weapons & keypresses
        if scroll_wheel or keys[pygame.K_SPACE]:
            self.switch_weapon()
        if (
            not self.active_weapon.is_attacking
            and mouse_buttons[MouseButton.LEFT.value]
        ):
            self.active_weapon.attack()

        self.regenerate_health(dt=dt)

        # Perform generic character update
        super().update()

    def switch_weapon(self) -> None:
        """
        Alternate between meelee and ranged weapon
        """
        if self.active_weapon is self.meelee_weapon:
            self.active_weapon = self.ranged_weapon
        else:
            self.active_weapon = self.meelee_weapon


class Enemy(Character):
    """
    Class for enemy NPCs
    """

    def __init__(
        self,
        pos: pygame.Vector2,
        player: Player,
        screen: pygame.Surface,
        enemy_follow_distance: float,
    ):
        """
        Construct the player
        """
        fwd_image = pygame.transform.smoothscale_by(
            pygame.image.load(
                Path("../assets/sprites/enemy/zombie/regular.png")
            ).convert_alpha(),
            ENEMY_SCALE_FACTOR,
        )
        super().__init__(
            pos=pos,
            sprites={AnimationFrame.REGULAR: fwd_image},
            max_health=ENEMY_HEALTH,
            screen=screen,
        )
        self.player = player
        self.enemy_follow_distance = enemy_follow_distance

    def update(
        self,
        scroll_delta: pygame.Vector2,
        dt: float,
    ) -> None:
        """
        Update enemy state
        """
        self.pos += scroll_delta
        self.rect.center = self.pos
        if self.pos.distance_to(self.player.pos) < self.enemy_follow_distance:
            self.pos = self.pos.move_towards(self.player.pos, ENEMY_MOVE_SPEED * dt)
        super().update()


class Pet(Character):
    """
    Class for friendly pets
    """

    def __init__(
        self,
        pos: pygame.Vector2,
        player: Player,
        screen: pygame.Surface,
    ):
        """
        Construct the player
        """
        fwd_image = pygame.transform.smoothscale_by(
            pygame.image.load(
                Path("../assets/sprites/panko/regular.png")
            ).convert_alpha(),
            PLAYER_SCALE_FACTOR,
        )
        super().__init__(
            pos=pos,
            sprites={AnimationFrame.REGULAR: fwd_image},
            max_health=ENEMY_HEALTH,
            screen=screen,
        )
        self.is_attacking = False
        self.meelee_weapon = None
        self.player = player
        self.targeted_enemy = None

    def update(
        self,
        scroll_delta: pygame.Vector2,
        dt: float,
        pet_enemy_collisions: CollisionsDict,
    ) -> None:
        """
        Update player
        """
        self.regenerate_health(dt=dt)

        if not self.targeted_enemy.alive():
            self.is_attacking = False

        if self.is_attacking:

            # Move with bg scroll
            self.pos += scroll_delta
            self.rect.center = self.pos

            # Move towards enemy
            self.pos.move_towards_ip(self.targeted_enemy.pos, PANKO_MOVEMENT_SPEED * dt)

            if self in pet_enemy_collisions and self.is_attacking:
                # Update damage to self
                self.health -= (
                    len(pet_enemy_collisions[self]) * ENEMY_COLLISION_DAMAGE * dt
                )

                # Update damage to targeted enemy
                if self.targeted_enemy in pet_enemy_collisions[self]:
                    self.targeted_enemy.health -= PANKO_BITE_DAMAGE * dt

        super().update()

    def kill(self) -> None:
        """
        Kill the pet
        """
        self.is_attacking = False
        super().kill()

    def attack(self, enemy: Enemy) -> None:
        """
        Target and begin attacking an enemy
        """
        self.targeted_enemy = enemy
        self.is_attacking = True
