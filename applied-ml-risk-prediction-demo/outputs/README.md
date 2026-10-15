# Outputs

Generated artifacts from the applied ML workflow.

| File | Purpose |
| --- | --- |
| `evaluation_metrics.csv` | Test-set accuracy, precision, recall, F1, and ROC AUC. |
| `confusion_matrix.csv` | Confusion matrix for the held-out test set. |
| `predictions_sample.csv` | Small sample of test predictions and probabilities. |
| `batch_predictions.csv` | Batch prediction output from `src/predict.py`. |
| `feature_importance.csv` | Feature importance or absolute coefficients when available. |
| `evaluation_summary.md` | Markdown summary of model evaluation. |
| `model_validation_notes.md` | Cautious validation notes explaining metrics, confusion matrix, feature importance, and limitations. |
| `confusion_matrix.png` | Confusion matrix plot. |
| `roc_curve.png` | ROC curve plot when probabilities are available. |
| `feature_importance.png` | Top feature importance plot when available. |

These outputs are generated from a public demonstration dataset and do not support real-world decision-making.
