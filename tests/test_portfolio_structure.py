from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_root_docs_exist() -> None:
    required = [
        "README.md",
        "REPRODUCE.md",
        "DATA_SOURCES.md",
        "docs/index.html",
        "docs/data.json",
        "docs/recruiter_navigation_guide.md",
    ]
    for relative_path in required:
        assert (ROOT / relative_path).exists(), relative_path


def test_project_1_key_files_exist() -> None:
    project = ROOT / "nz-open-data-insights-dashboard"
    required = [
        "README.md",
        "src/clean_data.py",
        "src/build_sqlite_database.py",
        "src/run_analysis_exports.py",
        "sql/02_data_quality_checks.sql",
        "sql/03_analysis_queries.sql",
        "powerbi/build_assets/dashboard_page_spec.md",
        "powerbi/build_assets/powerbi_measures.dax",
        "outputs/analysis_summary.md",
        "outputs/indicator_validation_notes.md",
    ]
    for relative_path in required:
        assert (project / relative_path).exists(), relative_path


def test_project_2_key_files_exist() -> None:
    project = ROOT / "applied-ml-risk-prediction-demo"
    required = [
        "README.md",
        "run_project.py",
        "src/prepare_data.py",
        "src/train_model.py",
        "src/evaluate_model.py",
        "src/predict.py",
        "reports/model_card.md",
        "reports/evaluation_report.md",
        "outputs/evaluation_metrics.csv",
        "outputs/model_validation_notes.md",
        "models/model_metadata.json",
    ]
    for relative_path in required:
        assert (project / relative_path).exists(), relative_path


def test_project_3_marked_as_planned() -> None:
    readme = ROOT / "scientific-ml-research-showcase" / "README.md"
    text = readme.read_text(encoding="utf-8")
    assert "synthetic demonstration" in text
    assert "No private PhD data is used" in text
