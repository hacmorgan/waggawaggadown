#!/usr/bin/env python3


"""
Main game logic
"""


from functools import partial
from pathlib import Path
from random import random
from typing import Tuple

import numpy as np
import PIL.Image
import pygame

from wwd.characters import Player, Enemy
from wwd.weapons import MeeleeWeapon, RangedWeapon


BG_SCALE_FACTOR = 1.5
SCROLL_DIST = 150
HOME_X, HOME_Y = 845, 5030
MOVEMENT_ENEMY_SPAWN_PROBABILITY = 0.05
SPRINT_SPEED_MULTIPLIER = 2.5
ENEMY_FOLLOW_DIST_MULTIPLIER = 0.5


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
        self.resolution = pygame.Vector2(1920, 1080)
        self.resolution = pygame.Vector2(1200, 800)
        self.screen = pygame.display.set_mode(self.resolution)
        # TODO: loading screen
        self.clock = pygame.time.Clock()

        # Load assets
        self.background = pygame.transform.smoothscale_by(
            pygame.image.load(Path("../assets/combined_bg.jpg")).convert(),
            BG_SCALE_FACTOR,
        )
        self.walls = np.array(PIL.Image.open(Path("../assets/walls.png")))[
            :, :, -1  # Mask is alpha channel
        ]

        # Initialise variables
        self.dt = 0
        self.center_screen = pygame.Vector2(
            self.screen.get_width() / 2, self.screen.get_height() / 2
        )
        self.screen_pos = self.numpy_pos_to_pygame(pygame.Vector2(HOME_X, HOME_Y))
        self.numpy_pos_ub = pygame.Vector2(
            self.background.get_width() / BG_SCALE_FACTOR - 1,
            self.background.get_height() / BG_SCALE_FACTOR - 1,
        )

        # Initialise characters and groups
        self.weapons_group = pygame.sprite.Group()
        self.player = Player(
            pos=self.center_screen,
            meelee_weapon=MeeleeWeapon(
                pos=self.center_screen.copy(),
                weapons_group=self.weapons_group,
                player_center=self.center_screen,
            ),
            ranged_weapon=RangedWeapon(
                pos=self.center_screen.copy(),
                weapons_group=self.weapons_group,
                player_center=self.center_screen,
                screen=self.screen,
            ),
            screen=self.screen,
        )
        self.player_group = pygame.sprite.Group(self.player)
        self.enemy_factory = partial(
            Enemy,
            player=self.player,
            screen=self.screen,
            enemy_follow_distance=min(self.resolution) * ENEMY_FOLLOW_DIST_MULTIPLIER,
        )
        self.enemies_group = pygame.sprite.Group(
            self.enemy_factory(pos=self.center_screen / 2)
        )

    def main_loop(self) -> None:
        """
        Main game logic
        """
        running = True
        while running:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            scroll_wheel = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEWHEEL:
                    scroll_wheel = True

            # Detect collisions (from last frame)
            player_enemy_collisions = pygame.sprite.groupcollide(
                groupa=self.player_group,
                groupb=self.enemies_group,
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
            keys, mouse_buttons, sprint = self.get_input()

            # Determine player/background movements
            scroll_delta = self.move_background(keys=keys, sprint=sprint)

            # Spawn new enemies on movement
            if scroll_delta:
                self.spawn_enemies(scroll_delta)

            # Draw background
            self.screen.fill("black")
            self.screen.blit(self.background, self.screen_pos)

            # Update logic
            self.player_group.update(
                scroll_delta=scroll_delta,
                dt=self.dt,
                player_enemy_collisions=player_enemy_collisions,
                mouse_buttons=mouse_buttons,
                scroll_wheel=scroll_wheel,
                keys=keys,
            )
            self.weapons_group.update(
                scroll_delta=scroll_delta,
                dt=self.dt,
                weapon_enemy_collisions=weapon_enemy_collisions,
            )
            self.enemies_group.update(
                scroll_delta=scroll_delta,
                dt=self.dt,
            )

            # End game if player is dead
            if not self.player.alive():
                print("you died")
                running = False

            # Draw sprites
            self.player_group.draw(surface=self.screen)
            self.weapons_group.draw(surface=self.screen)
            self.enemies_group.draw(surface=self.screen)

            # flip() the display to put your work on screen
            pygame.display.flip()

            # limits FPS to 60
            # dt is delta time in seconds since last frame, used for framerate-
            # independent physics.
            self.dt = self.clock.tick(60) / 1000

        pygame.quit()

    def player_pos(self) -> pygame.Vector2:
        """
        Return player position on the board
        """
        return self.pygame_pos_to_numpy(pos=self.screen_pos)

    def get_input(self) -> Tuple[Tuple[bool], Tuple[bool], bool]:
        """
        Get keyboard input, check for sprinting

        Returns:
            Key states
            True if sprinting, False otherwise
        """
        keys = pygame.key.get_pressed()
        modifiers = pygame.key.get_mods()
        mouse_buttons = pygame.mouse.get_pressed()
        # sprint = modifiers & pygame.KMOD_SHIFT
        sprint = modifiers & pygame.KMOD_CAPS
        return keys, mouse_buttons, sprint

    def move_background(self, keys: Tuple[bool], sprint: bool) -> None:
        """
        Move the background

        The player stays centred, so this is equivalent to moving the player
        """
        # Save position before move
        previous_pos = self.screen_pos.copy()

        # Determine how far to move
        scroll_dist = SCROLL_DIST * SPRINT_SPEED_MULTIPLIER if sprint else SCROLL_DIST

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
        new_numpy_pos = self.pygame_pos_to_numpy(new_pos)

        # Clamp coordinates within borders
        new_numpy_pos.x = pygame.math.clamp(
            new_numpy_pos.x,
            0,
            self.numpy_pos_ub.x,
        )
        new_numpy_pos.y = pygame.math.clamp(
            new_numpy_pos.y,
            0,
            self.numpy_pos_ub.y,
        )

        # Check for walls
        if not self.can_move_to(new_numpy_pos):
            best_effort_numpy_pos = self.best_effort_move(
                scroll_vector=scroll_vector, new_numpy_pos=new_numpy_pos
            )
            if best_effort_numpy_pos is not None:
                new_numpy_pos = best_effort_numpy_pos

        self.screen_pos = self.screen_pos.move_towards(
            self.numpy_pos_to_pygame(new_numpy_pos), scroll_vector.magnitude()
        )

        # Return true scroll delta
        return self.screen_pos - previous_pos

    def spawn_enemies(self, scroll_delta: pygame.Vector2) -> None:
        """
        Randomly spawn an enemy
        """
        if random() < MOVEMENT_ENEMY_SPAWN_PROBABILITY:
            spawn_point = pygame.Vector2()
            if scroll_delta.x:
                spawn_point.x = 0 if scroll_delta.x > 0 else self.screen.get_width() - 1
            else:
                spawn_point.x = random() * self.screen.get_width()
            if scroll_delta.y:
                spawn_point.y = (
                    0 if scroll_delta.y > 0 else self.screen.get_height() - 1
                )
            else:
                spawn_point.y = random() * self.screen.get_height()
            self.enemies_group.add(self.enemy_factory(pos=spawn_point))

    def can_move_to(self, new_numpy_position: pygame.Vector2) -> bool:
        """
        Check if the player can move to a desired position
        """
        unscaled_x, unscaled_y = new_numpy_position
        return self.walls[int(unscaled_y), int(unscaled_x)] == 255

    def best_effort_move(
        self,
        scroll_vector: pygame.Vector2,
        new_numpy_pos: pygame.Vector2,
        scroll_scale: float = 4.0,
    ) -> pygame.Vector2:
        """
        Move background as far as possible in desired direction

        Args:
            scroll_vector: Desired direction of movement
            scroll_scale: Multiplier for scroll_vector - required to function correctly
        """
        # Extract local region of background and walls
        move_distance = scroll_vector.magnitude() * scroll_scale / BG_SCALE_FACTOR
        region_offset = pygame.Vector2(move_distance, move_distance)
        region_lb = new_numpy_pos - region_offset
        region_ub = new_numpy_pos + region_offset
        region = self.walls[
            (lby := int(region_lb.y)) : (uby := int(region_ub.y)),
            (lbx := int(region_lb.x)) : (ubx := int(region_ub.x)),
        ]

        # Construct boolean mask of spaces player can move to
        free_space = region == 255

        # Get co-ordinates of free spaces
        ys, xs = np.meshgrid(range(lby, uby), range(lbx, ubx))
        ys, xs = ys[free_space.T], xs[free_space.T]

        # Sometimes there is no possible move
        if 0 in (len(xs), len(ys)):
            return None

        # Determine optimal space to move to
        best_move = pygame.Vector2()
        if scroll_vector.x == 0:  # Moving in Y only
            if scroll_vector.y > 0:
                best_move_idx = np.argmin(ys)
            else:
                best_move_idx = np.argmax(ys)
        elif scroll_vector.y == 0:  # Moving in X only
            if scroll_vector.x > 0:
                best_move_idx = np.argmin(xs)
            else:
                best_move_idx = np.argmax(xs)
        else:  # Moving diagonally
            best_move_idx = np.argmax(
                np.sqrt((xs - new_numpy_pos.x) ** 2 + (ys - new_numpy_pos.y) ** 2)
            )

        best_move.x, best_move.y = xs[best_move_idx], ys[best_move_idx]
        return best_move

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
