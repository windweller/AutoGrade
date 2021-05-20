# https://debuggercafe.com/getting-started-with-variational-autoencoder-using-pytorch/

# We are adding a "CUDA" mode to all of these

# ====== VAE ========

import torch
import torch.nn as nn
import torch.nn.functional as F

from torch.distributions.normal import Normal

# criterion = nn.MSELoss(reduction='mean')
criterion = nn.L1Loss(reduction='mean')
test_loss_criterion = nn.L1Loss(reduction='none')

# define a simple VAE

def final_loss(bce_loss, mu, logvar):
    """
    This function will add the reconstruction loss (BCELoss) and the
    KL-Divergence.
    KL-Divergence = 0.5 * sum(1 + log(sigma^2) - mu^2 - sigma^2)
    :param bce_loss: recontruction loss
    :param mu: the mean from the latent vector
    :param logvar: log variance from the latent vector
    """
    BCE = bce_loss
    KLD = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    return BCE  # + KLD


def train_vae_one_epoch(model, optimizer, data, cuda=False):
    model.train()
    optimizer.zero_grad()

    if cuda:
        data = data.to('cuda')

    reconstruction, mu, logvar = model(data)
    # bce_loss = criterion(reconstruction, data)
    mse_loss = criterion(reconstruction, data)

    loss = final_loss(mse_loss, mu, logvar)

    loss.backward()
    optimizer.step()

    if cuda:
        loss = loss.cpu()

    return loss.detach().item()


def compute_vae_loss(model, data, cuda=False):
    # need batch loss!!!
    if cuda:
        data = data.to('cuda')

    reconstruction, mu, logvar = model(data)
    mse_loss = test_loss_criterion(reconstruction, data)

    loss = final_loss(mse_loss, mu, logvar)
    loss = loss.mean(dim=1)

    if cuda:
        loss = loss.cpu()

    return loss.detach().numpy()

class VAE(nn.Module):
    def __init__(self, feature_dim):
        super(VAE, self).__init__()

        self.feature_dim = feature_dim
        self.z_dim = 64

        # encoder
        self.enc = nn.Sequential(
            nn.Linear(in_features=feature_dim, out_features=128),
            nn.GELU(),
            nn.Linear(in_features=128, out_features=128),
            nn.GELU(),
            nn.Linear(in_features=128, out_features=self.z_dim * 2)
        )
        # self.enc1 = nn.Linear(in_features=feature_dim, out_features=128)
        # self.enc2 = nn.Linear(in_features=128, out_features=feature_dim*2)

        # decoder
        # self.dec1 = nn.Linear(in_features=feature_dim, out_features=128)
        # self.dec2 = nn.Linear(in_features=128, out_features=feature_dim)

        self.dec = nn.Sequential(
            nn.Linear(in_features=self.z_dim, out_features=128),
            nn.GELU(),
            nn.Linear(in_features=128, out_features=128),
            nn.GELU(),
            nn.Linear(in_features=128, out_features=feature_dim)
        )

    def reparameterize(self, mu, log_var):
        """
        :param mu: mean from the encoder's latent space
        :param log_var: log variance from the encoder's latent space
        """
        std = torch.exp(0.5 * log_var)  # standard deviation
        eps = torch.randn_like(std)  # `randn_like` as we need the same size
        sample = mu + (eps * std)  # sampling as if coming from the input space
        return sample

    def forward(self, x):
        # encoding
        # x = F.gelu(self.enc1(x))
        # x = self.enc2(x).view(-1, 2, self.z_dim)

        x = self.enc(x).view(-1, 2, self.z_dim)
        # get `mu` and `log_var`
        mu = x[:, 0, :]  # the first feature values as mean
        log_var = x[:, 1, :]  # the other feature values as variance
        # get the latent vector through reparameterization
        z = self.reparameterize(mu, log_var)

        # decoding
        # x = F.gelu(self.dec1(z))
        # reconstruction = torch.sigmoid(self.dec2(x))
        # reconstruction = self.dec2(x)
        reconstruction = self.dec(z)

        return reconstruction, mu, log_var

# ====== LSTM ========

import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque

def prepare_batch(batch_list, feature_dim, action_input=False):
    # e: (T, dim)
    if not action_input:
        # x
        batch_list = sorted(batch_list, key=lambda x: x.shape[0], reverse=True)
        max_len = max([e.shape[0] for e in batch_list])

        data = torch.zeros(len(batch_list), max_len, feature_dim).float()
        target = torch.zeros(len(batch_list), max_len, feature_dim).float()

        masks = torch.zeros(len(batch_list), max_len, feature_dim).float()
        data_len = torch.Tensor([len(e) for e in batch_list]).int()

        for i, e in enumerate(batch_list):
            data[i, :len(e)-1] = torch.from_numpy(e).float()[:-1]
            target[i, :len(e) - 1] = torch.from_numpy(e).float()[1:]

            # mask is for y, loss
            # only consider sequence up till last step
            masks[i, :len(e) - 1] = 1.

        return data, target, masks, data_len
    else:
        # (x, a)
        batch_list = sorted(batch_list, key=lambda tup: tup[0].shape[0], reverse=True)
        max_len = max([e[0].shape[0] for e in batch_list])

        # add action dimension
        data = torch.zeros(len(batch_list), max_len, feature_dim).float()
        target = torch.zeros(len(batch_list), max_len, feature_dim).float()

        action = torch.zeros(len(batch_list), max_len).long()

        masks = torch.zeros(len(batch_list), max_len, feature_dim).float()
        data_len = torch.Tensor([len(e[0]) for e in batch_list]).int()

        for i, (e, a) in enumerate(batch_list):
            data[i, :len(e) - 1] = torch.from_numpy(e).float()[:-1]

            action[i, :len(e) - 1] = torch.from_numpy(a).long() + 1  # so that 0 is padding, action starts from 1 to 5

            # target is the SAME
            target[i, :len(e) - 1] = torch.from_numpy(e).float()[1:]

            # mask is for y, loss
            # only consider sequence up till last step
            masks[i, :len(e) - 1] = 1.

        return (data, action), target, masks, data_len


# HoareLSTM, Delta-HoareLSTM
# to be completely honest, action should be part of the input p(s|s,a)
class HoareLSTM(nn.Module):
    def __init__(self, feature_dim, num_actions=4, batch_size=32, delta=False, action_input=False):
        super(HoareLSTM, self).__init__()

        self.feature_dim = feature_dim
        self.batch_size = batch_size
        self.delta = delta
        self.action_input = action_input

        # encoder
        self.enc = nn.Sequential(
            nn.Linear(in_features=self.feature_dim, out_features=64),
            nn.GELU(),
            nn.Linear(in_features=64, out_features=64)
        )

        if self.action_input:
            self.lstm = nn.LSTM(64 + 5, 64)
        else:
            self.lstm = nn.LSTM(64, 64)

        self.dec = nn.Sequential(
            nn.Linear(in_features=64, out_features=64),
            nn.GELU(),
            nn.Linear(in_features=64, out_features=self.feature_dim),
        )

        # action embedding
        if self.action_input:
            # 4 + 1, considering padding
            self.emb = nn.Embedding(num_actions + 1, 5, padding_idx=0)

        self.batches = deque(maxlen=200)  # 100 batches
        self.current_batch = []

    def store(self, x, a=None):
        # x starts with env.reset() init state
        # y doesn't
        if self.action_input:
            assert a is not None, "model requires the storage of action"

        # maybe you didn't implement this right.
        # bug-lstm traj is longer than normal lstm
        if len(self.current_batch) == self.batch_size:
            self.batches.append(prepare_batch(self.current_batch, self.feature_dim, action_input=self.action_input))
            self.current_batch = []
            tup = x if not self.action_input else (x, a)
            self.current_batch.append(tup)
        else:
            tup = x if not self.action_input else (x, a)
            self.current_batch.append(tup)

    def reset(self):
        # this is NOT recursive
        for layer in self.children():
            if hasattr(layer, 'reset_parameters'):
                layer.reset_parameters()

        for layer in self.enc:
            if hasattr(layer, 'reset_parameters'):
                layer.reset_parameters()

        for layer in self.dec:
            if hasattr(layer, 'reset_parameters'):
                layer.reset_parameters()

    def forward(self, batch_x, data_len):
        # x: (batch_size, T, dim)
        if self.action_input:
            batch_x, batch_a = batch_x

        X = self.enc(batch_x)

        # if add action
        if self.action_input:
            action_emb = self.emb(batch_a)
            X = torch.cat([X, action_emb], dim=2)

        X = torch.nn.utils.rnn.pack_padded_sequence(X, data_len, batch_first=True)
        X, hidden = self.lstm(X)
        X, _ = torch.nn.utils.rnn.pad_packed_sequence(X, batch_first=True)

        if self.delta:
            delta_x = self.dec(X)
            y_hat = delta_x + batch_x
        else:
            y_hat = self.dec(X)

        return y_hat

    def predict_post_state(self, batch_x, pre_state=None, cuda=False):
        # x: (batch_size, dim)
        # pre_state: previous hidden state
        if self.action_input:
            assert type(batch_x) == tuple, "Must pass in (x, a) if HoareLSTM is configured for action"
            batch_x, batch_a = batch_x

            batch_a = torch.LongTensor([batch_a])
            batch_a = batch_a.view(1, 1)
            if cuda:
                batch_a = batch_a.to('cuda')

        batch_x = torch.from_numpy(batch_x).float()
        batch_x = batch_x.view(1, 1, -1)
        if cuda:
            batch_x = batch_x.to('cuda')

        x = self.enc(batch_x)
        if self.action_input:
            action_emb = self.emb(batch_a)  # (1, 1, 5)
            x = torch.cat([x, action_emb], dim=2)

        x, post_state = self.lstm(x, pre_state)
        if self.delta:
            delta_x = self.dec(x)
            y_hat = batch_x + delta_x
        else:
            y_hat = self.dec(x)

        if cuda:
            y_hat = y_hat.cpu()

        return y_hat.squeeze(), post_state

    def get_distance(self, y_hat, true_y):
        with torch.no_grad():
            # we also use p=1.0, same as loss
            return torch.cdist(y_hat.view(1, 1, -1), torch.from_numpy(true_y).float().view(1, 1, -1), p=1.0)


def train_lstm_one_epoch(model, optimizer, mse_loss, cuda=False):
    losses = []
    for batch_x, batch_y, masks, data_len in model.batches:
        model.zero_grad()

        if cuda:
            if type(batch_x) == tuple:
                batch_x = (batch_x[0].to('cuda'), batch_x[1].to('cuda'))
            else:
                batch_x = batch_x.to('cuda')

            batch_y = batch_y.to('cuda')
            masks = masks.to('cuda')

        y_hat = model(batch_x, data_len)
        y_hat = y_hat * masks
        loss = mse_loss(y_hat, batch_y)

        loss.backward()
        optimizer.step()

        if cuda:
            loss = loss.cpu()

        losses.append(loss.detach().item())

    return losses

