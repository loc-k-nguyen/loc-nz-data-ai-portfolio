"""Prepare a public binary classification dataset for risk prediction.

This project uses the Wisconsin Breast Cancer dataset bundled with
scikit-learn. It is a public demonstration dataset, not operational data.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

TARGET_COLUMN = "risk_label"
ID_COLUMN = "record_id"
RANDOM_STATE = 42
TEST_SIZE = 0.2
DATASET_SOURCE = "scikit-learn load_breast_cancer, Wisconsin Diagnostic Breast Cancer dataset"


def find_project_root() -> Path:
    """Locate the project root regardless of the launch directory."""
    current = Path(__file__).resolve()
    for parent in [current.parent, *current.parents]:
        if (parent / "src").exists() and (parent / "data").exists():
            return parent
    return current.parents[1]


PROJECT_ROOT = find_project_root()
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
MODEL_DIR = PROJECT_ROOT / "models"


def snake_case(text: str) -> str:
    """Convert a feature name to snake_case."""
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def build_dataset() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the public dataset and return data plus feature metadata."""
    dataset = load_breast_cancer()
    feature_names = [snake_case(name) for name in dataset.feature_names]
    df = pd.DataFrame(dataset.data, columns=feature_names)
    df.insert(0, ID_COLUMN, range(1, len(df) + 1))

    # sklearn target: 0 = malignant, 1 = benign.
    # Portfolio risk framing: risk_label=1 means malignant/high-risk class.
    df[TARGET_COLUMN] = (dataset.target == 0).astype(int)

    feature_info = pd.DataFrame(
        {
            "feature_name": feature_names,
            "role": "input_feature",
            "data_type": "numeric",
            "source_description": dataset.DESCR.splitlines()[0],
        }
    )
    return df, feature_info


def main() -> None:
    """Create train/test splits and feature metadata."""
    for directory in [RAW_DIR, PROCESSED_DIR, OUTPUT_DIR, MODEL_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    df, feature_info = build_dataset()
    train_df, test_df = train_test_split(
        df,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=df[TARGET_COLUMN],
    )

    train_path = PROCESSED_DIR / "train.csv"
    test_path = PROCESSED_DIR / "test.csv"
    feature_info_path = PROCESSED_DIR / "feature_info.csv"
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    feature_info.to_csv(feature_info_path, index=False)

    class_balance = df[TARGET_COLUMN].value_counts(normalize=True).sort_index()
    print(f"Dataset source: {DATASET_SOURCE}")
    print("Data type: public demonstration data, not private or operational data")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Target column: {TARGET_COLUMN}")
    print("Class balance:")
    for label, share in class_balance.items():
        print(f"  risk_label={label}: {share:.3f}")
    print(f"Train rows: {len(train_df)}")
    print(f"Test rows: {len(test_df)}")
    print(f"Wrote {train_path}")
    print(f"Wrote {test_path}")
    print(f"Wrote {feature_info_path}")


if __name__ == "__main__":
    main()

