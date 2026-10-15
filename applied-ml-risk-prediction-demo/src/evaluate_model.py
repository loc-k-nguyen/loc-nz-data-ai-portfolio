"""Evaluate the saved risk prediction model on held-out test data."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    RocCurveDisplay,
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

TARGET_COLUMN = "risk_label"
ID_COLUMN = "record_id"


def find_project_root() -> Path:
    """Locate the project root regardless of the launch directory."""
    current = Path(__file__).resolve()
    for parent in [current.parent, *current.parents]:
        if (parent / "src").exists() and (parent / "data").exists():
            return parent
    return current.parents[1]


PROJECT_ROOT = find_project_root()
TEST_PATH = PROJECT_ROOT / "data" / "processed" / "test.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "risk_prediction_model.joblib"
METADATA_PATH = PROJECT_ROOT / "models" / "model_metadata.json"
OUTPUT_DIR = PROJECT_ROOT / "outputs"


def split_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Split features and target."""
    drop_columns = [TARGET_COLUMN]
    if ID_COLUMN in df.columns:
        drop_columns.append(ID_COLUMN)
    return df.drop(columns=drop_columns), df[TARGET_COLUMN]


def get_feature_importance(model: object, feature_names: list[str]) -> pd.DataFrame | None:
    """Extract feature importance or logistic coefficients when available."""
    estimator = model.named_steps.get("model") if hasattr(model, "named_steps") else None
    if estimator is None:
        return None

    if hasattr(estimator, "feature_importances_"):
        values = estimator.feature_importances_
        importance_type = "feature_importance"
    elif hasattr(estimator, "coef_"):
        values = abs(estimator.coef_[0])
        importance_type = "absolute_coefficient"
    else:
        return None

    return (
        pd.DataFrame(
            {
                "feature": feature_names,
                "importance": values,
                "importance_type": importance_type,
            }
        )
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )


def main() -> None:
    """Evaluate model and write metrics, predictions, and plots."""
    if not TEST_PATH.exists():
        raise FileNotFoundError(f"Test data not found: {TEST_PATH}. Run prepare_data.py first.")
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}. Run train_model.py first.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    test_df = pd.read_csv(TEST_PATH)
    model = joblib.load(MODEL_PATH)
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8")) if METADATA_PATH.exists() else {}

    x_test, y_test = split_features(test_df)
    predictions = model.predict(x_test)
    probabilities = model.predict_proba(x_test)[:, 1] if hasattr(model, "predict_proba") else None

    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1": f1_score(y_test, predictions, zero_division=0),
    }
    if probabilities is not None:
        metrics["roc_auc"] = roc_auc_score(y_test, probabilities)

    metrics_df = pd.DataFrame([{"metric": key, "value": value} for key, value in metrics.items()])
    metrics_df.to_csv(OUTPUT_DIR / "evaluation_metrics.csv", index=False)

    cm = confusion_matrix(y_test, predictions, labels=[0, 1])
    cm_df = pd.DataFrame(
        cm,
        index=["actual_low_risk_0", "actual_high_risk_1"],
        columns=["predicted_low_risk_0", "predicted_high_risk_1"],
    )
    cm_df.to_csv(OUTPUT_DIR / "confusion_matrix.csv")

    sample_columns = [ID_COLUMN, TARGET_COLUMN] if ID_COLUMN in test_df.columns else [TARGET_COLUMN]
    sample = test_df[sample_columns].copy()
    sample["predicted_label"] = predictions
    if probabilities is not None:
        sample["predicted_probability_high_risk"] = probabilities
    sample.head(30).to_csv(OUTPUT_DIR / "predictions_sample.csv", index=False)

    display = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["low risk", "high risk"])
    display.plot(values_format="d", colorbar=False)
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "confusion_matrix.png", dpi=160)
    plt.close()

    if probabilities is not None:
        RocCurveDisplay.from_predictions(y_test, probabilities)
        plt.title("ROC Curve")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "roc_curve.png", dpi=160)
        plt.close()

    feature_importance = get_feature_importance(model, x_test.columns.tolist())
    if feature_importance is not None:
        feature_importance.to_csv(OUTPUT_DIR / "feature_importance.csv", index=False)
        top_features = feature_importance.head(15).sort_values("importance", ascending=True)
        plt.barh(top_features["feature"], top_features["importance"])
        plt.title("Top Feature Importance")
        plt.xlabel("Importance")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "feature_importance.png", dpi=160)
        plt.close()

    selected_model = metadata.get("selected_model", "unknown")
    summary = ["# Evaluation Summary", ""]
    summary.append("- Dataset: Wisconsin Diagnostic Breast Cancer public dataset via scikit-learn")
    summary.append(f"- Selected model: `{selected_model}`")
    summary.append(f"- Test rows: {len(test_df)}")
    summary.append("- Positive class: `risk_label=1` means malignant/high-risk demonstration class")
    summary.append("")
    summary.append("## Metrics")
    summary.append("")
    for key, value in metrics.items():
        summary.append(f"- {key}: {value:.4f}")
    summary.append("")
    summary.append("## Interpretation Note")
    summary.append("")
    summary.append(
        "This is a supervised ML portfolio demonstration using a public teaching dataset. "
        "It is not suitable for clinical, financial, legal, or operational decision-making."
    )
    (OUTPUT_DIR / "evaluation_summary.md").write_text("\n".join(summary), encoding="utf-8")

    print(f"Wrote {OUTPUT_DIR / 'evaluation_metrics.csv'}")
    print(f"Wrote {OUTPUT_DIR / 'confusion_matrix.csv'}")
    print(f"Wrote {OUTPUT_DIR / 'predictions_sample.csv'}")
    print(f"Wrote {OUTPUT_DIR / 'evaluation_summary.md'}")


if __name__ == "__main__":
    main()

