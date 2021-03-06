"""
ResNet for CIFAR dataset proposed in He+15, p 7.
"""

import math

import torch.nn as nn


def conv3x3(in_planes, out_planes, stride=1):
    "3x3 convolution with padding"
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride,
                     padding=1, bias=False)


class BasicBlock(nn.Module):
    def __init__(self, inplanes, planes, stride=1, pre_act=False):
        super(BasicBlock, self).__init__()
        self.conv1 = conv3x3(inplanes, planes)
        self.bn1 = nn.BatchNorm2d(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = conv3x3(planes, planes)
        self.bn2 = nn.BatchNorm2d(planes)
        self.downsample = nn.Sequential(nn.Conv2d(inplanes, planes, kernel_size=1,
                                                  stride=1, bias=False),
                                        nn.BatchNorm2d(planes))
        self.pre_act = pre_act
        self.stride = stride

    def forward(self, x):
        residual = self.downsample(x)

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        out += residual
        out = self.relu(out)

        return out


class ResNet(nn.Module):
    def __init__(self, block, n_size, num_classes=10):
        super(ResNet, self).__init__()
        self.inplane = 16
        self.conv1 = nn.Conv2d(3, self.inplane, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(self.inplane)
        self.relu = nn.ReLU(inplace=True)
        self.layer1 = self._make_layer(block, 16, blocks=2 * n_size, stride=2)
        self.layer2 = self._make_layer(block, 32, blocks=2 * n_size, stride=2)
        self.layer3 = self._make_layer(block, 64, blocks=2 * n_size, stride=2)
        self.avgpool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(64, num_classes)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

    def _make_layer(self, block, planes, blocks, stride):

        layers = []
        for i in range(1, blocks):
            layers.append(block(self.inplane, planes, stride))
            self.inplane = planes

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)

        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)

        return x


def resnet20(**kwargs):
    """Constructs a ResNet-18 model.
    
    """
    model = ResNet(BasicBlock, 3, **kwargs)
    return model


def resnet32(**kwargs):
    """Constructs a ResNet-34 model.
    
    """
    model = ResNet(BasicBlock, 5, **kwargs)
    return model
