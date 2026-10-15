"""Check reporting errors that could mislead dashboard readers."""

import csv
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("housing", ROOT / "scripts/build_housing_dashboard.py")
housing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(housing)


def test_exact_units_and_population_are_selected():
    payload = housing.build_payload(housing.DEFAULT_INPUT)
    rent = next(s for s in payload["series"] if s["id"] == "rent")
    assert rent["unit"] == "$"
    assert all(value > 100 for *_, value in rent["values"])
    assert payload["quality"]["sourceDuplicateKeys"] == 61
    assert payload["quality"]["selectedDuplicateKeys"] == 0
    assert len(payload["areas"]) == 67
    assert len({max(r[0] for r in s["values"]) for s in payload["series"]}) > 1


def test_duplicate_displayed_observation_stops_build(tmp_path):
    with housing.DEFAULT_INPUT.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    rows.append(next(r.copy() for r in rows if r["indicator_name"] == "Housing Register"))
    path = tmp_path / "conflict.csv"
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match="Duplicate keys"):
        housing.build_payload(path)


def test_empty_input_stops_build(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("period,indicator_value\n", encoding="utf-8")
    with pytest.raises(ValueError, match="schema"):
        housing.build_payload(path)
