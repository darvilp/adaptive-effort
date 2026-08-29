#!/usr/bin/env python3
"""Inspect Adaptive Effort and Superpowers across the active and adjacent Codex surfaces."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    tomllib = None

REQUIRED_SKILLS = {
    "subagent-driven-development",
    "test-driven-development",
    "verification-before-completion",
}
REVIEW_SKILLS = {"requesting-code-review", "receiving-code-review"}
BLOCKING_CHECKS = {"adaptive_effort_skill", "superpowers_skills", "multi_agent_config"}


@dataclass
class Check:
    name: str
    status: str
    detail: str
    surface: str


def _run(command: list[str], timeout: int = 15) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, "", str(exc)


def _iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from _iter_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_strings(child)


def _detect_surface() -> str:
    if os.name == "nt":
        return "windows"
    release = platform.release().lower()
    if os.environ.get("WSL_INTEROP") or os.environ.get("WSL_DISTRO_NAME") or "microsoft" in release:
        return "wsl"
    return "linux"


def _codex_plugin_check(codex: str, surface: str) -> Check:
    rc, stdout, stderr = _run([codex, "plugin", "list", "--json"])
    if rc != 0:
        detail = stderr.strip() or stdout.strip() or f"exit {rc}"
        return Check(
            "superpowers_plugin",
            "WARN",
            f"Codex plugin list unavailable: {detail}",
            surface,
        )
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return Check(
            "superpowers_plugin",
            "WARN",
            f"Could not parse Codex plugin JSON: {exc}",
            surface,
        )
    found = any("superpowers" in item.lower() for item in _iter_strings(payload))
    if found:
        return Check(
            "superpowers_plugin",
            "PASS",
            "Superpowers appears in Codex plugin inventory.",
            surface,
        )
    return Check(
        "superpowers_plugin",
        "WARN",
        "Superpowers was not found in this CLI inventory; capability detection remains authoritative.",
        surface,
    )


def _candidate_roots(
    home: Path, cwd: Path, *, use_environment: bool = True
) -> list[Path]:
    codex_home = (
        Path(os.environ.get("CODEX_HOME", home / ".codex")) if use_environment else home / ".codex"
    )
    return [
        cwd / ".agents" / "skills",
        home / ".agents" / "skills",
        codex_home / "plugins",
        codex_home / "plugins" / "cache",
        home / "plugins",
    ]


def _discover_skill_files(roots: list[Path]) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for root in roots:
        if not root.exists():
            continue
        try:
            candidates = root.rglob("SKILL.md")
        except OSError:
            continue
        for skill_file in candidates:
            name = skill_file.parent.name
            if name in REQUIRED_SKILLS or name in REVIEW_SKILLS:
                found.setdefault(name, []).append(str(skill_file))
    return found


def _filesystem_superpowers_check(
    home: Path, cwd: Path, surface: str, *, use_environment: bool = True
) -> Check:
    found = _discover_skill_files(_candidate_roots(home, cwd, use_environment=use_environment))
    missing = sorted(REQUIRED_SKILLS - found.keys())
    has_review = bool(REVIEW_SKILLS & found.keys())
    if not missing and has_review:
        locations = sorted({str(Path(path).parent.parent) for paths in found.values() for path in paths})
        return Check(
            "superpowers_skills",
            "PASS",
            "Required Superpowers skills found under: " + ", ".join(locations[:5]),
            surface,
        )
    pieces = []
    if missing:
        pieces.append("missing " + ", ".join(missing))
    if not has_review:
        pieces.append("no review workflow skill found")
    return Check("superpowers_skills", "FAIL", "; ".join(pieces), surface)


def _agents_config_check(
    home: Path, cwd: Path, surface: str, *, use_environment: bool = True
) -> Check:
    codex_home = (
        Path(os.environ.get("CODEX_HOME", home / ".codex")) if use_environment else home / ".codex"
    )
    user_config_path = codex_home / "config.toml"
    if tomllib is None:
        if not user_config_path.exists():
            return Check(
                "multi_agent_config",
                "PASS",
                "No applicable user or trusted-project override found; subagents default to enabled.",
                surface,
            )
        return Check(
            "multi_agent_config",
            "FAIL",
            "Python tomllib unavailable; config not parsed.",
            surface,
        )

    user_data: dict[str, Any] = {}
    config_paths: list[Path] = []
    if user_config_path.exists():
        try:
            user_data = tomllib.loads(user_config_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            return Check(
                "multi_agent_config",
                "FAIL",
                f"Could not parse {user_config_path}: {exc}",
                surface,
            )
        config_paths.append(user_config_path)

    cwd = cwd.resolve()
    projects = user_data.get("projects", {})
    if not isinstance(projects, dict):
        return Check(
            "multi_agent_config",
            "FAIL",
            f"Could not evaluate {user_config_path}: projects must be a table.",
            surface,
        )

    trust_matches: list[tuple[int, Path, str]] = []
    for raw_path, settings in projects.items():
        if not isinstance(settings, dict):
            continue
        trust_level = settings.get("trust_level")
        if trust_level not in {"trusted", "untrusted"}:
            continue
        project_path = Path(raw_path).expanduser().resolve()
        if cwd == project_path or project_path in cwd.parents:
            trust_matches.append((len(project_path.parts), project_path, trust_level))

    trusted_root: Path | None = None
    if trust_matches:
        _, matched_root, trust_level = max(trust_matches, key=lambda item: item[0])
        if trust_level == "trusted":
            trusted_root = matched_root

    if trusted_root is not None:
        current = trusted_root
        project_dirs = [current]
        for part in cwd.relative_to(trusted_root).parts:
            current = current / part
            project_dirs.append(current)
        config_paths.extend(
            config_path
            for directory in project_dirs
            if (config_path := directory / ".codex" / "config.toml").exists()
        )

    enabled = True
    effective_path: Path | None = None
    for config_path in config_paths:
        try:
            data = (
                user_data
                if config_path == user_config_path
                else tomllib.loads(config_path.read_text(encoding="utf-8"))
            )
            agents = data.get("agents", {})
            if not isinstance(agents, dict):
                raise ValueError("agents must be a table")
            configured = agents.get("enabled")
            if configured is not None:
                if not isinstance(configured, bool):
                    raise ValueError("agents.enabled must be a boolean")
                enabled = configured
                effective_path = config_path
        except Exception as exc:  # noqa: BLE001
            return Check(
                "multi_agent_config",
                "FAIL",
                f"Could not parse or evaluate {config_path}: {exc}",
                surface,
            )

    if enabled is False:
        assert effective_path is not None
        return Check(
            "multi_agent_config",
            "FAIL",
            f"Subagents are disabled by the effective setting in {effective_path}.",
            surface,
        )
    if effective_path is None:
        detail = "No applicable user or trusted-project override found; subagents default to enabled."
    else:
        detail = f"Subagents are enabled by the effective setting in {effective_path}."
    return Check(
        "multi_agent_config",
        "PASS",
        detail,
        surface,
    )


def _windows_home_from_wsl() -> Path | None:
    rc, stdout, _ = _run(["cmd.exe", "/d", "/c", "echo", "%USERPROFILE%"], timeout=5)
    profile = stdout.strip()
    if rc != 0 or not profile or profile == "%USERPROFILE%":
        return None
    rc, converted, _ = _run(["wslpath", "-u", profile], timeout=5)
    if rc != 0:
        return None
    path = Path(converted.strip())
    return path if path.exists() else None


def _discover_adjacent_homes(active_surface: str) -> dict[str, Path]:
    if active_surface == "wsl":
        windows_home = _windows_home_from_wsl()
        return {"windows": windows_home} if windows_home else {}
    return {}


def inspect(
    home: Path | None = None,
    cwd: Path | None = None,
    *,
    active_surface: str | None = None,
    adjacent_homes: Mapping[str, Path] | None = None,
    runtime_verified: bool = False,
) -> dict[str, Any]:
    home_was_explicit = home is not None
    home = home or Path.home()
    cwd = cwd or Path.cwd()
    active_surface = active_surface or _detect_surface()
    checks: list[Check] = []

    script_path = Path(__file__).resolve()
    skill_root = script_path.parent.parent
    checks.append(
        Check(
            "adaptive_effort_skill",
            "PASS" if (skill_root / "SKILL.md").exists() else "FAIL",
            str(skill_root),
            active_surface,
        )
    )

    codex = shutil.which("codex")
    if codex:
        rc, stdout, stderr = _run([codex, "--version"])
        version = (stdout or stderr).strip()
        checks.append(
            Check(
                "codex_cli",
                "PASS" if rc == 0 else "WARN",
                version or f"Found {codex}, version command exited {rc}.",
                active_surface,
            )
        )
        checks.append(_codex_plugin_check(codex, active_surface))
    else:
        checks.append(
            Check(
                "codex_cli",
                "WARN",
                "Codex CLI not found on PATH. App-only installation cannot be fully inspected here.",
                active_surface,
            )
        )

    checks.append(
        _filesystem_superpowers_check(
            home, cwd, active_surface, use_environment=not home_was_explicit
        )
    )
    checks.append(
        _agents_config_check(
            home, cwd, active_surface, use_environment=not home_was_explicit
        )
    )

    discovered_homes = (
        _discover_adjacent_homes(active_surface)
        if adjacent_homes is None
        else dict(adjacent_homes)
    )
    for surface, adjacent_home in sorted(discovered_homes.items()):
        if surface == active_surface:
            continue
        checks.append(
            _filesystem_superpowers_check(
                adjacent_home, adjacent_home, surface, use_environment=False
            )
        )
        checks.append(
            _agents_config_check(
                adjacent_home, adjacent_home, surface, use_environment=False
            )
        )

    active_blockers = [
        check
        for check in checks
        if check.surface == active_surface
        and check.name in BLOCKING_CHECKS
        and check.status == "FAIL"
    ]
    if active_blockers:
        readiness = "BLOCKED"
    elif runtime_verified:
        readiness = "RUNTIME_VERIFIED"
    else:
        readiness = "STATIC_READY"

    return {
        "readiness": readiness,
        "active_surface": active_surface,
        "checks": [asdict(check) for check in checks],
        "notes": [
            "STATIC_READY covers only the local skill and effective user/trusted-project configuration checks listed above.",
            "Request 'Check Adaptive Effort setup live' to perform one low-effort smoke spawn.",
            "RUNTIME_VERIFIED means the exact-token child spawn/tool path completed with the requested settings; model, effort, and context metadata require separate direct evidence.",
            "Adjacent-surface failures are informational unless that surface becomes active.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--project-dir",
        type=Path,
        metavar="PATH",
        help=(
            "Active project working directory whose trusted project config should "
            "be inspected; defaults to the process working directory."
        ),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero unless runtime routing is verified and no warnings remain.",
    )
    args = parser.parse_args()

    project_dir = args.project_dir
    if project_dir is not None:
        project_dir = project_dir.expanduser().resolve()
        if not project_dir.is_dir():
            parser.error(f"project directory is not a directory: {project_dir}")

    result = inspect(cwd=project_dir)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Adaptive Effort doctor: {result['readiness']}")
        for check in result["checks"]:
            print(
                f"[{check['status']}] {check['surface']}/{check['name']}: "
                f"{check['detail']}"
            )
        for note in result["notes"]:
            print(f"NOTE: {note}")

    if result["readiness"] == "BLOCKED":
        return 1
    if args.strict and (
        result["readiness"] != "RUNTIME_VERIFIED"
        or any(check["status"] != "PASS" for check in result["checks"])
    ):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
