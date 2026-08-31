# Adaptive Effort for Superpowers / Codex

Adaptive Effort is a Codex plugin prepared for the Universal Plugins Directory, with a Git marketplace fallback for repository-backed installation.

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

## Routing modes

Fast, Balanced, and Deep are task-local Adaptive Effort routing profiles. They do not change the user-selected parent model, parent reasoning effort, Codex speed mode, or Superpowers workflow.

| Work being routed | Fast | Balanced | Deep |
|---|---:|---:|---:|
| Bounded implementation | Low | Low | Low |
| Integration implementation requiring real cross-file judgment | Low | Low | Medium |
| Same-thread semantic repair | Retains worker effort, once | Retains worker effort, once | Retains worker effort, once |
| Fresh debugger | Medium | Medium | High |
| Routine spec review | Medium | Medium | High |
| Routine code-quality review | Medium | Medium | High |
| High-risk review | High | High | High |
| Recovery diagnostician | High, only with independent contract/design evidence | High, only with independent contract/design evidence | High, only with independent contract/design evidence |

Balanced is the default. Fast and Balanced currently choose the same effort for every defined route. Fast does not skip reviews, reduce acceptance gates, or permit weaker evidence. Deep leaves ordinary bounded implementation at Low. It raises only genuine integration implementation to Medium and routes debugging and routine reviews at High. A large diff alone does not make work an integration task.

A same-thread repair is not a new worker and retains the implementer's original effort. The separate one-shot mechanical correction also retains the current writer's effort and does not count as a reasoning escalation. Planned Medium or High reviewers are planned routes, not escalation events. Only corrective movement to a higher effort after a classified failure increments the escalation count. Adaptive Effort never automatically chooses `xhigh`, `max`, or `ultra`.

## How it works with Superpowers

1. The parent task coordinates the approved plan.
2. Superpowers determines the plan tasks, execution boundaries, worker count, sequential versus parallel topology, and TDD requirements.
3. A fresh implementer handles a bounded plan task.
4. Superpowers runs specification review before code-quality review.
5. Review findings are corrected and re-reviewed.
6. Final verification uses fresh evidence before completion.
7. Adaptive Effort changes the child effort, compact handoff, failure classification, and bounded repair/escalation route; it does not decide how many workers Superpowers creates.

Worker count and aggregate usage are optional AAR observations, not routing inputs or promises of per-agent accounting.

Superpowers chooses task decomposition, writer topology, parallelism, execution boundaries, reviews, and acceptance gates. Adaptive Effort supplies child effort and context, compact handoffs, failure classification, escalation counting, circuit breakers, and closeout. Planned medium/high reviews do not count as escalations; only corrective upward effort transitions do.

The parent keeps a human-readable routing trace for the current run. It separates worker status from downstream gate status and carries Superpowers-defined boundary results in adjacent detail lines. Semantic failures record a fingerprint before correction or escalation. The trace is ephemeral, not a ledger API or telemetry system.

Missing context gets at most one bundled same-thread continuation per worker dispatch at the existing effort. A second request, unavailable evidence, or need for new authority stops automatic handling without consuming a repair or escalation stage.

## Prerequisite

Install and enable **Superpowers** from the Universal Plugins Directory first.

Adaptive Effort feature-detects the Superpowers workflow skills. It does not install or vendor Superpowers.

## Install from the Universal Plugins Directory

After the public listing is verified, install Superpowers first, then install Adaptive Effort from the Universal Plugins Directory. Start a new Codex task after installation or update. Until publication is verified, use the Git marketplace flow below.

## Install from a Git marketplace

```bash
codex plugin marketplace add darvilp/adaptive-effort --ref main
codex plugin add adaptive-effort@adaptive-effort
```

Start a new Codex task after installation.

## Install from a local checkout

From the repository root:

```bash
codex plugin marketplace add "$(pwd)"
codex plugin add adaptive-effort@adaptive-effort
```

Start a new Codex task.

## Update

```bash
codex plugin marketplace upgrade adaptive-effort
codex plugin add adaptive-effort@adaptive-effort
```

Then start a new Codex task.

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

This skills-only snapshot uses only supported plugin surfaces:

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
make package
# or individually:
python3 scripts/package.py --output dist/adaptive-effort-source-0.1.2.zip
python3 scripts/package_submission.py --output dist/adaptive-effort-plugin-0.1.2.zip
```

## License

MIT
