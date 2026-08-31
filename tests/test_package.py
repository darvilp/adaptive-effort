from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "adaptive-effort"


class PackageTests(unittest.TestCase):
    def test_source_package_checks_do_not_write_plugin_bytecode(self) -> None:
        package_path = ROOT / "scripts/package.py"
        spec = importlib.util.spec_from_file_location("adaptive_package_checks", package_path)
        package = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(package)

        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            (fixture / "review_module.py").write_text("VALUE = 1\n")
            result = package.run_check_commands(
                [[sys.executable, "-c", "import review_module"]], cwd=fixture,
            )
            self.assertEqual(result, 0)
            self.assertFalse((fixture / "__pycache__").exists())

    def test_package_contains_canonical_design_without_local_inputs(self) -> None:
        package_path = ROOT / "scripts/package.py"
        spec = importlib.util.spec_from_file_location("adaptive_package", package_path)
        package = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(package)

        packaged = {path.relative_to(ROOT).as_posix() for path in package.files_to_package()}
        self.assertIn("docs/design.md", packaged)
        self.assertNotIn("Adaptive Effort for Superpowers - Codex — Plugin Design.md", packaged)
        self.assertNotIn("adaptive-effort-plugin-0.1.0.zip", packaged)
        self.assertFalse(any("Zone.Identifier" in path for path in packaged))

    def test_marketplace_points_to_plugin(self) -> None:
        data = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
        entry = data["plugins"][0]
        self.assertEqual(data["name"], "adaptive-effort")
        self.assertEqual(entry["name"], "adaptive-effort")
        self.assertEqual(entry["source"], {"source": "local", "path": "./plugins/adaptive-effort"})
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertIn(entry["policy"]["authentication"], {"ON_INSTALL", "ON_USE"})

    def test_manifest_is_skills_only_and_paths_exist(self) -> None:
        manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
        self.assertEqual(manifest["name"], "adaptive-effort")
        self.assertEqual(manifest["version"], "0.1.2")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertNotIn("agents", manifest)
        for key in ("composerIcon", "logo"):
            rel = manifest["interface"][key].removeprefix("./")
            self.assertTrue((PLUGIN / rel).exists(), rel)

    def test_single_primary_skill(self) -> None:
        skill_files = list((PLUGIN / "skills").glob("*/SKILL.md"))
        self.assertEqual([p.parent.name for p in skill_files], ["adaptive-effort"])

    def test_skill_keeps_parent_and_inherits_child_model(self) -> None:
        text = (PLUGIN / "skills/adaptive-effort/SKILL.md").read_text()
        self.assertIn("Do not alter the parent model", text)
        self.assertIn("omit `model`", text)
        self.assertIn('fork_turns="none"', text)

    def test_skill_agent_metadata_allows_implicit_invocation(self) -> None:
        text = (PLUGIN / "skills/adaptive-effort/agents/openai.yaml").read_text()
        self.assertIn("display_name:", text)
        self.assertIn("allow_implicit_invocation: true", text)
        self.assertIn("products: [CODEX]", text)
        self.assertIn("$adaptive-effort", text)

    def test_internal_manifest_when_present(self) -> None:
        manifest = ROOT / "MANIFEST.sha256"
        if not manifest.exists():
            self.skipTest("manifest is generated during packaging")

        import hashlib

        listed: set[str] = set()
        for line in manifest.read_text().splitlines():
            digest, rel = line.split("  ", 1)
            listed.add(rel)
            self.assertEqual(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest(), digest, rel)

        package_path = ROOT / "scripts/package.py"
        spec = importlib.util.spec_from_file_location("adaptive_package_manifest", package_path)
        package = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(package)
        expected = {
            path.relative_to(ROOT).as_posix()
            for path in package.files_to_package()
            if path != manifest
        }
        self.assertEqual(listed, expected)

    def test_no_custom_agent_tomls_are_shipped(self) -> None:
        self.assertEqual(list(PLUGIN.rglob("*.toml")), [])

    def test_submission_package_is_deterministic_plugin_only_snapshot(self) -> None:
        package_path = ROOT / "scripts/package_submission.py"
        spec = importlib.util.spec_from_file_location("submission_package", package_path)
        package = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(package)

        tracked_before = {path: path.read_bytes() for path in PLUGIN.rglob("*") if path.is_file()}
        with tempfile.TemporaryDirectory() as fixture, tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            plugin = Path(fixture) / "adaptive-effort"
            shutil.copytree(PLUGIN, plugin, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            first_zip = Path(first) / "submission.zip"
            second_zip = Path(second) / "submission.zip"
            package.build(first_zip, plugin)
            package.build(second_zip, plugin)
            self.assertEqual(first_zip.read_bytes(), second_zip.read_bytes())
            verifier_path = ROOT / "scripts/verify_submission.py"
            verifier_spec = importlib.util.spec_from_file_location("submission_verify_built", verifier_path)
            verifier = importlib.util.module_from_spec(verifier_spec)
            assert verifier_spec and verifier_spec.loader
            verifier_spec.loader.exec_module(verifier)
            verifier.verify(first_zip, plugin)
            with zipfile.ZipFile(first_zip) as archive:
                names = archive.namelist()
                self.assertTrue(names)
                self.assertEqual(names, sorted(names))
                self.assertTrue(all(name.startswith("adaptive-effort/") for name in names))
                self.assertIn("adaptive-effort/.codex-plugin/plugin.json", names)
                self.assertFalse(any("__pycache__" in name or name.endswith(".toml") for name in names))
            self.assertTrue(first_zip.with_suffix(".zip.sha256").is_file())
        self.assertEqual(tracked_before, {path: path.read_bytes() for path in PLUGIN.rglob("*") if path.is_file()})

    def test_submission_package_rejects_symlinks(self) -> None:
        package_path = ROOT / "scripts/package_submission.py"
        spec = importlib.util.spec_from_file_location("submission_package_symlink", package_path)
        package = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(package)

        with tempfile.TemporaryDirectory() as directory:
            plugin = Path(directory) / "adaptive-effort"
            plugin.mkdir()
            (plugin / "escape").symlink_to(ROOT / "README.md")
            with self.assertRaisesRegex(ValueError, "symlink"):
                package.collect_files(plugin)

    def test_submission_package_rejects_every_forbidden_surface(self) -> None:
        package_path = ROOT / "scripts/package_submission.py"
        spec = importlib.util.spec_from_file_location("submission_package_forbidden", package_path)
        package = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(package)

        forbidden = [
            "__pycache__/cached.pyc", ".pytest_cache/state", "archive.zip", "digest.sha256",
            "download:Zone.Identifier", "apps/example.json", "service.mcp.json",
            "screenshots/review.png", "hooks/preflight.py", "agents/custom.toml",
        ]
        for relative in forbidden:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                plugin = Path(directory) / "adaptive-effort"
                target = plugin / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("forbidden")
                with self.assertRaisesRegex(ValueError, "forbidden|unsafe|unreviewed"):
                    package.collect_files(plugin)

    def test_submission_package_rejects_every_unreviewed_file_and_directory(self) -> None:
        package_path = ROOT / "scripts/package_submission.py"
        spec = importlib.util.spec_from_file_location("submission_package_allowlist", package_path)
        package = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(package)

        unreviewed = [
            ".env",
            "notes.txt",
            ".mypy_cache/state.json",
            ".ruff_cache/state.json",
            ".hg/store/data",
            ".svn/entries",
            "empty-directory",
        ]
        for relative in unreviewed:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                plugin = Path(directory) / "adaptive-effort"
                shutil.copytree(PLUGIN, plugin, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
                target = plugin / relative
                if relative == "empty-directory":
                    target.mkdir()
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text("unreviewed")
                with self.assertRaisesRegex(ValueError, "unreviewed submission path"):
                    package.collect_files(plugin)

    def test_submission_package_rejects_unsafe_or_ambiguous_names(self) -> None:
        package_path = ROOT / "scripts/package_submission.py"
        spec = importlib.util.spec_from_file_location("submission_package_names", package_path)
        package = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(package)

        unsafe_names = [
            "back\\slash",
            "control\nname",
            "trailing-dot.",
            "trailing-space ",
            "colon:name",
            "CON",
            "e\N{COMBINING ACUTE ACCENT}",
        ]
        for name in unsafe_names:
            with self.subTest(name=repr(name)), tempfile.TemporaryDirectory() as directory:
                plugin = Path(directory) / "adaptive-effort"
                shutil.copytree(PLUGIN, plugin, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
                (plugin / name).write_text("unsafe")
                with self.assertRaisesRegex(ValueError, "unsafe or ambiguous path"):
                    package.collect_files(plugin)

    def test_submission_package_rejects_empty_forbidden_directories(self) -> None:
        package_path = ROOT / "scripts/package_submission.py"
        spec = importlib.util.spec_from_file_location("submission_package_empty_forbidden", package_path)
        package = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(package)

        for relative in ("apps", ".git", "__pycache__", "screenshots", "hooks"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                plugin = Path(directory) / "adaptive-effort"
                (plugin / relative).mkdir(parents=True)
                with self.assertRaisesRegex(ValueError, "forbidden.*" + relative.replace(".", r"\.")):
                    package.collect_files(plugin)

    def test_submission_package_rejects_special_files_clearly(self) -> None:
        package_path = ROOT / "scripts/package_submission.py"
        spec = importlib.util.spec_from_file_location("submission_package_special", package_path)
        package = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(package)

        with tempfile.TemporaryDirectory() as directory:
            plugin = Path(directory) / "adaptive-effort"
            plugin.mkdir()
            os.mkfifo(plugin / "named-pipe")
            with self.assertRaisesRegex(ValueError, "special file.*named-pipe"):
                package.collect_files(plugin)

    def test_submission_archive_verifier_rejects_tampered_metadata_and_membership(self) -> None:
        verifier_path = ROOT / "scripts/verify_submission.py"
        spec = importlib.util.spec_from_file_location("submission_verify", verifier_path)
        verifier = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(verifier)

        with tempfile.TemporaryDirectory() as directory:
            plugin = Path(directory) / "adaptive-effort"
            shutil.copytree(PLUGIN, plugin, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            archive_path = Path(directory) / "tampered.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                info = zipfile.ZipInfo("adaptive-effort/unreviewed.txt", date_time=(2025, 1, 1, 0, 0, 0))
                info.external_attr = 0o777 << 16
                archive.writestr(info, b"unreviewed")
            with self.assertRaisesRegex(ValueError, "membership|timestamp|mode"):
                verifier.verify(archive_path, plugin)

    def test_submission_archive_verifier_rejects_extra_member_present_in_source(self) -> None:
        package_path = ROOT / "scripts/package_submission.py"
        package_spec = importlib.util.spec_from_file_location("submission_package_extra", package_path)
        package = importlib.util.module_from_spec(package_spec)
        assert package_spec and package_spec.loader
        package_spec.loader.exec_module(package)

        verifier_path = ROOT / "scripts/verify_submission.py"
        verifier_spec = importlib.util.spec_from_file_location("submission_verify_extra", verifier_path)
        verifier = importlib.util.module_from_spec(verifier_spec)
        assert verifier_spec and verifier_spec.loader
        verifier_spec.loader.exec_module(verifier)

        with tempfile.TemporaryDirectory() as directory:
            plugin = Path(directory) / "adaptive-effort"
            shutil.copytree(PLUGIN, plugin, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            archive_path = Path(directory) / "submission.zip"
            package.build(archive_path, plugin)

            unwanted = plugin / "unreviewed.txt"
            unwanted.write_text("unreviewed")
            with zipfile.ZipFile(archive_path, "a", compression=zipfile.ZIP_DEFLATED) as archive:
                info = zipfile.ZipInfo(
                    "adaptive-effort/unreviewed.txt",
                    date_time=package.FIXED_TIMESTAMP,
                )
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = (0o100000 | 0o644) << 16
                archive.writestr(info, unwanted.read_bytes())

            with self.assertRaisesRegex(ValueError, "membership"):
                verifier.verify(archive_path, plugin)


if __name__ == "__main__":
    unittest.main()
