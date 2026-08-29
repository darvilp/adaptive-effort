# Adaptive Effort

Adaptive Effort is a skills-only Codex plugin that adds reasoning-effort routing and bounded escalation to Superpowers implementation workflows.

It keeps the parent model and effort selected by the user, then applies this default child ladder:

```text
low implementation
  → one low repair
  → fresh medium debugger
  → fresh high recovery diagnosis
  → stop or return to planning
```

Superpowers remains responsible for planning, TDD, reviews, and verification.

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
