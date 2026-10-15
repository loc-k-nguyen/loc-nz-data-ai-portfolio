# Recruiter Navigation Guide

## Data Analyst / BI Analyst

Start with [NZ Local Housing Statistics Insights Dashboard](../nz-open-data-insights-dashboard/).

Review:

- `README.md`
- `src/clean_data.py`
- `src/build_sqlite_database.py`
- `sql/02_data_quality_checks.sql`
- `sql/03_analysis_queries.sql`
- `powerbi/build_assets/`
- `reports/stakeholder_brief_template.md`

Evidence to look for:

- Official NZ public data
- Python cleaning
- SQL checks
- Power BI-ready outputs
- Stakeholder reporting

## Government Insights Analyst / Research Analyst

Start with Project 1, then review the documentation in Project 2.

Review:

- `nz-open-data-insights-dashboard/outputs/indicator_validation_notes.md`
- `nz-open-data-insights-dashboard/outputs/preliminary_findings.md`
- `applied-ml-risk-prediction-demo/outputs/model_validation_notes.md`

Evidence to look for:

- Careful interpretation
- Cautions around indicator direction
- Clear separation of data outputs and policy claims
- Reproducible methods

## Data Scientist / Junior ML Engineer

Start with [Applied ML Risk Prediction Demo](../applied-ml-risk-prediction-demo/).

Review:

- `README.md`
- `run_project.py`
- `src/train_model.py`
- `src/evaluate_model.py`
- `reports/model_card.md`
- `reports/evaluation_report.md`
- `outputs/model_validation_notes.md`

Evidence to look for:

- scikit-learn Pipeline
- Logistic Regression and Random Forest comparison
- Held-out test metrics
- Confusion matrix, ROC AUC, feature importance
- Batch prediction
- Model limitations

## Data Engineer

Start with Project 1.

Review:

- `src/build_sqlite_database.py`
- `src/run_analysis_exports.py`
- `sql/01_create_tables.sql`
- `.gitignore`

Evidence to look for:

- Reproducible generation of analysis-ready files
- SQLite database creation
- Artifact management
- Clear folder structure

## Lecturer / Research Fellow / Research Assistant

Review [Scientific ML Research Showcase](../scientific-ml-research-showcase/) for research engineering evidence, then review Projects 1 and 2 for applied public-data and ML practice.

Current status:

- Implemented as a synthetic scientific ML surrogate modelling demo.
- Uses PyTorch mini U-Net and small CNN code.
- Includes generated synthetic metrics, plots, an experiment summary, and research-style reporting.
- Does not use private PhD data and does not claim thesis results.

Evidence to look for:

- Methodological writing
- Reproducibility
- Responsible interpretation
- ML evaluation
- Synthetic scientific ML surrogate workflow
- PyTorch implementation and field metrics
