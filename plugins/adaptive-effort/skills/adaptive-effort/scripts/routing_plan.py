#!/usr/bin/env python3
"""Show one resolved Adaptive Effort plan and local model candidates."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Literal

_previous_bytecode_setting = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    import policy
finally:
    sys.dont_write_bytecode = _previous_bytecode_setting

MultiAgentVersion = Literal["v1", "v2", "unknown"]

PUBLIC_ROUTES = (
    ("implementer", "implementer", "routine"),
    ("routine-review", "reviewer", "routine"),
    ("high-risk-review", "reviewer", "high"),
    ("debugger", "debugger", "routine"),
    ("recovery", "recovery", "routine"),
)


def unavailable_catalog(
    reason: str, *, executable: str | None = None, version: str | None = None
) -> dict[str, Any]:
    return {
        "status": "unavailable",
        "scope": "local-client-candidates",
        "authority": "active-spawn-host",
        "source": {
            "kind": "codex-debug-models",
            "executable": executable,
            "version": version,
        },
        "surface_match": "unverified",
        "reason": reason,
        "models": [],
    }


def command_output(
    executable: str, arguments: list[str]
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [executable, *arguments],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,
        check=False,
    )


def discover_model_candidates(
    multi_agent_version: MultiAgentVersion,
) -> dict[str, Any]:
    executable = shutil.which("codex")
    if executable is None:
        return unavailable_catalog("codex executable not found on PATH")
    executable = str(Path(executable).resolve())

    version: str | None = None
    try:
        version_result = command_output(executable, ["--version"])
        if version_result.returncode == 0:
            version = version_result.stdout.strip() or None
    except (subprocess.TimeoutExpired, OSError):
        pass

    try:
        result = command_output(executable, ["debug", "models"])
    except subprocess.TimeoutExpired:
        return unavailable_catalog(
            "codex model discovery timed out",
            executable=executable,
            version=version,
        )
    except OSError as error:
        return unavailable_catalog(
            f"codex model discovery could not run: {error.strerror or error}",
            executable=executable,
            version=version,
        )

    if result.returncode != 0:
        return unavailable_catalog(
            f"codex debug models exited with status {result.returncode}",
            executable=executable,
            version=version,
        )
    try:
        document = json.loads(result.stdout)
    except json.JSONDecodeError:
        return unavailable_catalog(
            "codex debug models did not return valid JSON",
            executable=executable,
            version=version,
        )
    if not isinstance(document, dict) or not isinstance(document.get("models"), list):
        return unavailable_catalog(
            "codex debug models returned an unsupported JSON shape",
            executable=executable,
            version=version,
        )

    candidates: list[dict[str, Any]] = []
    try:
        for raw_model in document["models"]:
            if not isinstance(raw_model, dict):
                raise ValueError("model entry is not an object")
            if raw_model.get("visibility") != "list":
                continue
            model_id = raw_model["slug"]
            if not isinstance(model_id, str) or not model_id:
                raise ValueError("model slug is missing")
            model_backend = raw_model.get("multi_agent_version")
            if multi_agent_version == "v2" and model_backend == "disabled":
                continue
            raw_efforts = raw_model["supported_reasoning_levels"]
            if not isinstance(raw_efforts, list):
                raise ValueError("supported reasoning levels are missing")
            efforts: list[str] = []
            for raw_effort in raw_efforts:
                if not isinstance(raw_effort, dict):
                    raise ValueError("reasoning level is not an object")
                effort = raw_effort.get("effort")
                if not isinstance(effort, str) or not effort:
                    raise ValueError("reasoning effort is missing")
                efforts.append(effort)
            candidates.append(
                {
                    "model": model_id,
                    "display_name": raw_model.get("display_name"),
                    "default_reasoning_effort": raw_model.get(
                        "default_reasoning_level"
                    ),
                    "supported_reasoning_efforts": efforts,
                    "multi_agent_version": model_backend,
                }
            )
    except (KeyError, ValueError) as error:
        return unavailable_catalog(
            f"codex debug models returned an unsupported model entry: {error}",
            executable=executable,
            version=version,
        )

    candidates.sort(key=lambda candidate: candidate["model"])
    return {
        "status": "available",
        "scope": "local-client-candidates",
        "authority": "active-spawn-host",
        "source": {
            "kind": "codex-debug-models",
            "executable": executable,
            "version": version,
        },
        "surface_match": "unverified",
        "models": candidates,
    }


def public_overrides(
    overrides: policy.EffortOverrides | policy.ModelOverrides,
) -> dict[str, str]:
    values = asdict(overrides)
    return {
        public_role: values[field]
        for public_role, field in policy.EFFORT_KEYS.items()
        if values[field] is not None
    }


def model_validation(
    model: str | None,
    reasoning_effort: str,
    candidates: dict[str, Any],
) -> str:
    if model is None:
        return "inherited"
    if candidates["status"] != "available":
        return "host-validation-required"
    candidate = next(
        (item for item in candidates["models"] if item["model"] == model),
        None,
    )
    if candidate is None:
        return "host-validation-required"
    supported_efforts = candidate["supported_reasoning_efforts"]
    if supported_efforts and reasoning_effort not in supported_efforts:
        return "catalog-effort-not-listed"
    return "catalog-candidate"


def resolved_plan(
    mode: policy.Mode,
    effort_overrides: policy.EffortOverrides,
    model_overrides: policy.ModelOverrides,
    candidates: dict[str, Any],
) -> dict[str, Any]:
    routes: dict[str, Any] = {}
    for public_role, role, risk in PUBLIC_ROUTES:
        route = policy.route(
            mode,
            role,
            risk,
            effort_overrides=effort_overrides,
            model_overrides=model_overrides,
        )
        routes[public_role] = {
            "fork_turns": route.fork_turns,
            "model": route.model,
            "model_validation": model_validation(
                route.model, route.reasoning_effort, candidates
            ),
            "reasoning_effort": route.reasoning_effort,
        }
    profile = policy.resolve_profile(
        mode,
        effort_overrides=effort_overrides,
        model_overrides=model_overrides,
    )
    return {
        "mode": mode,
        "routes": routes,
        "overrides": {
            "effort": public_overrides(effort_overrides),
            "model": public_overrides(model_overrides),
        },
        "recovery_explicitly_requested": profile.recovery_explicitly_requested,
        "model_candidates": candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode", choices=["fast", "balanced", "deep"], default="balanced"
    )
    parser.add_argument(
        "--effort", action="append", default=[], metavar="ROLE=EFFORT"
    )
    parser.add_argument(
        "--model", action="append", default=[], metavar="ROLE=MODEL_ID"
    )
    parser.add_argument(
        "--multi-agent-version",
        choices=["v1", "v2", "unknown"],
        default="unknown",
    )
    args = parser.parse_args()
    try:
        effort_overrides = policy.parse_effort_assignments(args.effort)
    except ValueError as error:
        parser.error(f"--effort {error}")
    try:
        model_overrides = policy.parse_model_assignments(args.model)
    except ValueError as error:
        parser.error(f"--model {error}")
    candidates = discover_model_candidates(args.multi_agent_version)
    print(
        json.dumps(
            resolved_plan(args.mode, effort_overrides, model_overrides, candidates),
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
