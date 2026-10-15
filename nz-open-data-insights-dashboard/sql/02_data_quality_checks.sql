-- SQLite data quality checks for outputs/housing_indicators.sqlite.
-- Expected table: housing_indicators.

-- 1. Row count.
SELECT COUNT(*) AS row_count
FROM housing_indicators;

-- 2. Date and period range.
SELECT
    MIN(period_date) AS earliest_period_date,
    MAX(period_date) AS latest_period_date,
    COUNT(DISTINCT period) AS distinct_periods
FROM housing_indicators;

-- 3. Distinct geography levels and area counts.
SELECT
    geography_type,
    COUNT(DISTINCT geography_name) AS distinct_geographies,
    COUNT(*) AS row_count
FROM housing_indicators
GROUP BY geography_type
ORDER BY geography_type;

-- 4. Distinct territorial authority count.
SELECT COUNT(DISTINCT territorial_authority) AS distinct_territorial_authorities
FROM housing_indicators
WHERE territorial_authority IS NOT NULL AND TRIM(territorial_authority) <> '';

-- 5. Missing period values.
SELECT
    SUM(CASE WHEN period IS NULL OR TRIM(period) = '' THEN 1 ELSE 0 END) AS missing_period,
    SUM(CASE WHEN period_date IS NULL OR TRIM(period_date) = '' THEN 1 ELSE 0 END) AS missing_period_date,
    SUM(CASE WHEN year IS NULL THEN 1 ELSE 0 END) AS missing_year,
    SUM(CASE WHEN quarter IS NULL THEN 1 ELSE 0 END) AS missing_quarter
FROM housing_indicators;

-- 6. Missing geography values.
SELECT
    SUM(CASE WHEN geography_type IS NULL OR TRIM(geography_type) = '' THEN 1 ELSE 0 END) AS missing_geography_type,
    SUM(CASE WHEN geography_name IS NULL OR TRIM(geography_name) = '' THEN 1 ELSE 0 END) AS missing_geography_name,
    SUM(CASE WHEN geography_type = 'TA' AND (territorial_authority IS NULL OR TRIM(territorial_authority) = '') THEN 1 ELSE 0 END) AS missing_ta_name_for_ta_rows
FROM housing_indicators;

-- 7. Missing indicator names and values.
SELECT
    SUM(CASE WHEN indicator_name IS NULL OR TRIM(indicator_name) = '' THEN 1 ELSE 0 END) AS missing_indicator_names,
    SUM(CASE WHEN indicator_value IS NULL THEN 1 ELSE 0 END) AS missing_indicator_values
FROM housing_indicators;

-- 8. Duplicate-looking period/geography/indicator/ethnicity rows.
SELECT
    period,
    geography_type,
    area_id,
    geography_name,
    theme,
    indicator_name,
    ethnicity,
    unit,
    COUNT(*) AS duplicate_count
FROM housing_indicators
GROUP BY
    period,
    geography_type,
    area_id,
    geography_name,
    theme,
    indicator_name,
    ethnicity,
    unit
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC, period, geography_name, indicator_name;

-- 9. Suspicious negative values.
-- Negative values may be valid for annual-change indicators. Review by definition.
SELECT
    theme,
    indicator_name,
    unit,
    COUNT(*) AS negative_value_count,
    MIN(indicator_value) AS minimum_value
FROM housing_indicators
WHERE indicator_value < 0
GROUP BY theme, indicator_name, unit
ORDER BY negative_value_count DESC, theme, indicator_name;

-- 10. Data completeness by indicator.
SELECT
    theme,
    indicator_name,
    unit,
    COUNT(*) AS total_rows,
    SUM(CASE WHEN indicator_value IS NULL THEN 1 ELSE 0 END) AS missing_indicator_value_rows,
    ROUND(
        100.0 * SUM(CASE WHEN indicator_value IS NULL THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS missing_indicator_value_pct
FROM housing_indicators
GROUP BY theme, indicator_name, unit
ORDER BY missing_indicator_value_pct DESC, total_rows DESC;

