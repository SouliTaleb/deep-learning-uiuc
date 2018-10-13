"""
HW5: Implement a Deep Learning model for image ranking

Due October 19 at 5:00 PM.

@author: Zhenye Na

references: https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/42945.pdf

@author: Zhenye Na
"""

import os
import torch
import torchvision
import torch.optim
import torch.nn as nn
import torch.backends.cudnn as cudnn
import torchvision.transforms as transforms

import argparse

from utils import *


parser = argparse.ArgumentParser()

# directory
parser.add_argument('--dataroot', type=str, default="../data", help='path to dataset')
parser.add_argument('--ckptroot', type=str, default="../checkpoint/ckpt.t7", help='path to checkpoint')

# hyperparameters settings
parser.add_argument('--lr', type=float, default=0.01, help='learning rate')
parser.add_argument('--momentum', type=float, default=0.9, help='momentum factor')
parser.add_argument('--weight_decay', type=float, default=1e-5, help='weight decay (L2 penalty)')
parser.add_argument('--epochs', type=int, default=500, help='number of epochs to train')
parser.add_argument('--batch_size_train', type=int, default=129, help='training set input batch size')
parser.add_argument('--batch_size_test', type=int, default=256, help='test set input batch size')

# training settings
parser.add_argument('--resume', type=bool, default=False, help='whether re-training from ckpt')
parser.add_argument('--is_gpu', type=bool, default=False, help='whether training using GPU')

# parse the arguments
args = parser.parse_args()


def main():
    """Main pipeline of Image Similarity using Deep Ranking."""

    start_epoch = 0

    # resume training from the last time
    if args.resume:
        # Load checkpoint
        print('==> Resuming from checkpoint ...')
        assert os.path.isdir(
            '../checkpoint'), 'Error: no checkpoint directory found!'
        checkpoint = torch.load(args.ckptroot)
        net = checkpoint['net']
        start_epoch = checkpoint['epoch']
    else:
        # start over
        print('==> Building new ResNet model ...')
        net = resnet_cifar()

    print("==> Initialize CUDA support for ResNet model ...")

    # For training on GPU, we need to transfer net and data onto the GPU
    # http://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html#training-on-gpu
    if args.is_gpu:
        net = torch.nn.DataParallel(net).cuda()
        cudnn.benchmark = True

    trainloader, testloader = TinyImageNetLoader(train_root, test_root, batch_size_train, batch_size_test)


    train(net, trainloader, testloader)








if __name__ == '__main__':
    main()
