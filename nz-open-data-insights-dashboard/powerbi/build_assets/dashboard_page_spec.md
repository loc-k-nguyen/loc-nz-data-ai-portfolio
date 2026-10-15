> Historical build reference. Use the [completed report](../report/README.md) for the tested model, PBIX and PDF. Generic aggregation examples here are not used by the finished report.

# Dashboard Page Specification

Use `dashboard_main.csv` as the main Power BI input and rename the table to `housing_indicators`.

## Page 1: Executive Summary

Title:

```text
NZ Local Housing Indicators: Executive Summary
```

Subtitle:

```text
Official HUD Local Housing Statistics, preliminary SQL outputs, Power BI dashboard planned
```

Required filters:

- `indicator_name` filtered to `Rent affordability index` for the first build.
- `geography_type` filtered to `TA` for TA comparison visuals.

KPI cards:

- Latest period: `Latest Period Label`
- TA count: `TA Count`
- Indicator count: `Indicator Count`
- Latest selected indicator value: `Latest Selected Indicator Value`

Main visual:

- Bar chart: top 10 territorial authorities by selected indicator value.
- Axis: `territorial_authority`
- Value: `Latest Selected Indicator Value` or `indicator_value` filtered to latest period.
- Sort: descending by value.

Cautious interpretation note:

```text
This chart shows highest values for the selected rent affordability indicator. It is not a ranking of least affordable areas unless the indicator definition and direction are validated.
```

## Page 2: Territorial Authority Comparison

Title:

```text
Territorial Authority Comparison
```

Slicers:

- `indicator_name`
- `period`
- `ethnicity`

Visuals:

- Clustered bar chart or table by `territorial_authority`.
- Values: `indicator_value` or `Average Indicator Value`.
- Columns for table: `territorial_authority`, `period`, `theme`, `indicator_name`, `indicator_value`, `unit`, `ethnicity`.

Optional map note:

- Do not add a map unless validated latitude/longitude or shape data is added later.
- Do not use regional council wording because the dataset has `NZ` and `TA` geography levels only.

## Page 3: Indicator Trend

Title:

```text
Selected Indicator Trend
```

Filters:

- `indicator_name`
- `geography_name`
- `ethnicity`

Visuals:

- Line chart with `period_date` on the x-axis and `indicator_value` on the y-axis.
- Use `geography_name` as the legend for a small number of selected areas.
- Add New Zealand as a benchmark line by filtering `geography_type = NZ` or using a separate visual.

Interpretation caution:

```text
HUD CHAI-related indicators track change over time. Avoid simple point-in-time affordability rankings unless the indicator definition supports that use.
```

## Page 4: Data Quality & Methodology

Title:

```text
Data Quality & Methodology
```

Include:

- Source: Ministry of Housing and Urban Development / Te Tuapapa Kura Kainga.
- Dataset: HUD Local Housing Statistics data extract.
- Row count: 48,953 cleaned rows.
- Date range: 1996-01-01 to 2026-04-01 across all indicators.
- Geography levels: `NZ` and `TA`.
- Distinct territorial authorities: 67.
- Limitation: no explicit regional council field.
- Limitation: selected indicator direction requires definition validation.
- Reproducibility workflow:
  1. `python .\nz-open-data-insights-dashboard\src\clean_data.py`
  2. `python .\nz-open-data-insights-dashboard\src\build_sqlite_database.py`
  3. `python .\nz-open-data-insights-dashboard\src\run_analysis_exports.py`

Recommended visuals:

- Cards for row count, indicator count, and TA count.
- Table of indicator names and units.
- Text box for limitations and source notes.

