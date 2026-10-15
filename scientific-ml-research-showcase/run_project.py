"""Run the scientific ML showcase workflow."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
STEPS = [
    ("Train synthetic surrogate", PROJECT_ROOT / "src" / "train.py"),
    ("Evaluate saved surrogate", PROJECT_ROOT / "src" / "evaluate.py"),
]


def main() -> None:
    for label, script_path in STEPS:
        print(f"\n=== {label} ===")
        result = subprocess.run([sys.executable, str(script_path)], cwd=PROJECT_ROOT, check=False)
        if result.returncode != 0:
            raise SystemExit(f"Step failed: {label}")
    print("\nScientific ML showcase workflow completed successfully.")


if __name__ == "__main__":
    main()

