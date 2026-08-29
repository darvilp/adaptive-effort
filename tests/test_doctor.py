from __future__ import annotations

import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
DOCTOR_PATH = ROOT / "plugins/adaptive-effort/skills/adaptive-effort/scripts/doctor.py"

spec = importlib.util.spec_from_file_location("adaptive_doctor", DOCTOR_PATH)
doctor = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = doctor
spec.loader.exec_module(doctor)


def create_superpowers_skills(base: Path) -> None:
    for name in (
        "subagent-driven-development",
        "test-driven-development",
        "verification-before-completion",
        "requesting-code-review",
    ):
        path = base / ".agents" / "skills" / name
        path.mkdir(parents=True, exist_ok=True)
        (path / "SKILL.md").write_text(f"---\nname: {name}\n---\n")


def find_check(result: dict, name: str, surface: str | None = None) -> dict:
    selected_surface = surface or result["active_surface"]
    return next(
        item
        for item in result["checks"]
        if item["name"] == name and item["surface"] == selected_surface
    )


class DoctorTests(unittest.TestCase):
    def test_cli_project_dir_applies_trusted_config_from_skill_directory(self) -> None:
        with tempfile.TemporaryDirectory() as home_tmp, tempfile.TemporaryDirectory() as project_tmp:
            codex_home = Path(home_tmp) / ".codex"
            project = Path(project_tmp)
            create_superpowers_skills(project)
            codex_home.mkdir(parents=True)
            (codex_home / "config.toml").write_text(
                "[agents]\n"
                "enabled = true\n"
                f"[projects.{json.dumps(str(project.resolve()))}]\n"
                'trust_level = "trusted"\n'
            )
            project_config = project / ".codex" / "config.toml"
            project_config.parent.mkdir(parents=True)
            project_config.write_text("[agents]\nenabled = false\n")
            env = os.environ.copy()
            env["CODEX_HOME"] = str(codex_home)
            env["PATH"] = ""

            completed = subprocess.run(
                [
                    sys.executable,
                    str(DOCTOR_PATH),
                    "--json",
                    "--project-dir",
                    str(project),
                ],
                cwd=DOCTOR_PATH.parent,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(completed.returncode, 1, completed.stderr)
            result = json.loads(completed.stdout)
            config_check = find_check(result, "multi_agent_config")
            self.assertEqual(result["readiness"], "BLOCKED")
            self.assertEqual(config_check["status"], "FAIL")
            self.assertIn(str(project_config), config_check["detail"])

    def test_cli_rejects_project_dir_that_is_not_a_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing"
            env = os.environ.copy()
            env["PATH"] = ""

            completed = subprocess.run(
                [
                    sys.executable,
                    str(DOCTOR_PATH),
                    "--json",
                    "--project-dir",
                    str(missing),
                ],
                cwd=DOCTOR_PATH.parent,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(completed.returncode, 2)
            self.assertEqual(completed.stdout, "")
            self.assertIn("project directory is not a directory", completed.stderr)
            self.assertIn(str(missing), completed.stderr)

    def test_trusted_project_config_overrides_separate_explicit_home(self) -> None:
        with tempfile.TemporaryDirectory() as home_tmp, tempfile.TemporaryDirectory() as project_tmp:
            home = Path(home_tmp)
            project_root = Path(project_tmp)
            cwd = project_root / "nested"
            cwd.mkdir()
            create_superpowers_skills(home)
            user_config = home / ".codex" / "config.toml"
            user_config.parent.mkdir(parents=True)
            user_config.write_text(
                "[agents]\n"
                "enabled = true\n"
                f"[projects.{json.dumps(str(project_root.resolve()))}]\n"
                'trust_level = "trusted"\n'
            )
            root_config = project_root / ".codex" / "config.toml"
            root_config.parent.mkdir(parents=True)
            root_config.write_text("[agents]\nenabled = true\n")
            project_config = cwd / ".codex" / "config.toml"
            project_config.parent.mkdir(parents=True)
            project_config.write_text("[agents]\nenabled = false\n")

            result = doctor.inspect(home=home, cwd=cwd, adjacent_homes={})

            config_check = find_check(result, "multi_agent_config")
            self.assertEqual(config_check["status"], "FAIL")
            self.assertIn(str(project_config), config_check["detail"])
            self.assertEqual(result["readiness"], "BLOCKED")

    def test_malformed_trusted_project_config_blocks_static_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as home_tmp, tempfile.TemporaryDirectory() as project_tmp:
            home = Path(home_tmp)
            cwd = Path(project_tmp)
            create_superpowers_skills(home)
            user_config = home / ".codex" / "config.toml"
            user_config.parent.mkdir(parents=True)
            user_config.write_text(
                f"[projects.{json.dumps(str(cwd.resolve()))}]\n"
                'trust_level = "trusted"\n'
            )
            project_config = cwd / ".codex" / "config.toml"
            project_config.parent.mkdir(parents=True)
            project_config.write_text("[agents\nenabled = true\n")

            result = doctor.inspect(home=home, cwd=cwd, adjacent_homes={})

            self.assertEqual(find_check(result, "multi_agent_config")["status"], "FAIL")
            self.assertEqual(result["readiness"], "BLOCKED")

    def test_untrusted_project_config_is_not_applied(self) -> None:
        with tempfile.TemporaryDirectory() as home_tmp, tempfile.TemporaryDirectory() as project_tmp:
            home = Path(home_tmp)
            cwd = Path(project_tmp)
            create_superpowers_skills(home)
            user_config = home / ".codex" / "config.toml"
            user_config.parent.mkdir(parents=True)
            user_config.write_text(
                f"[projects.{json.dumps(str(cwd.resolve()))}]\n"
                'trust_level = "untrusted"\n'
            )
            project_config = cwd / ".codex" / "config.toml"
            project_config.parent.mkdir(parents=True)
            project_config.write_text("[agents]\nenabled = false\n")

            result = doctor.inspect(home=home, cwd=cwd, adjacent_homes={})

            self.assertEqual(find_check(result, "multi_agent_config")["status"], "PASS")
            self.assertEqual(result["readiness"], "STATIC_READY")

    def test_missing_config_does_not_require_tomllib(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            create_superpowers_skills(home)

            with mock.patch.object(doctor, "tomllib", None):
                result = doctor.inspect(home=home, cwd=home, adjacent_homes={})

            self.assertEqual(find_check(result, "multi_agent_config")["status"], "PASS")
            self.assertEqual(result["readiness"], "STATIC_READY")

    def test_default_home_honors_ambient_codex_home(self) -> None:
        with tempfile.TemporaryDirectory() as host_tmp, tempfile.TemporaryDirectory() as ambient_tmp:
            host_home = Path(host_tmp)
            ambient_codex_home = Path(ambient_tmp) / ".codex"
            for name in (
                "subagent-driven-development",
                "test-driven-development",
                "verification-before-completion",
                "requesting-code-review",
            ):
                path = ambient_codex_home / "plugins" / "cache" / name
                path.mkdir(parents=True, exist_ok=True)
                (path / "SKILL.md").write_text(f"---\nname: {name}\n---\n")
            (ambient_codex_home / "config.toml").write_text(
                "[agents]\nenabled = false\n"
            )

            with mock.patch.object(doctor.Path, "home", return_value=host_home), mock.patch.dict(
                os.environ, {"CODEX_HOME": str(ambient_codex_home)}
            ):
                result = doctor.inspect(cwd=host_home, adjacent_homes={})

            self.assertEqual(
                find_check(result, "superpowers_skills")["status"], "PASS"
            )
            self.assertEqual(
                find_check(result, "multi_agent_config")["status"], "FAIL"
            )
            self.assertEqual(result["readiness"], "BLOCKED")

    def test_malformed_active_config_blocks_static_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            create_superpowers_skills(home)
            config = home / ".codex" / "config.toml"
            config.parent.mkdir(parents=True)
            config.write_text("[agents\nenabled = true\n")

            result = doctor.inspect(home=home, cwd=home, adjacent_homes={})

            self.assertEqual(
                find_check(result, "multi_agent_config")["status"], "FAIL"
            )
            self.assertEqual(result["readiness"], "BLOCKED")

    def test_explicit_home_ignores_ambient_codex_home(self) -> None:
        with tempfile.TemporaryDirectory() as fixture_tmp, tempfile.TemporaryDirectory() as ambient_tmp:
            fixture_home = Path(fixture_tmp)
            ambient_codex_home = Path(ambient_tmp) / ".codex"
            create_superpowers_skills(fixture_home)
            ambient_codex_home.mkdir(parents=True)
            (ambient_codex_home / "config.toml").write_text("[agents]\nenabled = false\n")

            with mock.patch.dict(
                os.environ, {"CODEX_HOME": str(ambient_codex_home)}
            ):
                result = doctor.inspect(
                    home=fixture_home, cwd=fixture_home, adjacent_homes={}
                )

            self.assertEqual(
                find_check(result, "superpowers_skills")["status"], "PASS"
            )
            self.assertEqual(
                find_check(result, "multi_agent_config")["status"], "PASS"
            )
            self.assertEqual(result["readiness"], "STATIC_READY")

    def test_filesystem_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            create_superpowers_skills(home)
            result = doctor.inspect(home=home, cwd=home, adjacent_homes={})
            check = find_check(result, "superpowers_skills")
            self.assertEqual(check["status"], "PASS")
            self.assertEqual(check["surface"], result["active_surface"])
            self.assertEqual(result["readiness"], "STATIC_READY")

    def test_disabled_agents_is_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            create_superpowers_skills(home)
            config = home / ".codex" / "config.toml"
            config.parent.mkdir(parents=True)
            config.write_text("[agents]\nenabled = false\n")
            result = doctor.inspect(home=home, cwd=home, adjacent_homes={})
            self.assertEqual(find_check(result, "multi_agent_config")["status"], "FAIL")
            self.assertEqual(result["readiness"], "BLOCKED")

    def test_fake_codex_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            create_superpowers_skills(home)
            bindir = home / "bin"
            bindir.mkdir()
            codex = bindir / "codex"
            codex.write_text(
                "#!/bin/sh\n"
                "if [ \"$1\" = \"--version\" ]; then echo 'codex-cli 0.test'; exit 0; fi\n"
                "if [ \"$1\" = \"plugin\" ]; then echo '{\"installed\":[{\"name\":\"superpowers\"}]}'; exit 0; fi\n"
                "exit 1\n"
            )
            codex.chmod(codex.stat().st_mode | stat.S_IXUSR)
            with mock.patch.dict(os.environ, {"PATH": f"{bindir}:{os.environ.get('PATH', '')}"}):
                result = doctor.inspect(home=home, cwd=home, adjacent_homes={})
            self.assertEqual(find_check(result, "codex_cli")["status"], "PASS")
            self.assertEqual(find_check(result, "superpowers_plugin")["status"], "PASS")


    def test_adjacent_surface_failure_does_not_block_active_surface(self) -> None:
        with tempfile.TemporaryDirectory() as active_tmp, tempfile.TemporaryDirectory() as windows_tmp:
            active_home = Path(active_tmp)
            windows_home = Path(windows_tmp)
            create_superpowers_skills(active_home)
            config = windows_home / ".codex" / "config.toml"
            config.parent.mkdir(parents=True)
            config.write_text("[agents]\nenabled = false\n")

            with mock.patch.dict(
                os.environ, {"CODEX_HOME": str(active_home / ".codex")}
            ):
                result = doctor.inspect(
                    home=active_home,
                    cwd=active_home,
                    active_surface="wsl",
                    adjacent_homes={"windows": windows_home},
                )

            self.assertEqual(result["readiness"], "STATIC_READY")
            windows_config = next(
                item
                for item in result["checks"]
                if item["name"] == "multi_agent_config" and item["surface"] == "windows"
            )
            self.assertEqual(windows_config["status"], "FAIL")

    def test_runtime_evidence_promotes_static_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            create_superpowers_skills(home)
            result = doctor.inspect(
                home=home, cwd=home, adjacent_homes={}, runtime_verified=True
            )
            self.assertEqual(result["readiness"], "RUNTIME_VERIFIED")

if __name__ == "__main__":
    unittest.main()
