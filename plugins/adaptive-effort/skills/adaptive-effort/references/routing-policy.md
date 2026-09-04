# Routing policy

## Invariants

- Parent model and effort remain user-controlled.
- Unspecified roles inherit the parent model by omitting `model`.
- Explicit role model overrides pass the user's exact model ID unchanged.
- Child context is fresh unless a concrete dependency requires a small recent-turn fork.
- `xhigh`, `max`, and `ultra` are not selected automatically.
- Superpowers workflow requirements outrank cost-saving preferences.
- Planned medium/high reviews never count as escalations. They are planned routes selected by Superpowers.

## Mode matrix

This matrix defines the no-override defaults. Resolve the task-local profile
before dispatch; later routing consumes the resolved profile rather than
reading this matrix again.

Explicit role assignments patch the selected mode's profile. Dispatch implementation with `profile.implementer` and debugging with `profile.debugger`. Reviews use `profile.routine_review` or `profile.high_risk_review`. Recovery uses `profile.recovery`. In Fast, recovery also requires `profile.recovery_explicitly_requested` and independent contract/design evidence. A semantic or mechanical repair retains the actual writer route.

| Role | Fast | Balanced | Deep |
|---|---|---|---|
| Implementer | low | low | medium |
| Same-thread local repair | low, once | low, once | same effort as implementer, once |
| Fresh debugger | medium | medium | high |
| Recovery diagnostician | high only when explicitly requested; not automatic | high, only with independent contract/design evidence | high, only with independent contract/design evidence |
| Routine spec review | low | medium | high |
| Routine quality review | low | medium | high |
| High-risk review | high | high | high |

Deep always starts implementation at medium. Adaptive Effort assigns no implementation work category before dispatch.

Fast stops before automatic High recovery. An explicit user instruction may request a High recovery role; otherwise return to the user or planning after the debugger. Balanced and Deep retain evidence-gated automatic recovery.

The repair row is not a spawn route. It is one `followup_task` on the thread whose current diff is being repaired. Use `repair_effort(current_writer_route)` so the repair retains that actual writer route's resolved effort, whether the writer is an implementer, debugger, or recovery worker.

## Risk signals

Treat a task as higher risk when it involves one or more of:

- authentication, authorization, secrets, or cryptography
- concurrency, distributed coordination, or data races
- schema or data migrations
- public API or protocol compatibility
- irreversible operations
- money, billing, healthcare, legal, or safety-critical behavior
- broad cross-cutting changes
- weak or unavailable deterministic tests

Risk can raise review effort without raising the initial implementer.

Adaptive Effort records a dispatch purpose as `implementation`, `planned-review`, `debug`, or `recovery`. Only corrective upward effort transitions increment the escalation count.

## Spawn defaults

These are dispatch mechanics. Effort always comes from the resolved profile.
Model comes from the matching role override, or is omitted for inheritance.

### Implementer

```text
model: exact `implementer` override, otherwise omit
reasoning_effort: `profile.implementer`
fork_turns: none
```

### Debugger

```text
model: exact `debugger` override, otherwise omit
reasoning_effort: `profile.debugger`
fork_turns: none
```

### Recovery diagnostician

```text
model: exact `recovery` override, otherwise omit
reasoning_effort: `profile.recovery`
fork_turns: none
```

### Reviewer

Use the role selected by Superpowers and prefer a fresh handoff. Use the exact
`routine-review` or `high-risk-review` model override when present; otherwise
omit `model`. Use `profile.routine_review` for routine review and
`profile.high_risk_review` when Superpowers identifies a high-risk review.

## Task-local caps

Explicit user limits take precedence:

- no delegation → do the task in the parent
- low only → no medium/high child
- cap at medium → stop and report before high recovery
- no escalation → one initial child only unless the user also permits repair

A cap and a role assignment that disagree are a conflict. For example, `keep
implementation low` conflicts with `implementer=high`.
Report the conflicting role and value and stop before dispatch. Never clamp a
role assignment or pick one instruction silently.

## Task-local effort profiles

The five canonical override roles are `implementer`, `routine-review`,
`high-risk-review`, `debugger`, and `recovery`. Each accepts
`low, medium, high, xhigh, max, or ultra`.
Explicit per-role values override the selected mode;
roles without assignments retain the mode matrix value. Reject an unknown
role, unsupported value, or duplicate role assignment.

Resolve this profile once after validating caps and assignments. Every later
implementation, review, debugger, and recovery dispatch reads its effort from
the resolved profile.

The resolved profile also records `profile.recovery_explicitly_requested`.
This boolean is false for the Fast default `recovery="high"` and true only when
the user supplied a recovery effort or model assignment. A model-only recovery assignment
sets the boolean. Fast recovery requires this boolean
and independent contract/design evidence.

Repair is not an override role. Same-thread semantic and mechanical repairs
use `repair_effort(current_writer_route)` to retain the actual implementer,
debugger, or recovery writer effort. Explicit high efforts do not alter the
automatic policy: Adaptive Effort still never selects `xhigh`, `max`, or
`ultra` unless the user assigns one.

## Task-local model profiles

The model override keys are the same five canonical roles as effort overrides.
Each value is an exact model ID. Unspecified roles inherit the parent model.
Model and effort overrides resolve independently, and repairs remain on the
actual writer thread so they retain both values. Reject unknown roles, empty
values, surrounding whitespace, and duplicate assignments. Do not create
friendly aliases or pin a model in any mode default.

The routing-plan command reports local-client candidates from `codex debug
models`, including their supported efforts. This is selection help, not runtime
proof: the executable on `PATH` may differ from the Desktop or IDE process. The
active spawn host is authoritative. An unlisted exact model proceeds to host
validation; a host rejection stops the route with no silent fallback.

Check host/model compatibility before dispatch when the active host exposes it.
Stop and report an unsupported requested combination rather than silently
lowering or replacing the model or effort.

Fast recovery remains evidence-gated. An explicit `recovery` model or effort assignment allows
the recovery role only after independent contract/design evidence; without
that evidence, stop. Without an explicit recovery assignment, Fast stops before
recovery as usual.

Append active values to the initial trace in canonical role order:

```text
Adaptive Effort: <mode> · implementer inherited-model/<effort> · fresh context · overrides=<canonical-role:effort,...>
```

For model or mixed overrides, use:

```text
Adaptive Effort: <mode> · implementer <model-or-inherited>/<effort> · fresh context · model-overrides=<canonical-role:model,...> · effort-overrides=<canonical-role:effort,...>
```
