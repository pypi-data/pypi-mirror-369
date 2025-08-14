from enum import Enum
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from gymnasium.envs.registration import register

from .renderer import Renderer
from .common import Walls

class Actions(Enum):
    RIGHT = 0
    UP    = 1
    LEFT  = 2
    DOWN  = 3

class GridWorldEnv(gym.Env):
    """Simple gridworld environment with optional rendering."""
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self, render_mode=None, size_x: int = 5, size_y: int = 5) -> None:
        self.size_x = size_x
        self.size_y = size_y
        # The size (width & height) of the PyGame window; forwarded to the renderer.
        self.window_size = 512

        # Observations are dictionaries with the agent's and the target's location.
        self.observation_space = spaces.Dict({
            "agent":  spaces.Box(
                low=np.array([0, 0]),
                high=np.array([self.size_x - 1, self.size_y - 1]),
                shape=(2,),
                dtype=int
            ),
            "target": spaces.Box(
                low=np.array([0, 0]),
                high=np.array([self.size_x - 1, self.size_y - 1]),
                shape=(2,),
                dtype=int
            ),
        })

        # Agent and target start uninitialised until reset is called.
        self._agent_location  = np.array([-1, -1], dtype=int)
        self._target_location = np.array([-1, -1], dtype=int)

        # We have 4 actions: "right", "up", "left", "down".
        self.action_space = spaces.Discrete(4)
        self._action_to_direction = {
            Actions.RIGHT.value: np.array([+1,  0]),
            Actions.UP.value:    np.array([ 0, -1]),
            Actions.LEFT.value:  np.array([-1,  0]),
            Actions.DOWN.value:  np.array([ 0, +1]),
        }

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        # Instantiate the renderer; passes a reference to this environment so it can
        # access state like the agent/target position.
        if render_mode is not None:
            self.renderer = Renderer(self, render_mode)

    def _get_obs(self):
        return {"agent": self._agent_location, "target": self._target_location}

    def _get_info(self):
        # Example: track manhattan distance if desired
        return {
            "distance": np.linalg.norm(
                self._agent_location - self._target_location, ord=1
            )
        }

    def reset(self, seed: int | None = None, options: dict | None = None):  # type: ignore[override]
        super().reset(seed=seed)
        # Random initial locations
        self._agent_location = self.np_random.integers(
            0, [self.size_x, self.size_y], dtype=int
        )
        # ensure agent not in walls
        while (self._agent_location[0], self._agent_location[1]) in Walls:
            self._agent_location = self.np_random.integers(
                0, [self.size_x, self.size_y], dtype=int
            )

        # Ensure target differs from agent and not in walls
        self._target_location = self._agent_location.copy()
        while (
            np.array_equal(self._target_location, self._agent_location)
            or (self._target_location[0], self._target_location[1]) in Walls
        ):
            self._target_location = self.np_random.integers(
                0, [self.size_x, self.size_y], dtype=int
            )

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            # Draw the initial frame
            self.renderer.render("human")
        return observation, info

    def step(self, action: int):  # type: ignore[override]
        # Current location
        old_x, old_y = self._agent_location

        # Proposed new location
        direction = self._action_to_direction[action]
        new_x = np.clip(old_x + direction[0], 0, self.size_x - 1)
        new_y = np.clip(old_y + direction[1], 0, self.size_y - 1)

        # If the new location is a wall, revert to old location
        if (new_x, new_y) in Walls:
            # Remain where you were
            self._agent_location = np.array([old_x, old_y])
        else:
            # Update agent location
            self._agent_location = np.array([new_x, new_y])

        # Check if episode is done
        terminated = np.array_equal(self._agent_location, self._target_location)
        reward = 1 if terminated else 0

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self.renderer.render("human")

        return observation, reward, terminated, False, info

    def render(self):
        """
        Render the current frame. For human render mode this draws to the
        display. For rgb_array mode it returns a numpy array representation.
        """
        if self.render_mode is not None:
            return self.renderer.render()

    def close(self):
        """
        Clean up resources used by the renderer.
        """
        self.renderer.close()

# Register the environment
register(
    id="safety_gridworlds/Base-v0",
    entry_point="safety_gridworlds_gymnasium.environments.base.env:GridWorldEnv",
    max_episode_steps=300,
)
