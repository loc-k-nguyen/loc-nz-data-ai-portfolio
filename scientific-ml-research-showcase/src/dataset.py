"""Synthetic 2D field dataset for scientific ML surrogate modelling.

The generated data mimics the structure of a field-to-field scientific
surrogate task, but it is not groundwater data and does not reproduce private
PhD experiments.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, Subset, random_split


@dataclass(frozen=True)
class SyntheticConfig:
    num_samples: int
    image_size: int
    random_seed: int


class SyntheticPlumeDataset(Dataset):
    """Deterministic synthetic surrogate dataset.

    Input channels:
    - channel 0: permeability-like smooth random field
    - channel 1: source/location Gaussian pattern

    Target:
    - channel 0: transparent plume-like response generated from the two inputs
    """

    def __init__(self, config: SyntheticConfig) -> None:
        self.config = config
        self.inputs, self.targets = self._generate()

    def __len__(self) -> int:
        return self.config.num_samples

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.inputs[index], self.targets[index]

    def _generate(self) -> tuple[torch.Tensor, torch.Tensor]:
        rng = np.random.default_rng(self.config.random_seed)
        h = self.config.image_size
        w = self.config.image_size
        yy, xx = np.meshgrid(np.linspace(0, 1, h), np.linspace(0, 1, w), indexing="ij")

        input_fields: list[np.ndarray] = []
        target_fields: list[np.ndarray] = []
        for _ in range(self.config.num_samples):
            raw_perm = rng.normal(0, 1, size=(h, w)).astype("float32")
            perm = _smooth_field(raw_perm, kernel_size=5)
            perm = (perm - perm.min()) / (perm.max() - perm.min() + 1e-8)

            cx = rng.uniform(0.2, 0.8)
            cy = rng.uniform(0.2, 0.8)
            sigma = rng.uniform(0.04, 0.09)
            source = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * sigma**2)))

            stretch_x = 0.10 + 0.18 * float(perm.mean())
            stretch_y = 0.06 + 0.12 * float(1.0 - perm.mean())
            drift = 0.12 * (perm - 0.5)
            plume = np.exp(
                -(
                    ((xx - cx - 0.18) ** 2) / (2 * stretch_x**2)
                    + ((yy - cy + drift) ** 2) / (2 * stretch_y**2)
                )
            )
            # Keep the mapping learnable for a short CPU portfolio run while
            # retaining a plume-like structure influenced by the permeability proxy.
            target = 0.65 * source + 0.25 * perm + 0.10 * plume * (0.5 + perm)
            target = target / (target.max() + 1e-8)

            input_fields.append(np.stack([perm, source.astype("float32")], axis=0))
            target_fields.append(target.astype("float32")[None, :, :])

        return (
            torch.tensor(np.stack(input_fields), dtype=torch.float32),
            torch.tensor(np.stack(target_fields), dtype=torch.float32),
        )


def _smooth_field(field: np.ndarray, kernel_size: int) -> np.ndarray:
    """Smooth a 2D field with average pooling."""
    tensor = torch.tensor(field[None, None, :, :], dtype=torch.float32)
    padding = kernel_size // 2
    smoothed = F.avg_pool2d(tensor, kernel_size=kernel_size, stride=1, padding=padding)
    return smoothed.squeeze().numpy()


def create_splits(
    config: SyntheticConfig,
    train_fraction: float,
    validation_fraction: float,
) -> tuple[Subset, Subset, Subset]:
    """Create deterministic train/validation/test splits."""
    dataset = SyntheticPlumeDataset(config)
    train_size = int(train_fraction * len(dataset))
    validation_size = int(validation_fraction * len(dataset))
    test_size = len(dataset) - train_size - validation_size
    generator = torch.Generator().manual_seed(config.random_seed)
    return random_split(dataset, [train_size, validation_size, test_size], generator=generator)


def save_dataset_metadata(path: Path, config: SyntheticConfig) -> None:
    """Save metadata that documents the synthetic data source."""
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "dataset_type": "synthetic demonstration data",
        "private_data_used": False,
        "description": "2D permeability-like field and source Gaussian mapped to plume-like target field.",
        "num_samples": config.num_samples,
        "image_size": config.image_size,
        "random_seed": config.random_seed,
    }
    path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
