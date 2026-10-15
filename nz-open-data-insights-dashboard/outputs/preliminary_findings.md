# Preliminary Findings

## What Has Been Validated

- The cleaned HUD Local Housing Statistics dataset contains 48,953 rows and 15 columns.
- The SQLite export workflow loaded the cleaned data into the `housing_indicators` table.
- The generated data quality summary reports 230 distinct periods, 2 geography levels, 67 territorial authorities, 64 indicator names, and 11 themes.
- The cleaned data covers 1996-01-01 to 2026-04-01 across all indicators.
- The selected indicator export uses `Rent affordability index`.

## Selected Indicator

- Selected indicator: `Rent affordability index`
- Theme: `Affordability`
- Unit: `index`
- Geography levels in trend export: `NZ` and `TA`

Direction note: the workbook does not define whether a higher `Rent affordability index` value means more or less affordable. HUD documentation indicates the related CHAI indicators track change in affordability over time and should not be used as a simple point-in-time comparison of affordability levels between areas. This project therefore uses neutral wording.

## Latest Available Period

- Latest period across the full cleaned dataset: 2026-04-01.
- Latest period in `latest_period_summary.csv`: 2026-04-01, covering MSD Housing Register rows.
- Latest period for `Rent affordability index`: 2025-12-31.
- National `Rent affordability index` value at 2025-12-31: 1.1199.

## Top 10 Territorial Authorities By Selected Indicator

`top_ta_by_selected_indicator.csv` lists the following territorial authorities with the highest latest-period values for `Rent affordability index` at 2025-12-31:

| Rank | Territorial authority | Indicator value |
| --- | --- | ---: |
| 1 | Wellington City | 1.2654 |
| 2 | Selwyn District | 1.2554 |
| 3 | Auckland | 1.2070 |
| 4 | Porirua City | 1.1192 |
| 5 | Dunedin City | 1.1173 |
| 6 | Lower Hutt City | 1.1169 |
| 7 | Nelson City | 1.1095 |
| 8 | MacKenzie District | 1.0885 |
| 9 | Waimakariri District | 1.0771 |
| 10 | Tasman District | 1.0755 |

Interpretation caution: this is a neutral ranking of highest values for the selected indicator, not a validated ranking of least affordable areas.

## Trend Summary

- `selected_indicator_trend.csv` contains 6,499 rows for `Rent affordability index`.
- Trend period coverage: 2001-12-31 to 2025-12-31.
- Geography levels in the trend export:
  - `NZ`: 97 rows
  - `TA`: 6,402 rows

This trend export is suitable for a Power BI time-series page after the indicator definition and chart filters are validated.

## Data Quality Notes

- Missing `indicator_value` count in `data_quality_summary.csv`: 0.
- Duplicate-looking period/geography/indicator/ethnicity rows count: 61.
- Missing `territorial_authority` values are expected for national-level `NZ` rows.
- The data has no explicit regional council field.

## Interpretation Cautions

- Do not infer regional council trends because the dataset uses `NZ` and `TA` geography levels only.
- Do not describe the top-10 values as "worst", "best", "least affordable", or "most unaffordable" unless the indicator direction and point-in-time comparability are validated.
- This is descriptive analysis, not causal analysis.
- HUD documentation cautions that CHAI indicators track change over time and are not a simple comparison of relative affordability levels between areas.

## What Still Needs Power BI Validation

- Confirm data types after CSV import.
- Confirm the selected indicator and unit appear correctly in chart titles.
- Validate latest-period filters against `top_ta_by_selected_indicator.csv`.
- Validate trend charts against `selected_indicator_trend.csv`.
- Add source and caveat notes to the methodology page.
- Export screenshots only after the dashboard is real.

