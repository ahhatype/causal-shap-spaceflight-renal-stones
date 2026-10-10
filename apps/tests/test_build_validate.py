"""Cross-platform checks for the frozen-output release gate."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from causal_shap.build.validate import _compare, _content_hash, _hash_tree


class FrozenOutputHashTests(unittest.TestCase):
    def test_hash_tree_uses_manifest_style_posix_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            nested = root / "nested"
            nested.mkdir()
            artifact = nested / "artifact.txt"
            artifact.write_bytes(b"first\r\nsecond\r\n")

            hashes = _hash_tree(root)

        self.assertEqual(list(hashes), ["nested/artifact.txt"])
        self.assertEqual(
            hashes["nested/artifact.txt"],
            hashlib.sha256(b"first\nsecond\n").hexdigest(),
        )

    @unittest.skipUnless(shutil.which("git"), "git is needed to enumerate tracked files")
    def test_hash_tree_inside_a_checkout_covers_tracked_files_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "frozen.csv").write_text("a,b\n", encoding="utf-8")
            (root / "local_pilot").mkdir()
            (root / "local_pilot" / "stage_results.json").write_text("{}\n", encoding="utf-8")
            (root / "scratch.csv").write_text("x\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "frozen.csv"], check=True)

            hashes = _hash_tree(root)

        self.assertEqual(list(hashes), ["frozen.csv"])

    def test_binary_hash_preserves_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact = Path(temporary_directory) / "artifact.png"
            content = b"binary\r\npayload\x00"
            artifact.write_bytes(content)

            digest = _content_hash(artifact)

        self.assertEqual(digest, hashlib.sha256(content).hexdigest())

    def test_compare_reports_removed_added_and_changed_files(self) -> None:
        baseline = {"a.csv": "1", "b.csv": "2", "c.csv": "3"}
        current = {"b.csv": "2", "c.csv": "revised", "d.csv": "4"}

        self.assertEqual(
            _compare(baseline, current),
            [
                "analysis/output: file removed: a.csv",
                "analysis/output: file added: d.csv",
                "analysis/output: file changed: c.csv",
            ],
        )
        self.assertEqual(_compare(baseline, dict(baseline)), [])


if __name__ == "__main__":
    unittest.main()
