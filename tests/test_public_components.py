from __future__ import annotations

import unittest

import torch

from layermark import (
    MultiLayerAdapter,
    MultiLayerRemover,
    normalized_mae,
    remove_current_layer,
)


class PublicComponentsTest(unittest.TestCase):
    def test_paper_default_architectures(self) -> None:
        adapter = MultiLayerAdapter()
        remover = MultiLayerRemover()
        self.assertEqual(len(adapter.blocks), 6)
        self.assertEqual(adapter.stem.out_channels, 24)
        self.assertEqual(len(remover.blocks), 8)
        self.assertEqual(remover.stem.out_channels, 32)

    def test_adapter_and_remover_preserve_waveform_shape(self) -> None:
        torch.manual_seed(7)
        current = torch.randn(2, 1, 512)
        previous = 0.01 * torch.randn_like(current)
        new = 0.01 * torch.randn_like(current)
        adjusted = MultiLayerAdapter()(new, previous)
        restored, estimate = remove_current_layer(
            MultiLayerRemover(), current, adjusted
        )
        self.assertEqual(adjusted.shape, current.shape)
        self.assertEqual(estimate.feature.shape, current.shape)
        self.assertEqual(restored.shape, current.shape)

    def test_normalized_mae_is_zero_for_exact_reconstruction(self) -> None:
        target = torch.randn(2, 1, 64)
        self.assertEqual(float(normalized_mae(target, target)), 0.0)


if __name__ == "__main__":
    unittest.main()

