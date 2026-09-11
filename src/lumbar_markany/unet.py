"""Compact U-Net for single-channel ultrasound semantic segmentation."""
import torch
import torch.nn as nn


def block(i, o):
    return nn.Sequential(
        nn.Conv2d(i, o, 3, padding=1, bias=False), nn.BatchNorm2d(o), nn.ReLU(inplace=True),
        nn.Conv2d(o, o, 3, padding=1, bias=False), nn.BatchNorm2d(o), nn.ReLU(inplace=True),
    )


class UNet(nn.Module):
    def __init__(self, in_ch=1, n_classes=10, base=32, dropout=0.2):
        super().__init__()
        b = base
        self.e1 = block(in_ch, b)
        self.e2 = block(b, b * 2)
        self.e3 = block(b * 2, b * 4)
        self.e4 = block(b * 4, b * 8)
        self.pool = nn.MaxPool2d(2)
        self.bott = block(b * 8, b * 16)
        # Dropout is kept as a module so it can be re-enabled at test time for
        # Monte-Carlo dropout uncertainty estimation (see exp004).
        self.drop = nn.Dropout2d(dropout)
        self.u4 = nn.ConvTranspose2d(b * 16, b * 8, 2, 2)
        self.d4 = block(b * 16, b * 8)
        self.u3 = nn.ConvTranspose2d(b * 8, b * 4, 2, 2)
        self.d3 = block(b * 8, b * 4)
        self.u2 = nn.ConvTranspose2d(b * 4, b * 2, 2, 2)
        self.d2 = block(b * 4, b * 2)
        self.u1 = nn.ConvTranspose2d(b * 2, b, 2, 2)
        self.d1 = block(b * 2, b)
        self.head = nn.Conv2d(b, n_classes, 1)

    def forward(self, x):
        e1 = self.e1(x)
        e2 = self.e2(self.pool(e1))
        e3 = self.e3(self.pool(e2))
        e4 = self.e4(self.pool(e3))
        z = self.drop(self.bott(self.pool(e4)))
        d = self.d4(torch.cat([self.u4(z), e4], 1))
        d = self.d3(torch.cat([self.u3(d), e3], 1))
        d = self.d2(torch.cat([self.u2(d), e2], 1))
        d = self.d1(torch.cat([self.u1(d), e1], 1))
        return self.head(d)
