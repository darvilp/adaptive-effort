# Adaptive Effort design snapshot

The canonical product design is maintained in [`docs/design.md`](docs/design.md).

## Purpose

Adaptive Effort augments Superpowers with a compute policy. Superpowers decides what engineering workflow to run; Adaptive Effort decides the reasoning effort assigned to each delegated Codex role.

## Core rules

1. Parent model and effort remain user-selected.
2. Child model is inherited.
3. Implementation starts at Low in Fast and Balanced; Deep implementation starts at Medium.
4. One local failure gets one same-thread repair at the existing worker's effort.
5. Broader implementation failure gets a fresh Medium debugger in Fast/Balanced or High debugger in Deep.
6. Independent contract or architecture evidence can authorize one fresh High recovery diagnosis in Balanced/Deep; Fast stops before automatic recovery.
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
