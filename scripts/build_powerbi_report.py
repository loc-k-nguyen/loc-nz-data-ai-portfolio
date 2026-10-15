"""Build a portable Power BI project from the exact validated HUD series.

The import model uses embedded, typed Power Query tables, so opening the project
requires no credentials, machine-specific paths, or silent source download.
Regenerate deliberately when the preserved source changes. Desktop validation is
required before claiming this project is a finished report.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

from build_housing_dashboard import DEFAULT_INPUT, build_payload

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "nz-open-data-insights-dashboard/powerbi/report"
REPORT = DEST / "NZHousing.Report"
MODEL = DEST / "NZHousing.SemanticModel"
GREEN, PAPER, INK, MUTED = "#173C34", "#F6F5F0", "#19352E", "#607068"
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def literal(value: str | int | bool) -> dict:
    text = str(value).lower() if isinstance(value, bool) else f"{value}D" if isinstance(value, int) else str(value)
    if isinstance(value, str):
        text = "'" + value.replace("'", "''") + "'"
    return {"expr": {"Literal": {"Value": text}}}


def color(value: str) -> dict:
    return {"solid": {"color": literal(value)}}


def column(table: str, name: str) -> dict:
    return {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": name}}


def measure(name: str) -> dict:
    return {"Measure": {"Expression": {"SourceRef": {"Entity": "Indicator"}}, "Property": name}}


def projection(field: dict, label: str | None = None) -> dict:
    kind = next(iter(field))
    item = field[kind]
    table = item["Expression"]["SourceRef"]["Entity"]
    result = {"field": field, "queryRef": f"{table}.{item['Property']}"}
    if label:
        result["displayName"] = label
    return result


def selected_filter(table: str, field: str, value: str) -> dict:
    return {
        "Version": 2,
        "From": [{"Name": "s", "Entity": table, "Type": 0}],
        "Where": [
            {
                "Condition": {
                    "In": {
                        "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "s"}}, "Property": field}}],
                        "Values": [[{"Literal": {"Value": "'" + value.replace("'", "''") + "'"}}]],
                    }
                }
            }
        ],
    }


def visual(
    page: str,
    name: str,
    kind: str,
    box: tuple,
    title: str | None = None,
    roles: dict | None = None,
    objects: dict | None = None,
) -> dict:
    x, y, width, height = box
    container = {
        "title": [
            {
                "properties": {
                    "show": literal(bool(title)),
                    "text": literal(title or ""),
                    "fontSize": literal(14),
                    "fontColor": color(INK),
                    "fontFamily": literal("Segoe UI Semibold"),
                }
            }
        ],
        "background": [{"properties": {"show": literal(True), "color": color("#FFFFFF"), "transparency": literal(0)}}],
        "border": [{"properties": {"show": literal(False)}}],
        "visualHeader": [{"properties": {"show": literal(False)}}],
    }
    body = {"visualType": kind, "visualContainerObjects": container}
    if roles:
        body["query"] = {
            "queryState": {
                role: {"projections": [projection(field) for field in fields]} for role, fields in roles.items()
            }
        }
    if objects:
        body["objects"] = objects
    result = {
        "$schema": f"{SCHEMA}/visualContainer/2.7.0/schema.json",
        "name": name,
        "position": {"x": x, "y": y, "z": y, "width": width, "height": height, "tabOrder": y * 10 + x},
        "visual": body,
    }
    write(REPORT / f"definition/pages/{page}/visuals/{name}/visual.json", result)
    return result


def text(
    page: str,
    name: str,
    value: str,
    box: tuple,
    size: int = 14,
    foreground: str = MUTED,
    family: str = "Segoe UI",
    bold: bool = False,
) -> None:
    obj = {
        "general": [
            {
                "properties": {
                    "paragraphs": [
                        {
                            "textRuns": [
                                {
                                    "value": line,
                                    "textStyle": {
                                        "fontFamily": family,
                                        "fontSize": f"{size}pt",
                                        "color": foreground,
                                        "fontWeight": "bold" if bold else "normal",
                                    },
                                }
                            ]
                        }
                        for line in value.split("\n")
                    ]
                }
            }
        ]
    }
    item = visual(page, name, "textbox", box, objects=obj)
    item["visual"]["visualContainerObjects"]["background"][0]["properties"]["transparency"] = literal(100)
    write(REPORT / f"definition/pages/{page}/visuals/{name}/visual.json", item)


def card(page: str, name: str, title: str, metric: str, box: tuple, size: int = 20) -> None:
    visual(
        page,
        name,
        "card",
        box,
        title,
        {"Values": [measure(metric)]},
        {
            "labels": [
                {"properties": {"color": color(GREEN), "fontSize": literal(size), "labelDisplayUnits": literal(1)}}
            ],
            "categoryLabels": [{"properties": {"show": literal(False)}}],
        },
    )


def slicer(page: str, name: str, table: str, field: str, selection: str | None, box: tuple, title: str) -> None:
    objects = {
        "data": [{"properties": {"mode": literal("Dropdown")}}],
        "selection": [{"properties": {"singleSelect": literal(True), "selectAllCheckboxEnabled": literal(False)}}],
        "header": [{"properties": {"show": literal(False)}}],
    }
    if selection:
        objects["general"] = [{"properties": {"filter": {"filter": selected_filter(table, field, selection)}}}]
    visual(page, name, "slicer", box, title, {"Values": [column(table, field)]}, objects)


def page(name: str, title: str, subtitle: str, number: str) -> None:
    write(
        REPORT / f"definition/pages/{name}/page.json",
        {
            "$schema": f"{SCHEMA}/page/2.0.0/schema.json",
            "name": name,
            "displayName": title,
            "displayOption": "FitToPage",
            "width": 1440,
            "height": 900,
            "objects": {"background": [{"properties": {"color": color(PAPER), "transparency": literal(0)}}]},
        },
    )
    text(name, "title", title, (40, 25, 1090, 62), 31, GREEN, "Georgia")
    text(name, "subtitle", subtitle, (40, 94, 1300, 38), 14)
    text(name, "folio", f"NZ HOUSING / {number}", (1135, 38, 265, 34), 13, GREEN, bold=True)
    text(
        name,
        "footer",
        "Loc K. Nguyen  |  Independent portfolio  |  Preserved HUD April 2026 extract  |  Not a live feed",
        (40, 855, 1350, 30),
        11,
    )


def imported_table(name: str, specs: list[tuple[str, str]], rows: list) -> dict:
    encoded = base64.b64encode(json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()).decode()
    names = ", ".join('"' + col + '"' for col, _ in specs)
    mtypes = {"string": "type text", "double": "type number", "int64": "Int64.Type", "dateTime": "type date"}
    types = ", ".join('{"' + col + '", ' + mtypes[dtype] + "}" for col, dtype in specs)
    expression = [
        "let",
        f'    Rows = Json.Document(Binary.FromText("{encoded}", BinaryEncoding.Base64)),',
        f"    Source = Table.FromRows(Rows, {{{names}}}),",
        f'    Typed = Table.TransformColumnTypes(Source, {{{types}}}, "en-NZ")',
        "in",
        "    Typed",
    ]
    return {
        "name": name,
        "columns": [
            {
                "name": col,
                "dataType": dtype,
                "sourceColumn": col,
                "summarizeBy": "none",
                **({"formatString": "d MMM yyyy"} if dtype == "dateTime" else {}),
            }
            for col, dtype in specs
        ],
        "partitions": [{"name": name, "mode": "import", "source": {"type": "m", "expression": expression}}],
    }


def build() -> None:
    payload = build_payload(DEFAULT_INPUT)
    series = payload["series"]
    areas = [[area, label, "TA"] for area, label in payload["areas"].items()]
    areas.append(["NZ", "New Zealand", "NZ"])
    facts, indicators, dates = [], [], set()
    formats = {"rent": "$#,0", "rent-burden": "0.0%", "consents": "0.0", "rent-index": "0.0000"}
    for item in series:
        if item["id"] == "rent-burden" and any(not 0 <= row[3] <= 1 for row in item["values"]):
            raise ValueError("Rent-burden encoding changed; review the fractional percentage source")
        ta = [row for row in item["values"] if row[1] == "TA"]
        latest = max(row[0] for row in ta)
        unit = item["displayUnit"]
        note = item["note"]
        if item["id"] == "rent-burden":
            unit = "% of renting households"
            note += " Stored as a fraction: 0.426 displays as 42.6%. Source population and Census dates apply."
        indicators.append(
            [
                item["id"],
                item["label"],
                unit,
                note,
                formats.get(item["id"], "#,0"),
                latest,
                sum(row[0] == latest for row in ta),
                len(item["values"]),
            ]
        )
        for observed, geo, area, value in item["values"]:
            dates.add(observed)
            facts.append([item["id"], area if geo == "TA" else "NZ", observed, value])
    tables = [
        imported_table(
            "Observation",
            [("MetricID", "string"), ("AreaID", "string"), ("Date", "dateTime"), ("Value", "double")],
            facts,
        ),
        imported_table(
            "Indicator",
            [
                ("MetricID", "string"),
                ("Metric", "string"),
                ("Unit", "string"),
                ("Definition", "string"),
                ("NumberFormat", "string"),
                ("LatestDate", "dateTime"),
                ("Coverage", "int64"),
                ("Rows", "int64"),
            ],
            indicators,
        ),
        imported_table("Area", [("AreaID", "string"), ("Area", "string"), ("Geography", "string")], areas),
        imported_table(
            "Area picker", [("AreaID", "string"), ("Area", "string")], [row[:2] for row in areas if row[2] == "TA"]
        ),
        imported_table("Date", [("Date", "dateTime")], [[d] for d in sorted(dates)]),
    ]
    measures = {
        "Observed value": "IF(HASONEVALUE(Indicator[MetricID]) && COUNTROWS(Observation) = 1, MAX(Observation[Value]))",
        "Latest date": (
            "IF(HASONEVALUE(Indicator[MetricID]), CALCULATE(MAX(Observation[Date]), "
            "REMOVEFILTERS(Area), REMOVEFILTERS('Date')))"
        ),
        "Latest value": (
            "VAR d = [Latest date] RETURN IF(NOT ISBLANK(d), CALCULATE([Observed value], "
            "REMOVEFILTERS('Date'), 'Date'[Date] = d))"
        ),
        "Selected area latest": (
            "IF(HASONEVALUE('Area picker'[AreaID]), CALCULATE([Latest value], REMOVEFILTERS(Area), "
            "TREATAS(VALUES('Area picker'[AreaID]), Area[AreaID])))"
        ),
        "Selected area trend": (
            "IF(HASONEVALUE('Area picker'[AreaID]), CALCULATE([Observed value], REMOVEFILTERS(Area), "
            "TREATAS(VALUES('Area picker'[AreaID]), Area[AreaID])))"
        ),
        "Selected area display": (
            'VAR v = [Selected area latest] RETURN IF(ISBLANK(v), "Not available", FORMAT(v, '
            'SELECTEDVALUE(Indicator[NumberFormat], "#,0")))'
        ),
        "Observation date": 'IF(ISBLANK([Latest date]), "Select one metric", FORMAT([Latest date], "d mmm yyyy"))',
        "TA coverage": (
            "VAR d = [Latest date] RETURN IF(NOT ISBLANK(d), "
            "CALCULATE(DISTINCTCOUNT(Observation[AreaID]), REMOVEFILTERS(Area), "
            "REMOVEFILTERS('Date'), Area[Geography] = \"TA\", 'Date'[Date] = d))"
        ),
        "Coverage display": 'IF(ISBLANK([TA coverage]), "Not available", FORMAT([TA coverage], "0") & " / 67")',
        "National value": (
            "VAR d = [Latest date] RETURN IF(NOT ISBLANK(d), CALCULATE([Observed value], "
            "REMOVEFILTERS(Area), REMOVEFILTERS('Date'), Area[Geography] = \"NZ\", 'Date'[Date] = d))"
        ),
        "National display": (
            'VAR v = [National value] RETURN IF(ISBLANK(v), "Not available", FORMAT(v, '
            'SELECTEDVALUE(Indicator[NumberFormat], "#,0")))'
        ),
        "Top ten value": (
            'VAR v = [Latest value] VAR leaders = TOPN(10, FILTER(ALL(Area), Area[Geography] = "TA" '
            "&& NOT ISBLANK([Latest value])), [Latest value], DESC, Area[Area], ASC) RETURN "
            "IF(CONTAINS(leaders, Area[AreaID], SELECTEDVALUE(Area[AreaID])), v)"
        ),
        "Metric note": (
            'SELECTEDVALUE(Indicator[Definition], "Choose one metric. Mixed measures are never added or averaged.")'
        ),
        "Unit label": 'SELECTEDVALUE(Indicator[Unit], "Select one metric")',
        "Area label": "SELECTEDVALUE('Area picker'[Area], \"Select one territorial authority\")",
        "History note": (
            "VAR n = CALCULATE(COUNTROWS(Observation), REMOVEFILTERS(Area), REMOVEFILTERS('Date'), "
            "TREATAS(VALUES('Area picker'[AreaID]), Area[AreaID])) RETURN IF(n < 2, \"One observation "
            'or no data: a trend cannot be inferred.", "Observed dates only. Gaps are not '
            'interpolated. National and TA dates must match for comparison.")'
        ),
        "Source rows": str(payload["quality"]["sourceRows"]),
        "Source repeated keys": str(payload["quality"]["sourceDuplicateKeys"]),
        "Selected rows": str(len(facts)),
        "Selected duplicate keys": "0",
    }
    numeric = {
        "Observed value",
        "Latest value",
        "Selected area latest",
        "Selected area trend",
        "National value",
        "Top ten value",
    }
    tables[1]["measures"] = [
        {
            "name": name,
            "expression": expr,
            **(
                {
                    "formatStringDefinition": {"expression": 'SELECTEDVALUE(Indicator[NumberFormat], "#,0.##")'},
                }
                if name in numeric
                else {}
            ),
        }
        for name, expr in measures.items()
    ]
    for table in tables:
        for col in table["columns"]:
            if col["name"] in {"MetricID", "AreaID", "NumberFormat"}:
                col["isHidden"] = True
    write(MODEL / "definition.pbism", {"version": "1.0", "settings": {}})
    write(
        MODEL / "model.bim",
        {
            "name": "NZHousing",
            "compatibilityLevel": 1601,
            "model": {
                "culture": "en-NZ",
                "sourceQueryCulture": "en-NZ",
                "defaultPowerBIDataSourceVersion": "powerBI_V3",
                "tables": tables,
                "relationships": [
                    {
                        "name": f"Observation_{table}",
                        "fromTable": "Observation",
                        "fromColumn": key,
                        "toTable": table,
                        "toColumn": key,
                        "crossFilteringBehavior": "oneDirection",
                    }
                    for table, key in [("Indicator", "MetricID"), ("Area", "AreaID"), ("Date", "Date")]
                ],
            },
        },
    )
    write(
        DEST / "NZHousing.pbip",
        {
            "version": "1.0",
            "artifacts": [{"report": {"path": "NZHousing.Report"}}],
            "settings": {"enableAutoRecovery": True},
        },
    )
    write(
        REPORT / "definition.pbir",
        {"version": "4.0", "datasetReference": {"byPath": {"path": "../NZHousing.SemanticModel"}}},
    )
    write(
        REPORT / "definition/version.json",
        {"$schema": f"{SCHEMA}/versionMetadata/1.0.0/schema.json", "version": "2.0.0"},
    )
    write(
        REPORT / "definition/report.json",
        {
            "$schema": f"{SCHEMA}/report/3.0.0/schema.json",
            "themeCollection": {
                "baseTheme": {
                    "name": "CY24SU06",
                    "reportVersionAtImport": {"visual": "1.8.0", "report": "3.0.0", "page": "2.0.0"},
                    "type": "SharedResources",
                }
            },
            "settings": {"useStylableVisualContainerHeader": True, "exportDataMode": "AllowSummarized"},
        },
    )
    order = ["overview", "observations", "method"]
    write(
        REPORT / "definition/pages/pages.json",
        {"$schema": f"{SCHEMA}/pagesMetadata/1.0.0/schema.json", "pageOrder": order, "activePageName": "overview"},
    )
    page(
        "overview",
        "Housing, in context.",
        "Five source-defined indicators. One consistent view of place, time and data coverage.",
        "01",
    )
    slicer(
        "overview", "metric", "Indicator", "Metric", "Housing Register", (40, 146, 530, 74), "Indicator / select one"
    )
    slicer(
        "overview",
        "area",
        "Area picker",
        "Area",
        "Wellington City",
        (594, 146, 410, 74),
        "Territorial authority / select one",
    )
    text(
        "overview",
        "source_note",
        "LATEST AVAILABLE OBSERVATIONS\nDates differ by measure. Missing is not zero.",
        (1030, 155, 370, 64),
        12,
    )
    for i, (title, metric) in enumerate(
        [
            ("Selected area", "Selected area display"),
            ("Observation date", "Observation date"),
            ("TA reporting coverage", "Coverage display"),
            ("National source value", "National display"),
        ]
    ):
        card("overview", f"kpi_{i}", title, metric, (40 + i * 346, 245, 322, 114))
    chart = visual(
        "overview",
        "comparison",
        "clusteredBarChart",
        (40, 392, 660, 340),
        "Highest reported TA values",
        {"Category": [column("Area", "Area")], "Y": [measure("Top ten value")]},
        {
            "dataPoint": [{"properties": {"defaultColor": color(GREEN)}}],
            "labels": [{"properties": {"show": literal(True), "labelDisplayUnits": literal(1)}}],
            "categoryAxis": [{"properties": {"fontSize": literal(10)}}],
            "valueAxis": [{"properties": {"showAxisTitle": literal(False)}}],
        },
    )
    chart["visual"]["query"]["sortDefinition"] = {
        "sort": [{"field": measure("Top ten value"), "direction": "Descending"}],
        "isDefaultSort": False,
    }
    write(REPORT / "definition/pages/overview/visuals/comparison/visual.json", chart)
    visual(
        "overview",
        "trend",
        "lineChart",
        (740, 392, 660, 340),
        "Selected area / available history",
        {"Category": [column("Date", "Date")], "Y": [measure("Selected area trend")]},
        {
            "dataPoint": [{"properties": {"defaultColor": color(GREEN)}}],
            "categoryAxis": [{"properties": {"axisType": literal("Scalar"), "showAxisTitle": literal(False)}}],
            "lineStyles": [{"properties": {"showMarker": literal(True)}}],
        },
    )
    card("overview", "unit", "Unit / source definition", "Unit label", (40, 752, 440, 70), size=12)
    text(
        "overview",
        "caution",
        "INTERPRETATION  /  Read the source definition before comparing areas.\n"
        "Single observations do not establish trends. Missing is not zero; the index is not an affordability ranking.",
        (505, 752, 895, 75),
        12,
    )
    page(
        "observations",
        "Inspect the observations.",
        "Exact values, geography and reporting dates. Filter before interpreting; no mixed-unit totals.",
        "02",
    )
    slicer(
        "observations",
        "metric",
        "Indicator",
        "Metric",
        "Housing Register",
        (40, 146, 530, 74),
        "Indicator / select one",
    )
    slicer("observations", "area", "Area", "Area", "Wellington City", (594, 146, 410, 74), "Area / select one")
    slicer("observations", "date", "Date", "Date", None, (1030, 146, 370, 74), "Observation date / optional")
    visual(
        "observations",
        "values",
        "tableEx",
        (40, 250, 1360, 520),
        "Source observations",
        {
            "Values": [
                column("Date", "Date"),
                column("Area", "Area"),
                column("Area", "Geography"),
                measure("Observed value"),
                column("Indicator", "Unit"),
            ]
        },
        {
            "grid": [{"properties": {"gridVertical": literal(False), "rowPadding": literal(7)}}],
            "total": [{"properties": {"totals": literal(False)}}],
            "columnHeaders": [{"properties": {"fontColor": color(GREEN), "fontSize": literal(13)}}],
        },
    )
    text(
        "observations",
        "note",
        (
            "Dates are observation dates, not publication dates. A missing area or date has no "
            "observation.\nPercentage shares retain their source fractions and use percentage "
            "formatting; 0.426 = 42.6%."
        ),
        (40, 790, 1360, 52),
        12,
    )
    page(
        "method",
        "Data quality is part of the report.",
        "Preserved source. Explicit transformations. Checks that stop ambiguous series entering the model.",
        "03",
    )
    for i, (title, metric) in enumerate(
        [
            ("Rows in cleaned source", "Source rows"),
            ("Repeated source keys", "Source repeated keys"),
            ("Selected observations", "Selected rows"),
            ("Selected duplicate keys", "Selected duplicate keys"),
        ]
    ):
        card("method", f"quality_{i}", title, metric, (40 + i * 346, 152, 322, 114))
    visual(
        "method",
        "catalog",
        "tableEx",
        (40, 310, 1360, 275),
        "Selected series / latest TA observation and coverage",
        {
            "Values": [
                column("Indicator", "Metric"),
                column("Indicator", "Unit"),
                column("Indicator", "LatestDate"),
                column("Indicator", "Coverage"),
                column("Indicator", "Rows"),
            ]
        },
        {"grid": [{"properties": {"rowPadding": literal(9)}}], "total": [{"properties": {"totals": literal(False)}}]},
    )
    text(
        "method",
        "scope",
        (
            "SOURCE & SCOPE\nHUD Local Housing Statistics, preserved April 2026 extract.\nSource-wide "
            "dates: 1996 to April 2026; selected series have shorter histories.\n67 territorial "
            "authorities. No regional-council field or invented national aggregate."
        ),
        (40, 620, 655, 170),
        14,
    )
    text(
        "method",
        "limits",
        (
            "RULES FOR INTERPRETATION\nExact series, unit and population filters; duplicate selected "
            "keys stop the build.\nNo averaging of repeated source keys, no interpolation, no "
            "missing-to-zero fill.\nRent affordability index is a change indicator, not an affordability"
            " league table.\nConsents are intentions to build; a single rent snapshot does not establish"
            " a trend."
        ),
        (735, 620, 665, 180),
        14,
    )
    write(
        DEST / "validation_reference.json",
        {
            "source": payload["source"],
            "quality": payload["quality"],
            "selectedRows": len(facts),
            "latestSeries": [{"id": r[0], "date": r[5], "coverage": r[6]} for r in indicators],
            "wellington": {
                item["id"]: [row for row in item["values"] if row[1] == "TA" and row[2] == "47"][-1] for item in series
            },
            "status": "Generated project; Desktop refresh, calculation and visual validation required",
        },
    )
    print(f"Built {DEST}: {len(facts)} exact observations, {len(tables)} tables, {len(measures)} measures, 3 pages")


if __name__ == "__main__":
    build()
