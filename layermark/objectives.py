"""Core LayerMark objectives released with the architecture."""

from __future__ import annotations

import torch


def normalized_mae(
    prediction: torch.Tensor,
    target: torch.Tensor,
    epsilon: float = 1e-6,
) -> torch.Tensor:
    """Normalized mean absolute error used in Equations (5) and (6)."""
    if prediction.shape != target.shape:
        raise ValueError("prediction and target must have matching shapes")
    numerator = torch.mean(torch.abs(prediction - target))
    denominator = torch.mean(torch.abs(target)).detach().clamp_min(epsilon)
    return numerator / denominator

