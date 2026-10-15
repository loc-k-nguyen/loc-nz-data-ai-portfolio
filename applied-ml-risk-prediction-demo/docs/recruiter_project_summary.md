# Recruiter Project Summary

## Five-Line Summary

This project demonstrates an end-to-end supervised machine learning workflow for binary risk prediction.
It uses the public Wisconsin Diagnostic Breast Cancer dataset through scikit-learn.
The workflow prepares data, trains Logistic Regression and Random Forest models, evaluates the selected model, and exports predictions.
It includes model documentation, feature importance, plots, and a Streamlit demo scaffold.
It is a portfolio demonstration only, not a clinical or operational model.

## Skills Demonstrated

- Python project structure
- pandas data preparation
- scikit-learn Pipelines and preprocessing
- Model comparison
- Held-out evaluation
- Confusion matrix, ROC AUC, and feature importance reporting
- Batch prediction export
- Streamlit demo readiness
- Model card and responsible ML documentation

## Interview Talking Points

- Why Logistic Regression is a useful baseline
- How train/test split and validation selection are handled
- Why ROC AUC, recall, precision, and confusion matrix all matter
- Why high metrics on a public teaching dataset should not be overgeneralized
- How this structure could transfer to a non-sensitive New Zealand public dataset

## CV Bullet Points

- Built a reproducible Python machine learning workflow for binary risk prediction using scikit-learn pipelines, model comparison, held-out evaluation, and batch prediction export.
- Created model documentation including evaluation metrics, model card, feature importance, Streamlit demo readiness, and deployment cautions for responsible ML communication.
- Compared Logistic Regression and Random Forest classifiers, selected the best validation model, and reported test-set accuracy, precision, recall, F1, ROC AUC, and confusion matrix outputs.

## LinkedIn Post Draft

I built an applied ML risk prediction demo as part of my New Zealand data and AI portfolio.

The project focuses on practical machine learning workflow evidence: data preparation, scikit-learn Pipelines, model comparison, held-out evaluation, batch prediction, model card documentation, and responsible limitations.

It uses a public benchmark-style dataset and is explicitly not a clinical or operational model. The goal is to show reproducible ML engineering practice and clear communication of model limitations.

## Honest Limitations

- Public teaching dataset only
- Not New Zealand-specific
- Not suitable for clinical use
- No external validation
- No production monitoring
- High metrics should not be treated as deployment reliability

