import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "scientific-ml-research-showcase"
SRC = PROJECT / "src"
sys.path.insert(0, str(SRC))

from dataset import SyntheticConfig, SyntheticPlumeDataset  # noqa: E402
from metrics import compute_metrics  # noqa: E402
from models import build_model  # noqa: E402


def test_synthetic_dataset_shapes() -> None:
    dataset = SyntheticPlumeDataset(SyntheticConfig(num_samples=4, image_size=16, random_seed=7))
    x, y = dataset[0]
    assert x.shape == (2, 16, 16)
    assert y.shape == (1, 16, 16)


def test_model_forward_pass() -> None:
    model = build_model("small_cnn", input_channels=2, output_channels=1, base_channels=4)
    x = torch.rand(2, 2, 16, 16)
    y = model(x)
    assert y.shape == (2, 1, 16, 16)


def test_metrics_are_finite() -> None:
    y_true = torch.rand(2, 1, 8, 8)
    y_pred = y_true + 0.01 * torch.rand(2, 1, 8, 8)
    metrics = compute_metrics(y_true, y_pred)
    for value in metrics.values():
        assert torch.isfinite(torch.tensor(value))

