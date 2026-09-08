"""Compatibility wrapper for an optional archived Quarto render."""
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
if __name__ == '__main__':
    subprocess.run([sys.executable, str(ROOT/'analysis/package_classroom.py'),
                    '--output', str(ROOT/'site/resources/causal-shap-classroom.zip')], check=True)
