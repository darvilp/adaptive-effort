#!/usr/bin/env python3
"""Validate the marketplace and plugin snapshot without third-party packages."""

from __future__ import annotations

import json
import re
import runpy
import shlex
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
PLUGIN = ROOT / "plugins" / "adaptive-effort"
MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"
SKILL = PLUGIN / "skills" / "adaptive-effort" / "SKILL.md"
POLICY_PATH = SKILL.parent / "scripts" / "policy.py"
PUBLIC_DIRECTORIES = (".agents", ".github", "docs", "plugins", "scripts", "submission", "tests")
PUBLIC_ROOT_FILES = {
    ".gitignore",
    "CHANGELOG.md",
    "DESIGN.md",
    "LICENSE",
    "Makefile",
    "PRIVACY.md",
    "README.md",
    "SECURITY.md",
    "SOURCES.md",
    "TEST_DRIVE.md",
    "TEST_RESULTS.md",
}
REPOSITORY_URL = "https://github.com/darvilp/adaptive-effort"
AUTHOR_URL = "https://github.com/darvilp"
PUBLISHER_PLACEHOLDER = "OWN" + "ER"
SHORT_DESCRIPTION = "Route Superpowers workers"
LONG_DESCRIPTION = "Adaptive Effort is a Codex compute-policy layer for approved Superpowers implementation plans. It preserves the parent model and effort, routes child reasoning by Fast, Balanced, or Deep mode, and uses classified evidence to bound debugging and recovery. Superpowers still owns planning, worker topology, TDD, reviews, and verification."
CAPABILITIES = [
    "Route implementation and review effort by mode",
    "Escalate failed repairs using evidence",
    "Record compact routing and closeout traces",
]
STARTER_PROMPTS = [
    "Implement this approved Superpowers plan with balanced Adaptive Effort routing.",
    "Implement this approved Superpowers plan with deep Adaptive Effort routing.",
    "Check Adaptive Effort setup live.",
]
LISTING_URLS = {
    "websiteURL": REPOSITORY_URL,
    "supportURL": f"{REPOSITORY_URL}/issues",
    "privacyPolicyURL": f"{REPOSITORY_URL}/blob/main/PRIVACY.md",
    "termsOfServiceURL": f"{REPOSITORY_URL}/blob/main/LICENSE",
}
POLICY = runpy.run_path(str(POLICY_PATH))
POLICY_ROUTE = POLICY["route"]
FAILURE_ROUTE = POLICY["failure_route"]
EFFORT_OVERRIDES = POLICY["EffortOverrides"]
VALIDATE_EFFORT_CAPS = POLICY["validate_effort_caps"]
REPAIR_EFFORT = POLICY["repair_effort"]
RECOVERY_QUALIFIER = "only with independent contract/design evidence"
FAST_RECOVERY_QUALIFIER = "only when explicitly requested; not automatic"
REVIEW_CASE_SEMANTICS = {
    "balanced-default": {
        "prompt": "Implement this approved Superpowers plan with balanced Adaptive Effort routing and no role assignments.",
        "expectedWorkflow": "Dispatch one fresh inherited-model Low implementer.",
        "expectedResult": "A compact dispatch/result trace separates worker status from the downstream gate.",
        "rationale": "Balanced routes implementation to Low without an upfront work classification.",
    },
    "deep-default": {
        "prompt": "Implement this approved Superpowers plan with deep Adaptive Effort routing and no role assignments.",
        "expectedWorkflow": "Dispatch a fresh inherited-model Medium implementer without assigning a preliminary work category.",
        "expectedResult": "The compact trace records the Deep Medium implementation route and the plan-owned boundary.",
        "rationale": "Deep always starts implementation at Medium.",
    },
    "semantic-repair": {
        "scenario": "In this Balanced example with no role assignments, after the Low implementer reports, run the checked-in local deterministic defect fixture once and return its exact classified output to the original worker.",
        "expectedWorkflow": "Send one same-thread correction to the original worker at its original effort.",
        "expectedResult": "One repair event cites the injected evidence, followed by separate worker and gate results.",
        "rationale": "The deterministic correction uses the single semantic allowance without a fresh worker.",
    },
    "fresh-debugger": {
        "scenario": "Only after the permitted same-thread correction reports and deterministic correction verification still fails, run the separate checked-in reasoning-defect fixture and classify that evidence as an implementation-reasoning defect.",
        "expectedWorkflow": "Dispatch the single fresh mode-routed debugger.",
        "expectedResult": "The trace records the separately classified reasoning-defect fingerprint and the corrective upward transition when effort increases.",
        "rationale": "A separate implementation-reasoning defect established after correction failure warrants the one fresh debugger.",
    },
    "planned-review": {
        "scenario": "Complete an approved plan in Fast mode with no role assignments and allow Superpowers to run specification review followed by code-quality review without injecting a worker failure.",
        "expectedWorkflow": "Use Low for both routine reviews without counting either as an escalation; correct and re-review any finding through the Superpowers workflow.",
        "expectedResult": "Worker status remains separate from each downstream review gate and the escalation count is unchanged.",
        "rationale": "Fast lowers routine review effort without removing the workflow gates.",
    },
    "task-local-effort-overrides": {
        "prompt": "Use Fast handling with effort implementer=medium routine-review=high high-risk-review=low debugger=xhigh recovery=max for this approved Superpowers task.",
        "expectedWorkflow": "Apply the five explicit role values over Fast defaults, retain worker effort for repairs, and check host/model compatibility before each dispatch when available.",
        "expectedResult": "The initial trace lists the canonical task-local overrides; High-risk review uses Low, and Fast recovery at Max still requires independent contract/design evidence.",
        "rationale": "Explicit task-local role values take precedence without changing repair identity, compatibility checks, or recovery authorization.",
    },
    "pre-plan": {
        "prompt": "Brainstorm and architect this feature.",
        "expectedWorkflow": "Do not activate Adaptive Effort.",
        "expectedResult": "Normal Superpowers design work occurs with no Adaptive Effort worker or routing trace.",
        "safeFallback": "Finish design and obtain explicit plan approval before implementation.",
    },
    "missing-superpowers": {
        "scenario": "Attempt an approved-plan implementation after confirming that the required Superpowers SKILL.md entrypoints are absent or disabled.",
        "expectedWorkflow": "Stop before dispatch.",
        "expectedResult": "A clear prerequisite failure names the missing Superpowers workflow skills and no Adaptive Effort worker runs.",
        "safeFallback": "Install Superpowers from its public repository, verify its SKILL.md entrypoints, and start another new Codex task.",
    },
    "fast-recovery-stop": {
        "scenario": "In Fast mode, exhaust the permitted repair and debugger, then provide independent contract/design evidence that would authorize recovery in Balanced or Deep.",
        "expectedWorkflow": "Do not restart the ladder and do not dispatch automatic High recovery in Fast.",
        "expectedResult": "A bounded stop report records the consumed stages and Fast recovery limit.",
        "safeFallback": "Return to the user or planning, or use Balanced or Deep for evidence-gated automatic recovery.",
    },
}
REVIEW_FAILURE_INJECTIONS = {
    "semantic-repair": {
        "command": "python3 scripts/review_case_fixture.py submission/fixtures/local-deterministic-defect.json",
        "expectedExit": 1,
        "expectedOutput": '{"actual":"medium","boundary":"Balanced implementation route","classification":"local deterministic implementation defect","expected":"low","fingerprint":"review-fixture-local-v1","invariant":"Balanced implementation uses Low effort"}',
        "sequence": [
            "Run the exact command after the original Low worker reports and the downstream gate detects expected Low but actual Medium.",
            "Copy the single output line and exit code 1 into a same-thread correction sent to the original worker.",
        ],
    },
    "fresh-debugger": {
        "command": "python3 scripts/review_case_fixture.py submission/fixtures/implementation-reasoning-failure.json",
        "expectedExit": 1,
        "expectedOutput": '{"actual":"policy low; reviewer evidence medium after correction","boundary":"routing policy and reviewer contract","classification":"implementation-reasoning defect","expected":"low in both policy and reviewer evidence","fingerprint":"review-fixture-reasoning-v1","invariant":"Balanced implementation uses Low effort across policy and reviewer evidence"}',
        "sequence": [
            "Complete the same-thread correction and rerun the exact deterministic verification.",
            "Only if correction verification fails across the canonical policy and reviewer evidence, run the exact command above.",
            "Copy the single output line and exit code 1 into the failure report, preserving the command, fingerprint, classification, boundary, invariant, expected value, and actual value.",
        ],
    },
}
REVIEW_FAILURE_ROUTES = {
    "semantic-repair": "semantic_correction",
    "fresh-debugger": "debugger",
}
REVIEW_SETUP_PREFIX = "Clone https://github.com/darvilp/adaptive-effort and check out public main. Verify that plugins/adaptive-effort/.codex-plugin/plugin.json reports version 0.1.3."
CURRENT_PLUGIN_URLS = {
    "https://developers.openai.com/plugins",
    "https://developers.openai.com/plugins/build/plugins",
    "https://developers.openai.com/plugins/deploy/submission",
}
ROUTING_POLICY_CONSUMERS = (
    ROOT / "README.md",
    ROOT / "DESIGN.md",
    ROOT / "docs/design.md",
    ROOT / "TEST_DRIVE.md",
    PLUGIN / "README.md",
    SKILL,
    SKILL.parent / "references/routing-policy.md",
    SKILL.parent / "references/escalation-policy.md",
    SKILL.parent / "references/superpowers-integration.md",
)
ROUTING_CONTRACT_PHRASES = (
    "no-override defaults",
    "Explicit role assignments patch the selected mode's profile",
    "`profile.implementer`",
    "`profile.routine_review`",
    "`profile.high_risk_review`",
    "`profile.debugger`",
    "`profile.recovery`",
    "`profile.recovery_explicitly_requested`",
    "independent contract/design evidence",
    "actual writer route",
)
FIXED_EFFORT_REVIEW_CASE_IDS = (
    "balanced-default",
    "deep-default",
    "semantic-repair",
    "planned-review",
)
FORBIDDEN_UNCONDITIONAL_ROUTING = (
    "Action: start a fresh debugger at medium effort, or high in deep mode.",
    "Action: stop automatic handling in Fast.",
    "Fast has no automatic recovery transition.",
    "- recovery diagnostician: route=high/fresh",
)


def fail(message: str) -> None:
    raise AssertionError(message)


def is_numeric_test_pass_claim(sentence: str) -> bool:
    signals = (
        r"\b\d+\b",
        r"\bpass(?:ed|es)?\b",
        r"\btests?\b|\bunit\s+suite\b",
    )
    return all(re.search(signal, sentence, flags=re.IGNORECASE) for signal in signals)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"{path}: invalid JSON: {exc}")


def public_files() -> list[Path]:
    files = [ROOT / name for name in PUBLIC_ROOT_FILES]
    for directory in PUBLIC_DIRECTORIES:
        files.extend((ROOT / directory).rglob("*"))
    return sorted(
        path
        for path in files
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix not in {".pyc", ".zip"}
    )


def validate() -> list[str]:
    notes: list[str] = []

    marketplace = load_json(MARKETPLACE)
    if marketplace.get("name") != "adaptive-effort":
        fail("marketplace name must be adaptive-effort")
    entries = marketplace.get("plugins")
    if not isinstance(entries, list) or len(entries) != 1:
        fail("marketplace must contain exactly one plugin entry")
    entry = entries[0]
    if entry.get("name") != "adaptive-effort":
        fail("marketplace plugin name mismatch")
    if entry.get("source") != {"source": "local", "path": "./plugins/adaptive-effort"}:
        fail("marketplace source path mismatch")
    policy = entry.get("policy", {})
    if policy.get("installation") != "AVAILABLE" or policy.get("authentication") not in {"ON_INSTALL", "ON_USE"}:
        fail("marketplace policy incomplete")
    if entry.get("category") != "Developer Tools":
        fail("marketplace category mismatch")

    manifest = load_json(MANIFEST)
    required = {"name", "version", "description", "skills", "interface"}
    missing = required - manifest.keys()
    if missing:
        fail(f"manifest missing fields: {sorted(missing)}")
    if manifest["name"] != PLUGIN.name:
        fail("manifest name must match plugin folder")
    if manifest.get("description") != SHORT_DESCRIPTION:
        fail("manifest description mismatch")
    if manifest["version"] != "0.1.3":
        fail("manifest version must be 0.1.3")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", manifest["version"]):
        fail("manifest version is not semver-like")
    if manifest["skills"] != "./skills/":
        fail("manifest skills path must be ./skills/")
    if manifest.get("author") != {"name": "darvilp", "url": AUTHOR_URL}:
        fail("manifest author metadata mismatch")
    for field in ("homepage", "repository"):
        if manifest.get(field) != REPOSITORY_URL:
            fail(f"manifest {field} URL mismatch")
    interface = manifest.get("interface", {})
    if interface.get("displayName") != "Adaptive Effort":
        fail("manifest display name mismatch")
    if interface.get("developerName") != "darvilp":
        fail("manifest developer name mismatch")
    if interface.get("websiteURL") != REPOSITORY_URL:
        fail("manifest website URL mismatch")
    expected_interface = {
        "shortDescription": SHORT_DESCRIPTION,
        "longDescription": LONG_DESCRIPTION,
        "privacyPolicyURL": f"{REPOSITORY_URL}/blob/main/PRIVACY.md",
        "termsOfServiceURL": f"{REPOSITORY_URL}/blob/main/LICENSE",
    }
    for key, value in expected_interface.items():
        if interface.get(key) != value:
            fail(f"manifest {key} mismatch")
    if interface.get("capabilities") != CAPABILITIES:
        fail("manifest capabilities mismatch")
    if interface.get("defaultPrompt") != STARTER_PROMPTS:
        fail("manifest starter prompts mismatch")
    if "agents" in manifest:
        fail("current plugin schema does not support bundled custom agents")
    for path_key in ("composerIcon", "logo"):
        rel = manifest.get("interface", {}).get(path_key)
        if rel and not (PLUGIN / rel.removeprefix("./")).exists():
            fail(f"missing interface asset: {rel}")

    text = SKILL.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail("SKILL.md must start with YAML frontmatter")
    frontmatter = text.split("---", 2)[1]
    if "name: adaptive-effort" not in frontmatter:
        fail("skill name missing")
    if "description:" not in frontmatter:
        fail("skill description missing")
    required_phrases = [
        "Do not alter the parent model",
        "omit `model`",
        'fork_turns="none"',
        "one semantic same-thread correction",
        "followup_task",
        "Activate implicitly only when",
        "Do not activate for generic delegation",
        "Deep always starts implementers at Medium",
        "Fast stops automatic handling before High recovery",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            fail(f"skill missing policy phrase: {phrase}")
    forbidden = ["reasoning_effort:  xhigh", "reasoning_effort:  max", "model: gpt-", "agent_type:"]
    lowered = text.lower()
    for phrase in forbidden:
        if phrase in lowered:
            fail(f"skill contains forbidden automatic routing: {phrase}")

    for ref in [
        "routing-policy.md",
        "escalation-policy.md",
        "handoff-templates.md",
        "superpowers-integration.md",
        "compatibility.md",
    ]:
        if not (SKILL.parent / "references" / ref).exists():
            fail(f"missing reference: {ref}")

    agent_manifest = SKILL.parent / "agents" / "openai.yaml"
    if not agent_manifest.exists():
        fail("missing skill agents/openai.yaml")
    agent_text = agent_manifest.read_text(encoding="utf-8")
    for phrase in ("display_name:", "short_description:", "allow_implicit_invocation: true", "products: [CODEX]", "$adaptive-effort"):
        if phrase not in agent_text:
            fail(f"skill agent manifest missing: {phrase}")

    for script in ["doctor.py", "policy.py"]:
        path = SKILL.parent / "scripts" / script
        if not path.exists():
            fail(f"missing script: {script}")
        compile(path.read_text(encoding="utf-8"), str(path), "exec")

    listing = load_json(ROOT / "submission/listing.json")
    cases = load_json(ROOT / "submission/review-cases.json")
    expected_listing = {
        "name": "adaptive-effort", "version": "0.1.3", "displayName": "Adaptive Effort",
        "shortDescription": SHORT_DESCRIPTION, "longDescription": LONG_DESCRIPTION,
        "developerName": "darvilp", "category": "Developer Tools",
        "capabilities": CAPABILITIES, "starterPrompts": STARTER_PROMPTS, **LISTING_URLS,
    }
    if listing != expected_listing:
        fail("submission listing does not match the exact approved metadata")
    if len(cases.get("positiveCases", [])) != 6 or len(cases.get("negativeCases", [])) != 3:
        fail("review pack must contain exactly six positive and three negative cases")
    prerequisite = cases.get("externalPrerequisite", {})
    if prerequisite.get("name") != "Superpowers" or not all(
        phrase in prerequisite.get("verification", "")
        for phrase in ("github.com/obra/superpowers", "new Codex task", "SKILL.md")
    ):
        fail("review pack must provide concrete external Superpowers verification")
    positive_ids = ["balanced-default", "deep-default", "semantic-repair", "fresh-debugger", "planned-review", "task-local-effort-overrides"]
    negative_ids = ["pre-plan", "missing-superpowers", "fast-recovery-stop"]
    if [case.get("id") for case in cases["positiveCases"]] != positive_ids or [case.get("id") for case in cases["negativeCases"]] != negative_ids:
        fail("review case scenarios or order mismatch")
    for kind, review_cases in (("positive", cases["positiveCases"]), ("negative", cases["negativeCases"])):
        required_fields = {"id", "publicSetup", "expectedWorkflow", "expectedResult", "rationale" if kind == "positive" else "safeFallback"}
        for case in review_cases:
            if not ({"prompt", "scenario"} & case.keys()) or not required_fields <= case.keys():
                fail(f"review {kind} case fields incomplete: {case.get('id')}")
            setup = case.get("publicSetup", "")
            if REPOSITORY_URL not in setup or "new Codex task" not in setup:
                fail(f"review case is not publicly reproducible: {case.get('id')}")
            if "tag 0.1.3" in setup.lower() or not setup.startswith(REVIEW_SETUP_PREFIX):
                fail(f"review case public setup must use public main and manifest version: {case.get('id')}")
            if kind == "positive" and case["id"] in FIXED_EFFORT_REVIEW_CASE_IDS:
                serialized_case = json.dumps(case).lower()
                if "no role assignments" not in serialized_case:
                    fail(
                        "fixed-effort review case must say no role assignments: "
                        f"{case['id']}"
                    )
            expected_semantics = REVIEW_CASE_SEMANTICS[case["id"]]
            actual_semantics = {field: case.get(field) for field in expected_semantics}
            if actual_semantics != expected_semantics:
                fail(f"review case semantics mismatch: {case.get('id')}")
    for case_id in ("semantic-repair", "fresh-debugger"):
        case = next(case for case in cases["positiveCases"] if case["id"] == case_id)
        injection = case.get("evidenceInjection", {})
        expected_injection = REVIEW_FAILURE_INJECTIONS[case_id]
        if injection != expected_injection:
            fail(f"review case evidence injection mismatch: {case_id}")
        fixture_path = ROOT / shlex.split(injection["command"])[-1]
        fixture = load_json(fixture_path)
        actual_route = FAILURE_ROUTE(fixture.get("classification"))
        if actual_route != REVIEW_FAILURE_ROUTES[case_id]:
            fail(f"review case canonical failure route mismatch: {case_id}")
        serialized = json.dumps(fixture, sort_keys=True, separators=(",", ":"))
        if serialized != injection["expectedOutput"]:
            fail(f"review failure fixture output mismatch: {case_id}")
    override_fixture = load_json(ROOT / "submission/fixtures/task-local-effort-overrides.json")
    expected_assignments = [
        "implementer=medium",
        "routine-review=high",
        "high-risk-review=low",
        "debugger=xhigh",
        "recovery=max",
    ]
    if override_fixture != {
        "mode": "fast",
        "effortAssignments": expected_assignments,
        "routes": [
            {"name": "implementer", "role": "implementer", "expectedEffort": "medium"},
            {"name": "routine-review", "role": "reviewer", "risk": "routine", "expectedEffort": "high"},
            {"name": "high-risk-review", "role": "reviewer", "risk": "high", "expectedEffort": "low"},
            {"name": "debugger", "role": "debugger", "expectedEffort": "xhigh"},
            {"name": "recovery", "role": "recovery", "expectedEffort": "max"},
        ],
        "repairs": [
            {"currentWriterRole": "implementer", "expectedEffort": "medium"},
            {"currentWriterRole": "debugger", "expectedEffort": "xhigh"},
            {"currentWriterRole": "recovery", "expectedEffort": "max"},
        ],
        "conflictingInput": {
            "cap": "implementer=low",
            "assignment": "implementer=high",
            "expectedError": "effort override conflicts with cap: implementer=high exceeds low",
        },
        "fastRecovery": {"withoutEvidence": "stop", "withEvidence": "recovery"},
    }:
        fail("task-local effort override fixture mismatch")
    override_values = {
        key.replace("-", "_"): effort
        for key, effort in (
            assignment.split("=", 1)
            for assignment in override_fixture["effortAssignments"]
        )
    }
    effort_overrides = EFFORT_OVERRIDES(**override_values)
    for repair in override_fixture["repairs"]:
        writer_route = POLICY_ROUTE(
            override_fixture["mode"], repair["currentWriterRole"],
            effort_overrides=effort_overrides,
        )
        if REPAIR_EFFORT(writer_route) != repair["expectedEffort"]:
            fail("task-local repair does not retain current writer effort")
    conflict = override_fixture["conflictingInput"]
    try:
        VALIDATE_EFFORT_CAPS(
            EFFORT_OVERRIDES(implementer=conflict["assignment"].split("=", 1)[1]),
            EFFORT_OVERRIDES(implementer=conflict["cap"].split("=", 1)[1]),
        )
    except ValueError as exc:
        if str(exc) != conflict["expectedError"]:
            fail("task-local cap conflict error mismatch")
    else:
        fail("task-local cap conflict was not rejected")
    recovery = override_fixture["fastRecovery"]
    if FAILURE_ROUTE(
        "contract/design defect", mode="fast", effort_overrides=effort_overrides,
    ) != recovery["withoutEvidence"] or FAILURE_ROUTE(
        "contract/design defect", mode="fast",
        independent_contract_design_evidence=True,
        effort_overrides=effort_overrides,
    ) != recovery["withEvidence"]:
        fail("task-local Fast recovery authorization mismatch")
    if FAILURE_ROUTE("contract/design defect", mode="balanced") != "stop" or FAILURE_ROUTE(
        "contract/design defect", mode="balanced", independent_contract_design_evidence=True,
    ) != "recovery":
        fail("canonical recovery authorization rule mismatch")
    if FAILURE_ROUTE(
        "contract/design defect", mode="fast", independent_contract_design_evidence=True,
    ) != "stop":
        fail("canonical Fast recovery stop rule mismatch")
    portal = (ROOT / "submission/portal-checklist.md").read_text(encoding="utf-8")
    for gate in ("Apps Management Write", "verified `darvilp` identity", "Skills only draft", "exact CI submission artifact", "successful skill scan", "attestations only after", "Submit for Review", "Publish manually", "new-task pickup", "live routing"):
        if gate not in portal:
            fail(f"portal checklist missing gate: {gate}")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    bundled_readme = (PLUGIN / "README.md").read_text(encoding="utf-8")
    routing_policy = (SKILL.parent / "references/routing-policy.md").read_text(encoding="utf-8")
    escalation_policy = (SKILL.parent / "references/escalation-policy.md").read_text(encoding="utf-8")
    required_readme = [
        "| Implementation | Low | Low | Medium |",
        "| Routine spec review | Low | Medium | High |",
        "| Fresh debugger | Medium | Medium | High |",
        "Explicit role assignments patch the selected mode's profile",
        "Superpowers determines the plan tasks, execution boundaries, worker count, sequential versus parallel topology",
        "Planned reviewers are planned routes, not escalation events",
    ]
    for phrase in required_readme:
        if phrase not in readme:
            fail(f"README routing/topology agreement missing: {phrase}")
    recovery_efforts = [
        POLICY_ROUTE(mode, "recovery").reasoning_effort
        for mode in ("fast", "balanced", "deep")
    ]
    if recovery_efforts != ["high", "high", "high"]:
        fail("canonical recovery route effort mismatch")
    root_recovery_row = (
        f"| Recovery diagnostician | High {FAST_RECOVERY_QUALIFIER} | "
        f"High, {RECOVERY_QUALIFIER} | High, {RECOVERY_QUALIFIER} |"
    )
    policy_recovery_row = (
        f"| Recovery diagnostician | high {FAST_RECOVERY_QUALIFIER} | "
        f"high, {RECOVERY_QUALIFIER} | high, {RECOVERY_QUALIFIER} |"
    )
    if root_recovery_row not in readme:
        fail("README recovery authorization disagrees with canonical policy")
    if root_recovery_row not in bundled_readme:
        fail("bundled README recovery authorization disagrees with canonical policy")
    if policy_recovery_row not in routing_policy:
        fail("routing policy recovery authorization disagrees with canonical policy")
    authorization_rule = "Only the recovery diagnostician requires contract/design evidence"
    if authorization_rule not in escalation_policy:
        fail("recovery authorization rule disagrees with canonical policy")

    for path in ROUTING_POLICY_CONSUMERS:
        consumer = path.read_text(encoding="utf-8")
        for phrase in ROUTING_CONTRACT_PHRASES:
            if phrase not in consumer:
                fail(
                    "routing policy consumer omits the task-local profile contract in "
                    f"{path.relative_to(ROOT)}: {phrase}"
                )
        for stale in FORBIDDEN_UNCONDITIONAL_ROUTING:
            if stale.lower() in consumer.lower():
                fail(
                    "routing policy consumer contains unconditional fixed routing in "
                    f"{path.relative_to(ROOT)}: {stale}"
                )

    routing_guidance = {
        ROOT / "DESIGN.md": (
            "A broader implementation failure gets one fresh debugger at `profile.debugger`.",
            "Recovery uses `profile.recovery` only with independent contract/design evidence.",
        ),
        ROOT / "docs" / "design.md": (
            "reasoning effort:  profile.debugger",
            "Explicit role assignments replace the corresponding values above.",
        ),
        SKILL.parent / "references" / "handoff-templates.md": (
            "<implementation, retained-effort repair, debugger outcomes>",
        ),
    }
    for path, phrases in routing_guidance.items():
        guidance = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in guidance:
                fail(f"routing guidance mismatch in {path.relative_to(ROOT)}: {phrase}")

    documentation_paths = [
        ROOT / "README.md",
        ROOT / "DESIGN.md",
        ROOT / "docs/design.md",
        ROOT / "SOURCES.md",
        PLUGIN / "README.md",
        SKILL.parent / "references/compatibility.md",
    ]
    documentation = "\n".join(path.read_text(encoding="utf-8") for path in documentation_paths)
    for stale in (
        "community-marketplace",
        "community marketplace",
        "Git-hosted community marketplace",
        "https://developers.openai.com/codex/plugins",
        "https://developers.openai.com/codex/build-plugins",
        "https://developers.openai.com/plugins/submit/",
    ):
        if stale.lower() in documentation.lower():
            fail(f"distribution documentation contains stale terminology or URL: {stale}")
    sources = (ROOT / "SOURCES.md").read_text(encoding="utf-8")
    compatibility = (SKILL.parent / "references/compatibility.md").read_text(encoding="utf-8")
    for current_url in CURRENT_PLUGIN_URLS:
        if current_url not in sources or current_url not in compatibility:
            fail(f"distribution documentation missing current URL: {current_url}")
    test_results = (ROOT / "TEST_RESULTS.md").read_text(encoding="utf-8")
    for phrase in (
        "Fresh local verification for this commit:",
        "CI is configured to run",
        "No CI result is claimed for this unpushed commit.",
    ):
        if phrase not in test_results:
            fail(f"CI evidence documentation missing: {phrase}")
    if "repository verification is recorded in the release implementation report and CI" in test_results:
        fail("CI evidence documentation claims an unrun CI result")
    verification_marker = "Fresh local verification for this commit:"
    current_verification = test_results.split(verification_marker, 1)[1].lstrip("\n").split("\n\n", 1)[0]
    unit_suite_evidence = "`scripts/validate.py` passed, and the full unit suite passed."
    if unit_suite_evidence not in current_verification:
        fail("TEST_RESULTS unit-suite evidence is missing or stale")
    current_verification_sentences = re.split(r"(?<=[.!?])(?:\s+|$)", current_verification)
    if any(is_numeric_test_pass_claim(sentence) for sentence in current_verification_sentences):
        fail("TEST_RESULTS unit-suite evidence uses a brittle numeric count")
    policy_evidence = (
        "`plugins/adaptive-effort/skills/adaptive-effort/scripts/doctor.py` remains unchanged. "
        "`plugins/adaptive-effort/skills/adaptive-effort/scripts/policy.py` now differentiates Fast, "
        "Balanced, and Deep implementation, review, debugging, and automatic recovery routes."
    )
    if policy_evidence not in test_results:
        fail("TEST_RESULTS policy evidence is missing or false")
    if "`scripts/policy.py` and `doctor.py` are unchanged." in test_results:
        fail("TEST_RESULTS policy evidence falsely claims policy.py is unchanged")
    forbidden_names = {"apps", "mcp", "screenshots", "hooks"}
    forbidden_paths = [path for path in PLUGIN.rglob("*") if path.name.lower() in forbidden_names or path.suffix == ".toml" or path.is_symlink()]
    if forbidden_paths:
        fail(f"plugin contains forbidden submission surfaces: {forbidden_paths}")

    owner_paths = [
        path.relative_to(ROOT).as_posix()
        for path in public_files()
        if PUBLISHER_PLACEHOLDER in path.read_text(encoding="utf-8")
    ]
    if owner_paths:
        fail(f"public files contain the owner placeholder: {owner_paths}")

    notes.append("marketplace manifest valid")
    notes.append("plugin manifest valid")
    notes.append("skill and references valid")
    notes.append("skill agent metadata valid")
    notes.append("scripts compile")
    notes.append("public metadata valid")
    notes.append("submission reviewer pack valid")
    return notes


def main() -> int:
    try:
        notes = validate()
    except AssertionError as exc:
        print(f"VALIDATION FAILED: {exc}", file=sys.stderr)
        return 1
    for note in notes:
        print(f"PASS: {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
