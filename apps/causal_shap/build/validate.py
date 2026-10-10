"""Release gate for the Python bundle pipeline (mirrors validate_outputs.R).

Asserts three invariants: the frozen analysis/output record is unchanged (via a
committed baseline hash manifest), the bundle manifest resolves with no missing
files, and every expected stage artifact exists. The record is the set of files
git tracks under analysis/output; local pilots that .gitignore keeps out of the
public record (battery runs, detector outputs) are not part of it, so a checkout
with those folders present validates the same way CI does. Outside a git
checkout the whole tree is hashed. Text-file newlines are normalized to LF
before hashing so Git's Windows checkout conversion is not misclassified as a
scientific-output change; binary files remain byte-exact.

``freeze-baseline`` rewrites the manifest from the current record and prints
what changed, for the reviewed commit that adds or revises a checked output.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from ..bundles import BundleRepository
from .common import APP_DIR, PROJECT_DIR, print_status

ANALYSIS_OUTPUT = PROJECT_DIR / "analysis" / "output"
BASELINE_PATH = APP_DIR / "bundles" / "analysis_output_baseline_hashes.json"
MANIFEST_PATH = APP_DIR / "bundles" / "manifest.json"

EXPECTED_STAGE_ARTIFACTS = {
    "toy_chain_fork_collider": ["discovery.json", "complexity.json", "attribution.csv"],
    "layered_ladder": ["discovery.json", "complexity.json", "attribution.csv"],
    "acic_proxy_stress_test": ["discovery.json", "complexity.json"],
    "nasa_renal_clean_v3": ["complexity.json", "validation_scorecard.csv", "validation_estimands.csv"],
}

TEXT_OUTPUT_SUFFIXES = frozenset(
    {".csv", ".json", ".md", ".r", ".txt", ".yaml", ".yml"}
)


def _content_hash(path: Path) -> str:
    """Hash text with canonical LF newlines and binary output byte-for-byte."""
    content = path.read_bytes()
    if path.suffix.lower() in TEXT_OUTPUT_SUFFIXES:
        content = content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(content).hexdigest()


def _tracked_files(root: Path) -> list[Path] | None:
    """The files git tracks under ``root``, or None when ``root`` is not in a checkout."""
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--", "."],
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return [root / name for name in completed.stdout.decode("utf-8").split("\0") if name]


def _hash_tree(root: Path) -> dict[str, str]:
    tracked = _tracked_files(root)
    paths = tracked if tracked is not None else list(root.rglob("*"))
    hashes: dict[str, str] = {}
    for path in sorted(paths):
        if path.is_file():
            relative_name = path.relative_to(root).as_posix()
            hashes[relative_name] = _content_hash(path)
    return hashes


def _compare(baseline: dict[str, str], current: dict[str, str]) -> list[str]:
    """Describe every difference between the baseline manifest and the current record."""
    differences: list[str] = []
    for name in sorted(set(baseline) - set(current)):
        differences.append(f"analysis/output: file removed: {name}")
    for name in sorted(set(current) - set(baseline)):
        differences.append(f"analysis/output: file added: {name}")
    for name in sorted(set(baseline) & set(current)):
        if baseline[name] != current[name]:
            differences.append(f"analysis/output: file changed: {name}")
    return differences


def _read_baseline() -> dict[str, str]:
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


def _write_baseline(current: dict[str, str]) -> None:
    BASELINE_PATH.write_text(json.dumps(current, indent=2, sort_keys=True), encoding="utf-8")


def _check_frozen_output(errors: list[str]) -> None:
    current = _hash_tree(ANALYSIS_OUTPUT)
    if not BASELINE_PATH.exists():
        _write_baseline(current)
        print(f"  baseline created: {len(current)} files under analysis/output")
        return
    errors.extend(_compare(_read_baseline(), current))


def write_baseline() -> None:
    """Refresh the baseline from the current record and report what changed."""
    current = _hash_tree(ANALYSIS_OUTPUT)
    previous = _read_baseline() if BASELINE_PATH.exists() else {}
    changes = _compare(previous, current)
    _write_baseline(current)
    print_status(
        {
            "status": "OK",
            "baseline": BASELINE_PATH.relative_to(PROJECT_DIR).as_posix(),
            "files": len(current),
            "changes": changes,
        }
    )


def validate_bundles() -> None:
    errors: list[str] = []
    _check_frozen_output(errors)

    errors.extend(BundleRepository(APP_DIR, MANIFEST_PATH).validate())

    for bundle_id, artifacts in EXPECTED_STAGE_ARTIFACTS.items():
        stage_dir = APP_DIR / "bundles" / bundle_id / "stages"
        for artifact in artifacts:
            if not (stage_dir / artifact).exists():
                errors.append(f"{bundle_id}: missing stage artifact {artifact}")

    if errors:
        print_status({"status": "FAIL", "errors": errors})
        raise SystemExit(1)
    print_status({"status": "OK", "checked": sorted(EXPECTED_STAGE_ARTIFACTS)})
