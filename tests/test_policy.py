from __future__ import annotations

import importlib.util
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
