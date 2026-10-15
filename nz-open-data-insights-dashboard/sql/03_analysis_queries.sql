-- SQLite analysis queries for outputs/housing_indicators.sqlite.
-- Expected table: housing_indicators.
--
-- To change the selected dashboard indicator, replace:
-- 'Housing Register per 10k population'
-- with another value from indicator_catalog.csv.

-- 1. Latest available period summary.
WITH latest_period AS (
    SELECT MAX(period_date) AS period_date
    FROM housing_indicators
)
SELECT
    h.period,
    h.period_date,
    h.geography_type,
    h.geography_name,
    h.territorial_authority,
    h.theme,
    h.indicator_name,
    h.indicator_value,
    h.unit,
    h.ethnicity
FROM housing_indicators AS h
JOIN latest_period AS lp
    ON h.period_date = lp.period_date
ORDER BY h.theme, h.indicator_name, h.geography_type, h.geography_name;

-- 2. Top 10 territorial authorities by selected indicator.
-- Neutral wording: highest values for selected indicator.
WITH latest_selected_period AS (
    SELECT MAX(period_date) AS period_date
    FROM housing_indicators
    WHERE geography_type = 'TA'
      AND indicator_name = 'Housing Register per 10k population'
      AND indicator_value IS NOT NULL
)
SELECT
    h.period,
    h.period_date,
    h.territorial_authority,
    h.theme,
    h.indicator_name,
    h.indicator_value,
    h.unit,
    h.ethnicity
FROM housing_indicators AS h
JOIN latest_selected_period AS lsp
    ON h.period_date = lsp.period_date
WHERE h.geography_type = 'TA'
  AND h.indicator_name = 'Housing Register per 10k population'
  AND h.indicator_value IS NOT NULL
ORDER BY h.indicator_value DESC
LIMIT 10;

-- 3. Territorial authority comparison.
SELECT
    geography_name,
    theme,
    indicator_name,
    unit,
    COUNT(*) AS observations,
    AVG(indicator_value) AS average_indicator_value,
    MIN(indicator_value) AS minimum_indicator_value,
    MAX(indicator_value) AS maximum_indicator_value
FROM housing_indicators
WHERE geography_type = 'TA'
  AND indicator_value IS NOT NULL
GROUP BY geography_name, theme, indicator_name, unit
ORDER BY theme, indicator_name, average_indicator_value DESC;

-- 4. Indicator trend over time for selected indicator.
SELECT
    period,
    period_date,
    year,
    quarter,
    geography_type,
    geography_name,
    territorial_authority,
    theme,
    indicator_name,
    indicator_value,
    unit,
    ethnicity
FROM housing_indicators
WHERE indicator_name = 'Housing Register per 10k population'
  AND geography_type IN ('NZ', 'TA')
  AND indicator_value IS NOT NULL
ORDER BY geography_type, geography_name, period_date;

-- 5. Comparison against national median placeholder.
-- SQLite has no built-in median. This uses AVG as an executable placeholder.
-- Use Power BI, DuckDB, or PostgreSQL percentile functions for a true median.
WITH latest_ta_values AS (
    SELECT
        geography_name,
        territorial_authority,
        indicator_name,
        indicator_value
    FROM housing_indicators
    WHERE geography_type = 'TA'
      AND indicator_name = 'Housing Register per 10k population'
      AND indicator_value IS NOT NULL
      AND period_date = (
          SELECT MAX(period_date)
          FROM housing_indicators
          WHERE geography_type = 'TA'
            AND indicator_name = 'Housing Register per 10k population'
            AND indicator_value IS NOT NULL
      )
),
national_reference AS (
    SELECT AVG(indicator_value) AS national_median_placeholder
    FROM latest_ta_values
)
SELECT
    latest_ta_values.territorial_authority,
    latest_ta_values.indicator_name,
    latest_ta_values.indicator_value,
    national_reference.national_median_placeholder
FROM latest_ta_values
CROSS JOIN national_reference
WHERE latest_ta_values.indicator_value > national_reference.national_median_placeholder
ORDER BY latest_ta_values.indicator_value DESC;

-- 6. Data completeness by theme and indicator.
SELECT
    theme,
    indicator_name,
    unit,
    COUNT(*) AS total_rows,
    SUM(CASE WHEN indicator_value IS NULL THEN 1 ELSE 0 END) AS missing_value_rows,
    ROUND(
        100.0 * SUM(CASE WHEN indicator_value IS NULL THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS missing_value_pct
FROM housing_indicators
GROUP BY theme, indicator_name, unit
ORDER BY missing_value_pct DESC, total_rows DESC;

-- 7. Power BI import query.
SELECT
    period,
    period_date,
    year,
    quarter,
    geography_type,
    territorial_authority,
    geography_name,
    theme,
    indicator_name,
    indicator_value,
    unit,
    ethnicity,
    source
FROM housing_indicators
WHERE geography_type IN ('TA', 'NZ')
  AND indicator_value IS NOT NULL
ORDER BY period_date, geography_type, geography_name, theme, indicator_name;

