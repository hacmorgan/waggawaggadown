"""
Wagga Wagga Down character classes
"""


from enum import Enum
from typing import Dict, Iterator, List, Tuple

import pygame


# Scaling factors for sprites
PLAYER_SCALE_FACTOR = 2.5
ENEMY_SCALE_FACTOR = 1.0

# Damage done to player by enemy contact
ENEMY_COLLISION_DAMAGE = 1
WEAPON_COLLISION_DAMAGE = 50


CollisionsDict = Dict[pygame.sprite.Sprite, List[pygame.sprite.Sprite]]


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


class Character(pygame.sprite.Sprite):
    """
    Base class for all characters
    """

    def __init__(
        self,
        pos: pygame.Vector2,
        sprites: Dict[AnimationFrame, pygame.Surface],
        max_health: float,
    ):
        """
        Construct the character object
        """
        super().__init__()
        self.image = sprites[AnimationFrame.REGULAR]
        self.pos = pos
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.health = max_health

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


class Player(Character):
    """
    Class for player character
    """

    def __init__(self, pos: pygame.Vector2):
        """
        Construct the player
        """
        fwd_image = pygame.transform.smoothscale_by(
            pygame.image.load(
                "../assets/sprites/player/forward/regular.png"
            ).convert_alpha(),
            PLAYER_SCALE_FACTOR,
        )
        super().__init__(
            pos=pos, sprites={AnimationFrame.REGULAR: fwd_image}, max_health=100
        )
        self.meelee_weapon = None
        self.ranged_weapon = None
        self.active_weapon = self.meelee_weapon

    def update(
        self,
        scroll_delta: pygame.Vector2,
        player_enemy_collisions: CollisionsDict,
        mouse_buttons: Tuple[bool],
        scroll_wheel: bool,
    ) -> None:
        """
        Update player
        """
        # Check collisions
        if self in player_enemy_collisions:
            for _ in player_enemy_collisions[self]:
                self.health -= ENEMY_COLLISION_DAMAGE

        # Check weapons & keypresses
        if scroll_wheel:
            self.switch_weapon()
        if self.active_weapon.can_attack and mouse_buttons[MouseButton.LEFT]:
            self.active_weapon.attack()

        # Perform generic character update
        super().update()

    def switch_weapon(self) -> None:
        """
        Alternate between meelee and ranged weapon
        """
        if self.ac


class Enemy(Character):
    """
    Class for enemy NPCs
    """

    def __init__(self, pos: pygame.Vector2):
        """
        Construct the player
        """
        fwd_image = pygame.transform.smoothscale_by(
            pygame.image.load(
                "../assets/sprites/enemy/zombie/regular.png"
            ).convert_alpha(),
            ENEMY_SCALE_FACTOR,
        )
        super().__init__(
            pos=pos, sprites={AnimationFrame.REGULAR: fwd_image}, max_health=50
        )
        self.meelee_weapon = None

    def update(
        self,
        scroll_delta: pygame.Vector2,
        enemy_weapon_collisions: CollisionsDict,
    ) -> None:
        """
        Update enemy state
        """
        if self in enemy_weapon_collisions:
            for _ in enemy_weapon_collisions[self]:
                self.health -= WEAPON_COLLISION_DAMAGE

        self.pos += scroll_delta
        self.rect.center = self.pos
        super().update()


class Pet(Character):
    """
    Class for friendly pets
    """

    def __init__(self, pos: pygame.Vector2):
        """
        Construct the player
        """
        fwd_image = pygame.transform.smoothscale_by(
            pygame.image.load(
                "../assets/sprites/player/forward/regular.png"
            ).convert_alpha(),
            PLAYER_SCALE_FACTOR,
        )
        super().__init__(
            pos=pos, sprites={AnimationFrame.REGULAR: fwd_image}, max_health=100
        )
        self.meelee_weapon = None

    def update(
        self,
        scroll_delta: pygame.Vector2,
        player_enemy_collisions: CollisionsDict,
    ) -> None:
        """
        Update player
        """
        super().update()
