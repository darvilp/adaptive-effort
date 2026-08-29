# Escalation policy

Escalate only after classifying evidence. Time spent, token count, or the mere fact that a task is difficult are not enough.

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

Action: provide the missing context. Keep the same effort unless independent reasoning evidence also exists.

### Local deterministic defect

Examples:

- off-by-one result
- wrong branch or constant
- compile/type error directly tied to the patch
- one focused acceptance test fails with a clear expected/actual difference

Action: send one follow-up task to the same low-effort implementer with exact failure output.

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
| Same-thread local repair | 1 |
| Fresh debugger | 1 |
| High recovery diagnostician | 1 |

Reviews remain governed by Superpowers, but Adaptive Effort must not turn review findings into an unbounded fix/re-review loop. After two materially similar review failures, classify the underlying problem and either escalate once or return to planning.

## Stop report

When the ladder is exhausted, return:

```text
Implementation unresolved.

Contract:
<short identifier or summary>

Evidence:
- <command/test and result>

Attempts:
- low implementation: <outcome>
- low repair: <outcome>
- medium debugger: <outcome>
- high recovery: <outcome>

Classification:
<environment | context | implementation | design>

Recommended next action:
<specific replan, user decision, or environment fix>
```

Never silently restart the ladder.
