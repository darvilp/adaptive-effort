# Adaptive Effort for Superpowers / Codex

Adaptive Effort is a Codex community-marketplace plugin that routes Superpowers implementation work across reasoning-effort levels.

The user-selected parent model and effort stay untouched. Routine implementation starts at low effort, deterministic failures get one cheap repair, and fresh higher-effort agents are used only when evidence warrants them.

## What it changes

```text
Superpowers
  design → plan → TDD → implementation → review → verification

Adaptive Effort
  parent unchanged
  implementation: low
  local repair: same thread, once; retains its effort
  debugger: mode-routed; medium in fast/balanced, high in deep
  recovery diagnosis: high
  child model: inherited
  child context: fresh and compact
```

It does not replace Superpowers or implement a separate development methodology.

Superpowers chooses task decomposition, writer topology, parallelism, execution boundaries, reviews, and acceptance gates. Adaptive Effort supplies child effort and context, compact handoffs, failure classification, escalation counting, circuit breakers, and closeout. Planned medium/high reviews do not count as escalations; only corrective upward effort transitions do.

The parent keeps a human-readable routing trace for the current run. It separates worker status from downstream gate status and carries Superpowers-defined boundary results in adjacent detail lines. Semantic failures record a fingerprint before correction or escalation. The trace is ephemeral, not a ledger API or telemetry system.

Missing context gets at most one bundled same-thread continuation per worker dispatch at the existing effort. A second request, unavailable evidence, or need for new authority stops automatic handling without consuming a repair or escalation stage.

## Prerequisite

Install and enable **Superpowers** from Codex's plugin directory first.

Adaptive Effort feature-detects the Superpowers workflow skills. It does not install or vendor Superpowers.

## Install from a Git marketplace

```bash
codex plugin marketplace add darvilp/adaptive-effort --ref main
codex plugin add adaptive-effort@adaptive-effort
```

Start a new Codex session after installation.

## Install from a local checkout

From the repository root:

```bash
codex plugin marketplace add "$(pwd)"
codex plugin add adaptive-effort@adaptive-effort
```

Start a new Codex session.

## Update

```bash
codex plugin marketplace upgrade adaptive-effort
codex plugin add adaptive-effort@adaptive-effort
```

Then start a new session.

## Use

Work naturally through Superpowers:

```text
Design and implement retry handling without changing the public API.
```

or, after approving a plan:

```text
Implement the approved plan.
```

Adaptive Effort defaults to balanced routing. Task-local switches:

```text
Use fast handling for this.
Use deep handling for this.
Do this directly; don't delegate.
Keep implementation at Low.
Do not escalate above Medium.
```

The IDE or Desktop model/effort selector remains authoritative for the parent.

## Diagnostic

Ask:

```text
Check Adaptive Effort setup.
```

The normal check is static and returns `BLOCKED` or `STATIC_READY` with separate active and adjacent surface evidence. It does not spend a child spawn.

To verify the active host at runtime, ask explicitly:

```text
Check Adaptive Effort setup live.
```

A smoke child requested with inherited model, low effort, and fresh context upgrades the result to `RUNTIME_VERIFIED` when it returns the exact token. That token proves the child spawn/tool path completed with the requested settings. It does not independently observe the child's model, effort, or context metadata.

Direct static check from the active project directory, using the installed checker path:

```bash
python3 /absolute/path/to/installed/adaptive-effort/skills/adaptive-effort/scripts/doctor.py \
  --project-dir "$PWD"
```

`--project-dir` identifies the active project working directory whose applicable trusted `.codex/config.toml` layers are inspected. Pass an absolute path when it differs from `$PWD`.

## Current platform constraints

This snapshot uses only supported plugin surfaces:

- Plugins currently bundle skills, but not standalone custom-agent TOML files. Role behavior and effort are passed through `spawn_agent`.
- Codex IDE extensions do not currently support plugins. Use the Codex app or CLI for Adaptive Effort.
- A live smoke spawn verifies the child spawn/tool path. Proving the child's model, effort, or context metadata requires separate direct host or UI evidence.
- Adaptive Effort does not choose worker count or report per-agent token accounting. Available usage and worker-count observations may be included in a run report without becoming routing inputs.

## Repository layout

```text
.agents/plugins/marketplace.json
plugins/adaptive-effort/
  .codex-plugin/plugin.json
  assets/
  skills/adaptive-effort/
    SKILL.md
    references/
    scripts/
tests/
scripts/
```

## Validate

Requires Python 3.11+ and no third-party packages:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

## Package

```bash
python3 scripts/package.py --output dist/adaptive-effort-plugin-0.1.1.zip
```

## License

MIT
