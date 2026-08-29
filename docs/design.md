# Adaptive Effort for Superpowers / Codex

## 1. Summary

Adaptive Effort is a Codex plugin that extends Superpowers with reasoning-effort routing, bounded escalation, and context/cost controls.

Superpowers owns the software-development workflow:

- requirements clarification
- architecture and design
- implementation planning
- task decomposition
- test-driven development
- subagent-driven implementation
- code review
- verification

Adaptive Effort owns one narrower decision:

> Given the agent role and the evidence available, how much reasoning effort should the next Codex agent receive?

The intended pattern is:

```text
Interactive parent
Medium / High / user-selected
        │
        ▼
Superpowers design + planning
        │
        ▼
bounded implementation contract
        │
        ▼
Low implementation
        │
   deterministic verification
        │
    ┌───┴───┐
   pass     fail
    │        │
    ▼        ▼
continue   bounded repair
             │
             ▼
        selective escalation
```

The plugin should reduce unnecessary high-effort inference without weakening Superpowers' development and verification discipline.

---

## 2. Product model

```text
Codex
│
├── User-selected parent model / effort
│
├── Superpowers plugin
│     ├── design
│     ├── planning
│     ├── TDD
│     ├── task decomposition
│     ├── subagent-driven development
│     ├── review
│     └── verification
│
└── Adaptive Effort plugin
      ├── child effort routing
      ├── compact context handoff
      ├── evidence-driven escalation
      ├── circuit breakers
      └── routing observability
```

Adaptive Effort is a separate plugin. It does not vendor, fork, or duplicate Superpowers workflow skills.

---

## 3. Goals

Adaptive Effort should:

1. Preserve normal Superpowers behavior.
2. Require little or no manual agent invocation.
3. Respect the model and effort selected for the active Codex parent session.
4. Use lower reasoning effort for bounded implementation by default.
5. Increase reasoning effort only when verification evidence justifies it.
6. Avoid copying large parent conversations into worker contexts.
7. Prevent unbounded repair, review, or escalation loops.
8. Expose enough routing information to evaluate whether the policy saves compute.
9. Work through Codex's native plugin and agent mechanisms.
10. Install from a Git-hosted community marketplace.

---

## 4. Non-goals

Adaptive Effort does not implement its own:

- brainstorming methodology
- architecture methodology
- implementation planning
- TDD methodology
- task decomposition
- code-review methodology
- worktree strategy
- git workflow
- project-management system
- completion criteria

Those remain Superpowers responsibilities.

The plugin also does not automatically route between model families. The optimization dimension is **reasoning effort within the inherited parent model**.

For example:

```text
Parent: Sol / High

Implementer:
  model  = inherited Sol
  effort = Low
```

not:

```text
Parent: Sol
Implementer: automatically switch to Luna
```

---

## 5. Distribution

Adaptive Effort is distributed as a native Codex plugin through a Git-hosted community marketplace.

Repository layout:

```text
adaptive-effort/
├── .agents/
│   └── plugins/
│       └── marketplace.json
├── .github/
│   └── workflows/
│       └── ci.yml
├── plugins/
│   └── adaptive-effort/
│       ├── .codex-plugin/
│       │   └── plugin.json
│       ├── assets/
│       │   ├── adaptive-effort-small.svg
│       │   └── adaptive-effort.svg
│       ├── README.md
│       ├── skills/
│       │   └── adaptive-effort/
│       │       ├── agents/
│       │       │   └── openai.yaml
│       │       ├── references/
│       │       │   ├── compatibility.md
│       │       │   ├── escalation-policy.md
│       │       │   ├── handoff-templates.md
│       │       │   ├── routing-policy.md
│       │       │   └── superpowers-integration.md
│       │       ├── scripts/
│       │       │   ├── doctor.py
│       │       │   └── policy.py
│       │       └── SKILL.md
├── scripts/
│   ├── package.py
│   └── validate.py
├── tests/
│   ├── test_doctor.py
│   ├── test_package.py
│   ├── test_policy.py
│   └── test_references.py
├── README.md
├── CHANGELOG.md
└── LICENSE
```

The plugin is skills-only. `agents/openai.yaml` is skill presentation metadata. Delegated roles travel in spawn messages; the package contains no standalone custom-agent TOMLs or command files.

Normal installation requires no custom installer, package manager, shell wrapper, or manual file copying.

---

## 6. Marketplace installation

Assuming the repository is:

```text
github.com/darvilp/adaptive-effort
```

installation is:

```bash
codex plugin marketplace add darvilp/adaptive-effort --ref main
codex plugin add adaptive-effort@adaptive-effort
```

The user then starts a new Codex session.

The same marketplace structure supports:

- public GitHub repositories
- private Git repositories
- SSH Git sources
- local development checkouts

---

## 7. Superpowers dependency

Superpowers is required.

Adaptive Effort expects capabilities equivalent to:

```text
subagent-driven-development
test-driven-development
verification-before-completion
review workflow
```

The plugin does not install Superpowers automatically and does not provide replacement behavior when Superpowers is absent.

Installation order:

```text
1. Install Superpowers.
2. Add the Adaptive Effort marketplace.
3. Install Adaptive Effort.
4. Start a new Codex session.
```

Because Codex does not expose a general plugin dependency resolver, Adaptive Effort verifies the dependency through capability detection.

If required functionality is absent:

```text
Adaptive Effort is inactive.

Required Superpowers capability not detected:
  subagent-driven-development

Install or enable Superpowers and start a new Codex session.
```

The plugin should avoid repeatedly emitting this warning during unrelated work.

---

## 8. Plugin ownership boundary

### Superpowers owns

```text
What should be built?
How should it be designed?
How should work be decomposed?
What tests should exist?
When should implementation begin?
What review is required?
What counts as complete?
```

### Adaptive Effort owns

```text
At what reasoning effort should a child run?
Should the existing worker receive one cheap repair?
When does evidence justify escalation?
How much conversational context should a child inherit?
When must automatic escalation stop?
```

Instruction priority:

```text
Explicit user instruction
        ↓
Superpowers workflow requirements
        ↓
Adaptive Effort compute policy
```

Adaptive Effort cannot skip a Superpowers-required test or review merely to save compute.

---

## 9. Parent model and effort

The active Codex session is authoritative.

If the IDE or Desktop UI says:

```text
Model:  GPT-5.6 Sol
Effort: High
```

the parent remains Sol / High.

If the user selects another supported model or effort, Adaptive Effort leaves it unchanged.

Default policy:

```text
Parent:
  model  = Codex session setting
  effort = Codex session setting

Child:
  model  = inherit from parent
  effort = Adaptive Effort role policy
```

Adaptive Effort does not set a global parent model or reasoning effort.

---

## 10. User experience

Normal use should require no Adaptive Effort command.

Example:

```text
Add retry handling to this client and cover timeout,
eventual success, and exhausted retries.
```

Superpowers drives the engineering workflow.

When implementation is delegated, Adaptive Effort applies the appropriate child-effort policy.

For architecture-heavy work:

```text
/plan

Design retry handling without changing the public API.
```

The parent performs design at its currently selected model and effort.

After approval:

```text
Implement the plan.
```

Superpowers transitions into implementation and Adaptive Effort handles compute allocation for delegated work.

Manual `$adaptive-effort` invocation may exist for explicit use or diagnostics, but it is not the normal workflow.

---

## 11. Agent roles

### 11.1 Implementer

Purpose:

- execute one bounded implementation task
- follow the approved plan and task contract
- satisfy the tests and acceptance criteria supplied by Superpowers
- make the smallest appropriate change

Configuration:

```text
model:             inherit
reasoning effort:  Low
context:           fresh / compact
write access:      yes
```

The implementer should report significant ambiguity rather than inventing architecture outside the approved scope.

---

### 11.2 Debugger

Purpose:

- diagnose an implementation that failed deterministic verification
- inspect the contract, current diff, relevant source, and exact failures
- reconsider local implementation assumptions
- make a bounded repair

Configuration:

```text
model:             inherit
reasoning effort:  Medium
context:           fresh / compact
write access:      yes
```

The debugger starts fresh after the original implementer has exhausted its cheap repair attempt.

---

### 11.3 Recovery diagnostician

Purpose:

- distinguish implementation failure from design failure
- identify incorrect assumptions, missing invariants, or contradictory requirements
- determine whether execution should return to planning

Configuration:

```text
model:             inherit
reasoning effort:  High
context:           fresh / compact
write access:      constrained where practical
```

The recovery agent is a diagnostician, not simply a stronger implementer.

Its valid outcomes include:

```text
repair is locally possible
```

or:

```text
the implementation contract is invalid;
return to planning
```

---

## 12. Reviewer integration

Superpowers owns review timing and review requirements.

Adaptive Effort may supply reasoning-effort policy for reviewers:

```text
routine implementation review   Medium
high-risk review                 High
architectural challenge          High
```

It does not create an independent review lifecycle.

---

## 13. Implementation contract

Delegated workers receive a compact task contract rather than the entire parent conversation.

The contract should reuse artifacts already produced by Superpowers and contain only relevant information:

```text
Objective

Required behavior

Specific implementation task

Non-goals

Relevant files/modules

Interfaces that must remain stable

Known invariants

Acceptance tests

Regression requirements

Approved architecture decisions

Allowed scope
```

A typical contract should be measured in thousands of tokens, not hundreds of thousands.

---

## 14. Context policy

Fresh worker context is the default:

```text
fork_turns = none
```

or the equivalent supported Codex mechanism.

A child receives:

```text
role instructions
+ implementation contract
+ relevant file pointers
+ current diff, when applicable
+ exact failure output, when applicable
```

The child can inspect the repository itself as needed.

Preferred flow:

```text
Parent with large architecture context
        │
        └── compact contract
                 ↓
          Low implementer
                 │
                 └── diff + failures
                           ↓
                    Medium debugger
```

Avoid propagating the full parent transcript through every child.

Fresh context provides both token savings and an independent reasoning path.

---

## 15. Execution state machine

```text
SUPERPOWERS TASK READY
          │
          ▼
    LOW IMPLEMENTER
          │
      verification
       /        \
    PASS        FAIL
     │            │
     ▼            ▼
continue      LOW REPAIR
workflow          │
              verification
               /       \
            PASS       FAIL
             │           │
             ▼           ▼
          continue    FRESH MEDIUM
                       DEBUGGER
                          │
                      verification
                       /       \
                    PASS       FAIL
                     │           │
                     ▼           ▼
                  continue     HIGH
                            DIAGNOSTIC
                              RECOVERY
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
                repairable              design issue
                    │                       │
                    ▼                       ▼
                  repair              return to parent
                                      / planning
```

Automatic execution is bounded.

---

## 16. Cheap repair

The original Low implementer receives at most one normal repair attempt when:

- failure is deterministic
- the problem appears local
- the implementation remains inside approved scope
- there is no evidence of a conceptual design problem

Example:

```text
Verification failure:

Expected 3 attempts.
Observed 4 attempts.

Correct the implementation while preserving the approved contract.
```

If the repair still fails, start a fresh Medium debugger.

---

## 17. Escalation policy

### Low → Medium

Escalate when:

- the Low repair fails
- the failure involves non-obvious interactions
- tests conflict unexpectedly
- repository behavior differs from implementation assumptions
- broader control-flow or data-flow analysis is required

### Medium → High

Escalate when:

- deterministic verification still fails
- the contract appears incomplete or internally inconsistent
- repository behavior contradicts an architectural assumption
- required changes escape the approved scope
- testing exposes an unstated invariant
- the debugger determines that the plan itself may be wrong

### Do not escalate reasoning for

- missing executable
- unavailable dependency
- permissions failure
- unavailable service
- infrastructure outage
- broken external test environment
- user interruption

These are operational failures rather than reasoning failures.

---

## 18. Circuit breakers

Default limits:

```text
Low implementation attempts:  1
Low repair attempts:          1
Medium debugger attempts:     1
High recovery attempts:       1
```

When the ladder is exhausted, automatic execution stops.

The parent receives a structured summary:

```text
Implementation unresolved.

Attempts:
- Low implementation: failed X
- Low repair: failed Y
- Medium debugging: identified Z
- High recovery: contract likely conflicts with A

Recommended action:
Return to planning and revisit assumption B.
```

No additional agent sequence is spawned automatically.

---

## 19. Orchestration modes

Modes control Adaptive Effort behavior only. They never modify the active parent model or parent effort.

### Fast

```text
Implementer       Low
Cheap repair      Low
Debugger          Medium
High recovery     only for strong conceptual evidence
Additional review only when Superpowers requires it
```

Suitable for routine, low-risk work.

### Balanced

Default.

```text
Implementer       Low
Cheap repair      Low
Debugger          Medium
Recovery          High
Reviewer effort   Medium, raised to High for risk
```

### Deep

```text
Implementer       Low or Medium according to task complexity
Debugger          High
Recovery          High
Reviewer           higher-effort independent review
Verification       broad
```

XHigh and Max are outside the automatic routing policy.

---

## 20. User overrides

Natural task-level instructions should work:

```text
Use fast handling for this.

Use deep handling for this.

Do this directly; don't delegate.

Keep implementation at Low.

Do not escalate above Medium.
```

Task-local language affects only that workflow unless the user explicitly requests a persistent preference.

Normal development should not require manually naming worker agents.

---

## 21. Configuration

The default policy should remain small:

```text
mode = balanced

implementer_effort = low
debugger_effort = medium
recovery_effort = high

low_repairs = 1
medium_debuggers = 1
high_recoveries = 1
```

The plugin should not require global Codex configuration changes for its own policy.

It must not set:

```text
parent_model
parent_effort
```

and should not pin child models by default.

---

## 22. Installation isolation

Installing Adaptive Effort must not:

- edit global `AGENTS.md`
- overwrite `~/.codex/config.toml`
- create shell aliases
- install Python packages
- install Node packages
- add global executables
- change the parent model
- change the parent effort
- install Superpowers automatically

Any required Codex capability that cannot be supplied by the plugin itself should be detected and reported by diagnostics.

---

## 23. Skill activation

The plugin should expose one narrow implicit skill.

It becomes applicable when:

- Superpowers is performing subagent-driven implementation
- an implementation worker needs to be selected
- verification has failed and escalation is being considered
- a Superpowers reviewer requires an effort policy
- the user explicitly asks for Adaptive Effort behavior

It should not independently trigger to:

- brainstorm
- create architecture
- write an implementation plan
- decompose every request
- replace Superpowers
- perform generic model routing

The core instruction is:

```text
Augment Superpowers delegation with effort routing.
Do not initiate a separate development lifecycle.
```

Keeping a single primary implicit skill also minimizes skill-selection overhead and conflict.

---

## 24. Doctor capability

Adaptive Effort should provide a diagnostic action accessible naturally:

```text
Check Adaptive Effort setup.
```

The static doctor checks only:

```text
Adaptive Effort plugin loaded              PASS
Required Superpowers skill files           PASS
Effective user/trusted-project agents config PASS
Optional Codex CLI and plugin inventory    PASS/WARN
```

The script does not spawn a child, inspect the active tool schema, or observe child runtime metadata. It returns `STATIC_READY` when its active-surface blocking checks pass.

The CLI accepts `--project-dir PATH` to select the active project working directory for trusted project configuration discovery. Setup instructions pass that directory explicitly while invoking the installed doctor by absolute path, so the process does not change into the skill directory. If the option is omitted, the doctor uses the process working directory. An explicit path that does not name an existing directory fails before readiness is computed.

An explicitly requested live check may perform a trivial spawn outside the static script:

```text
Child requested:
  model:  inherit
  effort: Low
  context: fresh

Child response:
  ADAPTIVE_EFFORT_SMOKE_OK
```

That exact token means the child spawn/tool path completed with the requested settings, so the formal state becomes `RUNTIME_VERIFIED`. The token does not independently observe or prove the child's model, effort, or context metadata. When the host or UI exposes that metadata, record it as separate direct evidence and report any mismatch.

---

## 25. Observability

Routing should be visible without producing verbose orchestration chatter.

Example:

```text
Adaptive Effort
Implementer: inherited model / Low
Mode: balanced
Context: fresh
```

Escalation:

```text
Adaptive Effort
Low repair failed deterministic verification.
Escalating to a fresh Medium debugger.
```

Conceptual failure:

```text
Adaptive Effort
Recovery identified a design contradiction.
Returning control to planning.
```

Optional completion summary:

```text
Adaptive Effort summary

Low implementers:  1
Low repairs:       1
Medium debuggers:  0
High recoveries:   0
```

Do not expose private reasoning traces.

---

## 26. Security and trust

The plugin should remain small and auditable.

Requirements:

- no external telemetry by default
- no remote orchestration service
- no separate API keys
- no hidden network calls
- no dependency bootstrap scripts
- no bundled Superpowers code
- no unrelated configuration mutations
- no arbitrary executable downloads

The Git repository should contain the exact plugin source installed through the marketplace.

---

## 27. Compatibility

The package should record a tested compatibility matrix:

```text
Adaptive Effort     Superpowers     Codex
0.1.x               tested range    tested range
```

Runtime capability detection remains authoritative.

Behavior:

```text
Required capabilities present
    → enable

Required capabilities present,
unvalidated version combination
    → enable with concise compatibility warning

Required capability missing
    → disable Adaptive Effort
```

No fallback workflow is provided.

---

## 28. Testing

### Static validation

Verify:

- marketplace manifest
- `plugin.json`
- referenced paths
- skill metadata
- skill presentation metadata
- Python script syntax
- child models are unpinned
- no parent model/effort settings
- no global filesystem assumptions

### Policy tests

Test:

```text
Low succeeds
→ no escalation

Low fails, Low repair succeeds
→ no Medium

Low + repair fail
→ fresh Medium debugger

Medium identifies conceptual problem
→ High recovery

Environment failure
→ no reasoning escalation

Persistent failure
→ circuit breaker
```

### Superpowers integration

Exercise:

```text
design
→ plan
→ subagent-driven development
→ TDD
→ implementation
→ verification
→ review
```

Confirm that Adaptive Effort changes compute allocation without replacing Superpowers workflow semantics.

### Parent inheritance

Run with multiple parent configurations:

```text
Sol / Medium
Sol / High
another supported model
```

Verify:

```text
parent model unchanged
parent effort unchanged
child model inherited
child effort follows role policy
```

### Context behavior

Compare:

```text
full conversation inheritance
```

against:

```text
compact Adaptive Effort handoff
```

Child startup context should remain approximately bounded as parent history grows.

---

## 29. Benchmark

The central comparison is:

```text
A. Superpowers
   Parent Sol / High
   implementation children inherit High

B. Superpowers + Adaptive Effort
   Parent Sol / High
   implementation Low
   repair Low
   debugger Medium
   recovery High only when evidence warrants
```

Measure:

```text
task completion rate
acceptance-test success
regressions
review findings
wall-clock duration
input tokens
reasoning tokens
cached tokens
number of child agents
number of escalation events
```

Run the same comparison with a Medium parent.

The plugin is successful only if lower compute use does not materially degrade engineering outcomes.

---

## 30. Release scope

The plugin snapshot contains:

- native Codex plugin manifest
- Git community marketplace manifest
- Superpowers dependency detection
- one implicit Adaptive Effort skill
- Low implementer
- Medium debugger
- High recovery diagnostician
- inherited child model
- fresh-context handoff policy
- one cheap Low repair
- bounded escalation
- fast, balanced, and deep modes
- natural overrides
- doctor capability
- static and policy tests
- installation and compatibility documentation

Out of scope:

- automatic cross-model routing
- automatic Luna/Sol switching
- automatic XHigh/Max use
- learned complexity classification
- cost prediction
- persistent task history
- external orchestration runtime
- replacement of Superpowers workflow components

---

## 31. Repository snapshot

```text
adaptive-effort/
├── .agents/
│   └── plugins/
│       └── marketplace.json
├── .github/
│   └── workflows/
│       └── ci.yml
├── plugins/
│   └── adaptive-effort/
│       ├── .codex-plugin/
│       │   └── plugin.json
│       ├── assets/
│       │   ├── adaptive-effort-small.svg
│       │   └── adaptive-effort.svg
│       ├── README.md
│       ├── skills/
│       │   └── adaptive-effort/
│       │       ├── agents/
│       │       │   └── openai.yaml
│       │       ├── references/
│       │       │   ├── compatibility.md
│       │       │   ├── escalation-policy.md
│       │       │   ├── handoff-templates.md
│       │       │   ├── routing-policy.md
│       │       │   └── superpowers-integration.md
│       │       ├── scripts/
│       │       │   ├── doctor.py
│       │       │   └── policy.py
│       │       └── SKILL.md
├── scripts/
│   ├── package.py
│   └── validate.py
├── tests/
│   ├── test_doctor.py
│   ├── test_package.py
│   ├── test_policy.py
│   └── test_references.py
├── README.md
├── CHANGELOG.md
└── LICENSE
```

---

## 32. Quick start

Prerequisite:

```text
Install and enable Superpowers in Codex.
```

Add the community marketplace and plugin:

```bash
codex plugin marketplace add darvilp/adaptive-effort --ref main
codex plugin add adaptive-effort@adaptive-effort
```

Start a new Codex session.

Use Codex normally:

```text
Design and implement retry handling for this client.
```

Optional validation:

```text
Check Adaptive Effort setup.
```

No Adaptive Effort invocation is required for normal implementation work.

---

## 33. Success criteria

Adaptive Effort is successful when:

1. It installs as a normal Codex plugin from a Git marketplace.
2. It requires no wrapper executable or global configuration rewrite.
3. Superpowers remains the authoritative engineering workflow.
4. Users do not manually manage ordinary implementation/debugger agents.
5. Parent model and effort remain exactly as selected by the user.
6. Child models inherit the parent model.
7. Routine implementation normally runs at Low effort.
8. Escalation occurs in response to verification evidence.
9. Child context remains compact as the parent conversation grows.
10. Automatic retries terminate predictably.
11. Missing dependencies produce clear diagnostic behavior.
12. Compute use is materially below equivalent all-High workflows.
13. Correctness, tests, and review outcomes remain comparable.

The design is centered on one measurable hypothesis:

> **Strong planning, TDD, and deterministic verification allow low-effort agents to handle much of routine implementation, while evidence-driven escalation preserves performance on harder cases.**
