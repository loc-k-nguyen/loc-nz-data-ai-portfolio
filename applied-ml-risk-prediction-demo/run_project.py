"""Run the applied ML demo workflow end to end."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
STEPS = [
    ("Prepare data", PROJECT_ROOT / "src" / "prepare_data.py"),
    ("Train model", PROJECT_ROOT / "src" / "train_model.py"),
    ("Evaluate model", PROJECT_ROOT / "src" / "evaluate_model.py"),
    ("Run batch predictions", PROJECT_ROOT / "src" / "predict.py"),
]


def main() -> None:
    """Run each workflow step and stop on first failure."""
    for label, script_path in STEPS:
        print(f"\n=== {label} ===")
        result = subprocess.run([sys.executable, str(script_path)], cwd=PROJECT_ROOT.parent, check=False)
        if result.returncode != 0:
            raise SystemExit(f"Step failed: {label}")
    print("\nWorkflow completed successfully.")


if __name__ == "__main__":
    main()

