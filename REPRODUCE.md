# Reproduce the portfolio

Use Python 3.11. The interactive housing explorer can be rebuilt using the Python standard library alone:

```bash
python scripts/build_housing_dashboard.py
python scripts/build_housing_dashboard.py --check
python -m http.server 8842 --directory docs
```

Open `http://localhost:8842`. The preserved cleaned HUD CSV is included. The build selects five measures with parameterized SQLite queries, validates numeric values and unique reporting keys, then produces `docs/data.json`. Its input checksum normalizes CRLF to LF so Windows and Linux produce identical output. It does not download current data or change the source vintage.

The `Rebuild housing dashboard` GitHub Actions workflow runs on pushes and pull requests and can also be started manually. It checks reproducibility, tests unit/date/duplicate handling, and uploads the static site as a workflow artifact. GitHub Pages serves the committed `docs/` folder.

## Original workbook pipeline

The original April 2026 workbook is not redistributed here. If you hold that exact extract, place it in the documented `data/raw/` folder, install the project requirements, then run:

```bash
python -m pip install -r nz-open-data-insights-dashboard/requirements.txt
python nz-open-data-insights-dashboard/src/clean_data.py
python nz-open-data-insights-dashboard/src/build_sqlite_database.py
python nz-open-data-insights-dashboard/src/run_analysis_exports.py
python scripts/build_housing_dashboard.py
```

A new source vintage requires a deliberate metadata and interpretation review; the dashboard build refuses an unrecognized source filename. Do not rename a newer workbook to impersonate the preserved April extract. The current source page may serve a newer workbook.

## Other demonstrations

The applied ML project uses a public benchmark and documents its held-out evaluation. The scientific ML project is a separate synthetic demonstration, with no private PhD data. See each project's README for dependencies and commands. Rebuilding the housing explorer does not train either model.

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests/test_housing_dashboard.py -q
python -m ruff check .
```

The full existing test suite additionally needs the other projects' scientific dependencies, including CPU PyTorch.
