# NZ Local Housing Statistics Insights Dashboard

**Status:** A working [browser dashboard](https://loc-k-nguyen.github.io/loc-nz-data-ai-portfolio/) is now available, with automated SQLite selection, quality checks, and CSV downloads. The [completed Power BI report](powerbi/report/) includes a downloadable PBIX, editable source, three-page PDF and actual Desktop validation results.

Run `python scripts/build_housing_dashboard.py` from the repository root. See [reproduction](../REPRODUCE.md) and [source notes](../DATA_SOURCES.md).

## Summary

This project is a practical New Zealand analyst portfolio project using official Ministry of Housing and Urban Development (HUD) Local Housing Statistics data. It demonstrates a complete first-pass workflow: Python cleaning, SQLite database creation, SQL quality checks, SQL analysis exports, Power BI-ready outputs, and stakeholder reporting.

## What This Project Demonstrates

- Cleaning official NZ open data with Python and pandas
- Creating a local SQLite database from a cleaned CSV
- Running SQL data quality checks and analysis queries
- Exporting recruiter-friendly CSV and Markdown outputs
- Preparing a Power BI-ready dataset
- Communicating findings cautiously for policy and insight audiences

## Business Question

Which New Zealand territorial authorities show notable values for selected housing indicators, and how can those patterns be communicated clearly to policy, planning, and public-sector stakeholders?

## Dataset Used

- Dataset: HUD Local Housing Statistics data extract
- Source organisation: Ministry of Housing and Urban Development / Te Tuapapa Kura Kainga
- Source page: `https://www.hud.govt.nz/stats-and-insights/local-housing-statistics/about-the-local-housing-statistics-dashboard`
- Raw workbook: `data/raw/hud_local_housing_statistics_2026_04.xlsx`
- Raw sheet used: `Metrics`
- Cleaned file: `data/processed/local_housing_indicators_clean.csv`
- Cleaned dataset shape: 48,953 rows x 15 columns
- Geography levels: `NZ` and `TA`
- Distinct territorial authorities: 67

## Cleaned Columns

The cleaned file includes period fields, geography fields, indicator fields, values, units, source, and raw file lineage:

```text
period, period_date, year, quarter,
geography_type, area_id, geography_name, territorial_authority,
theme, indicator_name, indicator_value, unit, ethnicity,
source, raw_file_name
```

## Exported Outputs

| Output | Purpose |
| --- | --- |
| `outputs/data_quality_summary.csv` | Row count, period coverage, geography coverage, indicator count, missingness, duplicate-looking count |
| `outputs/indicator_catalog.csv` | Indicator catalog with theme, unit, geography level, row count, and period range |
| `outputs/latest_period_summary.csv` | Latest-period rows across the full dataset |
| `outputs/ta_latest_values_sample.csv` | Latest-period TA-level extract |
| `outputs/top_ta_by_selected_indicator.csv` | Highest latest-period TA values for the selected indicator |
| `outputs/selected_indicator_trend.csv` | Time series for the selected indicator |
| `outputs/dashboard_ready_housing_indicators.csv` | Recommended Power BI input |
| `outputs/analysis_summary.md` | Generated analysis summary |
| `outputs/indicator_validation_notes.md` | Indicator interpretation and safe wording notes |
| `outputs/preliminary_findings.md` | Cautious preliminary findings for stakeholder review |

## Selected Indicator Note

The automated export currently uses `Rent affordability index`.

The workbook does not define whether higher values mean more or less affordability. HUD documentation describes the related Change in Housing Affordability Indicators as change-over-time measures and cautions that they do not show relative affordability at a point in time. This project therefore uses neutral wording such as:

> highest values for the selected rent affordability indicator

It does not claim these are the "least affordable" or "worst" areas.

## How To Reproduce

From the repository root:

```powershell
python .\nz-open-data-insights-dashboard\src\clean_data.py
python .\nz-open-data-insights-dashboard\src\build_sqlite_database.py
python .\nz-open-data-insights-dashboard\src\run_analysis_exports.py
```

Optional verification:

```powershell
python -m compileall .\nz-open-data-insights-dashboard
```

## SQL Workflow

- `sql/01_create_tables.sql`: SQLite table schema
- `sql/02_data_quality_checks.sql`: executable quality checks
- `sql/03_analysis_queries.sql`: executable analysis queries and Power BI import query

The generated database is:

```text
outputs/housing_indicators.sqlite
```

It is ignored by Git because it is a reproducible binary artifact.

## Power BI report

Open [the finished report](powerbi/report/): three pages, five typed Power Query tables, twenty DAX measures, exact observation tables and explicit source-quality checks. Download the PBIX to use filters in Desktop, or view the PDF without installing Power BI. Tested, saved and reopened in Desktop on 16 October 2026.

The earlier `powerbi/build_assets/` and manual guide are historical references. Their generic aggregation examples are not the finished model and should not be applied to mixed-unit source rows.

## Preliminary Findings

See:

```text
outputs/preliminary_findings.md
```

The report calculations and visuals have been checked against the selected source observations. The earlier analysis notes remain exploratory; no stakeholder review or policy conclusion is claimed.

## Limitations

- The dataset has `NZ` and `TA` geography levels, with no explicit regional council field.
- Do not invent regions. Use `geography_type`, `geography_name`, and `territorial_authority`.
- The raw data file is ignored by Git and should be regenerated from the official HUD source.
- `outputs/housing_indicators.sqlite` is ignored because it is reproducible and relatively large.
- The selected indicator direction is not confirmed from the workbook itself.
- The completed report uses a preserved extract, not a scheduled live feed.
- This is descriptive analysis, not causal analysis.
