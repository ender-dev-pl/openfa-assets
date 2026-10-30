"""Minimal RRDBNet x2 inference architecture used by the HQ authoring tool.

The module follows the RRDBNet architecture published by XPixelGroup in
BasicSR and Real-ESRGAN under Apache-2.0. It intentionally contains only the
network definition required to load the official RealESRGAN_x2plus weights;
training, download, registry, and package integration code are out of scope.
"""

from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as functional


class ResidualDenseBlock(nn.Module):
    def __init__(self, feature_count: int = 64, growth_count: int = 32) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(feature_count, growth_count, 3, 1, 1)
        self.conv2 = nn.Conv2d(feature_count + growth_count, growth_count, 3, 1, 1)
        self.conv3 = nn.Conv2d(feature_count + growth_count * 2, growth_count, 3, 1, 1)
        self.conv4 = nn.Conv2d(feature_count + growth_count * 3, growth_count, 3, 1, 1)
        self.conv5 = nn.Conv2d(feature_count + growth_count * 4, feature_count, 3, 1, 1)
        self.activation = nn.LeakyReLU(negative_slope=0.2, inplace=True)

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        first = self.activation(self.conv1(value))
        second = self.activation(self.conv2(torch.cat((value, first), dim=1)))
        third = self.activation(self.conv3(torch.cat((value, first, second), dim=1)))
        fourth = self.activation(
            self.conv4(torch.cat((value, first, second, third), dim=1))
        )
        fifth = self.conv5(torch.cat((value, first, second, third, fourth), dim=1))
        return fifth * 0.2 + value


class ResidualInResidualDenseBlock(nn.Module):
    def __init__(self, feature_count: int = 64, growth_count: int = 32) -> None:
        super().__init__()
        self.rdb1 = ResidualDenseBlock(feature_count, growth_count)
        self.rdb2 = ResidualDenseBlock(feature_count, growth_count)
        self.rdb3 = ResidualDenseBlock(feature_count, growth_count)

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        output = self.rdb1(value)
        output = self.rdb2(output)
        output = self.rdb3(output)
        return output * 0.2 + value


class RrdbNetX2(nn.Module):
    """RRDBNet configured for the official 23-block x2 Real-ESRGAN weights."""

    def __init__(
        self,
        feature_count: int = 64,
        block_count: int = 23,
        growth_count: int = 32,
    ) -> None:
        super().__init__()
        self.conv_first = nn.Conv2d(12, feature_count, 3, 1, 1)
        self.body = nn.Sequential(
            *[
                ResidualInResidualDenseBlock(feature_count, growth_count)
                for _ in range(block_count)
            ]
        )
        self.conv_body = nn.Conv2d(feature_count, feature_count, 3, 1, 1)
        self.conv_up1 = nn.Conv2d(feature_count, feature_count, 3, 1, 1)
        self.conv_up2 = nn.Conv2d(feature_count, feature_count, 3, 1, 1)
        self.conv_hr = nn.Conv2d(feature_count, feature_count, 3, 1, 1)
        self.conv_last = nn.Conv2d(feature_count, 3, 3, 1, 1)
        self.activation = nn.LeakyReLU(negative_slope=0.2, inplace=True)

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        features = self.conv_first(functional.pixel_unshuffle(value, 2))
        body_features = self.conv_body(self.body(features))
        features = features + body_features
        features = self.activation(
            self.conv_up1(functional.interpolate(features, scale_factor=2, mode="nearest"))
        )
        features = self.activation(
            self.conv_up2(functional.interpolate(features, scale_factor=2, mode="nearest"))
        )
        return self.conv_last(self.activation(self.conv_hr(features)))
