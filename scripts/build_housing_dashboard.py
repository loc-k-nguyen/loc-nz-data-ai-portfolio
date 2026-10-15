"""Build a portable housing-data explorer from the preserved cleaned HUD extract.

No network requests, model training, or implicit source updates. Each displayed
series fixes its unit and population; conflicting or duplicate keys stop the build.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "nz-open-data-insights-dashboard"
DEFAULT_INPUT = PROJECT / "data/processed/local_housing_indicators_clean.csv"
SOURCE_URL = (
    "https://www.hud.govt.nz/stats-and-insights/local-housing-statistics/"
    "about-the-local-housing-statistics-dashboard"
)
SERIES = [
    {
        "id": "register",
        "name": "Housing Register",
        "unit": "",
        "ethnicity": "All",
        "label": "Housing Register",
        "displayUnit": "registered applications",
        "note": "Applications on the Housing Register. An application represents a household, not all housing need.",
    },
    {
        "id": "rent",
        "name": "Median Rent Price",
        "unit": "$",
        "ethnicity": "",
        "label": "Median weekly rent",
        "displayUnit": "NZD per week",
        "note": "A snapshot of the source rent measure. Dollar values are kept separate from the source's rank rows.",
    },
    {
        "id": "consents",
        "name": "Building Consents per 10k population",
        "unit": "per 10k population",
        "ethnicity": "",
        "label": "Building consents",
        "displayUnit": "per 10,000 population",
        "note": (
            "New dwelling consents over the source reporting period. "
            "Consents indicate intended building, not completions."
        ),
    },
    {
        "id": "rent-burden",
        "name": "Households whose rent is equal to or more than 30% of income",
        "unit": "%",
        "ethnicity": "",
        "label": "Rent at least 30% of income",
        "displayUnit": "% of households",
        "displayScale": 100,
        "note": (
            "Census-based rent-to-income measure. Read the source population definition; "
            "this is not a monthly estimate. Stored fractions use percentage display: 0.426 = 42.6%."
        ),
    },
    {
        "id": "rent-index",
        "name": "Rent affordability index",
        "unit": "index",
        "ethnicity": "",
        "label": "Rent affordability index",
        "displayUnit": "source index",
        "note": (
            "An index of change over time. Cross-area values are not an affordability league table. "
            "Direction is left neutral."
        ),
    },
]


def build_payload(source: Path) -> dict:
    """Validate and select exact series through parameterized SQLite queries."""
    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {
            "period",
            "geography_type",
            "area_id",
            "geography_name",
            "theme",
            "indicator_name",
            "indicator_value",
            "unit",
            "ethnicity",
            "raw_file_name",
        }
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Input does not match the cleaned HUD schema.")
        rows = list(reader)
    if not rows:
        raise ValueError("Input is empty.")
    raw_files = sorted({row["raw_file_name"] for row in rows})
    if raw_files != ["hud_local_housing_statistics_2026_04.xlsx"]:
        raise ValueError("New source vintage: review the source metadata and measure definitions before building.")
    with sqlite3.connect(":memory:") as db:
        db.execute(
            "CREATE TABLE observations (period TEXT, geo TEXT, area TEXT, name TEXT, theme TEXT, "
            "indicator TEXT, value REAL, unit TEXT, ethnicity TEXT)"
        )
        db.executemany(
            "INSERT INTO observations VALUES (?,?,?,?,?,?,?,?,?)",
            [
                (
                    r["period"],
                    r["geography_type"],
                    r["area_id"],
                    r["geography_name"],
                    r["theme"],
                    r["indicator_name"],
                    r["indicator_value"] or None,
                    r["unit"],
                    r["ethnicity"],
                )
                for r in rows
            ],
        )
        duplicates = db.execute(
            "SELECT COALESCE(SUM(n-1),0) FROM (SELECT COUNT(*) n FROM observations "
            "GROUP BY period,geo,area,theme,indicator,unit,ethnicity HAVING COUNT(*)>1)"
        ).fetchone()[0]
        areas = dict(db.execute("SELECT DISTINCT area,name FROM observations WHERE geo='TA' ORDER BY name"))
        selected = []
        for config in SERIES:
            values = db.execute(
                "SELECT period,geo,area,value FROM observations "
                "WHERE indicator=? AND unit=? AND ethnicity=? AND geo IN ('TA','NZ') "
                "ORDER BY period,geo,area",
                (config["name"], config["unit"], config["ethnicity"]),
            ).fetchall()
            if not values:
                raise ValueError(f"Missing series: {config['name']}")
            keys = [(date, geo, area) for date, geo, area, _ in values]
            if len(keys) != len(set(keys)):
                raise ValueError(f"Duplicate keys in displayed series: {config['name']}")
            if any(value is None or not isinstance(value, (int, float)) for *_, value in values):
                raise ValueError(f"Non-numeric or missing displayed values: {config['name']}")
            selected.append({**config, "values": values})
    return {
        "source": {
            "name": "HUD Local Housing Statistics",
            "url": SOURCE_URL,
            "vintage": "April 2026 extract",
            "file": raw_files[0],
            "input_lf_sha256": hashlib.sha256(source.read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        },
        "quality": {
            "sourceRows": len(rows),
            "sourceDuplicateKeys": duplicates,
            "selectedDuplicateKeys": 0,
            "territorialAuthorities": len(areas),
        },
        "areas": areas,
        "series": selected,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/data.json")
    parser.add_argument("--check", action="store_true", help="Fail if committed dashboard data is stale.")
    args = parser.parse_args()
    payload = build_payload(args.input)
    content = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n"
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != content:
            raise SystemExit("Dashboard data is stale. Run python scripts/build_housing_dashboard.py.")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8", newline="\n")
    print(f"Validated {len(payload['series'])} series from {payload['quality']['sourceRows']:,} source rows.")
    print(f"Dashboard: {args.output}")


if __name__ == "__main__":
    main()
