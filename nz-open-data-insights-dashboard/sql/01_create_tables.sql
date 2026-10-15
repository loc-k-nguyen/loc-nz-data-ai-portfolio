-- SQLite schema for data/processed/local_housing_indicators_clean.csv.
-- The build script creates this table automatically in outputs/housing_indicators.sqlite.

DROP TABLE IF EXISTS housing_indicators;

CREATE TABLE housing_indicators (
    period TEXT,
    period_date TEXT,
    year INTEGER,
    quarter INTEGER,
    geography_type TEXT,
    area_id INTEGER,
    geography_name TEXT,
    territorial_authority TEXT,
    theme TEXT,
    indicator_name TEXT,
    indicator_value REAL,
    unit TEXT,
    ethnicity TEXT,
    source TEXT,
    raw_file_name TEXT
);

CREATE INDEX IF NOT EXISTS idx_housing_indicators_period_date
    ON housing_indicators (period_date);

CREATE INDEX IF NOT EXISTS idx_housing_indicators_geography_type
    ON housing_indicators (geography_type);

CREATE INDEX IF NOT EXISTS idx_housing_indicators_territorial_authority
    ON housing_indicators (territorial_authority);

CREATE INDEX IF NOT EXISTS idx_housing_indicators_geography_name
    ON housing_indicators (geography_name);

CREATE INDEX IF NOT EXISTS idx_housing_indicators_indicator_name
    ON housing_indicators (indicator_name);

CREATE INDEX IF NOT EXISTS idx_housing_indicators_theme
    ON housing_indicators (theme);

