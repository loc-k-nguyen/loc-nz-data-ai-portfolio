"""Train baseline and tree-based risk prediction models."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET_COLUMN = "risk_label"
ID_COLUMN = "record_id"
RANDOM_STATE = 42


def find_project_root() -> Path:
    """Locate the project root regardless of the launch directory."""
    current = Path(__file__).resolve()
    for parent in [current.parent, *current.parents]:
        if (parent / "src").exists() and (parent / "data").exists():
            return parent
    return current.parents[1]


PROJECT_ROOT = find_project_root()
TRAIN_PATH = PROJECT_ROOT / "data" / "processed" / "train.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "risk_prediction_model.joblib"
METADATA_PATH = PROJECT_ROOT / "models" / "model_metadata.json"


def split_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Split features and target."""
    drop_columns = [TARGET_COLUMN]
    if ID_COLUMN in df.columns:
        drop_columns.append(ID_COLUMN)
    return df.drop(columns=drop_columns), df[TARGET_COLUMN]


def build_preprocessor(x: pd.DataFrame) -> ColumnTransformer:
    """Build preprocessing for numeric and categorical columns."""
    numeric_features = x.select_dtypes(include=["number"]).columns.tolist()
    categorical_features = x.select_dtypes(exclude=["number"]).columns.tolist()

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
    )


def evaluate(model: Pipeline, x_valid: pd.DataFrame, y_valid: pd.Series) -> dict[str, float]:
    """Evaluate a classifier on validation data."""
    predictions = model.predict(x_valid)
    metrics = {
        "accuracy": accuracy_score(y_valid, predictions),
        "precision": precision_score(y_valid, predictions, zero_division=0),
        "recall": recall_score(y_valid, predictions, zero_division=0),
        "f1": f1_score(y_valid, predictions, zero_division=0),
    }
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(x_valid)[:, 1]
        metrics["roc_auc"] = roc_auc_score(y_valid, probabilities)
    return metrics


def main() -> None:
    """Train candidate models and save the best validation model."""
    if not TRAIN_PATH.exists():
        raise FileNotFoundError(f"Training data not found: {TRAIN_PATH}. Run prepare_data.py first.")

    train_df = pd.read_csv(TRAIN_PATH)
    x, y = split_features(train_df)
    x_train, x_valid, y_train, y_valid = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    preprocessor = build_preprocessor(x_train)
    candidates = {
        "logistic_regression": LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            min_samples_leaf=2,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }

    results: dict[str, dict[str, float]] = {}
    fitted_models: dict[str, Pipeline] = {}
    for name, estimator in candidates.items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", estimator),
            ]
        )
        pipeline.fit(x_train, y_train)
        results[name] = evaluate(pipeline, x_valid, y_valid)
        fitted_models[name] = pipeline

    selected_model_name = max(results, key=lambda name: results[name].get("roc_auc", results[name]["f1"]))
    selected_model = fitted_models[selected_model_name]

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(selected_model, MODEL_PATH)

    metadata = {
        "dataset": "Wisconsin Diagnostic Breast Cancer dataset via scikit-learn",
        "target_column": TARGET_COLUMN,
        "positive_class": "risk_label=1 means malignant/high-risk demonstration class",
        "id_column": ID_COLUMN,
        "features": x.columns.tolist(),
        "models_compared": list(candidates.keys()),
        "validation_metrics": results,
        "selected_model": selected_model_name,
        "selection_rule": "highest validation ROC AUC when available, otherwise highest F1",
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Features used: {x.columns.tolist()}")
    print(f"Target: {TARGET_COLUMN}")
    print(f"Model names compared: {list(candidates.keys())}")
    print("Validation metrics:")
    for name, metrics in results.items():
        print(f"  {name}: {metrics}")
    print(f"Selected model: {selected_model_name}")
    print(f"Saved model to {MODEL_PATH}")
    print(f"Saved metadata to {METADATA_PATH}")


if __name__ == "__main__":
    main()

