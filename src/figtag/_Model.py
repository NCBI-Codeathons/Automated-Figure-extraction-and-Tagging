# This file exists only to satisfy `pickle`
import numpy as np
import torch
import torch.nn.functional as F
from torch import nn
import os
from copy import deepcopy


class CheckpointStore(object):
    def __init__(self, path):
        self.root = path

    def save(self, filename, model):
        """ Save model and its metadata.
            For `densenet` models saving/loading state dictionary
            does not work: we will not get same model back.
            Solution is to save complete model.
        """
        checkpoint = {
            'model': deepcopy(model),
        }
        path = os.path.join(self.root, filename)
        torch.save(checkpoint, path)
        return path

    @staticmethod
    def read(filepath):
        """ Return checkpoint dictionary.
        """
        # Read checkpoint file and re-map storage
        # to lowest common denominator - 'cpu'.
        return torch.load(filepath, map_location=lambda storage, loc: storage)

    @staticmethod
    def loadModel(filepath):
        cp = CheckpointStore.read(filepath)
        model = cp['model']
        model.to(cp.make_device())
        return model


class Model(torch.nn.Module):
    def __init__(self, depth, code_size):
        super(Model, self).__init__()
        self.depth = depth
        self.code_size = code_size

        self.conv1 = nn.Conv2d(depth, 16, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(16)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(32)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn3 = nn.BatchNorm2d(64)
        self.conv4 = nn.Conv2d(64, 16, kernel_size=3, stride=2, padding=1, bias=False)
        self.bn4 = nn.BatchNorm2d(16)

        # Latent vectors
        self.fc1 = nn.Linear(25*25*16, self.code_size)  # 2048
        self.fc_bn1 = nn.BatchNorm1d(self.code_size)
        self.fc21 = nn.Linear(self.code_size, self.code_size)
        self.fc22 = nn.Linear(self.code_size, self.code_size)

        # Sampling vector
        self.fc3 = nn.Linear(self.code_size, self.code_size)
        self.fc_bn3 = nn.BatchNorm1d(self.code_size)
        self.fc4 = nn.Linear(self.code_size, 25*25*16)
        self.fc_bn4 = nn.BatchNorm1d(25*25*16)

        # Decoder
        self.conv5 = nn.ConvTranspose2d(16, 64, kernel_size=3, stride=2,
                                        padding=1, output_padding=1, bias=False)
        self.bn5 = nn.BatchNorm2d(64)
        self.conv6 = nn.ConvTranspose2d(64, 32, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn6 = nn.BatchNorm2d(32)
        self.conv7 = nn.ConvTranspose2d(32, 16, kernel_size=3, stride=2,
                                        padding=1, output_padding=1, bias=False)
        self.bn7 = nn.BatchNorm2d(16)
        self.conv8 = nn.ConvTranspose2d(16, depth, kernel_size=3, stride=1, padding=1, bias=False)
        self.relu = nn.ReLU()

        # self.encoder_fc1 = torch.nn.Linear(input_size, hidden_size)
        # self.fc_mu = torch.nn.Linear(hidden_size, code_size)
        # self.fc_logvar = torch.nn.Linear(hidden_size, code_size)

        # self.decoder_fc1 = torch.nn.Linear(code_size, hidden_size)
        # self.decoder_fc2 = torch.nn.Linear(hidden_size, input_size)

    def fit(self, dataloader, device, num_epochs, learn_rate):
        """
        """
        optimizer = torch.optim.Adam(self.parameters(), lr=learn_rate)

        best_loss = 10000
        checkpoint = CheckpointStore("checkpoints.{}".format(self.code_size))

        train_loss = []
        test_loss = []
        for epoch in range(num_epochs):
            acc = []
            for x, _ in iter(dataloader('train')):
                self.train()
                x = x.to(device)
                optimizer.zero_grad()
                x_hat, mu, logvar = self.forward(x)
                loss = Model.vae_loss(x_hat, x, mu, logvar)
                acc.append(loss.item())
                loss.backward()
                optimizer.step()
            train_loss.append(np.mean(acc))
            loss = self.validate(dataloader('valid'), device)
            if loss < best_loss:
                checkpoint.save("best_model.pt", self)
            test_loss.append(loss)
            print("Epoch={} Loss={}".format(epoch, loss))
            checkpoint.save("model_{}.pt".format(len(test_loss)), self)
        return train_loss, test_loss

    def validate(self, dataloader, device):
        self.eval()
        with torch.no_grad():
            acc = []
            for x, _ in iter(dataloader):
                x = x.to(device)
                x_hat, mu, logvar = self.forward(x)
                loss = Model.vae_loss(x_hat, x, mu, logvar)
                acc.append(loss.item())
            return np.mean(acc)

    def encode(self, x):
        """ VAE encoder step.
            Return vectors mu and log_variance for
            distribution Q(z|x) that approximates P(z|x).
        """
        # h = F.relu(self.encoder_fc1(x))
        # return self.fc_mu(h), self.fc_logvar(h)
        conv1 = self.relu(self.bn1(self.conv1(x)))
        conv2 = self.relu(self.bn2(self.conv2(conv1)))
        conv3 = self.relu(self.bn3(self.conv3(conv2)))
        conv4 = self.relu(self.bn4(self.conv4(conv3))).view(-1, 25*25*16)
        # Latent vectors
        fc1 = self.relu(self.fc_bn1(self.fc1(conv4)))
        mu = self.fc21(fc1)
        std = self.fc22(fc1)
        return mu, std

    def decode(self, z):
        """ VAE decoder step.
            Return reconstructed vector x_hat.
        """
        # h = F.relu(self.decoder_fc1(z))
        # return torch.sigmoid(self.decoder_fc2(h))

        fc3 = self.relu(self.fc_bn3(self.fc3(z)))
        fc4 = self.relu(self.fc_bn4(self.fc4(fc3))).view(-1, 16, 25, 25)
        # print(fc4.shape)
        conv5 = self.relu(self.bn5(self.conv5(fc4)))
        # print(conv5.shape)
        conv6 = self.relu(self.bn6(self.conv6(conv5)))
        # print(conv6.shape)
        conv7 = self.relu(self.bn7(self.conv7(conv6)))
        # print(conv7.shape)
        out = self.conv8(conv7).view(-1, self.depth, 100, 100)
        return torch.sigmoid(out)

    def reparam(self, mu, logvar):
        """ Return vector representing latent state `z`.
            Sample `z` - latent vector - from
            distribution Q(z|x).
        """
        if self.training:
            sigma = torch.exp(0.5*logvar)
            e = torch.randn_like(sigma)
            return e.mul(sigma).add_(mu)
        else:
            return mu

    def forward(self, x):
        """ Forward step VAE encoder / decoder.
        """
        mu, logvar = self.encode(x)  # .encode(x.view(-1, self.input_size))
        z = self.reparam(mu, logvar)
        return self.decode(z), mu, logvar

    def infer(self, x):
        """ Return z - latent state sampled from Q(z|x)
        """
        self.eval()
        with torch.no_grad():
            mu, logvar = self.encode(x)  # self.encode(x.view(-1, self.input_size))
            return self.reparam(mu, logvar)

    @staticmethod
    def vae_loss(x_hat, x, mu, log_variance):
        """ Return value of lower bound of data log likelihood:
                sum of reconstruction error and divergence between
                Q(z|x) and P(z|x).
        """
        batch_size, c, w, h = x_hat.shape
        bce = F.binary_cross_entropy(x_hat, x)  # x.view(-1, x_size))

        divergence = -0.5 * torch.sum(1. + log_variance - mu.pow(2) - log_variance.exp())
        divergence /= (batch_size * c * w * h)
        return bce + divergence

    @staticmethod
    def loss_mse(x_hat, x):
        return nn.MSELoss(reduction="sum")(x_hat, x)
