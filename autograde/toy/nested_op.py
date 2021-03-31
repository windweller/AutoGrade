import numpy as np
from gym.utils import seeding
import math
import matplotlib.pyplot as plt
from .maze import MazeWorldSmall, MazeClassifierWrapper
from .gen_programs import get_broken_programs

from .q_learning import TabularQLearningAgent, train, execute_agent_collect_data
from .classifiers import MLPTotalRewardClassifier, LogisticRewardClassifier

def surrogate_nested_optimization(broken_program, agent=None, classifier=None, pretrain_agent=True, number_epochs=50,
                        collection_eps=0., batch_size=5):
    # agent: we can pass in an agent that was trained elsewhere
    # broken_program: let's start with ONE broken program (one possible bug)
    # collection_eps: controls how optimal the agent is

    correct_env = MazeWorldSmall()
    broken_env = MazeWorldSmall(broken_program)
    if agent is None:
        agent = TabularQLearningAgent(correct_env.action_space,
                                      correct_env.observation_space,
                                      gamma=0.9, lr=0.5,
                                      seed=12345)

    if classifier is None:
        classifier = LogisticRewardClassifier()

    if pretrain_agent:
        train(agent, correct_env, 100, eval_render=False, max_step=10)

    cls_losses, cls_accu = [], []
    for _ in range(number_epochs):
        correct_trajs = []
        for _ in range(batch_size):
            correct_traj = execute_agent_collect_data(correct_env, agent, max_step=30, num_balls_win=3, eps=collection_eps)
            correct_trajs.append(correct_traj)

        broken_trajs = []
        for _ in range(batch_size):
            broken_traj = execute_agent_collect_data(broken_env, agent, max_step=30, num_balls_win=3, eps=collection_eps)
            broken_trajs.append(broken_traj)

        loss, accuracy = classifier.train(correct_trajs, broken_trajs)
        cls_losses.append(loss)
        cls_accu.append(accuracy)

        print(f"Loss: {loss}, Accuracy: {accuracy}")

        # now we train agent to enter the error state in a broken environment
        # the classifier needs to be a broken environment detector, and outputs high prob
        # if it identifies the broken env
        train_env = MazeClassifierWrapper(broken_env, classifier=classifier)
        train(agent, train_env, 100, eval_render=False, max_step=20)

    return cls_losses, cls_accu

if __name__ == '__main__':
    import random
    random.seed(15123)

    broken_program = get_broken_programs(1)[0]
    surrogate_nested_optimization(broken_program)
