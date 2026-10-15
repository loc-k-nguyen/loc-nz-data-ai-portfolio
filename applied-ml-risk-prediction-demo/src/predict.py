"""Batch prediction entry point for the risk prediction demo."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd

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
MODEL_PATH = PROJECT_ROOT / "models" / "risk_prediction_model.joblib"
DEFAULT_INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "test.csv"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "outputs" / "batch_predictions.csv"


def run_predictions(input_path: Path, output_path: Path) -> None:
    """Load a CSV, score rows, and write predictions."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}. Run train_model.py first.")
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    model = joblib.load(MODEL_PATH)
    df = pd.read_csv(input_path)
    feature_df = df.drop(columns=[column for column in [TARGET_COLUMN, ID_COLUMN] if column in df.columns])

    result = df.copy()
    result["predicted_label"] = model.predict(feature_df)
    if hasattr(model, "predict_proba"):
        result["predicted_probability_high_risk"] = model.predict_proba(feature_df)[:, 1]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    print(f"Output path: {output_path}")
    print(f"Rows scored: {len(result)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run batch predictions for the risk demo.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH, help="Input CSV path")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help="Output CSV path")
    args = parser.parse_args()
    run_predictions(args.input, args.output)


if __name__ == "__main__":
    main()

