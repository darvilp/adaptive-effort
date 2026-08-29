# Escalation policy

Escalate only after classifying evidence. Time spent, token count, or the mere fact that a task is difficult are not enough.

Only corrective upward effort transitions count as escalations. An initial route and planned medium/high reviews do not. Every classified semantic failure records a fingerprint with behavior, boundary, and invariant fields adjacent to the failing result and before correction or escalation. An escalation reuses the same fingerprint. The same behavior and invariant recurring across different boundaries is materially similar; the boundary locates the evidence but does not make the failure new.

## Failure classes

### Environment failure

Examples:

- command or dependency is unavailable
- permission or sandbox denial
- external service outage
- network unavailable
- test fixture or CI environment is broken
- user interrupted the run

Action: report the operational blocker. Do not raise reasoning effort.

### Missing-context failure

Examples:

- a required file, API contract, or fixture was omitted from the handoff
- the worker asks a concrete question answerable from the plan or repository
- the task pointer is wrong

Action: allow one bundled same-thread context continuation per worker dispatch. Supply all concrete missing items currently available from the approved plan or repository in that follow-up. It does not raise effort and does not consume the semantic or mechanical correction allowance. It also consumes no debugger or recovery stage and is not a corrective upward transition. If required evidence is unavailable, supplying it needs new authority, or the worker makes any second context request, including for a newly revealed item, stop automatic handling with `worker=NEEDS_CONTEXT`, a blocked gate, and a missing-context closeout. Do not spawn a replacement worker or raise effort to obtain context.

### Local deterministic defect

Examples:

- off-by-one result
- wrong branch or constant
- compile/type error directly tied to the patch
- one focused acceptance test fails with a clear expected/actual difference

Action: use the one semantic same-thread correction allowed across pre-review verification and all Superpowers review stages for the implementation task. A local review correction consumes it when it remains unused. Send exact failure output to the thread whose local implementation is being corrected.

### Mechanical correction

A formatting, generated-file, checksum, or other deterministic hygiene failure may receive one deterministic same-thread mechanical correction per implementation task. This does not consume the semantic low-repair allowance. Target the thread that produced the current diff being checked, whether the original implementer, debugger, or explicitly authorized recovery writer. The follow-up must name exact targets and transformation, compare against the last semantically accepted diff, include a semantic-equivalence command and result, and rerun the failed hygiene gate. Independent review is not required before that comparison point.

A second mechanical correction stops automatic handling without raising effort. Report the remaining gate failure to the parent.

### Broader implementation reasoning defect

Examples:

- multiple interacting tests fail
- behavior differs across modules
- repository control or data flow was misunderstood
- the first repair fixes one symptom but creates another
- the implementer reports BLOCKED because the local approach is unclear

Action: start a fresh debugger at medium effort, or high in deep mode.

### Contract or design defect

Examples:

- approved requirements conflict
- repository behavior contradicts a settled assumption
- the required change cannot remain within approved scope
- tests expose an unstated invariant
- no local patch can satisfy all acceptance criteria
- the debugger concludes the plan is wrong

Action: start one high-effort recovery diagnostician. Its first task is to decide whether a bounded repair is safe or planning must resume.

## Circuit breaker

Default per implementation task:

| Stage | Limit |
|---|---:|
| Initial implementer | 1 |
| Same-thread missing-context continuation | 1 per worker dispatch |
| Same-thread local repair, the semantic correction | 1 across verification and all review stages |
| Same-thread mechanical correction | 1, separate from semantic repair |
| Fresh debugger | 1 |
| High recovery diagnostician | 1 |

Reviews remain governed by Superpowers, but Adaptive Effort must not turn review findings into an unbounded fix/re-review loop. The one semantic same-thread correction covers pre-review verification and all Superpowers review stages; a local review correction consumes it. If the allowance is already consumed, classify the failure. For an implementation reasoning defect, use the single fresh debugger stage only if it remains unused, routed at Medium in Fast/Balanced and High in Deep. If that debugger stage was already consumed, stop automatic handling and report the failed review gate unless contract/design evidence justifies the still-unused single recovery diagnostician. Only the recovery diagnostician requires contract/design evidence. High effort alone does not make a debugger a recovery, because Deep routes its debugger at High. Keep the required review gate, and never repeat the debugger or restart the ladder.

A Deep debugger-to-recovery transition dispatches the recovery role without an `escalate` event or escalation-count increment. Both roles use High effort in Deep, so recovery changes the role and fresh context but does not make a corrective upward effort transition.

## Stop report

When the ladder is exhausted, return:

```text
Implementation unresolved.

Contract:
<short identifier or summary>

Evidence:
- <command/test and result>

Attempts:
- implementation: route=<actual-effort>/<context> · <outcome>
- semantic correction: route=<retained-effort>/same-thread · <outcome>
- debugger: route=<actual-mode-routed-effort>/fresh · mode=<mode> · <outcome>
- recovery diagnostician: route=high/fresh · <outcome|not-used>

Classification:
<environment | context | implementation | design>

Recommended next action:
<specific replan, user decision, or environment fix>
```

Never silently restart the ladder.

## Counting example

This Balanced-mode example has separate design evidence. The approved contract requires one bounded implementation to pass effective project configuration to `inspect` through both the API and CLI entry points. The debugger result and deterministic gate evidence establish that the settled shared-propagation assumption is false and that no local patch within the approved scope can satisfy both acceptance criteria. Classify that contradiction as design. The repeated fingerprint establishes material similarity only; it does not authorize recovery. The Medium-to-High transition enters the still-unused single High recovery diagnostician.

The planned High review below is not an escalation. The two corrective upward transitions are:

```text
dispatch · role=reviewer · route=high/fresh · purpose=planned-review
result · worker=NOT_READY · gate=FAIL
boundaries · api=FAIL
fingerprint · value=active-project-context|api|effective-config-must-reach-inspect
escalate · from=low · to=medium · fingerprint=active-project-context|api|effective-config-must-reach-inspect
dispatch · role=debugger · route=medium/fresh · purpose=debug
result · worker=FIXED · gate=FAIL
boundaries · cli=FAIL
fingerprint · value=active-project-context|cli|effective-config-must-reach-inspect
escalate · from=medium · to=high · fingerprint=active-project-context|cli|effective-config-must-reach-inspect
closeout · gate=PASS · escalations=2 · stop=verification-passed
```

The repeated behavior and invariant make the API and CLI failures materially similar despite their different boundaries. The separate design evidence, not that recurrence, authorizes recovery.
