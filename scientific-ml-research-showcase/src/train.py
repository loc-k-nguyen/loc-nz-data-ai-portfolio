"""Train a lightweight synthetic scientific ML surrogate model."""

from __future__ import annotations

import json
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import yaml
from dataset import SyntheticConfig, create_splits, save_dataset_metadata
from metrics import compute_metrics
from models import build_model
from torch import nn
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "configs" / "config.yaml"


def set_seed(seed: int) -> None:
    """Set seeds for reproducible local runs."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def get_device(config: dict) -> torch.device:
    """Return CUDA when requested/available, otherwise CPU."""
    requested = str(config.get("device", "auto")).lower()
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(requested)


def evaluate_loader(model: nn.Module, loader: DataLoader, device: torch.device) -> dict[str, float]:
    """Evaluate model over a dataloader and return aggregate metrics."""
    model.eval()
    predictions: list[torch.Tensor] = []
    targets: list[torch.Tensor] = []
    with torch.no_grad():
        for x_batch, y_batch in loader:
            x_batch = x_batch.to(device)
            y_batch = y_batch.to(device)
            predictions.append(model(x_batch).cpu())
            targets.append(y_batch.cpu())
    return compute_metrics(torch.cat(targets), torch.cat(predictions))


def save_example_plots(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
    output_dir: Path,
) -> None:
    """Save prediction and error-map examples."""
    model.eval()
    x_batch, y_batch = next(iter(loader))
    with torch.no_grad():
        prediction = model(x_batch.to(device)).cpu()

    x = x_batch[0]
    target = y_batch[0, 0]
    pred = prediction[0, 0]
    error = torch.abs(target - pred)

    fig, axes = plt.subplots(1, 4, figsize=(12, 3))
    panels = [
        (x[0], "Permeability-like input"),
        (x[1], "Source input"),
        (target, "Synthetic target"),
        (pred, "Model prediction"),
    ]
    for axis, (field, title) in zip(axes, panels):
        axis.imshow(field.numpy(), cmap="viridis")
        axis.set_title(title)
        axis.axis("off")
    plt.tight_layout()
    fig.savefig(output_dir / "prediction_examples.png", dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(9, 3))
    for axis, field, title in [
        (axes[0], target, "Target"),
        (axes[1], pred, "Prediction"),
        (axes[2], error, "Absolute error"),
    ]:
        axis.imshow(field.numpy(), cmap="magma")
        axis.set_title(title)
        axis.axis("off")
    plt.tight_layout()
    fig.savefig(output_dir / "error_map_examples.png", dpi=160)
    plt.close(fig)


def main() -> None:
    """Run training, validation, test evaluation, and output export."""
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    set_seed(int(config["random_seed"]))
    device = get_device(config)

    output_dir = PROJECT_ROOT / config["output_dir"]
    model_dir = PROJECT_ROOT / config["model_dir"]
    data_dir = PROJECT_ROOT / config["data_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    synthetic_config = SyntheticConfig(
        num_samples=int(config["num_samples"]),
        image_size=int(config["image_size"]),
        random_seed=int(config["random_seed"]),
    )
    train_set, val_set, test_set = create_splits(
        synthetic_config,
        train_fraction=float(config["train_fraction"]),
        validation_fraction=float(config["validation_fraction"]),
    )
    save_dataset_metadata(data_dir / "synthetic_dataset_metadata.json", synthetic_config)

    train_loader = DataLoader(train_set, batch_size=int(config["batch_size"]), shuffle=True)
    val_loader = DataLoader(val_set, batch_size=int(config["batch_size"]))
    test_loader = DataLoader(test_set, batch_size=int(config["batch_size"]))

    model = build_model(
        model_name=str(config["model_name"]),
        input_channels=int(config["input_channels"]),
        output_channels=int(config["target_channels"]),
        base_channels=int(config["base_channels"]),
    ).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=float(config["learning_rate"]))
    loss_fn = nn.MSELoss()

    history: list[dict[str, float]] = []
    for epoch in range(1, int(config["epochs"]) + 1):
        model.train()
        losses: list[float] = []
        for x_batch, y_batch in train_loader:
            x_batch = x_batch.to(device)
            y_batch = y_batch.to(device)
            optimizer.zero_grad()
            loss = loss_fn(model(x_batch), y_batch)
            loss.backward()
            optimizer.step()
            losses.append(loss.item())
        val_metrics = evaluate_loader(model, val_loader, device)
        row = {"epoch": epoch, "train_loss": float(np.mean(losses)), **{f"val_{k}": v for k, v in val_metrics.items()}}
        history.append(row)
        print(f"Epoch {epoch}: train_loss={row['train_loss']:.5f}, val_rmse={row['val_rmse']:.5f}")

    val_metrics = evaluate_loader(model, val_loader, device)
    test_metrics = evaluate_loader(model, test_loader, device)
    pd.DataFrame(history).to_csv(output_dir / "training_history.csv", index=False)
    metrics_df = pd.DataFrame(
        [{"split": "validation", **val_metrics}, {"split": "test", **test_metrics}]
    )
    metrics_df.to_csv(output_dir / "metrics.csv", index=False)
    save_example_plots(model, test_loader, device, output_dir)

    model_path = model_dir / "scientific_surrogate_model.pt"
    torch.save(model.state_dict(), model_path)
    metadata = {
        "experiment_name": config["experiment_name"],
        "synthetic_data": True,
        "private_data_used": False,
        "model_name": config["model_name"],
        "device": str(device),
        "num_samples": config["num_samples"],
        "image_size": config["image_size"],
        "epochs": config["epochs"],
        "test_metrics": test_metrics,
    }
    (model_dir / "model_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    summary = [
        "# Experiment Summary",
        "",
        "- Data: synthetic demonstration fields, not private PhD data.",
        f"- Experiment: `{config['experiment_name']}`",
        f"- Model: `{config['model_name']}`",
        f"- Device: `{device}`",
        f"- Samples: {config['num_samples']}",
        f"- Image size: {config['image_size']} x {config['image_size']}",
        "",
        "## Test Metrics",
        "",
    ]
    for key, value in test_metrics.items():
        summary.append(f"- {key}: {value:.6f}")
    summary.extend(
        [
            "",
            "## Limitation",
            "",
            "These are synthetic demonstration results and should not be interpreted as real "
            "scientific or PhD findings.",
        ]
    )
    (output_dir / "experiment_summary.md").write_text("\n".join(summary), encoding="utf-8")

    print("Final test metrics:")
    for key, value in test_metrics.items():
        print(f"  {key}: {value:.6f}")
    print(f"Saved model to {model_path}")
    print(f"Saved outputs to {output_dir}")


if __name__ == "__main__":
    main()

