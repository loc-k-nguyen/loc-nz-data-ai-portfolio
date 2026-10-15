# NZ Local Housing Affordability Indicators: Preliminary Analyst Brief

## Audience

Policy, insights, planning, and research stakeholders reviewing territorial-authority housing indicators.

## Data Source

- Source organisation: Ministry of Housing and Urban Development / Te Tuapapa Kura Kainga
- Source dataset: HUD Local Housing Statistics data extract
- Raw workbook: `data/raw/hud_local_housing_statistics_2026_04.xlsx`
- Workbook sheet: `Metrics`
- Cleaned file: `data/processed/local_housing_indicators_clean.csv`
- Dashboard-ready file: `outputs/dashboard_ready_housing_indicators.csv`

## Period Covered

- Full cleaned dataset: 1996-01-01 to 2026-04-01.
- Selected indicator trend: 2001-12-31 to 2025-12-31.
- Latest selected indicator period: 2025-12-31.

## Selected Indicator

- Indicator: `Rent affordability index`
- Unit: `index`
- Theme: `Affordability`

The workbook instructions do not define the direction of this indicator. HUD's related CHAI documentation describes these indicators as measures of change in affordability over time and cautions that they should not be used as simple point-in-time comparisons of relative affordability levels between areas.

Safe interpretation: "highest values for the selected rent affordability indicator."

Avoid: "least affordable areas", "worst affordability", or "highest housing pressure" unless the indicator definition and direction are explicitly validated.

## Cautious Preliminary Observations

- The cleaned dataset contains 48,953 rows, 64 indicator names, 11 themes, and 67 territorial authorities.
- The generated top-10 export identifies the territorial authorities with the highest latest-period values for `Rent affordability index` at 2025-12-31.
- The selected indicator trend export includes both national and territorial-authority rows, making it suitable for a Power BI trend page.
- These observations are preliminary and require Power BI validation and stakeholder interpretation before being presented as findings.

## Evidence Inputs

| File | Use |
| --- | --- |
| `outputs/data_quality_summary.csv` | Dataset coverage, missingness, duplicate-looking row count |
| `outputs/indicator_catalog.csv` | Indicator, unit, geography, and date coverage |
| `outputs/top_ta_by_selected_indicator.csv` | Latest-period highest values for selected indicator |
| `outputs/selected_indicator_trend.csv` | Time-series data for selected indicator |
| `outputs/dashboard_ready_housing_indicators.csv` | Power BI input |
| `outputs/indicator_validation_notes.md` | Interpretation and wording guidance |
| `outputs/preliminary_findings.md` | Cautious preliminary summary |

## Data Quality Notes

- `data_quality_summary.csv` reports zero missing `indicator_value` rows.
- The workflow identifies 61 duplicate-looking period/geography/indicator/ethnicity rows that require review before final reporting.
- Geography levels are `NZ` and `TA`; there is no explicit regional council field.
- Missing `territorial_authority` values are expected for `NZ` rows.

## Limitations

- This is descriptive analysis, not causal analysis.
- The selected indicator requires interpretation of the HUD definition before policy language is used.
- Territorial authorities should not be aggregated into regions unless a validated lookup table is added.
- A Power BI dashboard has not yet been built.
- Findings remain preliminary until dashboard visuals and calculations are validated.

## Recommendations

[To be completed after Power BI validation and stakeholder interpretation]

## Next Steps For Power BI Validation

1. Import `outputs/dashboard_ready_housing_indicators.csv`.
2. Set `period_date` as Date and `indicator_value` as Decimal Number.
3. Build the Executive Summary, Territorial Authority Comparison, Indicator Trend, and Data Quality pages.
4. Validate the selected-indicator top-10 visual against `top_ta_by_selected_indicator.csv`.
5. Validate the trend chart against `selected_indicator_trend.csv`.
6. Export screenshots and update the project README only after the dashboard is real.

