> Historical build reference. Use the [completed report](report/README.md) for the tested model, PBIX and PDF. Generic aggregation examples here are not used by the finished report.

# Power BI Manual Build Guide

## Fast Build Path

1. Import:

```text
powerbi/build_assets/dashboard_main.csv
```

2. Rename the imported table to:

```text
housing_indicators
```

3. Set data types using:

```text
powerbi/build_assets/powerbi_field_mapping.md
```

4. Add DAX measures from:

```text
powerbi/build_assets/powerbi_measures.dax
```

5. Build the four pages using:

```text
powerbi/build_assets/dashboard_page_spec.md
```

6. Export screenshots to:

```text
screenshots/
```

The focused CSVs in `powerbi/build_assets/` are designed for a fast manual dashboard build. The broader export `outputs/dashboard_ready_housing_indicators.csv` remains available if you want the full dashboard-ready dataset.

## Input File

Use this file:

```text
outputs/dashboard_ready_housing_indicators.csv
```

Regenerate it with:

```powershell
python .\nz-open-data-insights-dashboard\src\run_analysis_exports.py
```

## A. Open Power BI Desktop

Open Power BI Desktop and create a new report.

## B. Import CSV

1. Select **Get Data > Text/CSV**.
2. Select `outputs/dashboard_ready_housing_indicators.csv`.
3. Load the data.
4. Rename the table to:

```text
dashboard_ready_housing_indicators
```

## C. Set Data Types

Check and adjust:

- `period_date`: Date
- `period`: Text
- `year`: Whole Number
- `quarter`: Whole Number
- `indicator_value`: Decimal Number
- `geography_type`: Text
- `territorial_authority`: Text
- `geography_name`: Text
- `theme`: Text
- `indicator_name`: Text
- `unit`: Text
- `ethnicity`: Text
- `source`: Text

## D. Create Measures

These formulas may need minor adjustment after import if Power BI changes table or column names.

```DAX
Latest Period =
MAX('dashboard_ready_housing_indicators'[period_date])
```

```DAX
Indicator Count =
DISTINCTCOUNT('dashboard_ready_housing_indicators'[indicator_name])
```

```DAX
TA Count =
DISTINCTCOUNT('dashboard_ready_housing_indicators'[territorial_authority])
```

```DAX
Average Indicator Value =
AVERAGE('dashboard_ready_housing_indicators'[indicator_value])
```

```DAX
Selected Latest Value =
CALCULATE(
    AVERAGE('dashboard_ready_housing_indicators'[indicator_value]),
    FILTER(
        'dashboard_ready_housing_indicators',
        'dashboard_ready_housing_indicators'[period_date] =
            MAX('dashboard_ready_housing_indicators'[period_date])
    )
)
```

## E. Build Pages

### 1. Executive Summary

Suggested visuals:

- KPI card: `Latest Period`
- KPI card: `Indicator Count`
- KPI card: `TA Count`
- KPI card: `Selected Latest Value`
- Bar chart: highest TA values for selected indicator
- Text box: source and caution note

Recommended filters:

- `indicator_name` = `Rent affordability index`
- `geography_type` = `TA`

Use neutral title text:

```text
Highest values for selected rent affordability indicator
```

### 2. Territorial Authority Comparison

Suggested visuals:

- Bar chart: `territorial_authority` by `indicator_value`
- Table: `territorial_authority`, `period`, `theme`, `indicator_name`, `indicator_value`, `unit`
- Slicers: `theme`, `indicator_name`, `period`, `ethnicity`

Avoid labels such as "worst" or "least affordable" unless indicator direction is validated.

### 3. Indicator Trend

Suggested visuals:

- Line chart: `period_date` by `indicator_value`
- Legend or small multiples: `geography_name`
- Slicer: `geography_type`
- Slicer: `territorial_authority`

Use `selected_indicator_trend.csv` as a reference check for the selected indicator.

### 4. Data Quality & Methodology

Suggested visuals and notes:

- Card: row count
- Card: indicator count
- Bar chart: rows by `theme`
- Table: indicators and units
- Text note: geography levels are `NZ` and `TA`; no explicit regional council field
- Text note: this is descriptive, not causal, analysis

## F. Export Screenshots

After the dashboard is built and checked, export screenshots to:

```text
screenshots/
```

Required files:

- `executive_summary.png`
- `ta_comparison.png`
- `indicator_trend.png`
- `methodology_page.png`

## G. Save `.pbix`

Save the Power BI file as:

```text
nz-open-data-insights-dashboard/powerbi/nz_housing_dashboard.pbix
```

If the file is large, confirm whether it should be tracked in Git or documented as a local artifact.

## Recommended Slicers

- `period`
- `theme`
- `indicator_name`
- `geography_type`
- `territorial_authority`
- `ethnicity`

## Design Notes

- Use a clean public-sector style.
- Keep visual titles factual and neutral.
- Show the selected indicator and unit in charts.
- Add source and limitation notes on every page or in a methodology section.
- Do not claim final dashboard findings until screenshots and calculations are validated.
