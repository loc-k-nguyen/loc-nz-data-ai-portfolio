"""Run SQL analysis exports for the HUD housing dashboard project."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

TABLE_NAME = "housing_indicators"
DATABASE_NAME = "housing_indicators.sqlite"
SELECTED_INDICATOR_TERMS = (
    "affordability",
    "rent",
    "rental",
    "housing need",
    "income",
    "price",
    "ownership",
    "emergency",
    "register",
)


def find_project_root() -> Path:
    """Locate this project root regardless of the launch directory."""
    current = Path(__file__).resolve()
    for parent in [current.parent, *current.parents]:
        if (parent / "src").exists() and (parent / "outputs").exists():
            return parent
    return current.parents[1]


PROJECT_ROOT = find_project_root()
OUTPUT_DIR = PROJECT_ROOT / "outputs"
DATABASE_PATH = OUTPUT_DIR / DATABASE_NAME


def read_sql(connection: sqlite3.Connection, query: str, params: tuple[object, ...] = ()) -> pd.DataFrame:
    """Run SQL and return a DataFrame."""
    return pd.read_sql_query(query, connection, params=params)


def choose_selected_indicator(connection: sqlite3.Connection) -> str:
    """Choose a sensible TA-level housing-pressure indicator for exports."""
    indicators = read_sql(
        connection,
        f"""
        SELECT
            indicator_name,
            COUNT(*) AS row_count,
            SUM(CASE WHEN indicator_value IS NOT NULL THEN 1 ELSE 0 END) AS numeric_rows,
            MAX(period_date) AS latest_period
        FROM {TABLE_NAME}
        WHERE geography_type = 'TA'
        GROUP BY indicator_name
        HAVING numeric_rows >= 50
        ORDER BY numeric_rows DESC, indicator_name
        """,
    )
    if indicators.empty:
        raise ValueError("No TA-level numeric indicator found for analysis exports.")

    lower_names = indicators["indicator_name"].str.lower()
    for term in SELECTED_INDICATOR_TERMS:
        matches = indicators[lower_names.str.contains(term, regex=False, na=False)]
        if not matches.empty:
            return str(matches.iloc[0]["indicator_name"])

    return str(indicators.iloc[0]["indicator_name"])


def export_csv(df: pd.DataFrame, filename: str) -> Path:
    """Export a DataFrame to outputs/ and return the path."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    df.to_csv(path, index=False)
    return path


def build_data_quality_summary(connection: sqlite3.Connection) -> pd.DataFrame:
    """Return one-row quality summary for the dataset."""
    return read_sql(
        connection,
        f"""
        WITH duplicate_rows AS (
            SELECT
                period,
                geography_type,
                area_id,
                theme,
                indicator_name,
                ethnicity,
                unit,
                COUNT(*) AS duplicate_count
            FROM {TABLE_NAME}
            GROUP BY
                period,
                geography_type,
                area_id,
                theme,
                indicator_name,
                ethnicity,
                unit
            HAVING COUNT(*) > 1
        )
        SELECT
            (SELECT COUNT(*) FROM {TABLE_NAME}) AS total_rows,
            (SELECT COUNT(DISTINCT period) FROM {TABLE_NAME}) AS distinct_periods,
            (SELECT MIN(period_date) FROM {TABLE_NAME}) AS earliest_period_date,
            (SELECT MAX(period_date) FROM {TABLE_NAME}) AS latest_period_date,
            (SELECT COUNT(DISTINCT geography_type) FROM {TABLE_NAME}) AS distinct_geography_types,
            (SELECT COUNT(DISTINCT territorial_authority) FROM {TABLE_NAME}) AS distinct_territorial_authorities,
            (SELECT COUNT(DISTINCT indicator_name) FROM {TABLE_NAME}) AS distinct_indicator_names,
            (SELECT COUNT(DISTINCT theme) FROM {TABLE_NAME}) AS distinct_themes,
            (SELECT COUNT(*) FROM {TABLE_NAME} WHERE indicator_value IS NULL) AS missing_indicator_value_count,
            (SELECT COALESCE(SUM(duplicate_count - 1), 0) FROM duplicate_rows) AS duplicate_looking_rows_count
        """
    )


def write_analysis_summary(
    quality_summary: pd.DataFrame,
    selected_indicator: str,
    exported_files: list[Path],
) -> Path:
    """Write a concise markdown summary of generated outputs."""
    row = quality_summary.iloc[0]
    file_lines = "\n".join(f"- `{path.name}`" for path in exported_files)
    text = f"""# Analysis Summary

## Database

- Database created: `outputs/{DATABASE_NAME}`
- Table: `{TABLE_NAME}`
- Rows: {int(row["total_rows"]):,}
- Indicators: {int(row["distinct_indicator_names"]):,}
- Date range: {row["earliest_period_date"]} to {row["latest_period_date"]}
- Geography levels: NZ and TA
- Distinct territorial authorities: {int(row["distinct_territorial_authorities"]):,}

## Selected Indicator

The selected indicator used for the top-10 and trend exports is:

`{selected_indicator}`

This was selected automatically from TA-level numeric indicators using housing-pressure keywords.
Interpret direction and policy meaning only after checking the HUD indicator definition.

## Exported CSV Files

{file_lines}

## Reporting Note

These outputs are preliminary. They support dashboard building and stakeholder review, but they are
not final findings until Power BI visuals, indicator definitions, SQL checks, and interpretation have
been validated.
"""
    path = OUTPUT_DIR / "analysis_summary.md"
    path.write_text(text, encoding="utf-8")
    return path


def main() -> None:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"SQLite database not found: {DATABASE_PATH}")

    with sqlite3.connect(DATABASE_PATH) as connection:
        selected_indicator = choose_selected_indicator(connection)
        quality_summary = build_data_quality_summary(connection)

        exports: list[Path] = []
        exports.append(export_csv(quality_summary, "data_quality_summary.csv"))

        exports.append(
            export_csv(
                read_sql(
                    connection,
                    f"""
                    SELECT
                        theme,
                        indicator_name,
                        unit,
                        geography_type,
                        COUNT(*) AS row_count,
                        MIN(period_date) AS earliest_period,
                        MAX(period_date) AS latest_period
                    FROM {TABLE_NAME}
                    GROUP BY theme, indicator_name, unit, geography_type
                    ORDER BY theme, indicator_name, geography_type, unit
                    """,
                ),
                "indicator_catalog.csv",
            )
        )

        exports.append(
            export_csv(
                read_sql(
                    connection,
                    f"""
                    WITH latest_period AS (
                        SELECT MAX(period_date) AS period_date
                        FROM {TABLE_NAME}
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
                    FROM {TABLE_NAME} AS h
                    JOIN latest_period AS lp
                        ON h.period_date = lp.period_date
                    ORDER BY h.theme, h.indicator_name, h.geography_type, h.geography_name
                    """,
                ),
                "latest_period_summary.csv",
            )
        )

        exports.append(
            export_csv(
                read_sql(
                    connection,
                    f"""
                    WITH latest_ta_period AS (
                        SELECT MAX(period_date) AS period_date
                        FROM {TABLE_NAME}
                        WHERE geography_type = 'TA'
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
                    FROM {TABLE_NAME} AS h
                    JOIN latest_ta_period AS ltp
                        ON h.period_date = ltp.period_date
                    WHERE h.geography_type = 'TA'
                    ORDER BY h.territorial_authority, h.theme, h.indicator_name
                    """,
                ),
                "ta_latest_values_sample.csv",
            )
        )

        exports.append(
            export_csv(
                read_sql(
                    connection,
                    f"""
                    WITH latest_selected_period AS (
                        SELECT MAX(period_date) AS period_date
                        FROM {TABLE_NAME}
                        WHERE geography_type = 'TA'
                          AND indicator_name = ?
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
                    FROM {TABLE_NAME} AS h
                    JOIN latest_selected_period AS lsp
                        ON h.period_date = lsp.period_date
                    WHERE h.geography_type = 'TA'
                      AND h.indicator_name = ?
                      AND h.indicator_value IS NOT NULL
                    ORDER BY h.indicator_value DESC
                    LIMIT 10
                    """,
                    (selected_indicator, selected_indicator),
                ),
                "top_ta_by_selected_indicator.csv",
            )
        )

        exports.append(
            export_csv(
                read_sql(
                    connection,
                    f"""
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
                    FROM {TABLE_NAME}
                    WHERE indicator_name = ?
                      AND geography_type IN ('NZ', 'TA')
                      AND indicator_value IS NOT NULL
                    ORDER BY geography_type, geography_name, period_date
                    """,
                    (selected_indicator,),
                ),
                "selected_indicator_trend.csv",
            )
        )

        exports.append(
            export_csv(
                read_sql(
                    connection,
                    f"""
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
                    FROM {TABLE_NAME}
                    WHERE geography_type IN ('TA', 'NZ')
                      AND indicator_value IS NOT NULL
                    ORDER BY period_date, geography_type, geography_name, theme, indicator_name
                    """,
                ),
                "dashboard_ready_housing_indicators.csv",
            )
        )

        summary_path = write_analysis_summary(quality_summary, selected_indicator, exports)

    print(f"Database path: {DATABASE_PATH}")
    print(f"Selected indicator: {selected_indicator}")
    print("Exported files:")
    for path in exports:
        print(f"  - {path}")
    print(f"Analysis summary: {summary_path}")


if __name__ == "__main__":
    main()

