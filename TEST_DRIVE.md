# Test drive

Use a fresh Codex app or CLI session with Superpowers and Adaptive Effort installed. Codex IDE extensions do not currently support plugins.

## 1. Setup check

Prompt:

```text
Check Adaptive Effort setup.
```

Expected:

- Adaptive Effort and required Superpowers skills are detected.
- multi-agent support is enabled or default-enabled.
- the result is `STATIC_READY` when static requirements pass.
- Windows, WSL, CLI, and current-host evidence remain separate.
- no child is spawned.

For the trusted-project boundary, set `agents.enabled = false` in the active project's `.codex/config.toml` while the user config marks that project trusted. Run the installed doctor by absolute path with `--project-dir` set to the active project directory. Confirm the result is `BLOCKED` and the multi-agent check names the project config even though the doctor script is installed elsewhere.

Then prompt:

```text
Check Adaptive Effort setup live.
```

Request one inherited-model, low-effort, fresh-context child. Confirm it returns `ADAPTIVE_EFFORT_SMOKE_OK` and the result becomes `RUNTIME_VERIFIED`. The token proves the child spawn/tool path completed with the requested settings. Confirm model, effort, or context metadata only when the host or UI exposes it directly.

## 1b. Implicit activation gate

In three fresh tasks, use representative Superpowers implementation prompts without naming Adaptive Effort. Include a bounded single-module task, a multi-file integration task, and an approved-plan continuation.

Confirm each run emits exactly one initial trace:

```text
Adaptive Effort: <mode> · implementer inherited-model/<effort> · fresh context
```

Also confirm Adaptive Effort does not activate for:

- brainstorming or architecture before implementation approval
- generic delegation outside a Superpowers workflow

## 2. Straight-through bounded task

Choose a small repository task with an existing test runner:

```text
Add a bounded retry option to this client. Preserve the public API defaults.
Cover eventual success and exhausted retries. Implement the approved plan.
```

Expected trace:

```text
parent: unchanged
implementer: inherited model / low / fresh context
verification: pass
no debugger or recovery
```

Confirm:

- the child did not receive the full parent transcript
- the child model matched the parent
- child effort was low when the UI exposes it
- tests were not weakened
- Superpowers reviews still ran

## 3. Cheap repair

Use a fixture or temporary branch where the first implementation is likely to produce a simple deterministic failure.

Expected:

```text
low implementer
→ exact test failure
→ one follow-up to the same low thread
→ pass
```

Confirm no fresh debugger was spawned after the successful repair.

## 4. Medium escalation

Create a task whose behavior crosses two modules, or temporarily add an acceptance test that catches a non-local interaction.

Expected:

```text
low implementer
→ low repair fails
→ fresh medium debugger
→ verification
```

Confirm the debugger received the contract, diff, and failure evidence, but not the first worker's reasoning transcript.

## 5. Design conflict

Use mutually incompatible acceptance criteria in a disposable test repository.

Expected:

```text
low
→ low repair
→ medium debugger
→ high recovery diagnostician
→ REPLAN_REQUIRED
→ automatic execution stops
```

Confirm no second escalation ladder starts.

## 6. Environment failure

Make the test command unavailable without changing the code.

Expected:

- environment blocker reported
- no medium/high reasoning escalation

## 7. Parent selection

Repeat a small task with parent UI effort set to Medium, then High.

Confirm:

- parent selection remains unchanged
- child model inherits parent model
- implementation still follows the Adaptive Effort role policy

## Record

For each run capture:

- Codex version, surface, and whether the host exposed the plugin skill
- Superpowers version/capabilities
- parent model and effort
- child model/effort as displayed
- child count
- context inheritance setting
- wall time
- token/usage metrics when available
- test and review results
