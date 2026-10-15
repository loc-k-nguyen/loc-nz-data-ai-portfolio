# Model Exploration Notes

## Project Framing

This project demonstrates a binary risk prediction workflow using a public teaching dataset. It is designed to show practical ML skills for portfolio review, not to support real-world decisions.

## Dataset Description

- Dataset: Wisconsin Diagnostic Breast Cancer dataset
- Source: `sklearn.datasets.load_breast_cancer`
- Features: 30 numeric measurement features
- Target: `risk_label`

## Target Variable

- `risk_label=1`: malignant/high-risk demonstration class
- `risk_label=0`: benign/lower-risk demonstration class

## Train/Test Split

`src/prepare_data.py` creates stratified train and test CSV files under `data/processed/`.

## Baseline Model

The baseline is Logistic Regression with preprocessing in a scikit-learn Pipeline.

## Model Comparison

The workflow compares Logistic Regression and Random Forest, then selects the model with the strongest validation ROC AUC when available.

## Evaluation Metrics

- Accuracy
- Precision
- Recall
- F1
- ROC AUC
- Confusion matrix

## Interpretation Cautions

This is not a clinical tool. Strong metrics on a small public dataset do not imply deployment readiness.

## Next Steps

- Add cross-validation.
- Add calibration.
- Add threshold tuning.
- Add a cleaner interactive app layout.

