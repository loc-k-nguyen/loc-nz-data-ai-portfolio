"""Small PyTorch surrogate models for synthetic scientific ML fields."""

from __future__ import annotations

import torch
from torch import nn


class SmallCNN(nn.Module):
    """A compact convolutional baseline for field-to-field regression."""

    def __init__(self, input_channels: int = 2, output_channels: int = 1, hidden: int = 16) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(input_channels, hidden, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(hidden, hidden, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(hidden, output_channels, kernel_size=1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class MiniUNet(nn.Module):
    """A lightweight encoder-decoder surrogate with skip connection."""

    def __init__(self, input_channels: int = 2, output_channels: int = 1, base_channels: int = 12) -> None:
        super().__init__()
        self.enc1 = _conv_block(input_channels, base_channels)
        self.down = nn.MaxPool2d(2)
        self.enc2 = _conv_block(base_channels, base_channels * 2)
        self.up = nn.Upsample(scale_factor=2, mode="bilinear", align_corners=False)
        self.dec1 = _conv_block(base_channels * 3, base_channels)
        self.out = nn.Sequential(nn.Conv2d(base_channels, output_channels, kernel_size=1), nn.Sigmoid())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        skip = self.enc1(x)
        encoded = self.enc2(self.down(skip))
        decoded = self.up(encoded)
        return self.out(self.dec1(torch.cat([decoded, skip], dim=1)))


def _conv_block(in_channels: int, out_channels: int) -> nn.Sequential:
    return nn.Sequential(
        nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
        nn.ReLU(),
    )


def build_model(
    model_name: str,
    input_channels: int,
    output_channels: int,
    base_channels: int,
) -> nn.Module:
    """Build a surrogate model from a config name."""
    if model_name == "small_cnn":
        return SmallCNN(input_channels=input_channels, output_channels=output_channels, hidden=base_channels)
    if model_name == "mini_unet":
        return MiniUNet(
            input_channels=input_channels,
            output_channels=output_channels,
            base_channels=base_channels,
        )
    raise ValueError(f"Unknown model_name: {model_name}")

