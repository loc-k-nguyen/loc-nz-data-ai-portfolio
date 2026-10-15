> Historical build reference. Use the [completed report](../report/README.md) for the tested model, PBIX and PDF. Generic aggregation examples here are not used by the finished report.

# Power BI Build Assets

This folder contains focused files for manually building the Power BI dashboard quickly and consistently.

## Files

| File | Purpose |
| --- | --- |
| `dashboard_main.csv` | Main Power BI input. Import this first and rename the table to `housing_indicators`. |
| `selected_indicator_latest_top10.csv` | Reference table for the Executive Summary top-10 chart. |
| `selected_indicator_trend.csv` | Reference table for the Indicator Trend page. |
| `indicator_catalog_for_filters.csv` | Reference list of themes, indicators, units, and geography levels for slicer planning. |
| `data_quality_summary_for_powerbi.csv` | Small summary table for the Data Quality & Methodology page. |
| `powerbi_measures.dax` | DAX measures to create after importing `dashboard_main.csv`. |
| `dashboard_page_spec.md` | Exact page-by-page dashboard build instructions. |
| `powerbi_field_mapping.md` | Field type and usage guide for Power BI. |

## Recommended Import Order

1. Import `dashboard_main.csv`.
2. Rename the table to `housing_indicators`.
3. Set data types using `powerbi_field_mapping.md`.
4. Add measures from `powerbi_measures.dax`.
5. Use the smaller CSV files as reference checks while building visuals.

## Dashboard Build Sequence

1. Build Executive Summary.
2. Build Territorial Authority Comparison.
3. Build Indicator Trend.
4. Build Data Quality & Methodology.
5. Check wording against `outputs/indicator_validation_notes.md`.
6. Export screenshots after the dashboard is real.

## Screenshot Export Checklist

Save screenshots to `../screenshots/`:

- `executive_summary.png`
- `territorial_authority_comparison.png`
- `indicator_trend.png`
- `data_quality_methodology.png`

Do not add placeholder images.

