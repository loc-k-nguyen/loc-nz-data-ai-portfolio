# Applied ML Risk Prediction Evaluation Report

## Problem Framing

This project demonstrates a supervised binary risk prediction workflow. The model predicts `risk_label` from numeric diagnostic measurement features in a public benchmark-style dataset.

This is a portfolio demonstration only. It is not a clinical model and must not be used for clinical, financial, legal, or operational decisions.

## Dataset

- Dataset: Wisconsin Diagnostic Breast Cancer dataset
- Source: `sklearn.datasets.load_breast_cancer`
- Data type: public demonstration data
- Full dataset rows: 569
- Features: 30 numeric measurement features
- Target: `risk_label`
- Positive class: `risk_label=1`, malignant/high-risk demonstration class

## Train/Test Split

`src/prepare_data.py` creates a stratified split:

- Train rows: 455
- Test rows: 114

## Models Compared

The training workflow compares:

| Model | Role |
| --- | --- |
| Logistic Regression | Interpretable baseline |
| Random Forest | Tree-based comparison model |

Validation metrics from `models/model_metadata.json`:

| Model | Accuracy | Precision | Recall | F1 | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: |
| Logistic Regression | 0.9670 | 0.9429 | 0.9706 | 0.9565 | 0.9948 |
| Random Forest | 0.9670 | 0.9697 | 0.9412 | 0.9552 | 0.9876 |

## Selected Model

Selected model:

```text
logistic_regression
```

Selection rule:

```text
highest validation ROC AUC when available, otherwise highest F1
```

## Test Metrics

Held-out test metrics from `outputs/evaluation_metrics.csv`:

| Metric | Value |
| --- | ---: |
| Accuracy | 0.9825 |
| Precision | 0.9762 |
| Recall | 0.9762 |
| F1 | 0.9762 |
| ROC AUC | 0.9960 |

These results show the workflow is functioning correctly on this public dataset. They should not be interpreted as deployment evidence.

## Confusion Matrix Interpretation

From `outputs/confusion_matrix.csv`:

|  | Predicted low risk 0 | Predicted high risk 1 |
| --- | ---: | ---: |
| Actual low risk 0 | 71 | 1 |
| Actual high risk 1 | 1 | 41 |

The current test run has one false positive and one false negative. In a real risk system, the costs of these errors would need domain review before choosing a decision threshold.

## ROC/AUC Interpretation

The ROC AUC is 0.9960 on the held-out test split. This indicates strong separation on this dataset, but the dataset is small and well-known. It does not prove real-world reliability.

## Feature Importance Discussion

The selected Logistic Regression model reports absolute coefficient magnitudes in `outputs/feature_importance.csv`. Top coefficient-magnitude features include:

- `worst_texture`
- `radius_error`
- `mean_concave_points`
- `worst_symmetry`
- `worst_radius`

These values describe model behavior on this dataset. They are not causal explanations or clinical conclusions.

## Limitations

- Public benchmark-style dataset only.
- No external validation.
- No calibration analysis.
- No fairness or subgroup analysis.
- No clinical workflow integration.
- No monitoring or drift detection.

## Ethical And Deployment Cautions

This model is not suitable for clinical use. It should not be used to triage, diagnose, approve, deny, prioritize, or automate any real-world decision.

## Next Steps

- Add cross-validation.
- Add calibration and threshold analysis.
- Add model robustness checks.
- Add a small app screenshot after manual testing.
- Adapt the project structure to a non-sensitive New Zealand public dataset for a locally relevant variant.

