"""Streamlit demo app for the risk prediction model."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

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
FEATURE_INFO_PATH = PROJECT_ROOT / "data" / "processed" / "feature_info.csv"
TEST_PATH = PROJECT_ROOT / "data" / "processed" / "test.csv"


st.set_page_config(page_title="Risk Prediction Demo", layout="wide")
st.title("Applied ML Risk Prediction Demo")
st.caption("Public dataset portfolio demo using a saved scikit-learn model.")
st.warning(
    "Demonstration only. This app is not for clinical, financial, legal, "
    "or operational decision-making."
)

if not MODEL_PATH.exists() or not FEATURE_INFO_PATH.exists() or not TEST_PATH.exists():
    st.info(
        "Run the pipeline first: `python run_project.py`. "
        "The app requires prepared data and a trained model."
    )
else:
    model = joblib.load(MODEL_PATH)
    feature_info = pd.read_csv(FEATURE_INFO_PATH)
    test_df = pd.read_csv(TEST_PATH)
    feature_names = feature_info["feature_name"].tolist()

    st.write(
        "Use the sliders below to score one demonstration record. "
        "Default values are medians from the held-out test split."
    )
    defaults = test_df[feature_names].median(numeric_only=True)
    values: dict[str, float] = {}
    columns = st.columns(2)
    for index, feature in enumerate(feature_names):
        series = test_df[feature]
        with columns[index % 2]:
            values[feature] = st.slider(
                feature,
                min_value=float(series.min()),
                max_value=float(series.max()),
                value=float(defaults[feature]),
            )

    input_df = pd.DataFrame([values])
    if st.button("Predict risk class"):
        prediction = int(model.predict(input_df)[0])
        probability = (
            float(model.predict_proba(input_df)[0, 1])
            if hasattr(model, "predict_proba")
            else None
        )
        st.metric("Predicted risk label", prediction)
        if probability is not None:
            st.metric("Predicted probability for risk_label=1", f"{probability:.3f}")
        st.caption(
            "risk_label=1 is the malignant/high-risk demonstration class in this public dataset. "
            "This output is for workflow demonstration only."
        )
