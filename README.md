# Loc K. Nguyen | Data and AI portfolio

[![Housing checks](https://github.com/loc-k-nguyen/loc-nz-data-ai-portfolio/actions/workflows/housing.yml/badge.svg)](https://github.com/loc-k-nguyen/loc-nz-data-ai-portfolio/actions/workflows/housing.yml)

Applied work in public-data analysis, SQL, reporting, and machine learning. Built by [Loc K. Nguyen](https://loc-k-nguyen.github.io/loc-k-nguyen/), a Wellington-based data science researcher whose PhD thesis was submitted in October 2026.

## Start with the housing explorer

**[Open the interactive dashboard](https://loc-k-nguyen.github.io/loc-nz-data-ai-portfolio/)** · [Read the analysis project](nz-open-data-insights-dashboard/) · [Reproduce it](REPRODUCE.md)

Explore five housing measures across 67 New Zealand territorial authorities, using a preserved April 2026 HUD extract. Change the indicator, area, and date; inspect exact observations; download the selected area's series. Every view retains its unit, source vintage, coverage, and reporting limitations.

The workflow demonstrates Python data preparation, parameterized SQLite selection, data-quality checks, descriptive reporting, an accessible browser dashboard, and automated reproducibility checks. It handles mixed dates, missing areas, and rank-versus-dollar records explicitly.

**Power BI report:** [download the completed PBIX](nz-open-data-insights-dashboard/powerbi/report/NZHousing.pbix), [preview the three pages](https://loc-k-nguyen.github.io/loc-nz-data-ai-portfolio/#powerbi), or [inspect the model and Desktop validation](nz-open-data-insights-dashboard/powerbi/report/). Built with Power Query, a star model and DAX; tested, saved and reopened in Power BI Desktop on 16 October 2026.

## Projects

| Project | Evidence | Scope |
| --- | --- | --- |
| [NZ Housing Explorer](nz-open-data-insights-dashboard/) | Python, SQLite, SQL quality checks, Power Query, DAX, Power BI report, browser reporting, CSV export, GitHub Actions | Public-data analyst portfolio; preserved extract, not a live feed |
| [Applied ML Risk Prediction](applied-ml-risk-prediction-demo/) | scikit-learn Pipeline, held-out evaluation, model card, batch prediction | Public benchmark demonstration, not a clinical model |
| [Scientific ML Example](scientific-ml-research-showcase/) | PyTorch mini U-Net, synthetic field generation, evaluation plots | Synthetic demonstration; no private doctoral data |

## Reproduce and inspect

```bash
python scripts/build_housing_dashboard.py
python scripts/build_housing_dashboard.py --check
python -m http.server 8842 --directory docs
```

Open `http://localhost:8842`. The housing build uses Python's standard library and the included cleaned CSV. CI verifies the committed JSON and tests reporting safeguards on each push; it can also run manually.

- [Source, attribution, and interpretation](DATA_SOURCES.md)
- [Reproduction commands and source-update process](REPRODUCE.md)
- [Project navigation](docs/recruiter_navigation_guide.md)
- [SQL quality checks](nz-open-data-insights-dashboard/sql/02_data_quality_checks.sql)
- [Completed Power BI report and editable source](nz-open-data-insights-dashboard/powerbi/report/)

## Contact

[Portfolio](https://loc-k-nguyen.github.io/loc-k-nguyen/) · [LinkedIn](https://www.linkedin.com/in/loc-khanh-nguyen/) · [Email](mailto:nguyenkloc122@gmail.com)

Original code is MIT-licensed. Source data and third-party materials retain their own terms. See [data sources](DATA_SOURCES.md).
