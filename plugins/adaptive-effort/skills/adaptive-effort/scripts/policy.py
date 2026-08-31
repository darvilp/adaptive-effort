#!/usr/bin/env python3
"""Canonical Adaptive Effort routing policy.

This script is primarily for validation and diagnostics. The skill can follow the
same small table directly during normal operation.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Literal

Mode = Literal["fast", "balanced", "deep"]
Role = Literal["implementer", "integration_implementer", "debugger", "recovery", "reviewer"]
Risk = Literal["routine", "high"]
FailureClass = Literal[
    "environment failure",
    "missing-context failure",
    "local deterministic implementation defect",
    "implementation-reasoning defect",
    "contract/design defect",
]
CorrectiveRoute = Literal[
    "report",
    "context_continuation",
    "semantic_correction",
    "debugger",
    "recovery",
    "stop",
]


@dataclass(frozen=True)
class Route:
    mode: str
    role: str
    reasoning_effort: str
    fork_turns: str = "none"
    model: None = None


def route(mode: Mode, role: Role, risk: Risk = "routine") -> Route:
    if mode not in {"fast", "balanced", "deep"}:
        raise ValueError(f"unsupported mode: {mode}")
    if role not in {
        "implementer",
        "integration_implementer",
        "debugger",
        "recovery",
        "reviewer",
    }:
        raise ValueError(f"unsupported role: {role}")
    if risk not in {"routine", "high"}:
        raise ValueError(f"unsupported risk: {risk}")

    if role == "implementer":
        effort = "low"
    elif role == "integration_implementer":
        effort = "medium" if mode == "deep" else "low"
    elif role == "debugger":
        effort = "high" if mode == "deep" else "medium"
    elif role == "recovery":
        effort = "high"
    else:  # reviewer
        effort = "high" if mode == "deep" or risk == "high" else "medium"

    return Route(
        mode=mode,
        role=role,
        reasoning_effort=effort,
    )


def failure_route(
    classification: FailureClass,
    *,
    independent_contract_design_evidence: bool = False,
) -> CorrectiveRoute:
    """Map a classified failure to the next policy route."""
    if classification == "environment failure":
        return "report"
    if classification == "missing-context failure":
        return "context_continuation"
    if classification == "local deterministic implementation defect":
        return "semantic_correction"
    if classification == "implementation-reasoning defect":
        return "debugger"
    if classification == "contract/design defect":
        return "recovery" if independent_contract_design_evidence else "stop"
    raise ValueError(f"unsupported failure classification: {classification}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["fast", "balanced", "deep"], default="balanced")
    parser.add_argument(
        "--role",
        choices=[
            "implementer",
            "integration_implementer",
            "debugger",
            "recovery",
            "reviewer",
        ],
        required=True,
    )
    parser.add_argument("--risk", choices=["routine", "high"], default="routine")
    args = parser.parse_args()
    print(json.dumps(asdict(route(args.mode, args.role, args.risk)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
