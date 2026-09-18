"""Build the explanatory supplement in its self-contained working folder.

Does not regenerate article text, diagrams, or manuscript files.
"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / 'docs' / 'playbook' / 'supplementary-information'


def main():
    subprocess.run([sys.executable, str(GUIDE / 'build.py')], check=True)
    print(f'Built {GUIDE / "main.pdf"}')


if __name__ == '__main__':
    main()
