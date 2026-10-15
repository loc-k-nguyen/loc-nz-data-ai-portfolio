# Indicator Validation Notes

## Selected Indicator

- Indicator name: `Rent affordability index`
- Theme: `Affordability`
- Unit: `index`
- Export files using this indicator:
  - `top_ta_by_selected_indicator.csv`
  - `selected_indicator_trend.csv`

## Source Files Checked

- Raw workbook: `data/raw/hud_local_housing_statistics_2026_04.xlsx`
- Workbook sheet checked: `Instructions`
- Output catalog checked: `outputs/indicator_catalog.csv`
- HUD Local Housing Statistics page: `https://www.hud.govt.nz/stats-and-insights/local-housing-statistics/about-the-local-housing-statistics-dashboard`
- HUD Change in Housing Affordability Indicators page: `https://www.hud.govt.nz/stats-and-insights/change-in-housing-affordability-indicators/about-the-indicators/`

## Instruction Sheet Notes

The workbook `Instructions` sheet says the extract is a copy of the data used to populate the Local Housing Statistics dashboard and is useful for ad-hoc analysis. It also says metric definitions should be checked on the Local Housing Statistics dashboard website, especially the "About the Local Housing Statistics Dashboard" tab.

The instruction sheet explains that the workbook contains a single `Metrics` sheet and that users can filter `theme` and `series`; the `value` column then contains the relevant data.

## Direction Check

Direction was not fully confirmed from the workbook itself.

HUD's Local Housing Statistics documentation describes rental affordability and stress metrics as indicators of income spent on rent and relative rental affordability. The related HUD CHAI documentation says the change indicators compare price changes with growth in median household disposable income and track whether affordability is improving or worsening over time.

Important caveat: HUD's CHAI documentation states that these indicators track change in affordability, not relative affordability at a point in time. It says they should not be used to compare the level of affordability between areas without careful interpretation.

## Safe Interpretation

Safe wording:

- "highest values for the selected rent affordability indicator"
- "selected rent affordability indicator values"
- "TA-level values for `Rent affordability index`"
- "preliminary ranking for dashboard exploration"
- "requires interpretation of the HUD indicator definition"

## Unsafe Interpretation To Avoid

Avoid:

- "least affordable territorial authorities"
- "worst rental affordability"
- "highest housing pressure"
- "most unaffordable places"
- "rent stress ranking"

These phrases overclaim unless the indicator direction and point-in-time comparability are explicitly validated.

## Recommended Wording

README:

> The automated export currently uses `Rent affordability index` as the selected indicator. Because HUD documentation frames CHAI indicators as change-over-time measures and cautions against simple point-in-time affordability comparisons, this project uses neutral wording such as "highest values for the selected rent affordability indicator".

Stakeholder brief:

> The top-10 export lists territorial authorities with the highest latest-period values for the selected rent affordability indicator. This is a preliminary analytical view and should not be interpreted as a ranking of least affordable areas without further validation.

Dashboard:

> Top 10 territorial authorities by selected indicator value

