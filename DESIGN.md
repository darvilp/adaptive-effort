# Adaptive Effort design snapshot

The canonical product design is maintained in [`docs/design.md`](docs/design.md).

## Purpose

Adaptive Effort augments Superpowers with a compute policy. Superpowers decides what engineering workflow to run; Adaptive Effort decides the reasoning effort assigned to each delegated Codex role.

## Core rules

The fixed values below are the no-override defaults. Explicit role assignments patch the selected mode's profile. Dispatch implementation with `profile.implementer` and debugging with `profile.debugger`. Reviews use `profile.routine_review` or `profile.high_risk_review`. Recovery uses `profile.recovery`. In Fast, recovery also requires `profile.recovery_explicitly_requested` and independent contract/design evidence. A semantic or mechanical repair retains the actual writer route.

1. Parent model and effort remain user-selected.
2. Child model is inherited.
3. No-override implementation uses Low in Fast and Balanced and Medium in Deep.
4. One local failure gets one same-thread repair at the actual writer route.
5. A broader implementation failure gets one fresh debugger at `profile.debugger`.
6. Recovery uses `profile.recovery` only with independent contract/design evidence. Fast also requires explicit recovery provenance.
7. Environment failures do not trigger more reasoning.
8. Child handoffs are compact and fresh.
9. Superpowers quality gates remain intact.
10. Automatic execution stops at a fixed circuit breaker.

## Packaging decision

The plugin is skills-only because the current Codex plugin manifest does not install custom-agent TOML definitions. The skill expresses roles through explicit spawn arguments and role prompts.

## Distribution

The plugin is prepared for the Universal Plugins Directory. The Git repository is also a Git marketplace through `.agents/plugins/marketplace.json`, and the plugin lives under `plugins/adaptive-effort`.

## Success measure

Compare equivalent Superpowers tasks with and without Adaptive Effort, measuring completion, tests, review findings, wall time, input/reasoning tokens, child count, and escalation rate.
