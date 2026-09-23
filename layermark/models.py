"""LayerMark architecture components described in Section 3.2 of the paper.

The AudioSeal Generator and Detector are external dependencies and are not
redistributed here. Both modules below operate on mono waveform-domain feature
tensors shaped ``[batch, 1, frames]``.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn
import torch.nn.functional as F


def _check_waveform(name: str, value: torch.Tensor) -> None:
    if value.ndim != 3 or value.shape[1] != 1:
        raise ValueError(f"{name} must have shape [batch, 1, frames]")
    if not torch.isfinite(value).all():
        raise ValueError(f"{name} must contain only finite values")


class _DilatedResidualBlock(nn.Module):
    def __init__(self, channels: int, dilation: int) -> None:
        super().__init__()
        self.temporal = nn.Conv1d(
            channels,
            channels,
            kernel_size=3,
            padding=dilation,
            dilation=dilation,
        )
        self.projection = nn.Conv1d(channels, channels, kernel_size=1)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return features + self.projection(F.silu(self.temporal(features)))


class MultiLayerAdapter(nn.Module):
    """Adjust a new watermark feature using the preceding layer's feature.

    The defaults match the paper: six 24-channel dilated convolutional blocks
    with dilation factors ``(1, 2, 4, 8, 16, 32)``.
    """

    def __init__(
        self,
        channels: int = 24,
        dilations: tuple[int, ...] = (1, 2, 4, 8, 16, 32),
    ) -> None:
        super().__init__()
        if channels <= 0 or not dilations or any(value <= 0 for value in dilations):
            raise ValueError("channels and dilations must be positive")
        self.stem = nn.Conv1d(2, channels, kernel_size=7, padding=3)
        self.blocks = nn.ModuleList(
            _DilatedResidualBlock(channels, dilation) for dilation in dilations
        )
        self.output = nn.Conv1d(channels, 1, kernel_size=1)

    def forward(
        self,
        new_feature: torch.Tensor,
        previous_feature: torch.Tensor,
    ) -> torch.Tensor:
        _check_waveform("new_feature", new_feature)
        _check_waveform("previous_feature", previous_feature)
        if new_feature.shape != previous_feature.shape:
            raise ValueError("new_feature and previous_feature must have matching shapes")
        features = self.stem(torch.cat((new_feature, previous_feature), dim=1))
        for block in self.blocks:
            features = block(features)
        return self.output(features)


@dataclass(frozen=True)
class RemovalEstimate:
    """Estimated feature and its two factors from the Multi-Layer Remover."""

    feature: torch.Tensor
    gain: torch.Tensor
    correction: torch.Tensor


class MultiLayerRemover(nn.Module):
    """Estimate the currently visible watermark feature for subtraction.

    The defaults match the paper: eight 32-channel dilated residual blocks
    with dilation factors ``(1, 2, 4, 8, 16, 32, 64, 128)`` and separate gain
    and correction output branches.
    """

    def __init__(
        self,
        channels: int = 32,
        dilations: tuple[int, ...] = (1, 2, 4, 8, 16, 32, 64, 128),
    ) -> None:
        super().__init__()
        if channels <= 0 or not dilations or any(value <= 0 for value in dilations):
            raise ValueError("channels and dilations must be positive")
        self.stem = nn.Conv1d(2, channels, kernel_size=7, padding=3)
        self.blocks = nn.ModuleList(
            _DilatedResidualBlock(channels, dilation) for dilation in dilations
        )
        self.gain_head = nn.Linear(channels, 1)
        self.correction_head = nn.Conv1d(channels, 1, kernel_size=1)

    def forward(
        self,
        watermarked_audio: torch.Tensor,
        watermark_feature: torch.Tensor,
    ) -> RemovalEstimate:
        _check_waveform("watermarked_audio", watermarked_audio)
        _check_waveform("watermark_feature", watermark_feature)
        if watermarked_audio.shape != watermark_feature.shape:
            raise ValueError(
                "watermarked_audio and watermark_feature must have matching shapes"
            )
        features = self.stem(torch.cat((watermarked_audio, watermark_feature), dim=1))
        for block in self.blocks:
            features = block(features)
        gain = 1.0 + torch.tanh(self.gain_head(features.mean(dim=-1))).unsqueeze(-1)
        correction = self.correction_head(features)
        estimate = gain * watermark_feature + correction
        return RemovalEstimate(feature=estimate, gain=gain, correction=correction)

