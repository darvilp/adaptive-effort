# Test results

Snapshot date: 2026-09-03

## Completed

- marketplace JSON structure
- plugin manifest fields and asset paths
- one primary implicit skill
- no unsupported plugin-packaged custom-agent TOMLs
- parent setting preservation instructions
- inherited child model defaults with exact task-local role overrides
- independent task-local model and effort resolution
- local routing-plan output with advisory model candidates
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
- rejection of forbidden files, special files, and empty forbidden directories
- exact approved semantics for the submission review pack
- deterministic public evidence replay for the same-thread repair and fresh debugger cases
- planned-review exclusion from escalation counts
- separate worker and downstream gate outcomes
- semantic fingerprints across execution boundaries
- separate one-shot mechanical correction
- carried boundary results and missing-context handling
- compact required closeout and request-only detailed AAR
- named boundary detail mapping without changing the five event forms
- pre-correction semantic fingerprint recording and escalation reuse
- one semantic correction allowance across verification and all review stages
- one mode-routed debugger stage across verification and review failures
- current-diff writer targeting and complete mechanical follow-up fields
- independent contract/design evidence before cross-boundary recovery
- one bundled non-escalating context continuation with a terminal blocked path
- actual debugger route and separate recovery role in traces and stop reports

Automated suite:

Fresh local verification for this commit:

`scripts/validate.py` passed, and the full unit suite passed. Independent source and submission builds were byte-identical. `sha256sum -c MANIFEST.sha256` passed, and `scripts/verify_submission.py` verified the sorted regular files under one `adaptive-effort/` directory. Final package checks rerun these commands after this evidence update.

CI is configured to run validation, the unit suite, independent double builds, checksum checks, submission-structure verification, and artifact upload on a future push or pull request. No CI result is claimed for this unpushed commit.

The installed plugin-creator validator reported only its stale rejection of `policy.products`. The CODEX-only product gate remains in the skill metadata as required.

The 0.1.1 pre-push release acceptance evidence below remains historical. Current 0.1.3 local repository verification does not establish portal, CI, or publication gates.

The historical 0.1.1 release archive was `dist/adaptive-effort-plugin-0.1.1.zip`. The 0.1.3 source and submission archive names are `dist/adaptive-effort-source-0.1.3.zip` and `dist/adaptive-effort-plugin-0.1.3.zip`.

`git diff --check` passed. Changed public files contained no CRLF or trailing whitespace. Scans found no publisher placeholder, no active 0.1.0 package command or path, and no tracked generated artifact. The only 0.1.0 archive-name match is a package regression assertion that excludes the obsolete archive. `plugins/adaptive-effort/skills/adaptive-effort/scripts/doctor.py` remains unchanged. `plugins/adaptive-effort/skills/adaptive-effort/scripts/policy.py` now differentiates Fast, Balanced, and Deep implementation, review, debugging, and automatic recovery routes. It also resolves exact task-local role model overrides independently from effort. `routing_plan.py` returned all five resolved routes and the complete picker-visible model list from the local Codex client; that catalog remains advisory rather than runtime-host proof.

The doctor CLI regression launches the installed script from its skill directory while passing a separate trusted project through `--project-dir`. A project `.codex/config.toml` that disables agents produces exit 1, `BLOCKED`, and a failing multi-agent check that names the project config. A separate error-path regression proves that a missing or non-directory project target exits 2 before readiness is computed.

The static doctor returned `STATIC_READY`: the Adaptive Effort skill, required Superpowers skills, and multi-agent configuration checks passed on the active surface. The CLI plugin-inventory check warned, so static readiness is capability evidence rather than a clean inventory-list result.

## Installed cache and runtime evidence

Historical installed-cache inspection found Adaptive Effort 0.1.0 and Superpowers 6.3.0. That older evidence proves the prior installation only; it is not 0.1.1 acceptance evidence.

Historical 0.1.0 runtime smoke proved that the spawn/tool path completed with the requested settings. It does not independently observe or prove the child's model, effort, or context metadata. Historical fresh-task pickup also remains prior-release evidence. The 0.1.3 installed-cache inspection and fresh-task startup proof are post-push acceptance gates and must be reported in the release handoff. Repository validation does not substitute for either gate.

## Not executed in this build environment

- installation through a real `codex plugin marketplace add`
- installation through a real `codex plugin add`
- 0.1.3 installed-cache inspection
- 0.1.3 fresh-task startup proof
- full authenticated implementation workflow beyond the exact smoke
- IDE discovery, because Codex IDE extensions do not currently support plugins
- token/latency comparison against an all-High workflow

Source validation, installed-cache inspection, runtime proof, and fresh-task pickup are separate claims. Follow `TEST_DRIVE.md` for broader workflow testing.
