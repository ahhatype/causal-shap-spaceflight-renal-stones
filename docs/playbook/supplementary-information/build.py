"""Compile the editable article; never regenerate or overwrite its TeX source."""
from pathlib import Path
import os
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / '.build'


def main():
    BUILD.mkdir(exist_ok=True)
    env = os.environ.copy()
    env['BIBINPUTS'] = str(ROOT) + os.pathsep + env.get('BIBINPUTS', '')
    latex = ['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
             f'-output-directory={BUILD}', 'main.tex']
    commands = [(latex, ROOT), (['bibtex', 'main'], BUILD),
                (latex, ROOT), (latex, ROOT)]
    with (BUILD / 'build-output.txt').open('w', encoding='utf-8') as log:
        for command, cwd in commands:
            result = subprocess.run(command, cwd=cwd, env=env,
                                    stdout=log, stderr=subprocess.STDOUT)
            if result.returncode:
                raise SystemExit(f'Build failed: see {BUILD / "build-output.txt"}')
    log = (BUILD / 'main.log').read_text(encoding='utf-8', errors='replace')
    warnings = re.findall(r'(?:LaTeX|Package \w+) Warning[^\n]*|(?:Overfull|Underfull)[^\n]*', log)
    if warnings:
        print('\n'.join(warnings))
    shutil.copyfile(BUILD / 'main.pdf', ROOT / 'main.pdf')
    print(f'Built {ROOT / "main.pdf"}')


if __name__ == '__main__':
    main()
