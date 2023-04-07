#!/usr/bin/env python3


"""
Main game logic
"""


from typing import Tuple
from itertools import combinations

import numpy as np
import PIL.Image
import pygame


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
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()

        self.center_screen = pygame.Vector2(
            self.screen.get_width() / 2, self.screen.get_height() / 2
        )
        self.player_pos = self.center_screen.copy()
        self.screen_pos = pygame.Vector2(HOME_X, HOME_Y)

        self.background = pygame.transform.smoothscale_by(
            pygame.image.load("../assets/combined_bg.png").convert(), BG_SCALE_FACTOR
        )
        self.walls = np.array(PIL.Image.open("../assets/walls.png"))[
            :, :, -1  # Mask is alpha channel
        ]

        self.dt = 0

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

            # Get pressed keys
            keys, sprint = self.check_keys()

            # Determine movements
            self.move_player_or_background(keys=keys, sprint=sprint)

            # Scroll the background
            self.screen.fill("black")
            self.screen.blit(self.background, self.screen_pos)

            pygame.draw.circle(self.screen, "red", self.player_pos, 40)

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

    def move_player_or_background(self, keys: Tuple[bool], sprint: bool) -> None:
        """
        Move the background or the player relative to the background
        """
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

        # # Decide whether to move the background or the player
        # if player_pos != center_screen or not self.can_move_background(scroll_vector):
        #     self.move_player(scroll_vector)
        # else:
        #     self.move_background(scroll_vector)

        self.move_background(scroll_vector)

    # def move_player(self, scroll_vector: pygame.Vector2) -> None:
    #     """
    #     Move player relative to background
    #     """
    #     self.player_pos -= scroll_vector

    #     # Clamp player to center of screen if nearby
    #     if (
    #         self.player_pos - self.center_screen
    #     ).magnitude() < scroll_vector.magnitude():
    #         self.player_pos = self.center_screen

    def move_background(self, scroll_vector: pygame.Vector2) -> None:
        """
        Move background
        """
        # Get position player wants to move to
        new_pos = self.screen_pos.copy() + scroll_vector

        # Check for walls
        if self.can_move_to(new_pos):
            self.screen_pos = new_pos
        else:
            self.screen_pos = self.best_effort_move(scroll_vector)

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

    def can_move_to(self, new_position: pygame.Vector2) -> bool:
        """
        Check if the player can move to a desired position
        """
        unscaled_x, unscaled_y = self.pygame_pos_to_numpy(pos=new_position)
        return self.walls[int(unscaled_y), int(unscaled_x)] == 255

    def best_effort_move(self, scroll_vector: pygame.Vector2) -> pygame.Vector2:
        """
        Move background as far as possible in desired direction
        """
        breakpoint()
        numpy_pos = self.pygame_pos_to_numpy(pos=self.screen_pos)
        move_distance = scroll_vector.magnitude() / BG_SCALE_FACTOR
        region_offset = pygame.Vector2(move_distance, move_distance)
        region_lb = numpy_pos - region_offset
        region_ub = numpy_pos + region_offset
        region = self.walls[
            (lby := int(region_lb.y)) : (uby := int(region_ub.y)),
            (lbx := int(region_lb.x)) : (ubx := int(region_ub.x)),
        ]
        free_space = region == 255

        # Construct array of positions that should correlate with free_space array mask
        xs, ys = np.meshgrid(range(lby, uby), range(lbx, ubx))
        xs, ys = xs[free_space.T], ys[free_space.T]

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
