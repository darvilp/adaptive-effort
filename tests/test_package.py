from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "adaptive-effort"


class PackageTests(unittest.TestCase):
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
        self.assertEqual(manifest["version"], "0.1.1")
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


if __name__ == "__main__":
    unittest.main()
