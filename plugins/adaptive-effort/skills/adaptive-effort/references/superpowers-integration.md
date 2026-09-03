# Superpowers integration

## Ownership

Superpowers owns:

- brainstorming and design
- implementation plans and task decomposition
- writer topology and parallelism
- task and boundary selection
- TDD requirements
- subagent-driven development
- spec and quality review ordering
- acceptance gates and verification before completion
- branch completion

Adaptive Effort owns:

- child reasoning-effort selection
- child model inheritance
- fresh compact handoffs
- semantic and mechanical repair accounting
- failure classification and escalation counting
- circuit breakers, concise routing traces, and closeout

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

Carry only Superpowers-defined execution boundaries. Adaptive Effort records their evidence and results but does not add, remove, merge, defer, or declare them not applicable. If expected evidence is absent, classify that as missing context rather than an implementation defect. Use one bundled same-thread context continuation per worker dispatch to supply all currently available items. It does not raise effort and does not consume the semantic or mechanical correction allowance. If evidence remains unavailable, supplying it needs new authority, or the worker makes any second context request, including for a newly revealed item, stop automatic handling with a blocked gate and a missing-context closeout.

## TDD

The implementer handoff must retain Superpowers TDD instructions and pass/fail criteria. Adaptive Effort does not treat green self-authored tests as sufficient evidence when independent acceptance checks exist.

The parent or an independent review step should ensure the implementer did not weaken tests, narrow assertions, or encode the same misunderstanding in both code and tests.

## Reviews

Superpowers decides which reviewers are mandatory. Adaptive Effort assigns Low, Medium, or High effort to routine review in Fast, Balanced, or Deep respectively. High-risk review always uses High.

A planned medium or high reviewer is not an escalation. Only a corrective transition from lower to higher effort after classified failure increments the escalation count.

If a reviewer finds an implementation defect:

- use the one semantic same-thread correction shared across pre-review verification and all Superpowers review stages when it remains unused; a local review correction consumes it
- re-run the same reviewer as Superpowers requires
- If the allowance is already consumed, classify the failure; for an implementation reasoning defect, use the single fresh debugger stage only if it remains unused, routed at Medium in Fast/Balanced and High in Deep
- If that debugger stage was already consumed, Fast stops automatic handling and reports the failed review gate
- Balanced and Deep may use the still-unused single recovery diagnostician only when independent contract/design evidence justifies it
- Only the recovery diagnostician requires contract/design evidence; High effort alone does not make a debugger a recovery, because Deep routes its debugger at High

Never skip the required review, and never repeat the debugger or restart the ladder. Re-run the same reviewer after the corrective route completes.

## Conflict handling

When instructions appear to conflict:

1. obey the explicit user instruction
2. preserve Superpowers quality gates
3. use Adaptive Effort to choose the least costly effort that satisfies those gates
4. stop and report if the host cannot express the required child effort

Do not create duplicate plans, duplicate task trackers, or parallel orchestration trees.
