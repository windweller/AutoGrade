# Training methods are stored here

from tqdm import tqdm

import numpy as np
import torch

from collections import deque
import torch.optim as optim

from sklearn.mixture import GaussianMixture
from sklearn.neural_network import MLPClassifier
from autograde.toy_car.classifiers import VAE, train_vae_one_epoch, compute_vae_loss, HoareLSTM, train_lstm_one_epoch

from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.linear_model import LogisticRegression

from autograde.toy_car.car import CarEnv

from collections import deque

# ========= MLP =========

def train_naive_supervised_classifier(policy, epochs=100, history_window=4):
    X = deque(maxlen=100)
    y = deque(maxlen=100)

    feat_dim = 4

    cls = MLPClassifier(solver='lbfgs', alpha=1e-5,
                        hidden_layer_sizes=(100, 100), random_state=1)

    env = CarEnv()  # 0
    bug_env = CarEnv(bug=True)  # 1

    test_accu = []

    # reset after 5 epochs
    for e in tqdm(range(epochs)):
        states = []
        state_buffer = deque(maxlen=history_window)

        state = env.reset()
        state_buffer.append(state)
        for i in range(30):
            # replace here with real policy
            state, reward, done, _ = env.step(policy.get_action(state))
            if len(state_buffer) == history_window:
                states.append(np.concatenate(state_buffer))
            state_buffer.append(state)
            if done:
                break
        states = np.vstack(states)
        X.append(states)
        y.append(np.ones(states.shape[0]))

        # bug_env
        states = []
        state_buffer = deque(maxlen=history_window)

        state = bug_env.reset()
        state_buffer.append(state)
        for i in range(30):
            # replace here with real policy
            state, reward, done, _ = bug_env.step(policy.get_action(state))
            if len(state_buffer) == history_window:
                states.append(np.concatenate(state_buffer))
            state_buffer.append(state)
            if done:
                break
        states = np.vstack(states)
        X.append(states)
        y.append(np.ones(states.shape[0]))

        cls.fit(np.vstack(X), np.concatenate(y))

        # get test set
        if e % 5 == 0:
            test_X, test_y = [], []
            for _ in range(5):
                states = []
                labels = []

                state = bug_env.reset()
                state_buffer = deque(maxlen=history_window)

                state_buffer.append(state)
                # labels.append(0)
                for i in range(30):
                    # replace here with real policy
                    state, reward, done, info = bug_env.step(policy.get_action(state))
                    if len(state_buffer) == history_window:
                        states.append(np.concatenate(state_buffer))
                        if info['bug_state']:
                            labels.append(1)
                        else:
                            labels.append(0)

                    state_buffer.append(state)

                    if done:
                        break

                assert len(states) == len(labels)
                states = np.vstack(states)
                test_X.append(states)
                test_y.append(np.array(labels))

            test_X, test_y = np.vstack(test_X), np.concatenate(test_y)
            test_y_hat = cls.predict(test_X)

            accu = accuracy_score(test_y_hat, test_y)
            test_accu.append(accu)

    return test_accu

# ========= GMM =============

def train_naive_gmm_model(policy, epochs=100, history_window=4):
    X = deque(maxlen=100)

    feat_dim = 4

    # model = VAE(feat_dim * history_window)
    # optimizer = optim.Adam(model.parameters(), lr=1e-5)

    model = GaussianMixture(n_components=5, covariance_type='full', max_iter=500)

    env = CarEnv()  # 0
    bug_env = CarEnv(bug=True)  # 1

    test_accu = []
    train_losses = []

    # reset after 5 epochs
    for e in tqdm(range(epochs)):
        states = []
        state_buffer = deque(maxlen=history_window)

        state = env.reset()
        state_buffer.append(state)
        for i in range(30):
            # replace here with real policy
            state, reward, done, _ = env.step(policy.get_action(state))
            if len(state_buffer) == history_window:
                states.append(np.concatenate(state_buffer))
            state_buffer.append(state)
            if done:
                break
        states = np.vstack(states)
        X.append(states)

        model.fit(np.vstack(X))

        # get test set
        if e % 5 == 0:
            test_X, test_y = [], []
            for _ in range(5):
                states = []
                labels = []

                state = bug_env.reset()
                state_buffer = deque(maxlen=history_window)

                state_buffer.append(state)
                # labels.append(0)
                for i in range(30):
                    # replace here with real policy
                    state, reward, done, info = bug_env.step(policy.get_action(state))
                    if len(state_buffer) == history_window:
                        states.append(np.concatenate(state_buffer))
                        if info['bug_state']:
                            labels.append(1)
                        else:
                            labels.append(0)

                    state_buffer.append(state)

                    if done:
                        break

                assert len(states) == len(labels)
                states = np.vstack(states)
                test_X.append(states)
                test_y.append(np.array(labels))

            test_X, test_y = np.vstack(test_X), np.concatenate(test_y)
            test_y_hat = model.predict(test_X)

            accu = accuracy_score(test_y_hat, test_y)
            test_accu.append(accu)

    return test_accu, train_losses

# ===== VAE =======

# TODO: add CUDA
# TODO: 1). Data need to be in CUDA; 2). Model needs to be in CUDA
def train_naive_vae_model(policy, env, bug_env, epochs=100, history_window=4, cuda=False):
    X = deque(maxlen=100)

    feat_dim = 4

    model = VAE(feat_dim * history_window)
    if cuda:
        model = model.to('cuda')

    optimizer = optim.Adam(model.parameters(), lr=1e-5)

    #env = CarEnv()  # 0
    #bug_env = CarEnv(bug=True)  # 1

    test_accu = []
    bug_precision, bug_recall = [], []

    train_losses = []

    # reset after 5 epochs
    for e in tqdm(range(epochs)):
        states = []
        state_buffer = deque(maxlen=history_window)

        state = env.reset()
        state_buffer.append(state)
        for i in range(30):
            # replace here with real policy
            state, reward, done, _ = env.step(policy.get_action(state))
            if len(state_buffer) == history_window:
                states.append(np.concatenate(state_buffer))
            state_buffer.append(state)
            if done:
                break
        states = np.vstack(states)
        X.append(states)

        # inner VAE optimization loop
        for _ in range(10):
            loss = train_vae_one_epoch(model, optimizer, torch.from_numpy(np.vstack(X)).float(), cuda=cuda)
            train_losses.append(loss)

        # get test set
        if e % 5 == 0:
            test_X, test_y = [], []
            for _ in range(5):
                states = []
                labels = []

                state = bug_env.reset()
                state_buffer = deque(maxlen=history_window)

                state_buffer.append(state)
                # labels.append(0)
                for i in range(30):
                    # replace here with real policy
                    state, reward, done, info = bug_env.step(policy.get_action(state))
                    if len(state_buffer) == history_window:
                        states.append(np.concatenate(state_buffer))
                        if info['bug_state']:
                            labels.append(1)
                        else:
                            labels.append(0)

                    state_buffer.append(state)

                    if done:
                        break

                assert len(states) == len(labels)
                states = np.vstack(states)
                test_X.append(states)
                test_y.append(np.array(labels))

            test_X, test_y = np.vstack(test_X), np.concatenate(test_y)
            test_y_hat = compute_vae_loss(model, torch.from_numpy(np.vstack(test_X)).float(), cuda=cuda) > np.mean(train_losses[-100:])

            accu = accuracy_score(test_y, test_y_hat)
            test_accu.append(accu)

            prec, rec, f1, _ = precision_recall_fscore_support(test_y, test_y_hat)
            if np.sum(test_y) > 1:
                bug_precision.append(prec[1])  # 2nd label is bug
                bug_recall.append(rec[1])
            else:
                bug_precision.append(np.nan)
                bug_recall.append(np.nan)

    return test_accu, bug_precision, bug_recall, train_losses

# ===== Sequential Autoencoder =======

import torch.nn as nn
l1_loss = nn.L1Loss(reduction='mean')

# TODO: add action to it
def train_naive_sae_lstm_model(policy, env, bug_env, epochs=100, history_window=4, cuda=False):
    feat_dim = 4

    lstm = HoareLSTM(4, batch_size=4)
    if cuda:
        lstm = lstm.to('cuda')

    optimizer = optim.Adam(lstm.parameters(), lr=1e-3)

    #env = CarEnv()  # 0
    #bug_env = CarEnv(bug=True)  # 1

    test_accu = []
    bug_precision, bug_recall = [], []

    train_losses = []

    # reset after 5 epochs
    for e in tqdm(range(epochs)):

        states = []
        state = env.reset()
        states.append(state)
        for i in range(30):
            # replace here with real policy
            state, reward, done, _ = env.step(policy.get_action(state))
            states.append(state)
            if done:
                break

        states = np.vstack(states)
        lstm.store(states)  # 1 data point in the batch

        # inner VAE optimization loop
        # for _ in range(10):
        #    loss = train_vae_one_epoch(model, optimizer, torch.from_numpy(np.vstack(X)).float())
        #    train_losses.append(loss)

        for _ in range(3):
            loss = train_lstm_one_epoch(lstm, optimizer, l1_loss, cuda=cuda)
            train_losses.append(np.mean(loss))  # average batch loss

        # get test set
        if e % 5 == 0:
            preds_y, test_y = [], []
            for _ in range(5):
                states = []
                preds = []
                labels = []

                state = bug_env.reset()
                hiddens = None

                # labels.append(0)
                for i in range(30):

                    # do a prediction here
                    y_hat, hiddens = lstm.predict_post_state(state, pre_state=hiddens, cuda=cuda)

                    # replace here with real policy
                    state, reward, done, info = bug_env.step(policy.get_action(state))
                    if info['bug_state']:
                        labels.append(1)
                    else:
                        labels.append(0)

                    # TODO: this is not quite correct...
                    dist = lstm.get_distance(y_hat, state)
                    preds.append(dist > np.mean(train_losses[-10:]))
                    states.append(state)

                    if done:
                        break

                assert len(preds) == len(labels)
                states = np.vstack(states)
                preds_y.append(np.array(preds))
                test_y.append(np.array(labels))

            test_y = np.concatenate(test_y)
            preds_y = np.concatenate(preds_y)

            accu = accuracy_score(test_y, preds_y)
            test_accu.append(accu)

            prec, rec, f1, _ = precision_recall_fscore_support(test_y, preds_y)
            # sometimes there's just no bug at all
            if np.sum(test_y) > 1:
                bug_precision.append(prec[1])  # 2nd label is bug
                bug_recall.append(rec[1])
            else:
                bug_precision.append(np.nan)
                bug_recall.append(np.nan)

    return test_accu, bug_precision, bug_recall, train_losses

# ======== HoareLSTM ========
def train_naive_hoare_lstm_model(policy, env, bug_env, epochs=100, history_window=4, hoare_threshold=0.01,
                                 fresh_lstm=False, cuda=False, delta=False, action_input=False,
                                 batch_size=4, test_every=5):
    lstm = HoareLSTM(4, batch_size=batch_size, delta=delta,
                     action_input=action_input)
    if cuda:
        lstm = lstm.to('cuda')
    optimizer = optim.Adam(lstm.parameters(), lr=1e-3)

    bug_lstm = HoareLSTM(4, batch_size=batch_size, delta=delta, action_input=action_input)
    if cuda:
        bug_lstm = bug_lstm.to('cuda')
    bug_optimizer = optim.Adam(bug_lstm.parameters(), lr=1e-3)

    return train_naive_hoare_lstm_model_inner(policy, lstm, bug_lstm, optimizer, bug_optimizer,
                                       env, bug_env, epochs, history_window, hoare_threshold,
                                       fresh_lstm, cuda, delta, action_input, batch_size,
                                       test_every)

# this is to help joint training with DQN
def train_naive_hoare_lstm_model_inner(policy, lstm, bug_lstm, optimizer, bug_optimizer,
                                       env, bug_env, epochs=100, history_window=4, hoare_threshold=0.01,
                                       broken_training_epochs=5, correct_training_epoch=5,
                                       fresh_lstm=False, cuda=False, delta=False, action_input=False,
                                       batch_size=4, test_every=5, eps=0, no_correct_lstm_training=False):
    # eps: we do want the policy to be relatively random; because we want to collect as much info as possible

    # dist1, dist2
    # dist1 - dist2 < epsilon_threshold
    # we call it correct, otherwise we go with whichever closer

    # force is 0.2 (each action)
    # so 0.1 threshold is good enough here

    test_accu = []
    bug_precision, bug_recall = [], []  # when we say it's a bug, it is indeed a bug
    train_losses, bug_train_losses = [], []

    correct_traj_states, broken_traj_states = [], []

    # reset after 5 epochs
    for e in tqdm(range(epochs)):

        # we can train correctLSTM on the outside!! elsewhere, till FULL convergence
        # no need to keep it in here...
        # but keep it in here makes training somewhat balanced
        if not no_correct_lstm_training:
            states, actions = [], []
            state = env.reset()
            states.append(state)
            for i in range(30):
                # replace here with real policy
                action = policy.get_action(state, eps=eps)
                state, reward, done, _ = env.step(action)
                states.append(state)
                actions.append(action)
                if done:
                    break

            states = np.vstack(states)
            actions = np.array(actions)
            if action_input:
                lstm.store(states, actions)
            else:
                lstm.store(states)  # 1 data point in the batch
            correct_traj_states.append(states)

            if e % 5 == 0:
                if fresh_lstm:
                    lstm.reset()
                    optimizer = optim.Adam(lstm.parameters(), lr=1e-3)
                    train_epochs = 20
                else:
                    train_epochs = correct_training_epoch
                for _ in range(train_epochs):
                    loss = train_lstm_one_epoch(lstm, optimizer, l1_loss, cuda=cuda)
                    # print("Correct", np.mean(loss))
                    train_losses.append(np.mean(loss))  # average batch loss

        states, actions = [], []
        state = bug_env.reset()
        states.append(state)
        for i in range(30):
            # replace here with real policy
            action = policy.get_action(state, eps=eps)
            state, reward, done, _ = bug_env.step(action)
            states.append(state)
            actions.append(action)
            if done:
                break

        states = np.vstack(states)
        actions = np.array(actions)
        if action_input:
            bug_lstm.store(states, actions)
        else:
            bug_lstm.store(states)  # 1 data point in the batch

        broken_traj_states.append(states)

        if e % 5 == 0:
            if fresh_lstm:
                bug_lstm.reset()
                bug_optimizer = optim.Adam(bug_lstm.parameters(), lr=1e-3)
                train_epochs = 30
            else:
                train_epochs = broken_training_epochs

            for _ in range(train_epochs):
                loss = train_lstm_one_epoch(bug_lstm, bug_optimizer, l1_loss, cuda=cuda)
                # print("Broken", np.mean(loss))
                bug_train_losses.append(np.mean(loss))  # average batch loss

        # get test set
        if e % test_every == 0:
            preds_y, test_y = [], []
            for _ in range(5):
                states, actions = [], []
                preds, labels = [], []

                state = bug_env.reset()
                hiddens, bug_hiddens = None, None

                # labels.append(0)
                for i in range(30):

                    # replace here with real policy
                    action = policy.get_action(state, eps=eps)

                    # do a prediction here
                    inp = state if not action_input else (state, action)
                    y_hat, hiddens = lstm.predict_post_state(inp, pre_state=hiddens, cuda=cuda)
                    bug_y_hat, bug_hiddens = bug_lstm.predict_post_state(inp, pre_state=bug_hiddens, cuda=cuda)

                    # next-state
                    state, reward, done, info = bug_env.step(action)
                    if info['bug_state']:
                        labels.append(1)
                    else:
                        labels.append(0)

                    dist_to_correct = lstm.get_distance(y_hat, state)
                    dist_to_broken = bug_lstm.get_distance(bug_y_hat, state)

                    if np.abs(dist_to_correct - dist_to_broken) < hoare_threshold:
                        preds.append(0)  # 0 means correct
                    else:
                        preds.append(np.argmin([dist_to_correct, dist_to_broken]))

                    # preds.append(dist > np.mean(train_losses[-10:]))
                    states.append(state)
                    actions.append(action)

                    if done:
                        break

                assert len(preds) == len(labels)
                states = np.vstack(states)
                preds_y.append(np.array(preds))
                test_y.append(np.array(labels))

            test_y = np.concatenate(test_y)
            preds_y = np.concatenate(preds_y)

            accu = accuracy_score(test_y, preds_y)
            test_accu.append(accu)

            prec, rec, f1, _ = precision_recall_fscore_support(test_y, preds_y)
            if np.sum(test_y) > 1:
                bug_precision.append(prec[1]) # 2nd label is bug
                bug_recall.append(rec[1])
            else:
                bug_precision.append(np.nan)
                bug_recall.append(np.nan)

    return test_accu, bug_precision, bug_recall, (train_losses, bug_train_losses, lstm, bug_lstm,
                                                  correct_traj_states, broken_traj_states)

def collect_trajs(agent, env, bug_env, epochs, max_t=30, eps=0):
    # reset after 5 epochs
    traj_states = []
    traj_labels = []
    for e in tqdm(range(epochs)):
        states, actions = [], []
        labels = []
        state = bug_env.reset()
        states.append(state)

        for i in range(max_t):
            # do a prediction here

            # replace here with real policy
            state, reward, done, info = bug_env.step(agent.get_action(state, eps))
            if info['bug_state']:
                labels.append(1)
            else:
                labels.append(0)

            states.append(state)

            if done:
                break

        states = np.vstack(states)
        traj_states.append(states)
        traj_labels.append(labels)

    return traj_states, traj_labels

def collect_classifier_behavior_on_traj(agent, env, bug_env, lstm, bug_lstm, epochs,
                                        max_t=30, eps=0, threshold=0.1):

    traj_accus = []
    traj_dists = []  # each dist is a feature for classfication
    traj_labels, traj_preds = [], []

    for e in range(epochs):
        preds_y, test_y = [], []

        states = []
        preds, labels = [], []

        hiddens, bug_hiddens = None, None

        dists = []

        state = bug_env.reset()
        states.append(states)
        for i in range(max_t):
            # do a prediction here
            action = agent.get_action(state, eps=eps)

            inp = (state, action)
            y_hat, hiddens = lstm.predict_post_state(inp, pre_state=hiddens, cuda=True)
            bug_y_hat, bug_hiddens = bug_lstm.predict_post_state(inp, pre_state=bug_hiddens, cuda=True)

            # replace here with real policy
            state, reward, done, info = bug_env.step(action)  #
            if info['bug_state']:
                labels.append(1)
            else:
                labels.append(0)

            states.append(state)

            dist_to_correct = lstm.get_distance(y_hat, state)
            dist_to_broken = bug_lstm.get_distance(bug_y_hat, state) # SAE, we'll put lstm here, instead of bug_lstm

            if np.abs(dist_to_correct - dist_to_broken) < threshold:
                preds.append(0)  # 0 means correct
            else:
                preds.append(np.argmin([dist_to_correct, dist_to_broken]))

            # decision boundary (not allowed to tune...since we don't know how)
            dists.append((dist_to_correct - dist_to_broken).numpy().squeeze())

            if done:
                break

        assert len(preds) == len(labels)

        preds_y.append(np.array(preds))
        test_y.append(np.array(labels))

        test_y = np.concatenate(test_y)
        preds_y = np.concatenate(preds_y)

        accu = accuracy_score(preds_y, test_y)
        traj_accus.append(accu)
        traj_dists.append(dists)
        traj_labels.append(test_y)
        traj_preds.append(preds_y)

    return traj_accus, traj_dists, traj_labels, traj_preds
