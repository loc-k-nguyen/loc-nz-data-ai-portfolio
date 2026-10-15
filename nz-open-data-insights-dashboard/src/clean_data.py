"""Clean HUD Local Housing Statistics data for SQL and Power BI.

The official HUD workbook has an Instructions sheet and a Metrics sheet. The
Metrics sheet is already close to analyst-ready long format, so this script
standardises names, preserves source fields, adds dashboard-friendly aliases,
and writes one cleaned CSV.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".txt"}
PREFERRED_SHEET = "Metrics"
OUTPUT_FILE_NAME = "local_housing_indicators_clean.csv"
SOURCE_NAME = "Ministry of Housing and Urban Development / HUD"
EXPECTED_METRIC_COLUMNS = {
    "date",
    "area_type",
    "area_id",
    "area_name",
    "theme",
    "series",
    "ethnicity",
    "value",
    "value_type",
}


def find_project_root() -> Path:
    """Locate this project root regardless of the launch directory."""
    current = Path(__file__).resolve()
    for parent in [current.parent, *current.parents]:
        if (parent / "src").exists() and (parent / "data").exists():
            return parent
    return current.parents[1]


PROJECT_ROOT = find_project_root()
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def standardise_column_name(column: object) -> str:
    """Convert a column name to snake_case."""
    text = str(column).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "unnamed_column"


def deduplicate_columns(columns: list[str]) -> list[str]:
    """Make repeated column names unique."""
    seen: dict[str, int] = {}
    result: list[str] = []
    for column in columns:
        count = seen.get(column, 0)
        result.append(column if count == 0 else f"{column}_{count + 1}")
        seen[column] = count + 1
    return result


def find_raw_files() -> list[Path]:
    """Return plausible source data files from data/raw."""
    if not RAW_DIR.exists():
        return []
    return [
        path
        for path in RAW_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]


def choose_raw_file(raw_files: list[Path]) -> Path:
    """Prefer the official local housing statistics workbook when present."""
    keywords = ("lhs", "local", "housing", "hud", "statistics", "afford")

    def score(path: Path) -> tuple[int, int]:
        name = path.name.lower()
        return sum(keyword in name for keyword in keywords), path.stat().st_size

    return sorted(raw_files, key=score, reverse=True)[0]


def read_raw_file(path: Path) -> tuple[pd.DataFrame, str | None]:
    """Read CSV, TXT, or Excel data and return the sheet name if applicable."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path), None
    if suffix == ".txt":
        return pd.read_csv(path, sep=None, engine="python"), None
    if suffix in {".xlsx", ".xls"}:
        workbook = pd.ExcelFile(path)
        sheet_name = PREFERRED_SHEET if PREFERRED_SHEET in workbook.sheet_names else workbook.sheet_names[0]
        return pd.read_excel(path, sheet_name=sheet_name), sheet_name
    raise ValueError(f"Unsupported file type: {suffix}")


def trim_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Trim whitespace in text columns without replacing missing values."""
    result = df.copy()
    for column in result.select_dtypes(include=["object", "string"]).columns:
        result[column] = result[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )
    return result


def convert_numeric_like_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert object columns to numeric only when almost all values parse."""
    result = df.copy()
    for column in result.select_dtypes(include=["object", "string"]).columns:
        values = result[column].dropna()
        if values.empty:
            continue
        cleaned = values.astype(str).str.replace(",", "", regex=False)
        numeric = pd.to_numeric(cleaned, errors="coerce")
        if numeric.notna().mean() >= 0.98:
            full_cleaned = result[column].astype(str).str.replace(",", "", regex=False)
            result[column] = pd.to_numeric(full_cleaned, errors="coerce")
    return result


def clean_hud_metrics(df: pd.DataFrame, raw_file_name: str) -> pd.DataFrame:
    """Create the analyst-ready cleaned structure for HUD metrics."""
    result = df.dropna(axis=0, how="all").dropna(axis=1, how="all").copy()
    result.columns = deduplicate_columns([standardise_column_name(column) for column in result.columns])
    result = trim_text_columns(result)
    result = convert_numeric_like_columns(result)

    missing_expected = EXPECTED_METRIC_COLUMNS.difference(result.columns)
    if missing_expected:
        raise ValueError(
            "The selected file does not match the expected HUD Metrics sheet. "
            f"Missing columns: {sorted(missing_expected)}"
        )

    result["period_date"] = pd.to_datetime(result["date"], errors="coerce")
    result["period"] = result["period_date"].dt.strftime("%Y-%m-%d")
    result["year"] = result["period_date"].dt.year.astype("Int64")
    result["quarter"] = result["period_date"].dt.quarter.astype("Int64")
    result["area_id"] = pd.to_numeric(result["area_id"], errors="coerce").astype("Int64")
    result["indicator_value"] = pd.to_numeric(result["value"], errors="coerce")
    result["indicator_name"] = result["series"]
    result["unit"] = result["value_type"]
    result["territorial_authority"] = result["area_name"].where(
        result["area_type"].eq("TA"), pd.NA
    )
    result["geography_name"] = result["area_name"]
    result["geography_type"] = result["area_type"]
    result["source"] = SOURCE_NAME
    result["raw_file_name"] = raw_file_name

    ordered_columns = [
        "period",
        "period_date",
        "year",
        "quarter",
        "geography_type",
        "area_id",
        "geography_name",
        "territorial_authority",
        "theme",
        "indicator_name",
        "indicator_value",
        "unit",
        "ethnicity",
        "source",
        "raw_file_name",
    ]
    return result[ordered_columns]


def infer_columns(columns: list[str], keywords: tuple[str, ...]) -> list[str]:
    """Return columns whose names contain any keyword."""
    return [column for column in columns if any(keyword in column for keyword in keywords)]


def print_profile(
    input_path: Path,
    output_path: Path,
    sheet_name: str | None,
    raw_shape: tuple[int, int],
    cleaned: pd.DataFrame,
) -> None:
    """Print a compact data profile for validation."""
    columns = cleaned.columns.tolist()
    missing_summary = cleaned.isna().sum().sort_values(ascending=False)
    missing_summary = missing_summary[missing_summary > 0]
    duplicate_count = cleaned.duplicated(
        ["period", "geography_type", "area_id", "theme", "indicator_name", "ethnicity", "unit"]
    ).sum()

    print(f"Input path: {input_path}")
    if sheet_name:
        print(f"Excel sheet used: {sheet_name}")
    print(f"Output path: {output_path}")
    print(f"Raw shape: {raw_shape}")
    print(f"Cleaned shape: {cleaned.shape}")
    print("Cleaned columns:")
    for column in columns:
        print(f"  - {column}")

    print("Missing value summary:")
    if missing_summary.empty:
        print("  No missing values detected.")
    else:
        for column, count in missing_summary.items():
            print(f"  - {column}: {count}")

    print(
        "Possible date/period columns: "
        f"{infer_columns(columns, ('date', 'period', 'year', 'quarter')) or '[none detected]'}"
    )
    print(
        "Possible geography columns: "
        f"{infer_columns(columns, ('geography', 'area', 'territorial', 'authority')) or '[none detected]'}"
    )
    print(
        "Possible indicator/value columns: "
        f"{infer_columns(columns, ('indicator', 'value', 'unit', 'theme')) or '[none detected]'}"
    )
    print(f"Duplicate-looking period/geography/indicator rows: {duplicate_count}")


def main() -> None:
    raw_files = find_raw_files()
    if not raw_files:
        raise FileNotFoundError(
            f"No plausible raw data files found in {RAW_DIR}. "
            "Download the official HUD Local Housing Statistics XLSX and rerun."
        )

    raw_path = choose_raw_file(raw_files)
    raw_df, sheet_name = read_raw_file(raw_path)
    cleaned = clean_hud_metrics(raw_df, raw_path.name)

    output_path = PROCESSED_DIR / OUTPUT_FILE_NAME
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(output_path, index=False)

    print(f"Using raw file: {raw_path.name}")
    print_profile(raw_path, output_path, sheet_name, raw_df.shape, cleaned)


if __name__ == "__main__":
    main()

