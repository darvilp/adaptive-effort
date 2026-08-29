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
        self.assertIn("does not remove the two-stage review", text)

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
