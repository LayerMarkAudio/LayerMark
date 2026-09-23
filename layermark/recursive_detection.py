"""Minimal runtime operation for one recursive LayerMark detection step."""

from __future__ import annotations

import torch

from .models import MultiLayerRemover, RemovalEstimate


def remove_current_layer(
    remover: MultiLayerRemover,
    current_audio: torch.Tensor,
    reconstructed_feature: torch.Tensor,
) -> tuple[torch.Tensor, RemovalEstimate]:
    """Estimate and subtract the visible layer before the next detection step."""
    estimate = remover(current_audio, reconstructed_feature)
    previous_audio = current_audio - estimate.feature
    return previous_audio, estimate

