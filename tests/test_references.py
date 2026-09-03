from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "plugins/adaptive-effort/skills/adaptive-effort"


class ReferenceTests(unittest.TestCase):
    def test_circuit_breaker_is_bounded(self) -> None:
        text = (SKILL_ROOT / "references/escalation-policy.md").read_text().lower()
        for stage in ("initial implementer", "same-thread local repair", "fresh debugger", "high recovery"):
            self.assertIn(stage, text)
        self.assertIn("never silently restart the ladder", text)

    def test_environment_failure_does_not_escalate(self) -> None:
        text = (SKILL_ROOT / "references/escalation-policy.md").read_text().lower()
        self.assertIn("do not raise reasoning effort", text)

    def test_superpowers_remains_owner(self) -> None:
        text = (SKILL_ROOT / "references/superpowers-integration.md").read_text()
        self.assertIn("Superpowers owns", text)
        self.assertIn("Adaptive Effort owns", text)
        for responsibility in ("task decomposition", "writer topology", "parallelism", "boundary selection", "acceptance gates"):
            self.assertIn(responsibility, text)
        self.assertIn("does not remove the two-stage review", text)

    def test_planned_reviews_are_not_escalations(self) -> None:
        routing = (SKILL_ROOT / "references/routing-policy.md").read_text()
        escalation = (SKILL_ROOT / "references/escalation-policy.md").read_text()
        self.assertIn("Planned medium/high reviews never count as escalations", routing)
        self.assertIn("Only corrective upward effort transitions count", escalation)

    def test_modes_have_distinct_routes_without_work_classification(self) -> None:
        routing = (SKILL_ROOT / "references/routing-policy.md").read_text()
        skill = (SKILL_ROOT / "SKILL.md").read_text()

        self.assertIn("| Implementer | low | low | medium |", routing)
        self.assertIn("| Routine spec review | low | medium | high |", routing)
        self.assertIn("| Routine quality review | low | medium | high |", routing)
        self.assertIn("Fast stops before automatic High recovery", routing)
        self.assertNotIn("integration_implementer", routing)
        self.assertNotIn("Multi-file integration implementer", routing)
        self.assertNotIn("classify implementation", routing.lower())
        self.assertIn("Deep always starts implementers at Medium", skill)
        self.assertIn("Fast stops automatic handling before High recovery", skill)

    def test_worker_and_gate_outcomes_are_separate(self) -> None:
        text = (SKILL_ROOT / "references/handoff-templates.md").read_text()
        self.assertIn("result   · worker=<status> · gate=<NOT_RUN|PASS|FAIL|BLOCKED>", text)
        self.assertIn("Worker status and downstream gate status are separate", text)

    def test_boundary_detail_maps_named_results_without_changing_event_vocabulary(self) -> None:
        text = (SKILL_ROOT / "references/handoff-templates.md").read_text()
        event_forms = [
            line.split(" ·", 1)[0]
            for line in text.splitlines()
            if line.startswith(("dispatch ·", "result   ·", "repair   ·", "escalate ·", "closeout ·"))
        ]
        self.assertEqual(event_forms, ["dispatch", "result  ", "repair  ", "escalate", "closeout"])
        self.assertIn(
            "boundaries · <name>=<PASS|FAIL|DEFERRED|NOT_APPLICABLE>...",
            text,
        )
        self.assertIn("adjacent detail line", text)
        self.assertIn("not the downstream `gate` field", text)
        self.assertIn("not a sixth counted event type", text)

    def test_semantic_fingerprint_crosses_boundaries(self) -> None:
        escalation = (SKILL_ROOT / "references/escalation-policy.md").read_text()
        handoff = (SKILL_ROOT / "references/handoff-templates.md").read_text()
        self.assertIn("behavior, boundary, and invariant", escalation)
        self.assertIn("same behavior and invariant", escalation)
        self.assertIn("different boundaries", escalation)
        self.assertIn("fingerprint · value=<behavior|boundary|invariant>", handoff)
        self.assertIn("adjacent to the failing `result`", handoff)
        self.assertIn("before any `repair` or `escalate` event", handoff)
        self.assertIn("reuses that exact fingerprint", handoff)

    def test_cross_boundary_recovery_requires_design_evidence(self) -> None:
        escalation = (SKILL_ROOT / "references/escalation-policy.md").read_text()
        example = escalation.split("## Counting example", 1)[1]

        for contract in (
            "This Balanced-mode example has separate design evidence",
            "settled shared-propagation assumption is false",
            "no local patch within the approved scope can satisfy both acceptance criteria",
            "The repeated fingerprint establishes material similarity only; it does not authorize recovery",
            "enters the still-unused single High recovery diagnostician",
        ):
            self.assertIn(contract, example)

        self.assertLess(
            example.index("separate design evidence"),
            example.index("escalate · from=medium · to=high"),
        )

    def test_mechanical_correction_has_separate_one_shot_limit(self) -> None:
        escalation = (SKILL_ROOT / "references/escalation-policy.md").read_text()
        handoff = (SKILL_ROOT / "references/handoff-templates.md").read_text()
        self.assertIn("one deterministic same-thread mechanical correction", escalation)
        self.assertIn("does not consume the semantic repair allowance", escalation)
        self.assertIn("A second mechanical correction stops automatic handling", escalation)
        self.assertIn("thread that produced the current diff", escalation)
        for field in (
            "TARGET THREAD",
            "EXACT TARGETS / TRANSFORMATION",
            "LAST SEMANTICALLY ACCEPTED DIFF",
            "SEMANTIC-EQUIVALENCE COMMAND / RESULT",
            "FAILED HYGIENE GATE",
            "REQUIRED RERUN",
        ):
            self.assertIn(field, handoff)
        self.assertIn("independent review is not required", handoff)

    def test_review_corrections_share_the_single_semantic_allowance(self) -> None:
        escalation = (SKILL_ROOT / "references/escalation-policy.md").read_text()
        integration = (SKILL_ROOT / "references/superpowers-integration.md").read_text()
        for text in (escalation, integration):
            self.assertIn("one semantic same-thread correction", text)
            self.assertIn("pre-review verification and all Superpowers review stages", text)
            self.assertIn("local review correction consumes it", text)
        self.assertIn("If the allowance is already consumed", integration)
        self.assertIn("Never skip the required review", integration)
        self.assertIn("restart the ladder", integration)

    def test_review_failure_uses_one_mode_routed_debugger_stage(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text()
        escalation = (SKILL_ROOT / "references/escalation-policy.md").read_text()
        integration = (SKILL_ROOT / "references/superpowers-integration.md").read_text()
        routing = (SKILL_ROOT / "references/routing-policy.md").read_text()

        self.assertIn("| Fresh debugger | medium | medium | high |", routing)
        for text in (skill, escalation, integration):
            self.assertIn("single fresh debugger stage", text)
            self.assertIn("Medium in Fast/Balanced and High in Deep", text)
            self.assertIn("If that debugger stage was already consumed", text)
            self.assertIn("Fast stops automatic handling and reports the failed review gate", text)
            self.assertIn("Balanced and Deep may use the still-unused single recovery diagnostician", text)
            self.assertIn("still-unused single recovery diagnostician", text)
            self.assertIn("Only the recovery diagnostician requires contract/design evidence", text)
            self.assertIn("High effort alone does not make a debugger a recovery", text)
            self.assertIn("never repeat the debugger or restart the ladder", text)

        visible_trace = skill.split("## Visible trace", 1)[1].split("## Setup check", 1)[0]
        stop_report = escalation.split("## Stop report", 1)[1].split(
            "Never silently restart the ladder", 1
        )[0]

        self.assertIn(
            "role=debugger · route=<actual-mode-routed-effort>/fresh · mode=<mode>",
            visible_trace,
        )
        self.assertNotIn("fresh medium debugger", visible_trace.lower())
        self.assertNotIn("low repair failed", visible_trace.lower())
        self.assertIn(
            "- debugger: route=<actual-mode-routed-effort>/fresh · mode=<mode> · <outcome>",
            stop_report,
        )
        self.assertIn(
            "- recovery diagnostician: route=high/fresh · <outcome|not-used>",
            stop_report,
        )
        self.assertNotIn("- medium debugger:", stop_report.lower())
        self.assertIn(
            "A Deep debugger-to-recovery transition dispatches the recovery role without an `escalate` event or escalation-count increment",
            escalation,
        )

    def test_boundaries_are_carried_not_selected(self) -> None:
        integration = (SKILL_ROOT / "references/superpowers-integration.md").read_text()
        handoff = (SKILL_ROOT / "references/handoff-templates.md").read_text()
        self.assertIn("Carry only Superpowers-defined execution boundaries", integration)
        self.assertIn("PASS, FAIL, DEFERRED, or NOT_APPLICABLE", handoff)
        self.assertIn("Missing expected boundary evidence is missing context", handoff)

    def test_missing_context_continuation_is_bounded_and_non_escalating(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text()
        escalation = (SKILL_ROOT / "references/escalation-policy.md").read_text()
        handoff = (SKILL_ROOT / "references/handoff-templates.md").read_text()
        integration = (SKILL_ROOT / "references/superpowers-integration.md").read_text()

        for text in (skill, escalation, integration):
            self.assertIn("one bundled same-thread context continuation per worker dispatch", text)
            self.assertIn("does not raise effort", text)
            self.assertIn("does not consume the semantic or mechanical correction allowance", text)
            self.assertIn("any second context request", text)

        self.assertIn(
            "| Same-thread missing-context continuation | 1 per worker dispatch |",
            escalation,
        )
        for field in ("MISSING ITEMS", "CONTINUATION LIMIT", "STOP CONDITIONS"):
            self.assertIn(field, handoff)
        self.assertIn("not a `repair` or `escalate` event", handoff)
        self.assertIn("result · worker=NEEDS_CONTEXT · gate=BLOCKED", handoff)
        self.assertIn(
            "closeout · gate=BLOCKED · escalations=<unchanged> · stop=missing-context",
            handoff,
        )

    def test_compact_closeout_is_required_and_aar_is_on_request(self) -> None:
        text = (SKILL_ROOT / "references/handoff-templates.md").read_text()
        self.assertIn("closeout · gate=<status> · escalations=<count> · stop=<reason>", text)
        self.assertIn("A compact closeout is required", text)
        self.assertIn("Detailed AAR is request-only", text)
        self.assertIn("Usage and worker-count observations are not telemetry or topology decisions", text)

    def test_activation_and_runtime_evidence_boundaries_are_consistent(self) -> None:
        integration = (SKILL_ROOT / "references/superpowers-integration.md").read_text()
        compatibility = (SKILL_ROOT / "references/compatibility.md").read_text()
        test_results = (ROOT / "TEST_RESULTS.md").read_text()
        design = (ROOT / "docs/design.md").read_text()

        self.assertIn(
            "Do not apply Adaptive Effort during brainstorming, architecture, or pre-implementation analysis.",
            integration,
        )
        self.assertNotIn("unless the user explicitly asks for a separate delegated analysis", integration)
        for text in (compatibility, test_results):
            self.assertIn("spawn/tool path completed with the requested settings", text)
            self.assertIn("does not independently observe or prove", text)
        self.assertIn("The static doctor checks only", design)
        for unsupported_check in (
            "spawn_agent available",
            "child effort override available",
            "fresh-context spawn available",
            "Adaptive role instructions available",
        ):
            self.assertNotIn(unsupported_check, design)

    def test_templates_require_evidence(self) -> None:
        text = (SKILL_ROOT / "references/handoff-templates.md").read_text()
        self.assertIn("Do not claim success without fresh evidence", text)
        self.assertIn("Do not weaken, delete, or bypass acceptance tests", text)
        self.assertIn("DESIGN_CONFLICT", text)

    def test_implicit_activation_is_narrow_and_visible(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text()
        self.assertIn("Activate implicitly only when", text)
        self.assertIn("Do not activate for generic delegation", text)
        self.assertIn(
            "Adaptive Effort: <mode> · implementer inherited-model/<effort> · fresh context",
            text,
        )

    def test_spawn_policy_uses_supported_fields_only(self) -> None:
        texts = [path.read_text() for path in SKILL_ROOT.rglob("*.md")]
        self.assertFalse(any("agent_type:" in text for text in texts))
        self.assertTrue(any("followup_task" in text for text in texts))


if __name__ == "__main__":
    unittest.main()
