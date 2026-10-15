"""Evaluate the saved synthetic scientific ML surrogate model."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import torch
import yaml
from dataset import SyntheticConfig, create_splits
from metrics import compute_metrics
from models import build_model
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "configs" / "config.yaml"


def get_device(config: dict) -> torch.device:
    requested = str(config.get("device", "auto")).lower()
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(requested)


def main() -> None:
    """Load model, regenerate deterministic test data, and export metrics."""
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    device = get_device(config)
    output_dir = PROJECT_ROOT / config["output_dir"]
    model_dir = PROJECT_ROOT / config["model_dir"]
    model_path = model_dir / "scientific_surrogate_model.pt"
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}. Run train.py first.")

    synthetic_config = SyntheticConfig(
        num_samples=int(config["num_samples"]),
        image_size=int(config["image_size"]),
        random_seed=int(config["random_seed"]),
    )
    _, _, test_set = create_splits(
        synthetic_config,
        train_fraction=float(config["train_fraction"]),
        validation_fraction=float(config["validation_fraction"]),
    )
    test_loader = DataLoader(test_set, batch_size=int(config["batch_size"]))
    model = build_model(
        model_name=str(config["model_name"]),
        input_channels=int(config["input_channels"]),
        output_channels=int(config["target_channels"]),
        base_channels=int(config["base_channels"]),
    ).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    predictions: list[torch.Tensor] = []
    targets: list[torch.Tensor] = []
    with torch.no_grad():
        for x_batch, y_batch in test_loader:
            predictions.append(model(x_batch.to(device)).cpu())
            targets.append(y_batch)
    metrics = compute_metrics(torch.cat(targets), torch.cat(predictions))
    output_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([metrics]).to_csv(output_dir / "evaluation_metrics.csv", index=False)
    (output_dir / "evaluation_summary.md").write_text(
        "# Evaluation Summary\n\n"
        "Deterministic evaluation on the synthetic test split.\n\n"
        + "\n".join(f"- {key}: {value:.6f}" for key, value in metrics.items())
        + "\n\nThese are synthetic demonstration results, not real PhD findings.\n",
        encoding="utf-8",
    )
    metadata_path = model_dir / "model_metadata.json"
    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["evaluation_metrics"] = metrics
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print("Evaluation metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.6f}")


if __name__ == "__main__":
    main()

