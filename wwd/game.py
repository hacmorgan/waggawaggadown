#!/usr/bin/env python3


"""
Main game logic
"""


from typing import Tuple

import numpy as np
import PIL.Image
import pygame

from wwd.characters import Player, Enemy
from wwd.weapons import MeeleeWeapon, RangedWeapon


BG_SCALE_FACTOR = 1.5
SCROLL_DIST = 100
HOME_X, HOME_Y = -616.5, -7179.2
SCREEN_POS_X_LB, SCREEN_POS_X_UB = -8320, 0
SCREEN_POS_Y_LB, SCREEN_POS_Y_UB = -7260, 0
SCREEN_SCROLL_OFFSET = pygame.Vector2(640, 360)


class Game:
    """
    Highest level game class
    """

    def __init__(self):
        """
        Construct the game object
        """
        # Initialise game
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        # TODO: loading screen
        self.clock = pygame.time.Clock()

        # Load assets
        self.background = pygame.transform.smoothscale_by(
            pygame.image.load("../assets/combined_bg.png").convert(), BG_SCALE_FACTOR
        )
        self.walls = np.array(PIL.Image.open("../assets/walls.png"))[
            :, :, -1  # Mask is alpha channel
        ]

        # Initialise variables
        self.dt = 0
        self.center_screen = pygame.Vector2(
            self.screen.get_width() / 2, self.screen.get_height() / 2
        )
        self.screen_pos = pygame.Vector2(HOME_X, HOME_Y)

        # Initialise characters and groups
        self.player = Player(pos=self.center_screen)
        self.player_group = pygame.sprite.Group(self.player)
        self.machete = MeeleeWeapon(
            pos=self.player.pos + pygame.Vector2(self.player.rect.width / 2, 0)
        )
        self.weapons_group = pygame.sprite.Group(self.machete)
        self.test_enemies = (Enemy(pos=self.center_screen / 2),)
        self.enemies_group = pygame.sprite.Group(*self.test_enemies)

    def main_loop(self) -> None:
        """
        Main game logic
        """
        running = True
        while running:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Detect collisions (from last frame)
            player_enemy_collisions = pygame.sprite.groupcollide(
                groupa=self.player_group,
                groupb=self.enemies_group,
                dokilla=False,
                dokillb=False,
            )
            enemy_weapon_collisions = pygame.sprite.groupcollide(
                groupa=self.enemies_group,
                groupb=self.weapons_group,
                dokilla=False,
                dokillb=False,
            )
            weapon_enemy_collisions = pygame.sprite.groupcollide(
                groupa=self.weapons_group,
                groupb=self.enemies_group,
                dokilla=False,
                dokillb=False,
            )

            # Get pressed keys
            keys, sprint = self.check_keys()

            # Determine player/background movements
            scroll_delta = self.move_background(keys=keys, sprint=sprint)

            # Update logic
            self.player_group.update(
                scroll_delta=scroll_delta,
                player_enemy_collisions=player_enemy_collisions,
            )
            self.weapons_group.update(
                scroll_delta=scroll_delta,
                weapon_enemy_collisions=weapon_enemy_collisions,
            )
            self.enemies_group.update(
                scroll_delta=scroll_delta,
                enemy_weapon_collisions=enemy_weapon_collisions,
            )  # n.b. enemies must update after weapons

            # End game if player is dead
            if not self.player.alive():
                print("you died")
                running = False

            # Draw background
            self.screen.fill("black")
            self.screen.blit(self.background, self.screen_pos)

            # Draw sprites
            self.player_group.draw(surface=self.screen)
            self.weapons_group.draw(surface=self.screen)
            self.enemies_group.draw(surface=self.screen)

            # flip() the display to put your work on screen
            pygame.display.flip()

            print(f"{self.screen_pos=}")

            # limits FPS to 60
            # dt is delta time in seconds since last frame, used for framerate-
            # independent physics.
            self.dt = self.clock.tick(60) / 1000

        pygame.quit()

    def check_keys(self) -> Tuple[Tuple[bool], bool]:
        """
        Get keyboard input, check for sprinting

        Returns:
            Key states
            True if sprinting, False otherwise
        """
        keys = pygame.key.get_pressed()
        modifiers = pygame.key.get_mods()
        sprint = modifiers & pygame.KMOD_SHIFT
        return keys, sprint

    def move_background(self, keys: Tuple[bool], sprint: bool) -> None:
        """
        Move the background or the player relative to the background
        """
        # Save position before move
        previous_pos = self.screen_pos.copy()

        # Determine how far to move
        scroll_dist = SCROLL_DIST * 5 if sprint else SCROLL_DIST

        # Determine movement direction
        scroll_vector = pygame.Vector2(0, 0)
        if keys[pygame.K_w]:
            scroll_vector.y = scroll_dist * self.dt
        if keys[pygame.K_s]:
            scroll_vector.y = -scroll_dist * self.dt
        if keys[pygame.K_a]:
            scroll_vector.x = scroll_dist * self.dt
        if keys[pygame.K_d]:
            scroll_vector.x = -scroll_dist * self.dt

        # Get position player wants to move to
        new_pos = self.screen_pos + scroll_vector

        # Check for walls
        if self.can_move_to(new_pos):
            self.screen_pos = new_pos
        else:
            self.screen_pos = self.best_effort_move(scroll_vector)

        # Clamp coordinates within borders
        self.screen_pos.x = pygame.math.clamp(
            self.screen_pos.x,
            SCREEN_POS_X_LB - self.center_screen.x,
            SCREEN_POS_X_UB + self.center_screen.x,
        )
        self.screen_pos.y = pygame.math.clamp(
            self.screen_pos.y,
            SCREEN_POS_Y_LB - self.center_screen.y,
            SCREEN_POS_Y_UB + self.center_screen.y,
        )

        # Return true scroll delta
        return self.screen_pos - previous_pos

    def can_move_to(self, new_position: pygame.Vector2) -> bool:
        """
        Check if the player can move to a desired position
        """
        unscaled_x, unscaled_y = self.pygame_pos_to_numpy(pos=new_position)
        return self.walls[int(unscaled_y), int(unscaled_x)] == 255

    def best_effort_move(
        self, scroll_vector: pygame.Vector2, scroll_scale: float = 4.0
    ) -> pygame.Vector2:
        """
        Move background as far as possible in desired direction

        Args:
            scroll_vector: Desired direction of movement
            scroll_scale: Multiplier for scroll_vector - required to function correctly
        """
        # breakpoint()
        numpy_pos = self.pygame_pos_to_numpy(pos=self.screen_pos)
        move_distance = scroll_vector.magnitude() * scroll_scale / BG_SCALE_FACTOR
        region_offset = pygame.Vector2(move_distance, move_distance)
        region_lb = numpy_pos - region_offset
        region_ub = numpy_pos + region_offset
        region = self.walls[
            (lby := int(region_lb.y)) : (uby := int(region_ub.y)),
            (lbx := int(region_lb.x)) : (ubx := int(region_ub.x)),
        ]
        free_space = region == 255

        # Construct array of positions that should correlate with free_space array mask
        ys, xs = np.meshgrid(range(lby, uby), range(lbx, ubx))
        ys, xs = ys[free_space.T], xs[free_space.T]

        if 0 in (len(xs), len(ys)):
            return self.screen_pos

        best_move = pygame.Vector2()
        if scroll_vector.x == 0:
            if scroll_vector.y > 0:
                best_move_idx = np.argmax(ys)
            else:
                best_move_idx = np.argmin(ys)
        elif scroll_vector.y == 0:
            if scroll_vector.x > 0:
                best_move_idx = np.argmax(xs)
            else:
                best_move_idx = np.argmin(xs)
        else:
            best_move_idx = np.argmax(
                np.sqrt((xs - numpy_pos.x) ** 2 + (ys - numpy_pos.y) ** 2)
            )
            return self.screen_pos
        best_move.x, best_move.y = xs[best_move_idx], ys[best_move_idx]

        return self.numpy_pos_to_pygame(best_move)

    def pygame_pos_to_numpy(self, pos: pygame.Vector2) -> pygame.Vector2:
        """
        Convert pygame screen position to numpy array co-ordinates
        """
        return -(pos - self.center_screen) / BG_SCALE_FACTOR

    def numpy_pos_to_pygame(self, pos: pygame.Vector2) -> pygame.Vector2:
        """
        Convert numpy array co-ordinates to pygame screen position
        """
        return self.center_screen - BG_SCALE_FACTOR * pos
