# Adaptive Effort

Adaptive Effort is a skills-only Codex plugin that adds reasoning-effort routing and bounded escalation to Superpowers implementation workflows.

It keeps the parent model and effort selected by the user, then applies this Balanced default child ladder:

```text
low implementation
  → one low repair
  → fresh medium debugger
  → fresh high recovery diagnosis
  → stop or return to planning
```

Superpowers remains responsible for planning, TDD, reviews, and verification.

## Routing modes

| Route | Fast | Balanced | Deep |
|---|---:|---:|---:|
| Bounded implementation | Low | Low | Low |
| Genuine integration implementation | Low | Low | Medium |
| Same-thread repair | Retains effort, once | Retains effort, once | Retains effort, once |
| Fresh debugger and routine reviews | Medium | Medium | High |
| High-risk review | High | High | High |
| Recovery diagnostician | High, only with independent contract/design evidence | High, only with independent contract/design evidence | High, only with independent contract/design evidence |

Balanced is the default; Fast currently has the same defined routes and never weakens reviews or gates. Deep raises only genuine integration work, debugging, and routine reviews. Planned reviewers are not escalation events. Adaptive Effort never automatically chooses `xhigh`, `max`, or `ultra`.

Superpowers coordinates the approved plan, chooses tasks, boundaries, worker count and topology, and requires TDD. A fresh implementer handles each bounded task. Superpowers runs specification review before code-quality review; findings are corrected and re-reviewed before final verification. Adaptive Effort changes child effort and handoffs, classifies failures, and bounds correction and escalation. Worker count and aggregate usage are optional AAR observations, not routing inputs or per-agent accounting promises.

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
