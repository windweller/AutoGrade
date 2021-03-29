import numpy as np
import sys
import gym
from gym.envs.toy_text import discrete
import torch
# import envs.utils_seeding as seeding

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

#GAME_FAIL_BUG = 4  # game will enter fail state instantly (receive penalty), and immediately end
#GAME_BROKE_BUG = 5  # immediately ends, with no reward or anything

GAME_FAIL_BUG = 4  # game will fail, receive negative penalty (e.g. paddle doesn't bounce)
GAME_CRASH_BUG = 5  # Game will crash
GAME_HALT_BUG = 6  # Will get stuck in this state forever (e.g. wall doesn't bounce; ball doesn't launch)
GAME_REWARD_BUG = 7  # will dish out reward at the bug time, won't end game

# class RNG(object):
#     def __init__(self):
#         self.np_random = None
#         self.curr_seed = None
#
#     def seed(self, seed=None):
#         self.np_random, seed = seeding.np_random(seed)
#         self.curr_seed = seed
#         return [seed]
#
#     def choice(self, a, size=None, replace=True, p=None):
#         return self.np_random.choice(a, size, replace, p)
#
#     def randint(self, low, high=None, size=None, dtype=int):
#         return self.np_random.randint(low, high, size, dtype)

# Adapted from CliffWalk
# https://github.com/prabodhhere/cliffwalker/blob/master/lib/envs/cliff_walking.py

class MazeWorldSmall(discrete.DiscreteEnv):
    """
    Maze World captures:
    1. Random initial condition / position
    (Can be understood as student set random seed, or some random choice)
    2. Linear classifier
    (We simulate the decision boundary by saying 80% get reward at O, otherrwise penalty, simulate failure)
    (Also, we give 10 steps budget, random init position, agent will not terminate and just exhaust its budget)
    (This makes reward different)
    3. Can manually specify sub-policy and execute
    (add bandit or thompson sampling)
    4. Can have cascading errors in this (have another error block the true error) (overlapping error)
    (for example, we train to discover one error, but we have another error blocking it)

    E  o  o  o  G
    o  F  o  F  o
    x  o  x  o  o
    o  F  o  F  o
    o  o  x  o  o

     x: agent initial location
     E: error locations
     G: goal state
     o: possible error locations
    """
    def __init__(self, program=None, seed=None, stochastic_reward=True):
        """
        :param program: is a {(x, x): 4/5/6} list of tuples showing where the pitfall is. If not set, the env is correct.
                             4/5/6 is the bug type: 4 - game fail, 5 - game halt (never fails or win), 6 - get reward (not end game)

        :param stochastic_reward: a small chance (10%) not receiving reward (for linear classifier boundary)

        state coverage is a concept for agent (an agent can be optimal but wanders around a lot)
        (Eps can be used to control agent optimality)
        """
        assert type(program) == dict or program is None

        self.shape = (5, 5)
        self.stochastic_reward = stochastic_reward
        self.seed(seed)

        # start index will actually be random
        possible_start_locs = [(2, 0), (4, 2), (2, 2)]
        # self.start_state_index = np.ravel_multi_index(rand_start_pos, self.shape)

        nS = np.prod(self.shape)
        nA = 4

        # Pitfall location
        # Just one spot in the maze that can be the pitfall
        self.program = program if program is not None else {}
        self._errors = np.zeros(self.shape, dtype=np.bool)
        if program is not None:
            for loc in program.keys():
                self._errors[loc] = True

        self._pitfalls = np.zeros(self.shape, dtype=np.bool)
        for pos in [(1, 1), (3, 1), (1, 3), (3, 3)]:
            self._pitfalls[pos] = True

        # Calculate transitiotn probabilities and rewards
        P = {}
        for s in range(nS):
            position = np.unravel_index(s, self.shape)
            P[s] = {a: [] for a in range(nA)}
            P[s][UP] = self._calculate_transition_prob(position, [-1, 0])
            P[s][RIGHT] = self._calculate_transition_prob(position, [0, 1])
            P[s][DOWN] = self._calculate_transition_prob(position, [1, 0])
            P[s][LEFT] = self._calculate_transition_prob(position, [0, -1])

        # Calculate initial state distribution
        # We always start in state (3, 0)
        isd = np.zeros(nS)
        uniform_prob = 1. / len(possible_start_locs)
        for pos in possible_start_locs:
            idx = np.ravel_multi_index(pos, self.shape)
            isd[idx] = uniform_prob

        super(MazeWorldSmall, self).__init__(nS, nA, P, isd)

    def _limit_coordinates(self, coord):
        """
        Prevent the agent from falling out of the grid world
        :param coord:
        :return:
        """
        coord[0] = min(coord[0], self.shape[0] - 1)
        coord[0] = max(coord[0], 0)
        coord[1] = min(coord[1], self.shape[1] - 1)
        coord[1] = max(coord[1], 0)
        return coord

    def _calculate_transition_prob(self, current, delta):
        """
        Determine the outcome for an action. Transition Prob is always 1.0.
        :param current: Current position on the grid as (row, col)
        :param delta: Change in position for transition
        :return: (1.0, new_state, reward, done)
        """
        # Need to do a halting check (any "bug", we don't escape)
        cur_position = tuple(np.array(current))
        if cur_position in self.program:
            if self.program[cur_position] == GAME_HALT_BUG:
                return [(1.0, np.array(current), 0, False)]
        cur_state = np.ravel_multi_index(cur_position, self.shape)

        new_position = np.array(current) + np.array(delta)
        new_position = self._limit_coordinates(new_position).astype(int)
        new_state = np.ravel_multi_index(tuple(new_position), self.shape)
        # 1. Error overrides everything, including winning and
        # 2. Error has types
        if self._errors[tuple(new_position)]:
            # this is a programming error condition
            bug_type = self.program[tuple(new_position)]
            # we assume for crash/fail, you don't reach the bug state ever
            # game terminates and you are on previous states; this makes classifier work harder
            if bug_type == GAME_FAIL_BUG:
                return [(1.0, cur_state, -5, True)]
            elif bug_type == GAME_CRASH_BUG:
                return [(1.0, cur_state, 0, True)]  # DONE
            elif bug_type == GAME_HALT_BUG:
                return [(1.0, new_state, 0, False)]  # will get into the new state and stay there
            elif bug_type == GAME_REWARD_BUG:
                return [(1.0, new_state, 10, False)]
            else:
                raise Exception(f"Game bug type {bug_type} not implemented")

        elif self._pitfalls[tuple(new_position)]:
            # this is the "failure" condition natural from the environment
            return [(1.0, new_state, -5, True)]

        terminal_state = (0, self.shape[0] - 1)
        is_done = tuple(new_position) == terminal_state
        r = 0 if not is_done else 10
        return [(1.0, new_state, r, is_done)]

    # need to mask this...
    def step(self, a):
        try:
            transitions = self.P[self.s][a]
        except:
            s = np.ravel_multi_index(self.s, self.shape)
            transitions = self.P[s][a]

        i = discrete.categorical_sample([t[0] for t in transitions], self.np_random)
        p, s, r, d= transitions[i]
        self.s = s
        self.lastaction = a
        if r == 10 and self.stochastic_reward:
            # terminal state
            r = 0 if self.np_random.rand() < 0.2 else r

        return (s, r, d, {"prob" : p})

    def render(self, mode='human', close=False):
        if close: return
        outfile = sys.stdout

        for s in range(self.nS):
            position = np.unravel_index(s, self.shape)
            if self.s == s:
                output = " x "
            # Print terminal state
            # Bug has the highest printing priority
            elif self._errors[position]:
                output = " B "
            elif position == (0, self.shape[0] - 1):
                output = " G "
            elif self._pitfalls[position]:
                output = " F "
            else:
                output = " o "

            if position[1] == 0:
                output = output.lstrip()
            if position[1] == self.shape[1] - 1:
                output = output.rstrip()
                output += '\n'

            outfile.write(output)
        outfile.write('\n')

class MazeClassifierWrapper(gym.Env):
    def __init__(self, env, classifier=None):
        self.env = env
        self.classifier = classifier
        self.action_space = self.env.action_space
        self.observation_space = self.env.observation_space

        # it's easy to keep some history in environment
        # all the "stacking" wrappers do this
        self.current_state = None

    def step(self, a):
        # this is a wrapper that uses classifier to determine reward
        # This cannot be in the training loop because we are using library like Stable-baselines
        # So we can't control their training loop...
        next_state, reward, game_done, p = self.env.step(a)
        if self.classifier is not None:
            # we can wait till the game ends and then give reward
            reward = self.classifier.predict_reward(self.current_state, a, reward, next_state, game_done)

        self.current_state = next_state

        return next_state, reward, game_done, p

    def reset(self):
        s = self.env.reset()
        self.current_state = s
        return s

    def render(self, mode='human', close=False):
        self.env.render(mode, close)

# this is an abstraction over the true environment
# class MazeRLEnv(gym.Env):
#     def __init__(self, program, stochastic_reward=True, number_to_win=1,
#                  finish_reward=20,
#                  classifier=None):
#         # num_positive_reward: sets the terminal condition
#         # we will use classifier to generate reward if specified here
#
#         self.env = MazeWorldSmall(program, stochastic_reward=stochastic_reward)
#         self.number_to_win = number_to_win
#
#         self.total_win, self.total_loss = 0, 0
#         self.finish_reward = finish_reward
#         self.classifier = classifier
#
#     def step(self, a):
#         # we actually don't know if the game succeeds or not
#         # we only observe reward
#         next_state, reward, game_done, p = self.env.step(a)
#         if reward == 10:
#             self.total_win += 1
#         elif reward == -5:
#             self.total_loss += 1
#
#         # not entirely sure if this part is correct
#         if game_done:
#             next_state = self.env.reset()
#
#         if self.total_win == self.number_to_win:
#             done = True
#             reward += self.finish_reward
#         elif self.total_loss == self.number_to_win:
#             done = True
#             reward -= self.finish_reward
#
#         return next_state, reward, done, {'total_win': self.total_win,
#                                           'total_loss': self.total_loss}
#
#     def render(self, mode='human', close=False):
#         self.env.render(mode, close)


if __name__ == '__main__':
    env = MazeWorldSmall(program={(0, 3): GAME_CRASH_BUG,
                                  (1, 4): GAME_CRASH_BUG})
    s = env.reset()
    print(env.s)
    print(env.render())