# Test drive

Use a fresh Codex app or CLI session with Superpowers and Adaptive Effort installed. Codex IDE extensions do not currently support plugins.

The mode matrix contains the no-override defaults. Explicit role assignments patch the selected mode's profile. Dispatch implementation with `profile.implementer` and debugging with `profile.debugger`. Reviews use `profile.routine_review` or `profile.high_risk_review`. Recovery uses `profile.recovery`. In Fast, recovery also requires `profile.recovery_explicitly_requested` and independent contract/design evidence. A semantic or mechanical repair retains the actual writer route.

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

In three fresh tasks, use representative Superpowers implementation prompts without naming Adaptive Effort. Include a small single-module task, a multi-file task, and an approved-plan continuation.

Confirm each run emits exactly one initial trace:

```text
Adaptive Effort: <mode> · implementer inherited-model/<effort> · fresh context
```

Also confirm Adaptive Effort does not activate for:

- brainstorming or architecture before implementation approval
- generic delegation outside a Superpowers workflow

Confirm each mode selects its initial implementation effort directly, without assigning a work category first.

## 2. Straight-through Balanced task

Choose a small repository task with an existing test runner. Do not supply role assignments, so this test uses the Balanced no-override defaults:

```text
Add a retry option to this client. Preserve the public API defaults.
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
- closeout reports `escalations=0`

## 2b. Mode differentiation

Repeat a routine task in Fast without role assignments. Confirm the resolved profile matches the Fast no-override defaults. Confirm required reviews still run.

Repeat a simple task in Deep without role assignments. Confirm the resolved profile matches the Deep no-override defaults. Confirm no work category is assigned before dispatch.

Repeat with non-default assignments for all five roles. Confirm each dispatch uses its `profile` field, routine and high-risk reviews use their separate fields, and each repair retains the actual writer route. In Fast, confirm recovery stops unless both explicit recovery provenance and independent contract/design evidence are present.

## 2c. Planned high review

Use a Superpowers-selected high-risk review after straight-through implementation. Confirm the review dispatch uses `purpose=planned-review` and the closeout still reports zero escalations. A planned High route is not a corrective transition.

## 2d. Task-local model routing and inspection

For an approved task, request exact model assignments for all five roles and a non-default effort for at least one role. Ask for the current Adaptive Effort routing plan and available worker models before dispatch.

Confirm:

- all five routes appear, including distinct routine and high-risk review routes
- each explicit model ID is preserved exactly
- model and effort assignments resolve independently
- unassigned roles show inherited model routing
- the local-client catalog is not truncated and includes its source executable and version
- the catalog is labeled advisory and the active spawn host remains authoritative
- an exact model absent from the catalog proceeds to host validation without local rejection or substitution
- an unavailable or malformed catalog still returns the resolved routing plan

In Fast, supply only a recovery model assignment. Confirm it sets explicit recovery provenance but still cannot dispatch recovery without independent contract/design evidence.

## 3. Cheap repair

Use a fixture or temporary branch where the first implementation is likely to produce a simple deterministic failure.

Expected with the Balanced no-override defaults:

```text
profile.implementer
→ exact test failure
→ one follow-up to the same thread at the actual writer route
→ pass
```

Confirm no fresh debugger was spawned after the successful repair.

## 4. Balanced no-override debugger example

Create a task whose behavior crosses two modules, or temporarily add an acceptance test that catches a non-local interaction.

Expected with no role assignments:

```text
profile.implementer
→ same-thread repair fails
→ fresh profile.debugger
→ verification
```

Confirm the debugger received the contract, diff, and failure evidence, but not the first worker's reasoning transcript.

Compare the actual implementer and debugger efforts. Confirm the escalation count increments only when the debugger effort is higher.

Confirm the first classified failure wrote its fingerprint beside the failing result before repair or escalation, and the escalation reused that exact value.

## 4b. Two true escalations across boundaries

Use a disposable Balanced-mode fixture with no role assignments where the same behavior and invariant fail first at one Superpowers-defined boundary, then at another. Before recovery, establish separate deterministic design evidence that the approved API and CLI propagation assumption is false and no local in-scope patch can satisfy both acceptance criteria. Compare actual resolved efforts and confirm both increases count as escalations. Confirm the boundary change does not make the repeated semantic failure unrelated, but the repeated fingerprint alone never authorizes recovery. Repeat without contract/design evidence after the debugger is spent and confirm automatic handling stops instead of entering recovery.

## 4c. Mechanical correction

Cause one deterministic hygiene failure such as formatting or checksum drift after semantic verification. Confirm the writer thread that produced the current diff receives the exact targets and transformation. Compare against the last semantically accepted diff, run the stated semantic-equivalence command, rerun the failed hygiene gate, and record a mechanical repair without consuming the semantic correction allowance.

Reproduce a second mechanical hygiene failure for the same task. Confirm automatic handling stops, reports the failed gate, and does not raise effort.

## 4d. Boundary evidence

Omit evidence expected for one Superpowers-defined boundary. Confirm an adjacent `boundaries` detail line records the named result without changing the downstream `gate` field. Adaptive Effort reports missing context rather than an implementation defect and does not choose a replacement boundary. Confirm the same worker receives one bundled continuation containing all currently available items at unchanged effort and that it consumes no repair, debugger, recovery, or escalation allowance.

Make that worker request context again, including a newly revealed item. Separately try an unavailable item and an item that needs new authority. Confirm each history stops automatic handling with `worker=NEEDS_CONTEXT`, `gate=BLOCKED`, an unchanged escalation count, and `stop=missing-context`.

Mark another Superpowers-defined boundary deferred. Confirm its result remains `DEFERRED`, no invented evidence is required, and the final acceptance gate decides whether closeout may pass.

## 4e. Review correction accounting

Use the semantic same-thread correction during pre-review verification, then introduce a local finding at a required Superpowers review. Confirm the implementation reasoning defect uses the single fresh debugger at `profile.debugger` when that stage remains unused. The visible trace must report `role=debugger`, the actual route, and the mode. Then reproduce the review failure after the debugger stage has already been consumed. Confirm recovery uses `profile.recovery` only with independent contract/design evidence. In Fast, also require `profile.recovery_explicitly_requested`. Compare the actual debugger and recovery efforts before expecting an `escalate` event. Confirm the stop report lists debugger and recovery separately, the debugger never repeats, and the ladder never restarts.

## 5. Design conflict

Use Balanced mode with mutually incompatible acceptance criteria in a disposable test repository. Omit role assignments so the expected sequence uses the no-override defaults.

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
- a child role without a model assignment inherits the parent model
- a child role with a model assignment receives the exact requested ID when the active host accepts it
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
- aggregate token/usage observations when available, without claiming per-agent accounting
- test and review results

Worker count is an observation only. Superpowers owns topology and parallelism.
