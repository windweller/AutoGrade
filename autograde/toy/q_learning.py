import numpy as np
from gym.utils import seeding
import math
import matplotlib.pyplot as plt
from maze import MazeWorldSmall


def randargmax(b, np_random=None):
    if np_random is None:
        np_random = np.random
    return np_random.choice(np.flatnonzero(b == b.max()))


class Agent(object):
    def __init__(self, env, seed=None):
        self.env = env
        self.np_random, _ = seeding.np_random(seed)

    @property
    def n_states(self):
        return self.env.observation_space.n

    @property
    def n_actions(self):
        return self.env.action_space.n

    def act(self, s, explore):
        raise NotImplementedError

    def update(self, s, a, s1, r, done, verbose=False):
        raise NotImplementedError

    def close(self):
        pass

# No function approximation
# So it's just thinking about value and RL
class TabularQLearningAgent(Agent):
    def __init__(
            self,
            action_space,
            observation_space,
            gamma,
            lr,
            seed=None):

        super().__init__(env=None, seed=seed)
        n = observation_space.n
        m = action_space.n
        self.Q = np.zeros((n, m))

        self.training_episode = 0
        self.lr = lr
        # self._boltzmann_schedule = boltzmann_schedule

        self.gamma = gamma

    def act(self, s, eps):
        # Break ties randomly.
        best_a = randargmax(self.Q[s, :], self.np_random)
        if eps == 0:
            return best_a

        # Epsilon-greedy action selection
        if self.np_random.random_sample() > eps:
            return best_a
        else:
            return self.np_random.choice(range(len(self.Q[s, :])))

    def step(self, s, a, r, s1, done):
        self.update(s, a, r, s1, done)

    def get_q_values(self, s):
        return self.Q[s, :]

    def update(self, s, a, r, s1, done, verbose=False):
        if verbose:
            print(a)
            print({
                'before': self.Q[s, :],
            })
        # update_q_value = q_table[action, state] + alpha * (reward + (gamma_discount * next_state_value) - q_table[action, state])

        self.Q[s, a] += self.lr * (r + self.gamma * np.max(self.Q[s1, :]) - self.Q[s, a])
        if verbose:
            print({'after': self.Q[s, :]})

        if done:
            self.training_episode += 1

    def save(self, path):
        # we are not saving
        np.savez_compressed(path, Q=self.Q, training_episodes=self.training_episode)

    def load(self, path):
        obj = np.load(path)
        self.Q = obj['Q']
        self.training_episode = obj['training_episodes']

    def visualize(self):
        print(self.Q)

# we pretend this is the Stable-baselines training loop that we are not allowed to change
def train(agent, env, n_episodes=20, max_step=10,
          eps_start=1.0, eps_end=0.01, eps_decay=0.9, eval_render=True):

    eps = eps_start

    rewards = []
    for episode in range(n_episodes):
        state = env.reset()
        score, done, step_cnt = 0, False, 0
        while not done and step_cnt <= max_step:
            action = agent.act(state, eps=eps)
            next_state, reward, done, _ = env.step(action)
            agent.step(state, action, reward, next_state, done)

            score += reward
            step_cnt += 1
            state = next_state
        eps = max(eps_end, eps_decay * eps)
        rewards.append(score)

    if eval_render:
        state = env.reset()
        score, step_cnt, done = 0, 0, False
        env.render()
        while not done and step_cnt < max_step:
            action = agent.act(state, eps=0)
            next_state, reward, done, _ = env.step(action)
            score += reward
            state = next_state
            step_cnt += 1
            env.render()

    # a plot on reward should be average across all training instances
    return rewards

def plot_average_corr_training_reward():
    n_episodes = 100
    num_of_runs = 100
    avg_rewards = np.zeros(n_episodes)
    for _ in range(num_of_runs):
        env = MazeWorldSmall(program=None)  # correct env
        agent = TabularQLearningAgent(env.action_space,
                                      env.observation_space,
                                      gamma=0.9, lr=0.5,
                                      seed=12345)
        rewards = train(agent, env, n_episodes, eps_end=0, eval_render=False, max_step=10)  # max_step=8
        avg_rewards += np.array(rewards)

    # expected highest reward is 9 (because we have 10% of not getting any reward)
    avg_rewards = avg_rewards / num_of_runs
    plt.plot(avg_rewards)
    plt.hlines(y=9, xmin=0, xmax=n_episodes, linestyle='--') # color ='r',
    plt.xlabel("Episodes")
    plt.ylabel("Reward")
    plt.title(f"Average across {n_episodes} runs, episodic reward")
    plt.show()

def run_once():
    env = MazeWorldSmall(program=None) # correct env
    agent = TabularQLearningAgent(env.action_space,
                                  env.observation_space,
                                  gamma=0.9, lr=0.5,
                                  seed=12345)
    # 20 episodes won't work...ha
    train(agent, env, 100, eval_render=True, max_step=8)

# The purpose to reset (evaluate continously) is because
# some games after failing, does not respawn correctly, or reset the game into playable condition
def evaluate_continuously(env, agent, max_step, num_balls_win, eps, finish_reward=100):

    total_reward, step_cnt = 0, 0
    total_win, total_loss = 0, 0
    while (max(total_win, total_loss) < num_balls_win) and step_cnt < max_step:
        score, done = 0, False
        state = env.reset()
        while not done and step_cnt <= max_step:
            action = agent.act(state, eps=eps)
            next_state, reward, done, _ = env.step(action)
            score += reward
            total_reward += reward

            state = next_state
            step_cnt += 1
            # print(step_cnt, score)

        if reward == 10:
            total_win += 1
        elif reward == -5:
            total_loss += 1

    if total_win == 3:
        total_reward += finish_reward
    elif total_loss == 3:
        total_reward -= finish_reward

    return total_reward, total_win, total_loss

# now we are outside the training loop, we can collect data however we want
def execute_agent_collect_data(env, agent, max_step, num_balls_win, eps):
    # finish_reward=100
    # We have not implemented this...

    total_reward, step_cnt = 0, 0
    total_win, total_loss = 0, 0
    trajectory = []
    while (max(total_win, total_loss) < num_balls_win) and step_cnt < max_step:
        score, done = 0, False
        state = env.reset()
        while not done and step_cnt <= max_step:
            action = agent.act(state, eps=eps)
            next_state, reward, done, _ = env.step(action)

            trajectory.append((state, action, reward, next_state))

            score += reward
            total_reward += reward

            state = next_state
            step_cnt += 1
            # print(step_cnt, score)

        if reward == 10:
            total_win += 1
        elif reward == -5:
            total_loss += 1

    # Not implemented yet
    # if total_win == 3:
    #     total_reward += finish_reward
    # elif total_loss == 3:
    #     total_reward -= finish_reward

    return trajectory

def test_evaluate_continuously():
    env = MazeWorldSmall(program=None)  # correct env
    agent = TabularQLearningAgent(env.action_space,
                                  env.observation_space,
                                  gamma=0.9, lr=0.5,
                                  seed=12345)
    # 20 episodes won't work...ha
    train(agent, env, 150, eval_render=True, max_step=10)  # max_step=8
    for _ in range(30):
        # max_step = 30
        total_reward = evaluate_continuously(env, agent, max_step=30, num_balls_win=3, eps=0., finish_reward=20)
        print(total_reward)

def test_collect_traj():
    env = MazeWorldSmall(program=None)  # correct env
    agent = TabularQLearningAgent(env.action_space,
                                  env.observation_space,
                                  gamma=0.9, lr=0.5,
                                  seed=12345)
    # 20 episodes won't work...ha
    train(agent, env, 150, eval_render=True, max_step=10)  # max_step=8
        # max_step = 30
    traj = execute_agent_collect_data(env, agent, max_step=30, num_balls_win=3, eps=0.)

    print(traj[-5:])

if __name__ == '__main__':
    pass
    # run_once()
    # plot_average_corr_training_reward()
    # test_evaluate_continuously()

    test_collect_traj()