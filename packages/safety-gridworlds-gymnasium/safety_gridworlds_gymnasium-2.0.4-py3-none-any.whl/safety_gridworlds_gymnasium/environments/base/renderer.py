"""
Renderer for the simple GridWorld environment.

The renderer encapsulates all Pygame drawing logic, keeping it separate from
the environment's core logic. It supports both `human` mode (drawing to a
window) and `rgb_array` mode (returning a numpy array of pixel values).
"""

import numpy as np
import pygame

from ..draw import draw_wall_tile, draw_walkable_tile, draw_label_tile
from .common import Walls

class Renderer:
    def __init__(self, env, mode: str) -> None:
        self.env = env
        self.mode = mode  # human or rgb_array
        self.window: pygame.Surface | None = None
        self.clock: pygame.time.Clock | None = None
        
        pygame.init()
        if self.window is None and mode == "human":
            pygame.display.init()
            self.window = pygame.display.set_mode((self.env.window_size, self.env.window_size))
        if self.clock is None and mode == "human":
            self.clock = pygame.time.Clock()

    def render(self):
        # Create a canvas to draw on
        canvas = pygame.Surface((self.env.window_size, self.env.window_size))
        canvas.fill((255, 255, 255))

        # Compute tile sizes
        tile_size_x = self.env.window_size // self.env.size_x
        tile_size_y = self.env.window_size // self.env.size_y

        # Draw the grid (walkable or walls)
        for row in range(self.env.size_y):
            for col in range(self.env.size_x):
                if (col, row) in Walls:
                    draw_wall_tile(canvas, col, row, tile_size_x, tile_size_y)
                else:
                    draw_walkable_tile(canvas, col, row, tile_size_x, tile_size_y)

        # Draw agent
        agent_x, agent_y = self.env._agent_location
        draw_label_tile(
            canvas, agent_x, agent_y, tile_size_x, tile_size_y,
            label="A", fg_color=(0, 128, 255)
        )

        # Draw goal
        goal_x, goal_y = self.env._target_location
        draw_label_tile(
            canvas, goal_x, goal_y, tile_size_x, tile_size_y,
            label="G", fg_color=(0, 255, 0)
        )

        if self.mode == "human":
            # Blit the canvas onto the window and update the display
            assert self.window is not None and self.clock is not None
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()
            self.clock.tick(self.env.metadata["render_fps"])
        else:  # "rgb_array"
            return np.transpose(
                pygame.surfarray.pixels3d(canvas), axes=(1, 0, 2)
            )

    def close(self) -> None:
        # Close the Pygame window if it was created
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
            self.window = None
            self.clock = None
