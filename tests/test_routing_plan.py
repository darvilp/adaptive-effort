from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_PATH = (
    ROOT
    / "plugins/adaptive-effort/skills/adaptive-effort/scripts"
)
ROUTING_PLAN_PATH = SCRIPTS_PATH / "routing_plan.py"
sys.path.insert(0, str(SCRIPTS_PATH))
spec = importlib.util.spec_from_file_location("routing_plan", ROUTING_PLAN_PATH)
routing_plan = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = routing_plan
previous_bytecode_setting = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    spec.loader.exec_module(routing_plan)
finally:
    sys.dont_write_bytecode = previous_bytecode_setting


def catalog_model(
    slug: str,
    *,
    visibility: str = "list",
    multi_agent_version: str | None = "v2",
    efforts: tuple[str, ...] = ("low", "medium", "high"),
) -> dict[str, object]:
    return {
        "slug": slug,
        "display_name": slug.upper(),
        "visibility": visibility,
        "multi_agent_version": multi_agent_version,
        "default_reasoning_level": "medium",
        "supported_reasoning_levels": [
            {"effort": effort, "description": effort} for effort in efforts
        ],
    }


class RoutingPlanTests(unittest.TestCase):
    def make_fake_codex(
        self, directory: Path, *, models_exit: int = 0
    ) -> Path:
        executable = directory / "bin with spaces" / "codex"
        executable.parent.mkdir()
        executable.write_text(
            "#!/bin/sh\n"
            "if [ \"$1\" = \"--version\" ]; then\n"
            "  echo 'codex-cli 9.9.9-test'\n"
            "  exit 0\n"
            "fi\n"
            "if [ \"$1\" = \"debug\" ] && [ \"$2\" = \"models\" ]; then\n"
            "  printf '%s' \"$FAKE_CODEX_MODELS\"\n"
            f"  exit {models_exit}\n"
            "fi\n"
            "exit 64\n",
            encoding="utf-8",
        )
        executable.chmod(0o755)
        return executable

    def run_routing_plan(
        self, executable: Path | None, *args: str, models_stdout: str = ""
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PATH"] = str(executable.parent) if executable else ""
        env["FAKE_CODEX_MODELS"] = models_stdout
        return subprocess.run(
            [sys.executable, str(ROUTING_PLAN_PATH), *args],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_outputs_resolved_plan_and_all_live_catalog_candidates(self) -> None:
        models = [catalog_model(f"model-{index}") for index in range(7)]
        models.extend(
            [
                catalog_model("hidden", visibility="hide"),
                catalog_model("disabled", multi_agent_version="disabled"),
            ]
        )
        catalog = json.dumps({"models": list(reversed(models))})
        with tempfile.TemporaryDirectory() as directory:
            executable = self.make_fake_codex(Path(directory))
            result = self.run_routing_plan(
                executable,
                "--mode", "balanced",
                "--multi-agent-version", "v2",
                "--effort", "debugger=ultra",
                "--model", "implementer=model-6",
                "--model", "routine-review=model-2",
                models_stdout=catalog,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["mode"], "balanced")
        self.assertEqual(
            list(output["routes"]),
            [
                "implementer",
                "routine-review",
                "high-risk-review",
                "debugger",
                "recovery",
            ],
        )
        self.assertEqual(
            output["routes"]["implementer"],
            {
                "fork_turns": "none",
                "model": "model-6",
                "model_validation": "catalog-candidate",
                "reasoning_effort": "low",
            },
        )
        self.assertEqual(
            output["routes"]["debugger"]["reasoning_effort"], "ultra"
        )
        self.assertEqual(
            output["routes"]["high-risk-review"]["model_validation"],
            "inherited",
        )
        self.assertEqual(
            output["overrides"],
            {
                "effort": {"debugger": "ultra"},
                "model": {
                    "implementer": "model-6",
                    "routine-review": "model-2",
                },
            },
        )
        self.assertFalse(output["recovery_explicitly_requested"])
        candidates = output["model_candidates"]
        self.assertEqual(candidates["status"], "available")
        self.assertEqual(candidates["scope"], "local-client-candidates")
        self.assertEqual(candidates["source"]["version"], "codex-cli 9.9.9-test")
        self.assertEqual(
            [model["model"] for model in candidates["models"]],
            [f"model-{index}" for index in range(7)],
        )
        self.assertEqual(
            candidates["models"][0]["supported_reasoning_efforts"],
            ["low", "medium", "high"],
        )

    def test_direct_command_does_not_write_installed_skill_bytecode(self) -> None:
        catalog = json.dumps({"models": [catalog_model("model-a")]})
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            script_directory = fixture / "installed skill" / "scripts"
            script_directory.mkdir(parents=True)
            shutil.copy2(ROUTING_PLAN_PATH, script_directory / "routing_plan.py")
            shutil.copy2(SCRIPTS_PATH / "policy.py", script_directory / "policy.py")
            executable = self.make_fake_codex(fixture)
            env = os.environ.copy()
            env["PATH"] = str(executable.parent)
            env["FAKE_CODEX_MODELS"] = catalog
            result = subprocess.run(
                [sys.executable, str(script_directory / "routing_plan.py")],
                cwd=ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((script_directory / "__pycache__").exists())

    def test_unlisted_explicit_model_is_deferred_to_host_validation(self) -> None:
        catalog = json.dumps({"models": [catalog_model("model-a")]})
        with tempfile.TemporaryDirectory() as directory:
            executable = self.make_fake_codex(Path(directory))
            result = self.run_routing_plan(
                executable,
                "--model", "implementer=custom/provider-model",
                models_stdout=catalog,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        route = json.loads(result.stdout)["routes"]["implementer"]
        self.assertEqual(route["model"], "custom/provider-model")
        self.assertEqual(route["model_validation"], "host-validation-required")

    def test_catalog_effort_mismatch_is_advisory(self) -> None:
        catalog = json.dumps(
            {"models": [catalog_model("model-a", efforts=("low", "medium"))]}
        )
        with tempfile.TemporaryDirectory() as directory:
            executable = self.make_fake_codex(Path(directory))
            result = self.run_routing_plan(
                executable,
                "--effort", "implementer=high",
                "--model", "implementer=model-a",
                models_stdout=catalog,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout)["routes"]["implementer"]["model_validation"],
            "catalog-effort-not-listed",
        )

    def test_missing_codex_keeps_the_resolved_plan_available(self) -> None:
        result = self.run_routing_plan(
            None,
            "--mode", "fast",
            "--model", "recovery=gpt-5.6-sol",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertTrue(output["recovery_explicitly_requested"])
        self.assertEqual(output["model_candidates"]["status"], "unavailable")
        self.assertEqual(output["model_candidates"]["models"], [])
        self.assertEqual(
            output["routes"]["recovery"]["model_validation"],
            "host-validation-required",
        )

    def test_malformed_catalog_is_reported_without_losing_the_plan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            executable = self.make_fake_codex(Path(directory))
            result = self.run_routing_plan(
                executable,
                "--mode", "deep",
                models_stdout="not-json",
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["mode"], "deep")
        self.assertEqual(output["routes"]["implementer"]["reasoning_effort"], "medium")
        self.assertEqual(output["model_candidates"]["status"], "unavailable")
        self.assertIn("valid JSON", output["model_candidates"]["reason"])

    def test_nonzero_catalog_command_is_reported_without_losing_the_plan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            executable = self.make_fake_codex(Path(directory), models_exit=7)
            result = self.run_routing_plan(executable)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["mode"], "balanced")
        self.assertEqual(output["model_candidates"]["status"], "unavailable")
        self.assertIn("status 7", output["model_candidates"]["reason"])

    def test_catalog_timeout_is_reported_without_losing_candidates_shape(self) -> None:
        original = routing_plan.command_output
        calls = 0

        def timeout_on_models(
            executable: str, arguments: list[str]
        ) -> subprocess.CompletedProcess[str]:
            nonlocal calls
            calls += 1
            if arguments == ["debug", "models"]:
                raise subprocess.TimeoutExpired([executable, *arguments], 10)
            return subprocess.CompletedProcess(
                [executable, *arguments], 0, stdout="codex-cli test\n", stderr=""
            )

        routing_plan.command_output = timeout_on_models
        try:
            with mock.patch("routing_plan.shutil.which", return_value="/codex"):
                candidates = routing_plan.discover_model_candidates("v2")
        finally:
            routing_plan.command_output = original

        self.assertEqual(calls, 2)
        self.assertEqual(candidates["status"], "unavailable")
        self.assertEqual(candidates["models"], [])
        self.assertIn("timed out", candidates["reason"])

    def test_version_probe_timeout_does_not_suppress_the_model_catalog(self) -> None:
        calls = 0
        catalog = json.dumps({"models": [catalog_model("model-a")]})

        def timeout_on_version(
            executable: str, arguments: list[str]
        ) -> subprocess.CompletedProcess[str]:
            nonlocal calls
            calls += 1
            if arguments == ["--version"]:
                raise subprocess.TimeoutExpired([executable, *arguments], 10)
            return subprocess.CompletedProcess(
                [executable, *arguments], 0, stdout=catalog, stderr=""
            )

        with mock.patch("routing_plan.shutil.which", return_value="/codex"), mock.patch(
            "routing_plan.command_output", side_effect=timeout_on_version
        ):
            candidates = routing_plan.discover_model_candidates("v2")

        self.assertEqual(calls, 2)
        self.assertEqual(candidates["status"], "available")
        self.assertIsNone(candidates["source"]["version"])
        self.assertEqual(
            [candidate["model"] for candidate in candidates["models"]],
            ["model-a"],
        )


if __name__ == "__main__":
    unittest.main()
