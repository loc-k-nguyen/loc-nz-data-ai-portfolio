"""Regression checks for the portable model and Desktop-discovered format errors."""

import base64
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("powerbi", ROOT / "scripts/build_powerbi_report.py")
powerbi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(powerbi)


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.setattr(powerbi, "DEST", tmp_path)
    monkeypatch.setattr(powerbi, "REPORT", tmp_path / "NZHousing.Report")
    monkeypatch.setattr(powerbi, "MODEL", tmp_path / "NZHousing.SemanticModel")
    powerbi.build()
    return tmp_path


def table_rows(table):
    query = "\n".join(table["partitions"][0]["source"]["expression"])
    encoded = query.split('Binary.FromText("', 1)[1].split('"', 1)[0]
    return json.loads(base64.b64decode(encoded))


def test_embedded_model_preserves_values_and_unique_dimensions(project):
    model_text = (project / "NZHousing.SemanticModel/model.bim").read_text(encoding="utf-8")
    model = json.loads(model_text)
    tables = {table["name"]: table for table in model["model"]["tables"]}
    facts = table_rows(tables["Observation"])
    assert len(facts) == 13685
    assert len({tuple(row[:3]) for row in facts}) == len(facts)
    assert ["rent-burden", "47", "2023-01-01", 0.426] in facts
    assert ["register", "47", "2026-04-01", 663] in facts
    assert not any(row[0] == "rent" and row[1] == "67" for row in facts)
    for name in ["Area", "Indicator", "Date", "Area picker"]:
        rows = table_rows(tables[name])
        assert len({row[0] for row in rows}) == len(rows)
    assert "File.Contents" not in model_text
    assert "C:\\Users" not in model_text
    assert model["compatibilityLevel"] >= 1601
    for measure in tables["Indicator"]["measures"]:
        assert not ("formatStringDefinition" in measure and "formatString" in measure)


def test_native_slicer_filter_envelope_and_visual_references(project):
    folder = project / "NZHousing.Report/definition/pages"
    metric = json.loads((folder / "overview/visuals/metric/visual.json").read_text(encoding="utf-8"))
    native_filter = metric["visual"]["objects"]["general"][0]["properties"]["filter"]["filter"]
    assert native_filter["Where"][0]["Condition"]["In"]["Values"][0][0]["Literal"]["Value"] == "'Housing Register'"
    model = json.loads((project / "NZHousing.SemanticModel/model.bim").read_text(encoding="utf-8"))
    tables = {table["name"]: table for table in model["model"]["tables"]}
    for path in folder.rglob("visual.json"):
        visual = json.loads(path.read_text(encoding="utf-8"))
        for role in visual["visual"].get("query", {}).get("queryState", {}).values():
            for projection in role["projections"]:
                kind, field = next(iter(projection["field"].items()))
                table = tables[field["Expression"]["SourceRef"]["Entity"]]
                members = table["columns"] if kind == "Column" else table.get("measures", [])
                assert field["Property"] in {member["name"] for member in members}
        box = visual["position"]
        assert box["x"] + box["width"] <= 1440
        assert box["y"] + box["height"] <= 900


def test_card_sizes_use_typed_powerbi_numeric_literals(project):
    folder = project / "NZHousing.Report/definition/pages/overview/visuals"
    for name, size in [("unit", "12D"), ("kpi_0", "20D"), ("kpi_3", "20D")]:
        visual = json.loads((folder / name / "visual.json").read_text(encoding="utf-8"))
        assert visual["visual"]["objects"]["labels"][0]["properties"]["fontSize"]["expr"]["Literal"]["Value"] == size
