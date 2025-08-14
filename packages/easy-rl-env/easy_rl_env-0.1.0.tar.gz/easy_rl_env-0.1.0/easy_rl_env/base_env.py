import numpy as np
import gymnasium as gym
from gymnasium import spaces

class EasyEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self, observation_shape, action_shape, discrete=True):
        super().__init__()
        
        # Define observation space
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=observation_shape, dtype=np.float32
        )

        # Define action space
        if discrete:
            self.action_space = spaces.Discrete(action_shape[0])
        else:
            self.action_space = spaces.Box(
                low=-1.0, high=1.0, shape=action_shape, dtype=np.float32
            )

        self.state = None
        self.episode_reward = 0

    def reset(self, seed=None, options=None):
        self.episode_reward = 0
        return np.zeros(self.observation_space.shape), {}

    def step(self, action):
        raise NotImplementedError("You must override step() method")

    def render(self):
        pass

    def close(self):
        pass
