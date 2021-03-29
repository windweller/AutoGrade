"""
Currently all wrappers are for Bounce

Modified from https://github.com/openai/coinrun/blob/master/coinrun/wrappers.py
"""

import gym
import numpy as np
import cv2
from collections import deque

class VelAndSkipEnv(gym.Wrapper):
    def __init__(self, env=None, skip=1, history_window=2):
        """skip n states, but compute velocity using first and last"""
        super(VelAndSkipEnv, self).__init__(env)
        # most recent raw observations (for max pooling across time steps)
        self._obs_buffer = deque(maxlen=history_window)
        self._skip = skip

        # used to be 3 (x, y, paddle_x)
        # now we want:
        # current locations, change from previous location
        # (x, y, paddle_x, x - x', y - y', paddle_x - paddle_x')
        # the last 4 dimensions should be close to +1, -1 (or most +2, -2)
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(6,), dtype=np.float)

    def step(self, action):
        total_reward = 0.0
        done = None
        for _ in range(self._skip):
            obs, reward, done, info = self.env.step(action)
            self._obs_buffer.append(obs)
            total_reward += reward
            if done:
                break

        # max_frame = np.max(np.stack(self._obs_buffer), axis=0)
        # can't pop!
        last = self._obs_buffer[-1]
        first = self._obs_buffer[0]

        vel_frame = np.concatenate([last, last-first], axis=0)

        return vel_frame, total_reward, done, info

    # override reset so that it won't go wrong...
    def reset(self, **kwargs):
        obs = self.env.reset(**kwargs)
        expanded_obs = np.concatenate([obs, np.array([0, 0, 0])], axis=0)
        return expanded_obs

class EpsilonGreedyWrapper(gym.Wrapper):
    """
    Wrapper to perform a random action each step instead of the requested action,
    with the provided probability.
    """

    def __init__(self, env, prob=0.05):
        gym.Wrapper.__init__(self, env)
        self.prob = prob
        self.num_envs = env.num_envs

    def reset(self):
        return self.env.reset()

    def step(self, action):
        if np.random.uniform() < self.prob:
            action = np.random.randint(self.env.action_space.n, size=self.num_envs)

        return self.env.step(action)

class ResizeFrame(gym.ObservationWrapper):
    def __init__(self, env):
        """
        Warp frames to 84x84 as done in the Nature paper and later work.

        Does not cast GRAYSCALE (because it leads to weird image)
        This wrapper is ONLY used with recurrent policy

        :param env: (Gym Environment) the environment
        """
        gym.ObservationWrapper.__init__(self, env)
        self.width = 84
        self.height = 84
        self.observation_space = gym.spaces.Box(low=0, high=255, shape=(self.height, self.width, 3),
                                            dtype=env.observation_space.dtype)

    def observation(self, frame):
        """
        returns the current observation from a frame

        :param frame: ([int] or [float]) environment frame
        :return: ([int] or [float]) the observation
        """
        frame = cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_AREA)
        return frame
