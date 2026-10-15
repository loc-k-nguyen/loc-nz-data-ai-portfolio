# Outputs

This folder stores generated SQL database files, analysis exports, and Power BI-ready data for the HUD Local Housing Statistics portfolio project.

Expected generated files:

| File | Purpose |
| --- | --- |
| `housing_indicators.sqlite` | Local SQLite database containing the cleaned HUD table `housing_indicators`. Regenerate with `src/build_sqlite_database.py`. |
| `data_quality_summary.csv` | One-row summary of row counts, period coverage, geography coverage, indicator counts, missingness, and duplicate-looking rows. |
| `indicator_catalog.csv` | Catalog of themes, indicators, units, geography levels, row counts, and date coverage. |
| `latest_period_summary.csv` | Latest-period extract by indicator and geography level. |
| `ta_latest_values_sample.csv` | Latest-period territorial-authority rows for dashboard review. |
| `top_ta_by_selected_indicator.csv` | Top 10 territorial authorities by highest value for the automatically selected indicator. |
| `selected_indicator_trend.csv` | Time trend for the selected indicator across NZ and TA geography levels. |
| `dashboard_ready_housing_indicators.csv` | Recommended Power BI import file. |
| `analysis_summary.md` | Markdown summary of generated outputs and caveats. |
| `indicator_validation_notes.md` | Notes on selected indicator meaning, direction, safe wording, and overclaims to avoid. |
| `preliminary_findings.md` | Cautious preliminary findings based on generated SQL exports. |

Generated files are preliminary analysis artifacts. Do not treat them as final findings until SQL checks, Power BI visuals, indicator definitions, and stakeholder interpretation are validated.
