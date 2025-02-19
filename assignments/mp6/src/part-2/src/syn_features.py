"""
HW6: Understanding CNNs and Generative Adversarial Networks.

Part 2: Visualization

@author: Zhenye Na
"""

from plot import plot
from model import DiscriminatorBottom
from torch.autograd import Variable

import os
import torch
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


def syn_features(testloader, modelroot, batch_size, cuda):
    """Synthetic Features Maximizing Features at Various Layers."""
    testloader = enumerate(testloader)
    # if train D without G
    model_pth = os.path.join(modelroot, "cifar10.model")
    # else if train D with G
    # model_pth = os.path.join(modelroot, "tempD.model")
    model = torch.load(model_pth, map_location=lambda storage, loc: storage)

    # conv6
    model = DiscriminatorBottom(model)

    # if cuda:
    #     model.cuda()
    model.eval()
    batch_idx, (X_batch, Y_batch) = testloader.__next__()

    X = X_batch.mean(dim=0)
    X = X.repeat(batch_size, 1, 1, 1)
    X = Variable(X, requires_grad=True).cuda()

    Y = torch.arange(batch_size).type(torch.int64)
    Y = Variable(Y).cuda()

    lr = 0.1
    weight_decay = 0.001
    for i in range(200):
        # if train D without G
        # output, _, _ = model(X)
        # else if train D with G
        output = model(X)

        loss = -output[torch.arange(batch_size).type(torch.int64),
                       torch.arange(batch_size).type(torch.int64)]
        gradients = torch.autograd.grad(outputs=loss, inputs=X,
                                        grad_outputs=torch.ones(
                                            loss.size()).cuda(),
                                        create_graph=True, retain_graph=False, only_inputs=True)[0]

        # first column has actual prob
        prediction = output.data.max(1)[1]
        accuracy = (float(prediction.eq(Y.data).sum()) /
                    float(batch_size)) * 100.0
        print("Ieration: {} | Accuracy: {} | Loss: {}".format(
            i, accuracy, -loss.data[0]))

        X = X - lr * gradients.data - weight_decay * X.data * torch.abs(X.data)
        X[X > 1.0] = 1.0
        X[X < -1.0] = -1.0

    # save new images
    samples = X.data.cpu().numpy()
    samples += 1.0
    samples /= 2.0
    samples = samples.transpose(0, 2, 3, 1)

    fig = plot(samples[0:100])
    if not os.path.isdir('../visualization'):
        os.mkdir('../visualization')
    plt.savefig('../visualization/max_features.png', bbox_inches='tight')
    plt.close(fig)
