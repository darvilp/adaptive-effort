# Routing policy

## Invariants

- Parent model and effort remain user-controlled.
- Child model is inherited by omitting `model`.
- Child context is fresh unless a concrete dependency requires a small recent-turn fork.
- `xhigh`, `max`, and `ultra` are not selected automatically.
- Superpowers workflow requirements outrank cost-saving preferences.
- Planned medium/high reviews never count as escalations. They are planned routes selected by Superpowers.

## Mode matrix

| Role | Fast | Balanced | Deep |
|---|---|---|---|
| Bounded implementer | low | low | low |
| Multi-file integration implementer | low | low | medium |
| Same-thread local repair | low, once | low, once | same effort as implementer, once |
| Fresh debugger | medium | medium | high |
| Recovery diagnostician | high, only with independent contract/design evidence | high, only with independent contract/design evidence | high, only with independent contract/design evidence |
| Routine spec review | medium | medium | high |
| Routine quality review | medium | medium | high |
| High-risk review | high | high | high |

Deep mode raises implementation to medium only when the task requires real integration judgment. A large line count by itself is not sufficient.

The repair row is not a spawn route. It is one `followup_task` on the existing implementer thread, so it retains that thread's original Low or Medium effort.

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

### Implementer

```text
model: omit
reasoning_effort: low (or medium for deep integration work)
fork_turns: none
```

### Debugger

```text
model: omit
reasoning_effort: medium (high in deep)
fork_turns: none
```

### Recovery diagnostician

```text
model: omit
reasoning_effort: high
fork_turns: none
```

### Reviewer

Use the role selected by Superpowers. Omit the model, choose medium or high effort from the matrix, and prefer a fresh handoff.

## Task-local caps

Explicit user limits take precedence:

- no delegation → do the task in the parent
- low only → no medium/high child
- cap at medium → stop and report before high recovery
- no escalation → one initial child only unless the user also permits repair
