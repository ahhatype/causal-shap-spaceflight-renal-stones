"""Build the offline teaching companion independently of Quarto or Pages."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import argparse

ROOT = Path(__file__).resolve().parents[1]
FILES = ('README.md', 'educator-guide.md', 'worksheet.md', 'lab.py', 'index.html', 'animation.html')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'dist/causal-shap-classroom.zip')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sources = {name: ROOT/'docs/classroom'/name for name in FILES}
    sources['LICENSE'] = ROOT/'LICENSE'
    with ZipFile(args.output, 'w', compression=ZIP_DEFLATED) as archive:
        for name, source in sources.items():
            info = ZipInfo(name, date_time=(2026, 9, 7, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, source.read_bytes())
    print(f'Packaged {len(sources)} files into {args.output}')


if __name__ == '__main__':
    main()
