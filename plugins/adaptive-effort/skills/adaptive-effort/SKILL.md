---
name: adaptive-effort
description: Use alongside Superpowers when an approved implementation task is being executed with Codex subagents. Do not use for brainstorming, architecture, generic model routing, or without Superpowers.
---

# Adaptive Effort

Apply this skill as a compute-policy layer over Superpowers. Superpowers owns task decomposition, writer topology, parallelism, TDD, boundary selection, reviews, acceptance gates, and completion. This skill owns child effort and context, compact handoffs, failure classification, escalation counting, circuit breakers, and closeout.

## Hard boundaries

- Do not start a second development lifecycle.
- Do not replace or skip any Superpowers-required step.
- Do not alter the parent model or parent reasoning effort.
- Omit `model` on child spawns so the child inherits the parent model.
- Do not automatically select `xhigh`, `max`, or `ultra`.
- Do not run multiple write-capable implementation agents concurrently unless Superpowers has explicitly proven their write sets are disjoint.
- Stop at the circuit breaker instead of creating an open-ended repair or review loop.
- If Superpowers is unavailable, explain the dependency once when this workflow is relevant, then stop Adaptive Effort handling.

## Determine the mode

Default to **balanced**.

Natural task-local overrides:

- “fast handling” → fast
- “deep handling” → deep
- “do this directly” or “don't delegate” → bypass Adaptive Effort delegation
- “keep implementation low” → never raise the implementer above low
- “do not escalate above Medium” → cap escalation at medium

Modes affect child routing only. They never change the parent session.

Read `references/routing-policy.md` when the mode or reviewer effort is not obvious.

## Integration point

Activate implicitly only when Superpowers has an approved implementation task and is about to delegate implementation, repair, debugging, or review. The user does not need to name Adaptive Effort.

Do not activate for generic delegation, brainstorming, architecture, or work that is not currently following the Superpowers workflow. Explicit user instructions to bypass delegation or Adaptive Effort take precedence.

When implicit activation begins, emit the one-line routing trace before the first worker is spawned.

Keep Superpowers' task order and review order. For each child spawn, add the Adaptive Effort arguments and compact role handoff described here.

### Spawn mechanics

For current Codex multi-agent tools:

- omit `model`
- set `reasoning_effort` explicitly
- set `fork_turns="none"` for fresh compact handoffs
- express the implementation, debugging, recovery, or review role in the spawn message; do not require an `agent_type` spawn field
- use Superpowers' selected review role; Adaptive Effort supplies effort, not a competing review prompt
- if the host exposes an older spawn API, use the equivalent fresh-context option (`fork_context=false`) and explicit reasoning effort

A plugin cannot currently install standalone custom-agent TOML files. The role instructions therefore travel in the spawn message. Do not look for Adaptive Effort custom agents on disk.

## Per-task flow

1. Build a compact implementation contract from the approved Superpowers plan.
2. Spawn one fresh implementer:
   - inherited model
   - low effort in fast/balanced
   - medium effort in deep
   - fresh context
3. Let Superpowers run deterministic verification and its required reviews.
4. If verification passes, continue the Superpowers workflow.
5. If verification fails, classify the failure before spending more reasoning:
   - environment/permissions/infrastructure → report; do not escalate
   - missing context → use the one bundled same-thread context continuation per worker dispatch; keep the same effort and stop on another context request
   - local deterministic implementation defect → use the one semantic same-thread correction if it remains available across verification and review
   - broader reasoning defect → the single fresh debugger, at medium in fast/balanced or high in deep
   - contract/design contradiction → stop in fast; in balanced/deep, use a fresh high recovery diagnostician only with independent contract/design evidence
6. After the allowed ladder is exhausted, return a structured unresolved report to the parent and stop automatic execution.

The parent keeps an ephemeral routing ledger for the current run. It records the initial routing trace, dispatches, worker results, downstream gates, repairs, corrective upward transitions, and closeout. It is a compact human-readable trace, not persistent state, telemetry, or an executable API. Planned medium/high reviews do not count as escalations. Count only corrective upward effort transitions.

Read `references/escalation-policy.md` before escalating.

Missing-context handling does not raise effort and does not consume the semantic or mechanical correction allowance. Supply every concrete item currently available from the approved plan or repository in the one continuation. If any second context request comes from that worker, required evidence is unavailable, or new authority is needed, stop automatic handling with a blocked gate and a missing-context closeout.

## Handoff discipline

Never hand a child the full planning transcript by default. Send:

- exact task and objective
- required behavior and non-goals
- settled architecture decisions
- stable interfaces and invariants
- relevant file pointers
- acceptance and regression checks
- allowed write scope
- current diff and exact failure output when debugging
- required final status and changed-file list

Use the templates in `references/handoff-templates.md`.

## Repair and escalation

The normal balanced ladder is:

```text
low implementer
    → one same-thread low repair
    → fresh medium debugger
    → fresh high recovery diagnostician
    → stop or return to planning
```

Deep always starts implementers at Medium. Fast stops automatic handling before High recovery.

Use one semantic same-thread correction across pre-review verification and every Superpowers review stage for the implementation task. Call `followup_task` (or the host's equivalent) on the thread whose local implementation is being corrected. A local review correction consumes the allowance if unused. If the allowance is already consumed, classify the failure. For an implementation reasoning defect, use the single fresh debugger stage only if it remains unused, routed at Medium in Fast/Balanced and High in Deep. If that debugger stage was already consumed, Fast stops automatic handling and reports the failed review gate. Balanced and Deep may use the still-unused single recovery diagnostician only when independent contract/design evidence justifies it. Only the recovery diagnostician requires contract/design evidence. High effort alone does not make a debugger a recovery, because Deep routes its debugger at High. Never skip a required review, and never repeat the debugger or restart the ladder.

If contract/design evidence authorizes recovery after a Balanced or Deep debugger, dispatch the separate recovery role at High. Fast stops before that automatic recovery stage. Do not emit or count a Deep High-to-High escalation because the effort did not increase.

One deterministic same-thread mechanical correction is also allowed per implementation task. It targets the thread that produced the current diff being checked, including an implementer, debugger, or explicitly authorized recovery writer. It has its own one-shot limit and does not consume the semantic repair allowance. Follow the template, proof, and stop rules in the references.

The high recovery role diagnoses first. It may recommend a bounded repair, but it must return to planning when the contract is incomplete, contradictory, or outside approved scope.

## Reviews

Superpowers owns whether and when spec, quality, and final reviews run.

Adaptive Effort only recommends effort:

- fast routine spec or quality review: low
- balanced routine spec or quality review: medium
- deep routine spec or quality review: high
- high-risk, security-sensitive, concurrency, migration, or architectural review: high
- fast mode does not remove mandatory reviews

A reviewer should normally receive a fresh compact handoff and no model override.

## Visible trace

Keep routing output terse:

```text
Adaptive Effort: <mode> · implementer inherited-model/<effort> · fresh context
```

On escalation:

```text
Adaptive Effort: same-effort repair failed deterministic verification; starting role=debugger · route=<actual-mode-routed-effort>/fresh · mode=<mode>.
```

Do not reveal private reasoning or dump internal prompts.

Use the compact event forms in `references/handoff-templates.md`. Always separate worker status from downstream gate status and finish with a compact closeout.

## Setup check

When the user asks to check or diagnose Adaptive Effort:

1. Keep the process working directory at the user's active project. Run this skill's doctor by absolute path with `python3 <absolute-skill-directory>/scripts/doctor.py --json --project-dir <absolute-active-project-directory>` when local execution is available. Do not change into the installed skill directory before running it.
2. Report the `BLOCKED` or `STATIC_READY` result and keep each check attached to its Windows, WSL, Linux, CLI, or current-host surface.
3. Do not spend a child spawn during the normal static setup check.
4. Only when the user explicitly asks for a live setup check and the host exposes `spawn_agent`, perform one read-only smoke spawn:
   - omit model
   - request low reasoning effort
   - use fresh context
   - ask the child to return exactly `ADAPTIVE_EFFORT_SMOKE_OK`
   - close the child afterward
5. Report `RUNTIME_VERIFIED` only when the smoke child returns the exact token. This proves the child spawn/tool path completed with the requested settings, not independently observed model, effort, or context metadata. Record any direct host or UI metadata separately. Otherwise retain the static readiness and report the runtime failure separately.

Never let a broken adjacent-surface CLI override a healthy active surface. Adjacent failures remain visible as informational evidence.

## References

- `references/routing-policy.md` — role and mode matrix
- `references/escalation-policy.md` — failure classification and circuit breakers
- `references/handoff-templates.md` — compact spawn messages
- `references/superpowers-integration.md` — ownership and review integration
- `references/compatibility.md` — supported surfaces and current platform limits
