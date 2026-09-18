"""Build the current LaTeX playbook and refresh its compatibility PDF link.

Does not regenerate article text, diagrams, or manuscript files.
"""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / 'docs' / 'playbook' / 'study-guide-latex'


def main():
    subprocess.run([sys.executable, str(GUIDE / 'build.py')], check=True)
    target = GUIDE.parent / 'study-guide.pdf'
    shutil.copyfile(GUIDE / 'main.pdf', target)
    print(f'Refreshed {target}')


if __name__ == '__main__':
    main()
