# Data sources and reporting boundaries

## Housing explorer

- Source: **HUD Local Housing Statistics**, Ministry of Housing and Urban Development / Te Tuapapa Kura Kainga, as named in the preserved April 2026 extract.
- [Official dashboard, definitions, and data download](https://www.hud.govt.nz/stats-and-insights/local-housing-statistics/about-the-local-housing-statistics-dashboard).
- Source filename: `hud_local_housing_statistics_2026_04.xlsx`; source sheet: `Metrics`.
- Preserved cleaned data: `nz-open-data-insights-dashboard/data/processed/local_housing_indicators_clean.csv`.
- Input has 48,953 rows, 67 territorial authorities, 64 named indicators, and observation dates from 1996-01-01 to 2026-04-01. These are source-wide ranges, not the dates for every measure.
- The source contains 61 repeated reporting keys. They are retained in the source, not silently averaged or relabeled as clean. The five displayed series contain no duplicate period/geography/area keys after fixing their exact unit and population.

The original extract predates the agency's July 2026 organizational change. This portfolio retains its historical source attribution; the current official page identifies the successor ministry.

## Selected measures

| View | Exact source series | Unit / population |
| --- | --- | --- |
| Housing Register | Housing Register | Source count; ethnicity field `All` |
| Median weekly rent | Median Rent Price | `$`; rank rows excluded |
| Building consents | Building Consents per 10k population | `per 10k population` |
| Rent at least 30% of income | Households whose rent is equal to or more than 30% of income | `%` |
| Rent affordability index | Rent affordability index | `index` |

Each view starts at the latest available **TA observation date for that selected series**. It does not substitute the dataset-wide maximum date. National values are displayed only when a source NZ row exists on the same date. They are never manufactured by averaging or summing TA values.

The HUD guidance cautions that rent-price compositions may change and that change-in-affordability measures do not establish relative affordability at a point in time. The explorer therefore reports values neutrally. Missing areas remain unavailable; no interpolation, causal claim, or policy recommendation is made.

## Attribution and rights

This is an independent portfolio, not an official government product. Credit HUD and the upstream agencies identified in its documentation when reusing the data. The repository's MIT license covers original portfolio code; it does not replace source-data or third-party terms. Consult the official source terms before reuse. Raw workbooks are not included.

## Other projects

The applied ML demo and synthetic scientific ML example retain their own source and limitation notes. Their outputs are demonstrations, not evidence of clinical deployment or reproductions of private doctoral experiments.
