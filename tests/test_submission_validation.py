from __future__ import annotations

import json
import importlib.util
import shlex
import shutil
import subprocess
import tempfile
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "plugins/adaptive-effort/skills/adaptive-effort/scripts/policy.py"
spec = importlib.util.spec_from_file_location("submission_adaptive_policy", POLICY_PATH)
policy = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = policy
spec.loader.exec_module(policy)


class SubmissionValidationTests(unittest.TestCase):
    def copied_repo(self, directory: str) -> Path:
        copy = Path(directory) / "repo"
        shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", ".superpowers", "dist", "__pycache__", "*.pyc"))
        return copy

    def run_validator(self, copy: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", "scripts/validate.py"], cwd=copy, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
        )

    def test_validator_rejects_mutated_exact_listing_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = self.copied_repo(directory)
            path = copy / "submission/listing.json"
            listing = json.loads(path.read_text())
            listing["capabilities"].reverse()
            path.write_text(json.dumps(listing))
            result = self.run_validator(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("listing", result.stdout.lower())

    def test_validator_rejects_incomplete_review_case_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = self.copied_repo(directory)
            path = copy / "submission/review-cases.json"
            cases = json.loads(path.read_text())
            del cases["positiveCases"][0]["publicSetup"]
            path.write_text(json.dumps(cases))
            result = self.run_validator(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("review", result.stdout.lower())

    def test_validator_rejects_nonexistent_release_tag_in_public_setup(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = self.copied_repo(directory)
            path = copy / "submission/review-cases.json"
            cases = json.loads(path.read_text())
            for case in cases["positiveCases"] + cases["negativeCases"]:
                case["publicSetup"] = case["publicSetup"].replace(
                    "Clone https://github.com/darvilp/adaptive-effort and check out public main. Verify that plugins/adaptive-effort/.codex-plugin/plugin.json reports version 0.1.3.",
                    "Clone https://github.com/darvilp/adaptive-effort at tag 0.1.3,",
                )
            path.write_text(json.dumps(cases))
            result = self.run_validator(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("public main and manifest version", result.stdout.lower())

    def test_validator_rejects_planned_review_escalation_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = self.copied_repo(directory)
            path = copy / "submission/review-cases.json"
            cases = json.loads(path.read_text())
            planned = cases["positiveCases"][4]
            planned["scenario"] = "A failed worker triggers corrective escalation."
            planned["expectedWorkflow"] = "Dispatch a higher-effort corrective agent."
            planned["expectedResult"] = "The escalation count increases."
            path.write_text(json.dumps(cases))
            result = self.run_validator(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertRegex(
                result.stdout.lower(),
                r"review case semantics|fixed-effort review case",
            )

    def test_validator_rejects_route_semantic_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = self.copied_repo(directory)
            path = copy / "submission/review-cases.json"
            cases = json.loads(path.read_text())
            cases["positiveCases"][0]["expectedWorkflow"] = "Dispatch a Medium implementer."
            cases["negativeCases"][2]["safeFallback"] = "Restart the ladder."
            path.write_text(json.dumps(cases))
            result = self.run_validator(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("review case semantics", result.stdout.lower())

    def test_validator_rejects_task_local_override_semantic_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = self.copied_repo(directory)
            path = copy / "submission/review-cases.json"
            cases = json.loads(path.read_text())
            override = next(
                case for case in cases["positiveCases"]
                if case["id"] == "task-local-effort-overrides"
            )
            override["expectedWorkflow"] = "Ignore the role assignments and use Fast defaults."
            path.write_text(json.dumps(cases))
            result = self.run_validator(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("review case semantics", result.stdout.lower())

    def test_validator_rejects_task_local_model_fixture_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = self.copied_repo(directory)
            path = copy / "submission/fixtures/task-local-model-overrides.json"
            fixture = json.loads(path.read_text())
            fixture["routes"][0]["expectedModel"] = "silently-substituted-model"
            path.write_text(json.dumps(fixture))
            result = self.run_validator(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("model override fixture", result.stdout.lower())

    def test_validator_requires_the_routing_plan_command(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = self.copied_repo(directory)
            command = (
                copy
                / "plugins/adaptive-effort/skills/adaptive-effort/scripts/routing_plan.py"
            )
            command.unlink()
            result = self.run_validator(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("routing_plan.py", result.stdout)

    def test_validator_rejects_unconditional_child_model_inheritance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = self.copied_repo(directory)
            path = copy / "plugins/adaptive-effort/skills/adaptive-effort/references/routing-policy.md"
            text = path.read_text()
            text = text.replace(
                "Unspecified roles inherit the parent model by omitting `model`.",
                "Child model is always inherited by omitting `model`.",
            ).replace(
                "Explicit role model overrides pass the user's exact model ID unchanged.",
                "Explicit role model overrides are ignored.",
            )
            path.write_text(text)
            result = self.run_validator(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("model override contract", result.stdout.lower())

    def test_task_local_override_review_fixture_is_executable_policy_input(self) -> None:
        fixture = json.loads(
            (ROOT / "submission/fixtures/task-local-effort-overrides.json").read_text()
        )
        for route in fixture["routes"]:
            with self.subTest(route=route["name"]):
                result = subprocess.run(
                    [
                        "python3",
                        "plugins/adaptive-effort/skills/adaptive-effort/scripts/policy.py",
                        "--mode", fixture["mode"],
                        "--role", route["role"],
                        "--risk", route.get("risk", "routine"),
                        *[
                            item
                            for assignment in fixture["effortAssignments"]
                            for item in ("--effort", assignment)
                        ],
                    ],
                    cwd=ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    json.loads(result.stdout)["reasoning_effort"],
                    route["expectedEffort"],
                )
        assignments = {
            key.replace("-", "_"): effort
            for key, effort in (
                assignment.split("=", 1)
                for assignment in fixture["effortAssignments"]
            )
        }
        overrides = policy.EffortOverrides(**assignments)
        for repair in fixture["repairs"]:
            writer = policy.route(
                fixture["mode"], repair["currentWriterRole"],
                effort_overrides=overrides,
            )
            self.assertEqual(repair["expectedEffort"], policy.repair_effort(writer))

        conflict = fixture["conflictingInput"]
        cap_role, cap_effort = conflict["cap"].split("=", 1)
        conflicting_role, conflicting_effort = conflict["assignment"].split("=", 1)
        with self.assertRaisesRegex(ValueError, conflict["expectedError"]):
            policy.validate_effort_caps(
                policy.EffortOverrides(**{conflicting_role: conflicting_effort}),
                policy.EffortOverrides(**{cap_role: cap_effort}),
            )

        recovery = fixture["fastRecovery"]
        without_evidence = policy.failure_route(
            "contract/design defect", mode="fast", effort_overrides=overrides
        )
        with_evidence = policy.failure_route(
            "contract/design defect", mode="fast",
            independent_contract_design_evidence=True,
            effort_overrides=overrides,
        )
        self.assertEqual(without_evidence, recovery["withoutEvidence"])
        self.assertEqual(with_evidence, recovery["withEvidence"])

    def test_task_local_model_override_fixture_is_executable_policy_input(self) -> None:
        fixture = json.loads(
            (ROOT / "submission/fixtures/task-local-model-overrides.json").read_text()
        )
        for route in fixture["routes"]:
            with self.subTest(route=route["name"]):
                result = subprocess.run(
                    [
                        "python3",
                        "plugins/adaptive-effort/skills/adaptive-effort/scripts/policy.py",
                        "--mode", fixture["mode"],
                        "--role", route["role"],
                        "--risk", route.get("risk", "routine"),
                        *[
                            item
                            for assignment in fixture["effortAssignments"]
                            for item in ("--effort", assignment)
                        ],
                        *[
                            item
                            for assignment in fixture["modelAssignments"]
                            for item in ("--model", assignment)
                        ],
                    ],
                    cwd=ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                actual = json.loads(result.stdout)
                self.assertEqual(actual["reasoning_effort"], route["expectedEffort"])
                self.assertEqual(actual["model"], route["expectedModel"])

        recovery_model = fixture["fastRecoveryModelOnly"]
        overrides = policy.ModelOverrides(recovery=recovery_model)
        self.assertEqual(
            policy.failure_route(
                "contract/design defect",
                mode="fast",
                model_overrides=overrides,
            ),
            "stop",
        )
        self.assertEqual(
            policy.failure_route(
                "contract/design defect",
                mode="fast",
                independent_contract_design_evidence=True,
                model_overrides=overrides,
            ),
            "recovery",
        )

    def test_fixed_effort_review_cases_are_labeled_no_override_examples(self) -> None:
        cases = json.loads((ROOT / "submission/review-cases.json").read_text())
        by_id = {case["id"]: case for case in cases["positiveCases"]}
        for case_id in (
            "balanced-default",
            "deep-default",
            "semantic-repair",
            "planned-review",
        ):
            with self.subTest(case_id=case_id):
                serialized = " ".join(str(value) for value in by_id[case_id].values())
                self.assertIn("no role assignments", serialized.lower())

    def test_validator_rejects_unlabeled_fixed_effort_review_case(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = self.copied_repo(directory)
            path = copy / "submission/review-cases.json"
            cases = json.loads(path.read_text())
            semantic_repair = next(
                case for case in cases["positiveCases"]
                if case["id"] == "semantic-repair"
            )
            semantic_repair["scenario"] = semantic_repair["scenario"].replace(
                " with no role assignments", ""
            )
            path.write_text(json.dumps(cases))
            result = self.run_validator(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("fixed-effort review case", result.stdout.lower())

    def test_repair_and_debugger_cases_run_the_public_failure_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = self.copied_repo(directory)
            cases = json.loads((copy / "submission/review-cases.json").read_text())
            by_id = {case["id"]: case for case in cases["positiveCases"]}
            for case_id in ("semantic-repair", "fresh-debugger"):
                with self.subTest(case_id=case_id):
                    injection = by_id[case_id]["evidenceInjection"]
                    result = subprocess.run(
                        shlex.split(injection["command"]), cwd=copy, text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
                    )
                    self.assertEqual(result.returncode, injection["expectedExit"])
                    self.assertEqual(result.stdout.strip(), injection["expectedOutput"])
                    self.assertGreaterEqual(len(injection["sequence"]), 2)

            repair = by_id["semantic-repair"]["evidenceInjection"]
            debugger = by_id["fresh-debugger"]["evidenceInjection"]
            self.assertNotEqual(repair["command"], debugger["command"])
            self.assertIn('"classification":"local deterministic implementation defect"', repair["expectedOutput"])
            self.assertIn('"classification":"implementation-reasoning defect"', debugger["expectedOutput"])
            self.assertIn("correction verification fails", " ".join(debugger["sequence"]).lower())

    def test_validator_anchors_review_failure_classes_to_canonical_policy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = self.copied_repo(directory)
            cases_path = copy / "submission/review-cases.json"
            cases = json.loads(cases_path.read_text())
            repair = cases["positiveCases"][2]["evidenceInjection"]
            fixture_path = copy / shlex.split(repair["command"])[-1]
            fixture = json.loads(fixture_path.read_text())
            fixture["classification"] = "implementation-reasoning defect"
            fixture_path.write_text(json.dumps(fixture))
            result = self.run_validator(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("canonical failure route", result.stdout.lower())

    def test_validator_rejects_readme_policy_disagreement(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = self.copied_repo(directory)
            path = copy / "README.md"
            path.write_text(path.read_text().replace("| Fresh debugger | Medium | Medium | High |", "| Fresh debugger | Low | Low | Low |"))
            result = self.run_validator(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("readme", result.stdout.lower())

    def test_validator_rejects_stale_mode_guidance_outside_main_tables(self) -> None:
        mutations = {
            "DESIGN.md": (
                "A broader implementation failure gets one fresh debugger at `profile.debugger`.",
                "Every implementation failure starts a Medium debugger.",
            ),
            "docs/design.md": (
                "reasoning effort:  profile.debugger",
                "reasoning effort:  Medium",
            ),
            "plugins/adaptive-effort/skills/adaptive-effort/references/handoff-templates.md": (
                "<implementation, retained-effort repair, debugger outcomes>",
                "<low implementation, low repair, debugger outcomes>",
            ),
        }
        for relative, (approved, stale) in mutations.items():
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                copy = self.copied_repo(directory)
                path = copy / relative
                path.write_text(path.read_text().replace(approved, stale))
                result = self.run_validator(copy)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("routing guidance", result.stdout.lower())

    def test_validator_audits_every_maintained_routing_policy_consumer(self) -> None:
        consumers = (
            "README.md",
            "DESIGN.md",
            "docs/design.md",
            "TEST_DRIVE.md",
            "plugins/adaptive-effort/README.md",
            "plugins/adaptive-effort/skills/adaptive-effort/SKILL.md",
            "plugins/adaptive-effort/skills/adaptive-effort/references/routing-policy.md",
            "plugins/adaptive-effort/skills/adaptive-effort/references/escalation-policy.md",
            "plugins/adaptive-effort/skills/adaptive-effort/references/superpowers-integration.md",
        )
        stale_instruction = "Action: start a fresh debugger at medium effort, or high in deep mode."
        for relative in consumers:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                copy = self.copied_repo(directory)
                path = copy / relative
                path.write_text(path.read_text() + f"\n\n{stale_instruction}\n")
                result = self.run_validator(copy)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("routing policy consumer", result.stdout.lower())

    def test_validator_rejects_recovery_authorization_disagreement(self) -> None:
        mutations = {
            "README.md": (
                "| Recovery diagnostician | High only when explicitly requested; not automatic | High, only with independent contract/design evidence | High, only with independent contract/design evidence |",
                "| Recovery diagnostician | High | High | High |",
            ),
            "plugins/adaptive-effort/README.md": (
                "| Recovery diagnostician | High only when explicitly requested; not automatic | High, only with independent contract/design evidence | High, only with independent contract/design evidence |",
                "| Recovery diagnostician | High | High | High |",
            ),
            "plugins/adaptive-effort/skills/adaptive-effort/references/routing-policy.md": (
                "| Recovery diagnostician | high only when explicitly requested; not automatic | high, only with independent contract/design evidence | high, only with independent contract/design evidence |",
                "| Recovery diagnostician | high | high | high |",
            ),
        }
        for relative, (approved, incorrect) in mutations.items():
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                copy = self.copied_repo(directory)
                path = copy / relative
                path.write_text(path.read_text().replace(approved, incorrect))
                result = self.run_validator(copy)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("recovery", result.stdout.lower())

        with tempfile.TemporaryDirectory() as directory:
            copy = self.copied_repo(directory)
            path = copy / "plugins/adaptive-effort/skills/adaptive-effort/references/escalation-policy.md"
            path.write_text(path.read_text().replace(
                "Only the recovery diagnostician requires contract/design evidence",
                "The recovery diagnostician does not require contract/design evidence",
            ))
            result = self.run_validator(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("recovery", result.stdout.lower())

    def test_validator_rejects_stale_distribution_docs_and_ci_claims(self) -> None:
        mutations = {
            "README.md": ("Universal Plugins Directory", "community marketplace"),
            "plugins/adaptive-effort/skills/adaptive-effort/references/compatibility.md": (
                "https://developers.openai.com/plugins/build/plugins",
                "https://developers.openai.com/codex/build-plugins",
            ),
            "SOURCES.md": (
                "https://developers.openai.com/plugins/deploy/submission",
                "https://developers.openai.com/plugins/submit/",
            ),
            "TEST_RESULTS.md": (
                "No CI result is claimed for this unpushed commit.",
                "CI passed this unpushed commit.",
            ),
        }
        for relative, (approved, stale) in mutations.items():
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                copy = self.copied_repo(directory)
                path = copy / relative
                path.write_text(path.read_text().replace(approved, stale))
                result = self.run_validator(copy)
                self.assertNotEqual(result.returncode, 0)
                self.assertRegex(result.stdout.lower(), "distribution|documentation|ci evidence")

    def test_validator_rejects_false_policy_unchanged_claim(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = self.copied_repo(directory)
            path = copy / "TEST_RESULTS.md"
            accurate = (
                "`plugins/adaptive-effort/skills/adaptive-effort/scripts/doctor.py` remains unchanged. "
                "`plugins/adaptive-effort/skills/adaptive-effort/scripts/policy.py` now differentiates Fast, "
                "Balanced, and Deep implementation, review, debugging, and automatic recovery routes."
            )
            false_claim = "`scripts/policy.py` and `doctor.py` are unchanged."
            path.write_text(path.read_text().replace(accurate, false_claim))
            result = self.run_validator(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("policy evidence", result.stdout.lower())

    def test_validator_rejects_numeric_count_in_current_verification_paragraph(self) -> None:
        accurate = "`scripts/validate.py` passed, and the full unit suite passed."
        numeric_variants = (
            "All 69 tests passed.",
            "The full unit suite passed 69 tests.",
            "69 UNIT TESTS PASSED.",
            "Passed all 69 unit tests.",
        )
        for numeric_claim in numeric_variants:
            with self.subTest(numeric_claim=numeric_claim), tempfile.TemporaryDirectory() as directory:
                copy = self.copied_repo(directory)
                path = copy / "TEST_RESULTS.md"
                path.write_text(path.read_text().replace(accurate, f"{accurate} {numeric_claim}"))
                result = self.run_validator(copy)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("unit-suite evidence", result.stdout.lower())

    def test_validator_allows_numeric_count_in_historical_section(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = self.copied_repo(directory)
            path = copy / "TEST_RESULTS.md"
            path.write_text(
                path.read_text()
                + "\n## Historical verification example\n\nall 67 unit tests passed.\n"
            )
            result = self.run_validator(copy)
            self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
