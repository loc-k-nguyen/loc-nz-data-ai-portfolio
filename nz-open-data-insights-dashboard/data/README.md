# Data README

## Source

- Dataset: HUD Local Housing Statistics data extract
- Source organisation: Ministry of Housing and Urban Development / Te Tuapapa Kura Kainga
- Source page: `https://www.hud.govt.nz/stats-and-insights/local-housing-statistics/about-the-local-housing-statistics-dashboard`
- Raw download used: `LHS-data-download-April-2026.xlsx`
- Local raw file: `data/raw/hud_local_housing_statistics_2026_04.xlsx`
- Raw sheet used: `Metrics`
- Download date: 2026-05-28
- Licence/source notes: confirm current reuse terms on the official HUD source page before publishing raw data.

## Raw Columns

The `Metrics` sheet contains:

- `date`
- `area_type`
- `area_id`
- `area_name`
- `theme`
- `series`
- `ethnicity`
- `value`
- `value_type`

Raw shape: 48,953 rows x 9 columns.

## Cleaned Output

Cleaned file:

```text
data/processed/local_housing_indicators_clean.csv
```

Cleaned shape after the current script run: 48,953 rows x 15 columns.

Cleaned columns:

- `period`
- `period_date`
- `year`
- `quarter`
- `geography_type`
- `area_id`
- `geography_name`
- `territorial_authority`
- `theme`
- `indicator_name`
- `indicator_value`
- `unit`
- `ethnicity`
- `source`
- `raw_file_name`

## Cleaned Structure

The HUD `Metrics` sheet is already long-format, so the cleaner does not reshape the data. It standardises column names, preserves source fields, adds time fields, renames `series` to `indicator_name`, renames `value` to `indicator_value`, renames `value_type` to `unit`, and creates geography fields suitable for SQL and Power BI.

## Known Data Quality Notes

- Date range in cleaned data: 1996-01-01 to 2026-04-01.
- Geography types found: `NZ` and `TA`.
- Distinct geography names found: 68.
- Distinct territorial authorities found: 67.
- Missing values found in `ethnicity`, `unit`, and `territorial_authority`. Missing `territorial_authority` is expected for national-level rows.
- 61 duplicate-looking period/geography/indicator rows were detected by the cleaner using the current key. These require review before final reporting.
- Negative values exist for change indicators and may be valid.

## Important Reporting Note

Final findings are pending until SQL data quality checks, Power BI dashboard calculations, and stakeholder interpretation are validated.

