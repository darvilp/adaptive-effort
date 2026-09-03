# Adaptive Effort

Adaptive Effort is a skills-only Codex plugin that adds reasoning-effort routing and bounded escalation to Superpowers implementation workflows.

It keeps the parent model and effort selected by the user. This example shows the Balanced no-override defaults:

```text
profile.implementer
  → one same-thread repair at the actual writer route
  → fresh profile.debugger
  → fresh profile.recovery after authorization
  → stop or return to planning
```

Superpowers remains responsible for planning, TDD, reviews, and verification.

## No-override defaults

The matrix contains the no-override defaults. Explicit role assignments patch the selected mode's profile. Dispatch implementation with `profile.implementer` and debugging with `profile.debugger`. Reviews use `profile.routine_review` or `profile.high_risk_review`. Recovery uses `profile.recovery`. In Fast, recovery also requires `profile.recovery_explicitly_requested` and independent contract/design evidence. A semantic or mechanical repair retains the actual writer route.

| Route | Fast | Balanced | Deep |
|---|---:|---:|---:|
| Implementation | Low | Low | Medium |
| Same-thread repair | Retains effort, once | Retains effort, once | Retains effort, once |
| Fresh debugger | Medium | Medium | High |
| Routine spec and quality reviews | Low | Medium | High |
| High-risk review | High | High | High |
| Recovery diagnostician | High only when explicitly requested; not automatic | High, only with independent contract/design evidence | High, only with independent contract/design evidence |

Balanced is the default. The matrix applies only to roles without explicit assignments. No upfront work classification is required. Required reviews still run. Planned reviewers are not escalation events. Adaptive Effort never automatically chooses `xhigh`, `max`, or `ultra`.

Superpowers coordinates the approved plan, chooses tasks, boundaries, worker count and topology, and requires TDD. A fresh implementer handles each approved task. Superpowers runs specification review before code-quality review; findings are corrected and re-reviewed before final verification. Adaptive Effort changes child effort and handoffs, classifies failures, and bounds correction and escalation. Worker count and aggregate usage are optional AAR observations, not routing inputs or per-agent accounting promises.

Superpowers also chooses task boundaries, writer topology, parallelism, and acceptance gates. Adaptive Effort carries those choices into compact child handoffs, classifies failures, counts only corrective upward effort transitions, and records a compact closeout. Planned higher-effort reviews are not escalations.

One semantic correction is shared across verification and every Superpowers review stage. A separate one-shot mechanical correction targets the writer of the current diff. Adaptive Effort never chooses new execution boundaries. Missing expected boundary evidence gets one bundled same-thread continuation at the existing effort; another request or unavailable evidence stops automatic handling without spending a repair or escalation stage.

## Requirements

- Superpowers installed and enabled
- Codex subagent support
- a Codex host that supports plugins and explicit child reasoning effort

See `skills/adaptive-effort/references/compatibility.md` for the snapshot limitations.

## Normal use

No manual skill invocation is normally needed:

```text
Implement the approved plan.
```

Natural overrides include:

```text
Use fast handling for this.
Use deep handling for this.
Do this directly; don't delegate.
Do not escalate above Medium.
```

## Setup check

Ask Codex:

```text
Check Adaptive Effort setup.
```

This returns static, surface-tagged readiness without spawning a child. For one runtime smoke spawn, ask:

```text
Check Adaptive Effort setup live.
```

Or keep the shell in the active project and run the installed checker by absolute path:

```bash
python3 /absolute/path/to/installed/adaptive-effort/skills/adaptive-effort/scripts/doctor.py \
  --project-dir "$PWD"
```

`--project-dir` selects the active project working directory whose applicable trusted `.codex/config.toml` layers are inspected. Pass the current nested working directory when nested project configuration may apply.

## Important platform note

The current plugin manifest format does not install custom Codex agent TOMLs. Adaptive Effort supplies explicit `reasoning_effort`, inherited model, fresh context, and role instructions on each spawn without requiring an agent-type field.

Codex IDE extensions do not currently support plugins. Use the Codex app or CLI for Adaptive Effort.
