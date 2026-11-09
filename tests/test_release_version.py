import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

from scripts.check_release_version import check_version


class ReleaseVersionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.package = Path(self.temp.name) / "package.json"
        self.archive = Path(self.temp.name) / "plugin.zip"
        self.write_package("0.45.1")

    def write_package(self, version):
        self.package.write_text(json.dumps({"version": version}), encoding="utf-8")

    def write_zip(self, version, path="decky-localsend/package.json"):
        with ZipFile(self.archive, "w") as zipped:
            zipped.writestr(path, json.dumps({"version": version}))

    def test_branch_and_pr_builds_need_no_tag(self):
        self.assertEqual(check_version(self.package), "0.45.1")
        self.assertEqual(check_version(self.package, ""), "0.45.1")

    def test_matching_tag_and_zip(self):
        self.write_zip("0.45.1")
        self.assertEqual(check_version(self.package, "v0.45.1", self.archive), "0.45.1")

    def test_historical_tag_and_wrong_future_tag_are_rejected(self):
        for tag in ("v0.45", "v0.4.6", "v0.45.2", "0.45.1", "V0.45.1"):
            with self.subTest(tag=tag), self.assertRaisesRegex(ValueError, "release tag"):
                check_version(self.package, tag)

    def test_versions_that_break_legacy_upgrade_path_are_rejected(self):
        for version in ("0.4.5", "0.4.6", "0.44.99", "0.45.0"):
            self.write_package(version)
            with self.subTest(version=version), self.assertRaisesRegex(ValueError, "newer than"):
                check_version(self.package, f"v{version}")

    def test_future_versions_use_numeric_ordering(self):
        for version in ("0.45.2", "0.46.0", "0.100.0", "1.0.0"):
            self.write_package(version)
            with self.subTest(version=version):
                self.assertEqual(check_version(self.package, f"v{version}"), version)

    def test_noncanonical_or_missing_versions_are_rejected(self):
        for version in ("0.45", "v0.45.1", "00.45.1", "0.045.1", "0.45.01", "0.45.1\n", "0.45.1-rc.1", "0.45.1+build", None, 0.45):
            self.write_package(version)
            with self.subTest(version=version), self.assertRaises(ValueError):
                check_version(self.package)
        for content in ("{}", "[]", "invalid json"):
            self.package.write_text(content, encoding="utf-8")
            with self.subTest(content=content), self.assertRaises(ValueError):
                check_version(self.package)

    def test_zip_must_match_source_even_without_a_tag(self):
        for version in ("0.4.5", "0.45.2"):
            self.write_zip(version)
            with self.subTest(version=version), self.assertRaisesRegex(ValueError, "differs from source"):
                check_version(self.package, archive=self.archive)

    def test_dependency_manifests_are_ignored(self):
        self.write_zip("0.45.1")
        with ZipFile(self.archive, "a") as zipped:
            zipped.writestr("decky-localsend/node_modules/example/package.json", '{"version":"1.0.0"}')
        self.assertEqual(check_version(self.package, "v0.45.1", self.archive), "0.45.1")

    def test_missing_or_ambiguous_plugin_manifest_is_rejected(self):
        for path in ("package.json", "plugin/node_modules/example/package.json", "../package.json"):
            self.write_zip("0.45.1", path)
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "exactly one"):
                check_version(self.package, archive=self.archive)
        self.write_zip("0.45.1")
        with ZipFile(self.archive, "a") as zipped:
            zipped.writestr("other-plugin/package.json", '{"version":"0.45.1"}')
        with self.assertRaisesRegex(ValueError, "exactly one"):
            check_version(self.package, archive=self.archive)

    def test_cli_exit_status_blocks_bad_releases(self):
        script = Path(__file__).resolve().parents[1] / "scripts/check_release_version.py"
        for tag, expected_code in (("v0.45.1", 0), ("v0.45", 1)):
            result = subprocess.run(
                [sys.executable, str(script), "--package-json", str(self.package), "--tag", tag],
                capture_output=True, text=True,
            )
            with self.subTest(tag=tag):
                self.assertEqual(result.returncode, expected_code, result.stdout + result.stderr)
        self.archive.write_bytes(b"not a zip")
        result = subprocess.run(
            [sys.executable, str(script), "--package-json", str(self.package), "--archive", str(self.archive)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Version check failed", result.stderr)


if __name__ == "__main__":
    unittest.main()
