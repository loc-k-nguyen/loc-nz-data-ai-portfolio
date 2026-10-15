# Applied ML Risk Prediction Evaluation Report

This file is retained as a readable evaluation summary. The cleaner report version is:

```text
reports/evaluation_report.md
```

## Dataset Summary

- Dataset: Wisconsin Diagnostic Breast Cancer public dataset
- Source: `sklearn.datasets.load_breast_cancer`
- Target: `risk_label`
- Positive class: `risk_label=1`, malignant/high-risk demonstration class
- Data split: train/test split created by `src/prepare_data.py`

## Model Comparison

The training workflow compares:

- Logistic Regression baseline
- Random Forest classifier

The current run selected:

```text
logistic_regression
```

Validation metrics from `models/model_metadata.json`:

| Model | Accuracy | Precision | Recall | F1 | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: |
| Logistic Regression | 0.9670 | 0.9429 | 0.9706 | 0.9565 | 0.9948 |
| Random Forest | 0.9670 | 0.9697 | 0.9412 | 0.9552 | 0.9876 |

The selected model is stored in:

```text
models/risk_prediction_model.joblib
```

Model metadata is stored in:

```text
models/model_metadata.json
```

## Metrics

Held-out test metrics:

| Metric | Value |
| --- | ---: |
| Accuracy | 0.9825 |
| Precision | 0.9762 |
| Recall | 0.9762 |
| F1 | 0.9762 |
| ROC AUC | 0.9960 |

Generated metrics are stored in:

```text
outputs/evaluation_metrics.csv
```

These metrics are useful for demonstrating workflow quality but should not be described as evidence of deployment reliability.

## Confusion Matrix Notes

The confusion matrix is stored in:

```text
outputs/confusion_matrix.csv
outputs/confusion_matrix.png
```

Current confusion matrix:

|  | Predicted low risk 0 | Predicted high risk 1 |
| --- | ---: | ---: |
| Actual low risk 0 | 71 | 1 |
| Actual high risk 1 | 1 | 41 |

For real risk systems, false negatives and false positives should be discussed with domain experts. This project does not make operational threshold recommendations.

## Threshold Discussion

The current workflow uses the default classification threshold. Future work could tune thresholds based on a clearly defined cost of false positives and false negatives.

## Limitations

- Public teaching dataset only.
- Not a clinical, financial, legal, or operational system.
- No external validation.
- No fairness or subgroup analysis.

## Next Steps

- Add cross-validation.
- Add calibration analysis.
- Add threshold tuning.
- Add model monitoring concepts.
- Adapt the pipeline to a non-sensitive New Zealand public dataset.
