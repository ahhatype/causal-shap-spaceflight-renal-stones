"""Compile the editable article; never regenerate or overwrite its TeX source."""
from pathlib import Path
import argparse
import os
import re
import shutil
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / '.build'


def export_overleaf():
    """Export a full root article, with assets below it; never edit the source."""
    source = (ROOT / 'main.tex').read_text(encoding='utf-8')
    local_path = r'\providecommand{\SupplementRoot}{}'
    remote_path = r'\providecommand{\SupplementRoot}{supplementary-information/}'
    if source.count(local_path) != 1:
        raise ValueError('Expected one local SupplementRoot definition; review export paths.')
    article = source.replace(local_path, remote_path, 1)
    output = BUILD / 'overleaf-supplement.zip'
    with ZipFile(output, 'w', compression=ZIP_DEFLATED) as archive:
        archive.writestr('supplement.tex', article)
        archive.write(ROOT / 'references.bib', 'supplementary-information/references.bib')
        for folder, suffixes in [('figures', {'.pdf'}), ('diagrams', {'.drawio', '.md'})]:
            for path in sorted((ROOT / folder).iterdir()):
                if path.is_file() and path.suffix in suffixes:
                    archive.write(path, f'supplementary-information/{folder}/{path.name}')
    print(f'Exported {output}; edit the canonical source, not the generated ZIP.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export-overleaf', action='store_true',
                        help='also export a complete root supplement.tex and supporting files')
    args = parser.parse_args()
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
    if args.export_overleaf:
        export_overleaf()


if __name__ == '__main__':
    main()
