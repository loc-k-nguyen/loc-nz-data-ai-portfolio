"""Lightweight portfolio health checks before publishing to GitHub."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = [
    "README.md",
    "REPRODUCE.md",
    "DATA_SOURCES.md",
    "requirements-dev.txt",
    "pyproject.toml",
    "docs/recruiter_navigation_guide.md",
    "docs/index.html",
    "docs/data.json",
    "nz-open-data-insights-dashboard/README.md",
    "nz-open-data-insights-dashboard/data/README.md",
    "nz-open-data-insights-dashboard/outputs/README.md",
    "applied-ml-risk-prediction-demo/README.md",
    "applied-ml-risk-prediction-demo/data/README.md",
    "applied-ml-risk-prediction-demo/outputs/README.md",
    "scientific-ml-research-showcase/README.md",
    "scientific-ml-research-showcase/data/README.md",
    "scientific-ml-research-showcase/outputs/README.md",
]


EXPECTED_OUTPUTS = [
    "nz-open-data-insights-dashboard/data/processed/local_housing_indicators_clean.csv",
    "nz-open-data-insights-dashboard/outputs/dashboard_ready_housing_indicators.csv",
    "nz-open-data-insights-dashboard/outputs/preliminary_findings.md",
    "applied-ml-risk-prediction-demo/outputs/evaluation_metrics.csv",
    "applied-ml-risk-prediction-demo/outputs/confusion_matrix.png",
    "applied-ml-risk-prediction-demo/outputs/roc_curve.png",
    "applied-ml-risk-prediction-demo/reports/model_card.md",
    "scientific-ml-research-showcase/outputs/metrics.csv",
    "scientific-ml-research-showcase/outputs/prediction_examples.png",
    "scientific-ml-research-showcase/outputs/error_map_examples.png",
]


EXPECTED_SCREENSHOTS = [
    "nz-open-data-insights-dashboard/screenshots/executive_summary.png",
    "nz-open-data-insights-dashboard/screenshots/territorial_authority_comparison.png",
    "nz-open-data-insights-dashboard/screenshots/indicator_trend.png",
    "nz-open-data-insights-dashboard/screenshots/data_quality_methodology.png",
]


FORBIDDEN_TEXT_PATTERNS = [
    (re.compile(r"E:\\\\|C:\\\\", re.IGNORECASE), "absolute Windows path"),
    (
        re.compile(r"least affordable|most unaffordable|policy failure", re.IGNORECASE),
        "overclaim about housing affordability",
    ),
]

MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def run_git_ls_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def check_exists(paths: list[str]) -> tuple[list[str], list[str]]:
    present = []
    missing = []
    for relative_path in paths:
        if (ROOT / relative_path).exists():
            present.append(relative_path)
        else:
            missing.append(relative_path)
    return present, missing


def scan_markdown() -> list[str]:
    warnings = []
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        relative = path.relative_to(ROOT).as_posix()
        for line_number, line in enumerate(text.splitlines(), start=1):
            lower_line = line.lower()
            stripped_line = line.strip()
            if any(
                phrase in lower_line
                for phrase in ("avoid", "unsafe", "do not", "not use", "should not")
                + ("does not", "not a", "unless")
            ):
                continue
            if stripped_line.startswith(('- "', '> "')):
                continue
            for pattern, label in FORBIDDEN_TEXT_PATTERNS:
                if pattern.search(line):
                    warnings.append(f"{relative}:{line_number}: contains {label}")
    return warnings


def check_markdown_links() -> list[str]:
    warnings = []
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in MARKDOWN_LINK_RE.finditer(text):
            target = match.group(1).strip()
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            if "://" in target:
                continue
            target_without_anchor = target.split("#", 1)[0]
            target_without_anchor = target_without_anchor.replace("%20", " ")
            linked_path = (path.parent / target_without_anchor).resolve()
            try:
                linked_path.relative_to(ROOT)
            except ValueError:
                warnings.append(
                    f"{path.relative_to(ROOT).as_posix()}: link leaves repo: {target}"
                )
                continue
            if not linked_path.exists():
                warnings.append(
                    f"{path.relative_to(ROOT).as_posix()}: missing linked file: {target}"
                )
    return warnings


def check_tracked_risky_files(tracked_files: list[str]) -> list[str]:
    warnings = []
    risky_suffixes = (".sqlite", ".db", ".env")
    for tracked in tracked_files:
        lower = tracked.lower()
        if lower.endswith(risky_suffixes):
            warnings.append(f"tracked risky file: {tracked}")
        if lower.startswith("nz-open-data-insights-dashboard/data/raw/") and not lower.endswith("readme.md"):
            warnings.append(f"tracked raw HUD data file: {tracked}")
    return warnings


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    _, missing_required = check_exists(REQUIRED_FILES)
    _, missing_outputs = check_exists(EXPECTED_OUTPUTS)
    _, missing_screenshots = check_exists(EXPECTED_SCREENSHOTS)

    errors.extend(f"missing required file: {path}" for path in missing_required)
    errors.extend(f"missing expected output: {path}" for path in missing_outputs)
    warnings.extend(f"Power BI screenshot not present yet: {path}" for path in missing_screenshots)

    try:
        tracked_files = run_git_ls_files()
    except subprocess.CalledProcessError as exc:
        errors.append(f"git ls-files failed: {exc}")
        tracked_files = []

    warnings.extend(check_tracked_risky_files(tracked_files))
    warnings.extend(scan_markdown())
    warnings.extend(check_markdown_links())

    print("Portfolio health check")
    print("======================")
    print(f"Repository: {ROOT}")
    print(f"Required files checked: {len(REQUIRED_FILES)}")
    print(f"Expected outputs checked: {len(EXPECTED_OUTPUTS)}")
    print(f"Tracked files checked: {len(tracked_files)}")
    print()

    if errors:
        print("FAIL")
        for item in errors:
            print(f"ERROR: {item}")
    else:
        print("PASS: required files and expected outputs are present.")

    if warnings:
        print()
        print("Warnings")
        for item in warnings:
            print(f"WARN: {item}")
    else:
        print("No warnings.")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
