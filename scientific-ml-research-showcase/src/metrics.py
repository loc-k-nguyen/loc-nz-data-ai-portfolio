"""Metrics for field-to-field scientific ML surrogate experiments."""

from __future__ import annotations

import torch


def mae(y_true: torch.Tensor, y_pred: torch.Tensor) -> float:
    """Mean absolute error."""
    return torch.mean(torch.abs(y_true - y_pred)).item()


def rmse(y_true: torch.Tensor, y_pred: torch.Tensor) -> float:
    """Root mean squared error."""
    return torch.sqrt(torch.mean((y_true - y_pred) ** 2)).item()


def relative_mae(y_true: torch.Tensor, y_pred: torch.Tensor) -> float:
    """MAE normalized by mean absolute target value."""
    denominator = torch.mean(torch.abs(y_true)).clamp_min(1e-8)
    return (torch.mean(torch.abs(y_true - y_pred)) / denominator).item()


def field_correlation(y_true: torch.Tensor, y_pred: torch.Tensor) -> float:
    """Global Pearson correlation over flattened fields."""
    true_flat = y_true.flatten()
    pred_flat = y_pred.flatten()
    true_centered = true_flat - torch.mean(true_flat)
    pred_centered = pred_flat - torch.mean(pred_flat)
    denominator = torch.linalg.norm(true_centered) * torch.linalg.norm(pred_centered)
    if denominator.item() == 0:
        return float("nan")
    return torch.dot(true_centered, pred_centered).div(denominator).item()


def simple_ssim_like(y_true: torch.Tensor, y_pred: torch.Tensor) -> float:
    """Small global SSIM-like score for smoke-test comparison, not publication SSIM."""
    c1 = 0.01**2
    c2 = 0.03**2
    mu_x = torch.mean(y_true)
    mu_y = torch.mean(y_pred)
    var_x = torch.var(y_true)
    var_y = torch.var(y_pred)
    cov_xy = torch.mean((y_true - mu_x) * (y_pred - mu_y))
    score = ((2 * mu_x * mu_y + c1) * (2 * cov_xy + c2)) / (
        (mu_x**2 + mu_y**2 + c1) * (var_x + var_y + c2)
    )
    return score.item()


def compute_metrics(y_true: torch.Tensor, y_pred: torch.Tensor) -> dict[str, float]:
    """Return all field metrics."""
    return {
        "mae": mae(y_true, y_pred),
        "rmse": rmse(y_true, y_pred),
        "relative_mae": relative_mae(y_true, y_pred),
        "field_correlation": field_correlation(y_true, y_pred),
        "simple_ssim_like": simple_ssim_like(y_true, y_pred),
    }

