"""Build a local SQLite database from the cleaned HUD housing CSV."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

TABLE_NAME = "housing_indicators"
INPUT_FILE_NAME = "local_housing_indicators_clean.csv"
OUTPUT_DATABASE_NAME = "housing_indicators.sqlite"


def find_project_root() -> Path:
    """Locate this project root regardless of the launch directory."""
    current = Path(__file__).resolve()
    for parent in [current.parent, *current.parents]:
        if (parent / "src").exists() and (parent / "data").exists():
            return parent
    return current.parents[1]


PROJECT_ROOT = find_project_root()
INPUT_CSV = PROJECT_ROOT / "data" / "processed" / INPUT_FILE_NAME
OUTPUT_DATABASE = PROJECT_ROOT / "outputs" / OUTPUT_DATABASE_NAME


CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
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
"""


INDEX_STATEMENTS = [
    f"CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_period_date ON {TABLE_NAME} (period_date)",
    f"CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_geography_type ON {TABLE_NAME} (geography_type)",
    f"CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_territorial_authority ON {TABLE_NAME} (territorial_authority)",
    f"CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_geography_name ON {TABLE_NAME} (geography_name)",
    f"CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_indicator_name ON {TABLE_NAME} (indicator_name)",
    f"CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_theme ON {TABLE_NAME} (theme)",
]


def load_cleaned_csv(path: Path) -> pd.DataFrame:
    """Load cleaned data and enforce practical dtypes before SQLite import."""
    if not path.exists():
        raise FileNotFoundError(f"Cleaned CSV not found: {path}")

    df = pd.read_csv(path)
    integer_columns = ["year", "quarter", "area_id"]
    for column in integer_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")

    if "indicator_value" in df.columns:
        df["indicator_value"] = pd.to_numeric(df["indicator_value"], errors="coerce")

    return df


def build_database(df: pd.DataFrame, database_path: Path) -> None:
    """Create the SQLite table, load rows, and add indexes."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        connection.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
        connection.execute(CREATE_TABLE_SQL)
        df.to_sql(TABLE_NAME, connection, if_exists="append", index=False)
        for statement in INDEX_STATEMENTS:
            connection.execute(statement)
        connection.commit()


def main() -> None:
    df = load_cleaned_csv(INPUT_CSV)
    build_database(df, OUTPUT_DATABASE)

    print(f"Input CSV path: {INPUT_CSV}")
    print(f"Output database path: {OUTPUT_DATABASE}")
    print(f"Rows loaded: {len(df)}")
    print(f"Columns loaded: {len(df.columns)}")
    print(f"Table name: {TABLE_NAME}")
    print("Indexes created:")
    for statement in INDEX_STATEMENTS:
        index_name = statement.split()[5]
        print(f"  - {index_name}")


if __name__ == "__main__":
    main()

