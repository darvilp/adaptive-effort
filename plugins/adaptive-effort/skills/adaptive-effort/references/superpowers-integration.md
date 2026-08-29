# Superpowers integration

## Ownership

Superpowers owns:

- brainstorming and design
- implementation plans and task boundaries
- TDD requirements
- subagent-driven development
- spec and quality review ordering
- verification before completion
- branch completion

Adaptive Effort owns:

- child reasoning-effort selection
- child model inheritance
- fresh compact handoffs
- one cheap repair
- evidence-based escalation
- circuit breakers and concise routing traces

Explicit user instructions outrank both. Superpowers workflow requirements outrank Adaptive Effort cost preferences.

## Where to apply

Apply Adaptive Effort when Superpowers is about to dispatch:

- an implementation worker
- a repair worker
- a debugger after implementation failure
- a spec, quality, or final reviewer
- a recovery/diagnostic agent

Do not apply Adaptive Effort during brainstorming, architecture, or pre-implementation analysis. A request to delegate analysis does not activate effort routing. If the user explicitly asks to use Adaptive Effort before implementation, explain that it applies only after Superpowers has an approved implementation plan. The parent session remains at the user-selected model and effort.

## Subagent-driven development

Preserve these Superpowers semantics:

- one fresh implementation context per plan task
- no full parent-history inheritance
- implementer statuses and questions are handled before review
- spec review precedes code-quality review
- review findings are fixed and re-reviewed
- final verification uses fresh evidence
- do not pause between ordinary plan tasks solely for confirmation

Adaptive Effort changes the spawn effort and bounds repeated failures. It does not remove the two-stage review.

## TDD

The implementer handoff must retain Superpowers TDD instructions and pass/fail criteria. Adaptive Effort does not treat green self-authored tests as sufficient evidence when independent acceptance checks exist.

The parent or an independent review step should ensure the implementer did not weaken tests, narrow assertions, or encode the same misunderstanding in both code and tests.

## Reviews

Superpowers decides which reviewers are mandatory. Adaptive Effort assigns medium effort to routine review and high effort to high-risk/deep review.

If a reviewer finds an implementation defect:

- send one focused correction to the existing implementer when it remains local
- re-run the same reviewer as Superpowers requires
- if substantially the same issue persists twice, classify it instead of looping indefinitely

## Conflict handling

When instructions appear to conflict:

1. obey the explicit user instruction
2. preserve Superpowers quality gates
3. use Adaptive Effort to choose the least costly effort that satisfies those gates
4. stop and report if the host cannot express the required child effort

Do not create duplicate plans, duplicate task trackers, or parallel orchestration trees.
