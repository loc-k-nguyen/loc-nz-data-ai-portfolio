# Model Validation Notes

## Dataset Used

- Dataset: Wisconsin Diagnostic Breast Cancer dataset
- Source: `sklearn.datasets.load_breast_cancer`
- Data type: public benchmark-style demonstration data
- Target: `risk_label`
- Positive class: `risk_label=1`, malignant/high-risk demonstration class

This project does not use private, operational, customer, citizen, or sensitive user data.

## Selected Model

- Selected model: `logistic_regression`
- Selection rule: highest validation ROC AUC when available, otherwise highest F1
- Models compared:
  - Logistic Regression
  - Random Forest

## Metrics Summary

Held-out test metrics from `outputs/evaluation_metrics.csv`:

| Metric | Value |
| --- | ---: |
| Accuracy | 0.9825 |
| Precision | 0.9762 |
| Recall | 0.9762 |
| F1 | 0.9762 |
| ROC AUC | 0.9960 |

## Confusion Matrix Summary

From `outputs/confusion_matrix.csv`:

|  | Predicted low risk 0 | Predicted high risk 1 |
| --- | ---: | ---: |
| Actual low risk 0 | 71 | 1 |
| Actual high risk 1 | 1 | 41 |

This means the current held-out test run has one false positive and one false negative. This should not be generalized to real-world performance.

## Feature Importance Summary

The selected model is Logistic Regression, so `outputs/feature_importance.csv` reports absolute coefficient magnitudes, not causal effects.

Top coefficient-magnitude features in the current run include:

- `worst_texture`
- `radius_error`
- `mean_concave_points`
- `worst_symmetry`
- `worst_radius`

These features should be read as model signals within this dataset, not clinical explanations.

## Key Cautions

- This is a public teaching dataset.
- The model is not suitable for clinical use.
- The model is not suitable for operational deployment.
- High metrics may reflect dataset size, dataset quality, feature separability, and train/test split characteristics.
- No external validation, fairness analysis, calibration, or monitoring has been performed.

## Employability Evidence

This project demonstrates:

- Reproducible Python ML workflow
- scikit-learn Pipeline and preprocessing
- Baseline and tree-based model comparison
- Held-out evaluation
- Confusion matrix, ROC AUC, and feature importance outputs
- Batch prediction script
- Streamlit demo readiness
- Model card and responsible ML documentation

## What This Project Does Not Demonstrate

- Production deployment
- Clinical validation
- Real-time monitoring
- Data governance implementation
- Regulatory approval
- Real-world decision system reliability

