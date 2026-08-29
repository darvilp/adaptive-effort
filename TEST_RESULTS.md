# Test results

Snapshot date: 2026-08-28

## Completed

- marketplace JSON structure
- plugin manifest fields and asset paths
- one primary implicit skill
- no unsupported plugin-packaged custom-agent TOMLs
- parent setting preservation instructions
- inherited child model policy
- fresh-context policy
- fast, balanced, and deep routing matrix
- low → medium → high bounds
- environment-failure no-escalation rule
- Superpowers ownership boundary
- compact handoff evidence requirements
- doctor filesystem/configuration detection
- surface-tagged Windows/WSL doctor evidence
- static and runtime readiness states
- implicit activation and trace contract
- same-thread repair without a repair spawn
- allowlisted repository packaging and exact manifest coverage
- deterministic ZIP packaging and checksums

Automated suite:

The release acceptance commands passed with the real ambient `CODEX_HOME`. This proves the source validator, 35 unit tests, plugin schema validator, repository manifest, adjacent archive checksum, and deterministic package bytes.

The doctor CLI regression launches the installed script from its skill directory while passing a separate trusted project through `--project-dir`. A project `.codex/config.toml` that disables agents produces exit 1, `BLOCKED`, and a failing multi-agent check that names the project config. A separate error-path regression proves that a missing or non-directory project target exits 2 before readiness is computed.

The static doctor returned `STATIC_READY`: the Adaptive Effort skill, required Superpowers skills, and multi-agent configuration checks passed on the active surface. The CLI plugin-inventory check warned, so static readiness is capability evidence rather than a clean inventory-list result.

## Installed cache and runtime evidence

Installed-cache inspection found Adaptive Effort 0.1.0 and Superpowers 6.3.0. That evidence proves installation only; it does not prove routing behavior.

The exact runtime smoke requested an inherited-model, low-effort worker with fresh context. It returned `ADAPTIVE_EFFORT_SMOKE_OK`, which proves the child spawn/tool path completed with the requested settings. The token does not independently observe or prove the child's model, effort, or context metadata. A fresh task then exposed Adaptive Effort from the installed plugin, which separately proves new-task pickup.

## Not executed in this build environment

- installation through a real `codex plugin marketplace add`
- installation through a real `codex plugin add`
- full authenticated implementation workflow beyond the exact smoke
- IDE discovery, because Codex IDE extensions do not currently support plugins
- token/latency comparison against an all-High workflow

Source validation, installed-cache inspection, runtime proof, and fresh-task pickup are separate claims. Follow `TEST_DRIVE.md` for broader workflow testing.
