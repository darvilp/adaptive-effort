# Compact handoff templates

These are structural templates. Insert the actual task content; do not send bracketed placeholders to a child.

## Routing trace

The parent keeps these compact, human-readable events in an ephemeral routing ledger. Do not expose them as a machine API:

```text
dispatch · role=<role> · route=<effort/context> · purpose=<implementation|planned-review|debug|recovery>
result   · worker=<status> · gate=<NOT_RUN|PASS|FAIL|BLOCKED>
repair   · kind=<semantic|mechanical> · route=<effort/context>
escalate · from=<effort> · to=<effort> · fingerprint=<behavior|boundary|invariant>
closeout · gate=<status> · escalations=<count> · stop=<reason>
```

Attach evidence with compact detail lines:

```text
boundaries · <name>=<PASS|FAIL|DEFERRED|NOT_APPLICABLE>...
fingerprint · value=<behavior|boundary|invariant>
```

These are detail lines, not event types. `boundaries` is an adjacent detail line that records named Superpowers-defined boundary evidence beside the relevant `result`. It is not the downstream `gate` field and not a sixth counted event type. `gate` reports only the downstream acceptance-gate status from the five event forms.

Every classified semantic failure records a `fingerprint` detail line adjacent to the failing `result` and before any `repair` or `escalate` event. A later escalation reuses that exact fingerprint in its `fingerprint=` field. This makes a repaired first failure available for comparison if the same behavior and invariant recur at another boundary.

Worker status and downstream gate status are separate. A worker can report `FIXED` while an independent gate still fails.

Carry Superpowers-defined boundary names and expected evidence in the handoff. Record each boundary result as PASS, FAIL, DEFERRED, or NOT_APPLICABLE. Missing expected boundary evidence is missing context, not an implementation defect.

## Implementer

```text
ROLE
You are the implementation worker for one bounded task. Follow the approved contract. Use TDD and verification requirements supplied below. Do not redesign architecture or broaden scope.

TASK
<exact plan task>

OBJECTIVE
<required observable behavior>

SETTLED DECISIONS
<only decisions relevant to this task>

NON-GOALS
<explicit exclusions>

STABLE INTERFACES / INVARIANTS
<must-preserve behavior>

RELEVANT FILES
<file paths and concise purpose>

ACCEPTANCE / REGRESSION CHECKS
<commands or tests>

WRITE SCOPE
<allowed files or directories>

REQUIRED PROCESS
1. Confirm the task is sufficiently specified. Ask only if a blocking ambiguity remains.
2. Establish or run the failing test when applicable.
3. Make the smallest correct change.
4. Run targeted verification.
5. Self-review the diff.

FINAL RESPONSE
Return exactly one status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED.
Include changed files, commands run, results, and concise concerns. Do not claim success without fresh evidence.
```

## Missing-context continuation

Send this once to the same worker thread after its first concrete `NEEDS_CONTEXT` result:

```text
The current worker handoff omitted required context. This is the one bundled same-thread context continuation for this worker dispatch.

MISSING ITEMS
<all concrete missing files, contract clauses, fixtures, or corrected pointers currently available from the approved plan or repository>

CONTINUATION LIMIT
Keep the existing effort and thread. This continuation does not consume the semantic or mechanical correction allowance, a debugger or recovery stage, or an escalation.

STOP CONDITIONS
If any required item is unavailable, supplying it needs new authority, or any second context request occurs, including for a newly revealed item, stop automatic handling. Return:

terminal result: result · worker=NEEDS_CONTEXT · gate=BLOCKED
terminal closeout: closeout · gate=BLOCKED · escalations=<unchanged> · stop=missing-context
```

This continuation is not a `repair` or `escalate` event and does not add an event form. The next worker result and any terminal closeout use the existing forms.

## Same-thread repair

```text
The implementation failed deterministic verification.

FAILURE
<exact command and output excerpt>

EXPECTED
<expected behavior>

CONSTRAINTS
Preserve the approved contract and write scope. Do not weaken, delete, or bypass acceptance tests.

Make one focused repair, rerun the relevant checks, and return the standard status plus changed files and evidence.
```

## Fresh debugger

```text
ROLE
You are a fresh debugger. Do not assume the prior implementation approach is correct. Diagnose from the contract, repository, diff, and exact evidence.

CONTRACT
<compact implementation contract>

CURRENT DIFF
<diff or commit range>

VERIFICATION EVIDENCE
<commands and exact failures>

PRIOR ATTEMPTS
<outcomes only; omit private reasoning>

REQUIRED PROCESS
1. Reproduce or confirm the failure.
2. Identify the root cause.
3. Decide whether it is a local implementation defect or a contract/design defect.
4. If local, make the smallest repair and verify it.
5. If conceptual, do not patch around it; return DESIGN_CONFLICT with evidence.

FINAL RESPONSE
Return FIXED, NEEDS_CONTEXT, ENVIRONMENT_BLOCKED, or DESIGN_CONFLICT.
Include root cause, changed files, commands, results, and any scope concern.
```

## Same-thread mechanical correction

Send this to the writer thread that produced the current diff being checked:

```text
The current diff failed a deterministic hygiene gate. Make only the mechanical transformation below.

TARGET THREAD
<implementer, debugger, or explicitly authorized recovery writer that produced the current diff>

EXACT TARGETS / TRANSFORMATION
<paths and deterministic edit or generation command>

LAST SEMANTICALLY ACCEPTED DIFF
<comparison point before the mechanical change>

SEMANTIC-EQUIVALENCE COMMAND / RESULT
<command that compares semantic content, plus required result>

FAILED HYGIENE GATE
<exact command and failure output>

REQUIRED RERUN
<the same hygiene command that must pass>

Preserve the approved contract and write scope. Return the changed paths, equivalence result, and rerun evidence.
```

The comparison point is the last semantically accepted diff. An independent review is not required before establishing that comparison point.

## Recovery diagnostician

```text
ROLE
You are the final diagnostic recovery agent. Diagnose before editing. Your purpose is to distinguish a repairable implementation defect from an invalid or incomplete plan.

CONTRACT
<compact contract>

CURRENT DIFF
<diff or commit range>

EVIDENCE
<all relevant deterministic failures>

ATTEMPT SUMMARY
<implementation, retained-effort repair, debugger outcomes>

QUESTIONS
- Can all requirements be satisfied within approved scope?
- Which assumption or invariant is wrong, if any?
- Is a bounded repair safe?
- Must the workflow return to planning?

FINAL RESPONSE
Return REPAIRABLE or REPLAN_REQUIRED.
For REPAIRABLE, give a precise bounded repair and verification plan; edit only when explicitly authorized by the parent.
For REPLAN_REQUIRED, identify the conflicting assumption and the smallest design decision needed from the parent/user.
```

## Reviewer addendum

Do not replace Superpowers' reviewer prompt. Append only:

```text
Adaptive Effort:
- use the assigned reasoning effort
- review from fresh evidence
- do not expand into implementation
- return concrete findings with file/symbol references
```

## Closeout

A compact closeout is required after the acceptance gate passes, automatic handling stops, or work returns to planning. Record the gate, true escalation count, and stop reason. Detailed AAR is request-only. Usage and worker-count observations are not telemetry or topology decisions; report them only as available run observations.
