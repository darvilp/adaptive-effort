from __future__ import annotations

import importlib.util
import json
import subprocess
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "plugins/adaptive-effort/skills/adaptive-effort/scripts/policy.py"

spec = importlib.util.spec_from_file_location("adaptive_policy", POLICY_PATH)
policy = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = policy
spec.loader.exec_module(policy)


class PolicyTests(unittest.TestCase):
    def test_resolve_profile_preserves_each_mode_default(self) -> None:
        self.assertEqual(
            policy.resolve_profile("fast"),
            policy.RoutingProfile("low", "low", "high", "medium", "high"),
        )
        self.assertEqual(
            policy.resolve_profile("balanced"),
            policy.RoutingProfile("low", "medium", "high", "medium", "high"),
        )
        self.assertEqual(
            policy.resolve_profile("deep"),
            policy.RoutingProfile("medium", "high", "high", "high", "high"),
        )

    def test_partial_and_full_overrides_replace_only_named_roles(self) -> None:
        partial = policy.EffortOverrides(implementer="medium", debugger="xhigh")
        self.assertEqual(
            policy.resolve_profile("fast", effort_overrides=partial),
            policy.RoutingProfile("medium", "low", "high", "xhigh", "high"),
        )
        full = policy.EffortOverrides(
            implementer="medium",
            routine_review="high",
            high_risk_review="low",
            debugger="xhigh",
            recovery="max",
        )
        self.assertEqual(
            policy.resolve_profile("fast", effort_overrides=full),
            policy.RoutingProfile(
                "medium", "high", "low", "xhigh", "max",
                recovery_explicitly_requested=True,
            ),
        )

    def test_profile_preserves_explicit_recovery_provenance(self) -> None:
        self.assertFalse(policy.resolve_profile("fast").recovery_explicitly_requested)
        self.assertTrue(
            policy.resolve_profile(
                "fast", effort_overrides=policy.EffortOverrides(recovery="high")
            ).recovery_explicitly_requested
        )

    def test_effort_cap_conflicts_are_rejected_before_dispatch(self) -> None:
        overrides = policy.EffortOverrides(implementer="high", debugger="low")
        caps = policy.EffortOverrides(implementer="low", debugger="medium")
        with self.assertRaisesRegex(
            ValueError,
            "effort override conflicts with cap: implementer=high exceeds low",
        ):
            policy.validate_effort_caps(overrides, caps)
        policy.validate_effort_caps(
            policy.EffortOverrides(implementer="low"), caps
        )

    def test_effort_cap_errors_use_canonical_public_review_keys(self) -> None:
        for field, public_key in (
            ("routine_review", "routine-review"),
            ("high_risk_review", "high-risk-review"),
        ):
            with self.subTest(public_key=public_key), self.assertRaisesRegex(
                ValueError,
                rf"effort override conflicts with cap: {public_key}=high exceeds low",
            ):
                policy.validate_effort_caps(
                    policy.EffortOverrides(**{field: "high"}),
                    policy.EffortOverrides(**{field: "low"}),
                )

    def test_repair_effort_comes_from_the_actual_overridden_writer_route(self) -> None:
        overrides = policy.EffortOverrides(
            implementer="medium", debugger="xhigh", recovery="max"
        )
        for role, expected in (
            ("implementer", "medium"),
            ("debugger", "xhigh"),
            ("recovery", "max"),
        ):
            with self.subTest(role=role):
                writer = policy.route("fast", role, effort_overrides=overrides)
                self.assertEqual(policy.repair_effort(writer), expected)
        with self.assertRaisesRegex(ValueError, "reviewer is not a repair writer"):
            policy.repair_effort(policy.route("fast", "reviewer"))

    def test_route_uses_review_risk_and_never_treats_repair_as_an_override_role(self) -> None:
        overrides = policy.EffortOverrides(
            routine_review="xhigh", high_risk_review="ultra"
        )
        self.assertEqual(
            policy.route("balanced", "reviewer", effort_overrides=overrides).reasoning_effort,
            "xhigh",
        )
        self.assertEqual(
            policy.route("balanced", "reviewer", "high", effort_overrides=overrides).reasoning_effort,
            "ultra",
        )
        with self.assertRaises(TypeError):
            policy.EffortOverrides(repair="high")

    def test_explicit_high_efforts_are_supported_but_defaults_remain_capped(self) -> None:
        for effort in ("xhigh", "max", "ultra"):
            with self.subTest(effort=effort):
                overrides = policy.EffortOverrides(implementer=effort)
                self.assertEqual(
                    policy.route("balanced", "implementer", effort_overrides=overrides).reasoning_effort,
                    effort,
                )
        self.assertEqual(policy.route("balanced", "implementer").reasoning_effort, "low")

    def test_invalid_effort_values_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported effort"):
            policy.EffortOverrides(debugger="extreme")

    def test_fast_explicit_recovery_requires_independent_evidence(self) -> None:
        overrides = policy.EffortOverrides(recovery="max")
        self.assertEqual(
            policy.failure_route(
                "contract/design defect", mode="fast", effort_overrides=overrides
            ),
            "stop",
        )
        self.assertEqual(
            policy.failure_route(
                "contract/design defect",
                mode="fast",
                independent_contract_design_evidence=True,
                effort_overrides=overrides,
            ),
            "recovery",
        )
        self.assertEqual(
            policy.route("fast", "recovery", effort_overrides=overrides).reasoning_effort,
            "max",
        )

    def test_cli_accepts_repeatable_effort_assignments(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(POLICY_PATH),
                "--mode", "fast",
                "--role", "reviewer",
                "--risk", "high",
                "--effort", "implementer=medium",
                "--effort", "high-risk-review=ultra",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["reasoning_effort"], "ultra")

    def test_cli_rejects_invalid_and_duplicate_effort_assignments(self) -> None:
        invalid = ("reviewer=high", "implementer=extreme", "implementer")
        for assignment in invalid:
            with self.subTest(assignment=assignment):
                result = subprocess.run(
                    [sys.executable, str(POLICY_PATH), "--role", "implementer", "--effort", assignment],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("--effort", result.stderr)
        duplicate = subprocess.run(
            [
                sys.executable, str(POLICY_PATH), "--role", "implementer",
                "--effort", "implementer=low", "--effort", "implementer=medium",
            ],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        self.assertNotEqual(duplicate.returncode, 0)
        self.assertIn("duplicate", duplicate.stderr.lower())

    def test_fast_ladder_prioritizes_cost_and_stops_before_recovery(self) -> None:
        self.assertEqual(policy.route("fast", "implementer").reasoning_effort, "low")
        self.assertEqual(policy.route("fast", "reviewer").reasoning_effort, "low")
        self.assertEqual(policy.route("fast", "debugger").reasoning_effort, "medium")
        self.assertEqual(
            policy.failure_route(
                "contract/design defect",
                mode="fast",
                independent_contract_design_evidence=True,
            ),
            "stop",
        )

    def test_balanced_ladder_starts_low_and_retains_guarded_recovery(self) -> None:
        self.assertEqual(policy.route("balanced", "implementer").reasoning_effort, "low")
        self.assertEqual(policy.route("balanced", "reviewer").reasoning_effort, "medium")
        self.assertEqual(policy.route("balanced", "debugger").reasoning_effort, "medium")
        self.assertEqual(policy.route("balanced", "recovery").reasoning_effort, "high")
        self.assertEqual(
            policy.failure_route("contract/design defect", mode="balanced"),
            "stop",
        )
        self.assertEqual(
            policy.failure_route(
                "contract/design defect",
                mode="balanced",
                independent_contract_design_evidence=True,
            ),
            "recovery",
        )

    def test_deep_ladder_always_starts_implementation_at_medium(self) -> None:
        self.assertEqual(policy.route("deep", "implementer").reasoning_effort, "medium")
        self.assertEqual(policy.route("deep", "reviewer").reasoning_effort, "high")
        self.assertEqual(policy.route("deep", "debugger").reasoning_effort, "high")
        self.assertEqual(policy.route("deep", "recovery").reasoning_effort, "high")

    def test_review_risk(self) -> None:
        self.assertEqual(policy.route("fast", "reviewer", "routine").reasoning_effort, "low")
        self.assertEqual(policy.route("fast", "reviewer", "high").reasoning_effort, "high")

    def test_implementation_does_not_require_an_upfront_work_classification(self) -> None:
        with self.assertRaises(ValueError):
            policy.route("deep", "integration_implementer")

    def test_repair_reuses_existing_thread_instead_of_routing_a_spawn(self) -> None:
        with self.assertRaises(ValueError):
            policy.route("balanced", "repair")

    def test_model_is_always_inherited_and_context_fresh(self) -> None:
        for mode in ("fast", "balanced", "deep"):
            for role in (
                "implementer",
                "debugger",
                "recovery",
                "reviewer",
            ):
                route = policy.route(mode, role)
                self.assertIsNone(route.model)
                self.assertEqual(route.fork_turns, "none")
                self.assertNotIn(route.reasoning_effort, {"xhigh", "max", "ultra"})
                self.assertFalse(hasattr(route, "agent_type"))
    def test_invalid_values_rejected(self) -> None:
        with self.assertRaises(ValueError):
            policy.route("turbo", "implementer")
        with self.assertRaises(ValueError):
            policy.route("balanced", "architect")

    def test_failure_classes_select_the_canonical_corrective_route(self) -> None:
        self.assertTrue(
            hasattr(policy, "failure_route"),
            "policy.py must own the failure-class to corrective-route mapping",
        )
        if not hasattr(policy, "failure_route"):
            return
        self.assertEqual(
            policy.failure_route("local deterministic implementation defect"),
            "semantic_correction",
        )
        self.assertEqual(
            policy.failure_route("implementation-reasoning defect"),
            "debugger",
        )
        self.assertEqual(
            policy.failure_route("contract/design defect"),
            "stop",
        )
        self.assertEqual(
            policy.failure_route(
                "contract/design defect",
                independent_contract_design_evidence=True,
            ),
            "recovery",
        )


if __name__ == "__main__":
    unittest.main()
