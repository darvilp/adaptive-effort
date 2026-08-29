#!/usr/bin/env python3
"""Validate the marketplace and plugin snapshot without third-party packages."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
PLUGIN = ROOT / "plugins" / "adaptive-effort"
MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"
SKILL = PLUGIN / "skills" / "adaptive-effort" / "SKILL.md"
PUBLIC_DIRECTORIES = (".agents", ".github", "docs", "plugins", "scripts", "tests")
PUBLIC_ROOT_FILES = {
    ".gitignore",
    "CHANGELOG.md",
    "DESIGN.md",
    "LICENSE",
    "Makefile",
    "README.md",
    "SECURITY.md",
    "SOURCES.md",
    "TEST_DRIVE.md",
    "TEST_RESULTS.md",
}
REPOSITORY_URL = "https://github.com/darvilp/adaptive-effort"
AUTHOR_URL = "https://github.com/darvilp"
PUBLISHER_PLACEHOLDER = "OWN" + "ER"


def fail(message: str) -> None:
    raise AssertionError(message)


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
    if manifest["version"] != "0.1.1":
        fail("manifest version must be 0.1.1")
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
    if interface.get("developerName") != "darvilp":
        fail("manifest developer name mismatch")
    if interface.get("websiteURL") != REPOSITORY_URL:
        fail("manifest website URL mismatch")
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
        "one same-thread low repair",
        "followup_task",
        "Activate implicitly only when",
        "Do not activate for generic delegation",
        "fresh medium debugger",
        "high recovery",
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
    for phrase in ("display_name:", "short_description:", "allow_implicit_invocation: true"):
        if phrase not in agent_text:
            fail(f"skill agent manifest missing: {phrase}")

    for script in ["doctor.py", "policy.py"]:
        path = SKILL.parent / "scripts" / script
        if not path.exists():
            fail(f"missing script: {script}")
        compile(path.read_text(encoding="utf-8"), str(path), "exec")

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
