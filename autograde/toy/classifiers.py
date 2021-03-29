import sklearn
import sklearn.linear_model
import numpy as np

class Classifier(object):

    def predict_reward(self, state, a, reward, next_state, game_done):
        # the type signature matches returns from the environment's step
        raise Exception("Not implemented")

    def train(self, correct_trajs, broken_trajs):
        raise Exception("Not implemented")

class LogisticRewardClassifier(Classifier):
    def __init__(self, use_prob_as_reward=False):
        self.cls = sklearn.linear_model.LogisticRegression()
        self.total_reward = 0
        self.use_prob_as_reward = use_prob_as_reward

    def predict_reward(self, state, a, reward, next_state, game_done):
        # only return a reward when the game has ended
        # game ends when a winning condition or losing condition is met
        # can be explicitly set
        self.total_reward += reward
        if game_done:
            if not self.use_prob_as_reward:
                rew = self.cls.predict(np.array([self.total_reward]).reshape(1, 1))
            else:
                rew = self.cls.predict_proba(np.array([self.total_reward]).reshape(1, 1))
            return rew
        return 0

    def train(self, correct_trajs, broken_trajs):
        X, y = self.process_data(correct_trajs, broken_trajs)
        self.cls.fit(X, y)

        y_pred = self.cls.predict(X)
        y_prob = self.cls.predict_proba(X)

        accu = sklearn.metrics.accuracy_score(y, y_pred)
        loss = sklearn.metrics.log_loss(y, y_prob)

        return accu, loss

    def process_data(self, correct_trajs, broken_trajs):
        # broken=1, correct=0;
        X, y = [], []
        for correct_traj in correct_trajs:
            rs = [tup[2] for tup in correct_traj]
            total_r = sum(rs)
            X.append(total_r)
            y.append(0)

        for broken_traj in broken_trajs:
            rs = [tup[2] for tup in broken_traj]
            total_r = sum(rs)
            X.append(total_r)
            y.append(1)

        return np.array(X).reshape(-1, 1), np.array(y)


# these all need to expect vectorized values
# but that's not too difficult to coordinate
class MLPTotalRewardClassifier(Classifier):
    def __init__(self, use_prob_as_reward=False):
        self.cls = sklearn.neural_network.multilayer_perceptron.MLPClassifier(alpha=0)
        self.total_reward = 0
        self.use_prob_as_reward = use_prob_as_reward

    def predict_reward(self, state, next_state, a, reward, game_done):
        # only return a reward when the game has ended
        # game ends when a winning condition or losing condition is met
        # can be explicitly set
        self.total_reward += reward
        if game_done:
            if not self.use_prob_as_reward:
                rew = self.cls.predict(np.array([self.total_reward]).reshape(1, 1))
            else:
                rew = self.cls.predict_proba(np.array([self.total_reward]).reshape(1, 1))
            return rew
        return 0

    def store(self, state, next_state, a, reward, game_done):
        # process and store the training data...
        pass

    def process_data(self, correct_trajs, broken_trajs):
        # how often do we do this?
        # Also, it's not as if the old data were lost
        # It's still in MLP's memory
        X, y = [], []