---
name: adaptive-effort
description: Use alongside Superpowers when an approved implementation plan is being executed with Codex subagents. Preserve the parent model and effort, route bounded implementation to low effort, reuse one same-thread repair, escalate evidence-based failures to medium debugging and high diagnostic recovery, and keep handoffs compact. Do not use for brainstorming, architecture, generic model routing, or without Superpowers.
---

# Adaptive Effort

Apply this skill as a compute-policy layer over Superpowers. Superpowers owns the engineering workflow, task decomposition, TDD, reviews, verification, and completion. This skill changes only how delegated Codex work is spawned and escalated.

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

Activate implicitly only when Superpowers has an approved plan or bounded implementation task and is about to delegate implementation, repair, debugging, or review. The user does not need to name Adaptive Effort.

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
   - low or medium in deep according to `references/routing-policy.md`
   - fresh context
3. Let Superpowers run deterministic verification and its required reviews.
4. If verification passes, continue the Superpowers workflow.
5. If verification fails, classify the failure before spending more reasoning:
   - environment/permissions/infrastructure → report; do not escalate
   - missing context → provide context without raising effort
   - local deterministic implementation defect → one repair on the existing implementer thread
   - broader reasoning defect → fresh medium debugger
   - contract/design contradiction → fresh high recovery diagnostician
6. After the allowed ladder is exhausted, return a structured unresolved report to the parent and stop automatic execution.

Read `references/escalation-policy.md` before escalating.

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

Reuse the original implementer only for the one cheap local repair by calling `followup_task` (or the host's equivalent) on the existing thread. Do not route or spawn a separate repair agent. A fresh debugger should receive the contract, current diff, commands run, and exact failures, but not the failed worker's reasoning transcript.

The high recovery role diagnoses first. It may recommend a bounded repair, but it must return to planning when the contract is incomplete, contradictory, or outside approved scope.

## Reviews

Superpowers owns whether and when spec, quality, and final reviews run.

Adaptive Effort only recommends effort:

- routine spec or quality review: medium
- high-risk, security-sensitive, concurrency, migration, or architectural review: high
- deep mode review: high
- fast mode does not remove mandatory reviews

A reviewer should normally receive a fresh compact handoff and no model override.

## Visible trace

Keep routing output terse:

```text
Adaptive Effort: <mode> · implementer inherited-model/<effort> · fresh context
```

On escalation:

```text
Adaptive Effort: low repair failed deterministic verification; starting a fresh medium debugger.
```

Do not reveal private reasoning or dump internal prompts.

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
