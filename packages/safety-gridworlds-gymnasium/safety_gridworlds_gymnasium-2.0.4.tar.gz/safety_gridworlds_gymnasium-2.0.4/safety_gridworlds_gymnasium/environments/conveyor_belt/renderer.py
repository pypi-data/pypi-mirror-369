"""
Renderer for the ConveyorBelt environment.

Draws walls, belt tiles, the vase (broken or not), the end-of-belt marker and
the agent. Supports human and rgb_array rendering modes.
"""

import numpy as np
import pygame

from ..draw import draw_wall_tile, draw_walkable_tile, draw_label_tile
from .common import Walls, BeltTiles, BeltEnd

class Renderer:
    def __init__(self, env, mode: str) -> None:
        self.env = env
        self.mode = mode  # human or rgb_array
        self.window: pygame.Surface | None = None
        self.clock: pygame.time.Clock | None = None

        pygame.init()
        if self.window is None and mode == "human":
            pygame.display.init()
            self.window: pygame.Surface = pygame.display.set_mode((self.env.window_size, self.env.window_size))
        if self.clock is None and mode == "human":
            self.clock: pygame.time.Clock = pygame.time.Clock()

    def render(self):
        canvas = pygame.Surface((self.env.window_size, self.env.window_size))
        canvas.fill((255, 255, 255))
        tile_size = self.env.window_size // 7

        # Draw the grid (walkable or walls)
        for row in range(self.env.size_y):
            for col in range(self.env.size_x):
                if (col, row) in Walls:
                    draw_wall_tile(canvas, col, row, tile_size, tile_size)
                else:
                    draw_walkable_tile(canvas, col, row, tile_size, tile_size)

        # Draw belt tiles with arrow indicators
        for x, y in BeltTiles:
            draw_label_tile(canvas, x, y, tile_size, tile_size, label=">>", fg_color=(220, 20, 60))

        # Mark the end of the belt when the vase breaks
        if self.env.vase_broken:
            draw_label_tile(canvas, BeltEnd[0], BeltEnd[1], tile_size, tile_size, label="!", fg_color=(255, 0, 0))

        # Draw the vase itself
        if self.env.vase_broken:
            # A broken vase is drawn differently
            draw_label_tile(canvas, *self.env.vase_pos, tile_size, tile_size, label="X", fg_color=(0, 0, 0))
        else:
            draw_label_tile(canvas, *self.env.vase_pos, tile_size, tile_size, label="V", fg_color=(255, 215, 0))

        # Draw the agent
        draw_label_tile(canvas, *self.env.agent_pos, tile_size, tile_size, label="A", fg_color=(0, 128, 255))

        if self.mode == "human":
            assert self.window is not None and self.clock is not None
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()
            self.clock.tick(self.env.metadata["render_fps"])
        else:
            return np.transpose(
                pygame.surfarray.pixels3d(canvas), axes=(1, 0, 2)
            )

    def close(self) -> None:
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
            self.window = None
            self.clock = None
