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
Role = Literal["implementer", "debugger", "recovery", "reviewer"]
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
Effort = Literal["low", "medium", "high", "xhigh", "max", "ultra"]

EFFORTS = {"low", "medium", "high", "xhigh", "max", "ultra"}
EFFORT_RANK = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "xhigh": 3,
    "max": 4,
    "ultra": 5,
}
EFFORT_KEYS = {
    "implementer": "implementer",
    "routine-review": "routine_review",
    "high-risk-review": "high_risk_review",
    "debugger": "debugger",
    "recovery": "recovery",
}
PUBLIC_EFFORT_KEYS = {field: public for public, field in EFFORT_KEYS.items()}


@dataclass(frozen=True)
class EffortOverrides:
    implementer: Effort | None = None
    routine_review: Effort | None = None
    high_risk_review: Effort | None = None
    debugger: Effort | None = None
    recovery: Effort | None = None

    def __post_init__(self) -> None:
        for effort in asdict(self).values():
            if effort is not None and effort not in EFFORTS:
                raise ValueError(f"unsupported effort: {effort}")


@dataclass(frozen=True)
class ModelOverrides:
    implementer: str | None = None
    routine_review: str | None = None
    high_risk_review: str | None = None
    debugger: str | None = None
    recovery: str | None = None

    def __post_init__(self) -> None:
        for model in asdict(self).values():
            if model is not None and (
                not isinstance(model, str) or not model or model != model.strip()
            ):
                raise ValueError(f"invalid model override: {model!r}")


@dataclass(frozen=True)
class RoutingProfile:
    implementer: Effort
    routine_review: Effort
    high_risk_review: Effort
    debugger: Effort
    recovery: Effort
    recovery_explicitly_requested: bool = False


def validate_effort_caps(
    effort_overrides: EffortOverrides, effort_caps: EffortOverrides
) -> None:
    """Reject explicit role efforts that exceed explicit task-local caps."""
    overrides = asdict(effort_overrides)
    for role, cap in asdict(effort_caps).items():
        effort = overrides[role]
        if (
            cap is not None
            and effort is not None
            and EFFORT_RANK[effort] > EFFORT_RANK[cap]
        ):
            public_role = PUBLIC_EFFORT_KEYS[role]
            raise ValueError(
                f"effort override conflicts with cap: {public_role}={effort} exceeds {cap}"
            )


@dataclass(frozen=True)
class Route:
    mode: str
    role: str
    reasoning_effort: str
    fork_turns: str = "none"
    model: str | None = None


def parse_effort_assignments(assignments: list[str]) -> EffortOverrides:
    values: dict[str, str] = {}
    for assignment in assignments:
        key, separator, effort = assignment.partition("=")
        if not separator or key not in EFFORT_KEYS or effort not in EFFORTS:
            raise ValueError(
                "must be ROLE=EFFORT using a canonical role and one of "
                "low, medium, high, xhigh, max, ultra"
            )
        field = EFFORT_KEYS[key]
        if field in values:
            raise ValueError(f"duplicate assignment for {key}")
        values[field] = effort
    return EffortOverrides(**values)


def parse_model_assignments(assignments: list[str]) -> ModelOverrides:
    values: dict[str, str] = {}
    for assignment in assignments:
        key, separator, model = assignment.partition("=")
        if (
            not separator
            or key not in EFFORT_KEYS
            or not model
            or model != model.strip()
        ):
            raise ValueError(
                "must be ROLE=MODEL_ID using a canonical role and an exact, "
                "non-empty model ID"
            )
        field = EFFORT_KEYS[key]
        if field in values:
            raise ValueError(f"duplicate assignment for {key}")
        values[field] = model
    return ModelOverrides(**values)


def repair_effort(current_writer_route: Route) -> str:
    """Retain the actual effort of the writer receiving a same-thread repair."""
    if current_writer_route.role not in {"implementer", "debugger", "recovery"}:
        raise ValueError(f"{current_writer_route.role} is not a repair writer")
    return current_writer_route.reasoning_effort


def resolve_profile(
    mode: Mode = "balanced",
    *,
    effort_overrides: EffortOverrides | None = None,
    model_overrides: ModelOverrides | None = None,
) -> RoutingProfile:
    if mode not in {"fast", "balanced", "deep"}:
        raise ValueError(f"unsupported mode: {mode}")
    defaults = {
        "fast": RoutingProfile("low", "low", "high", "medium", "high"),
        "balanced": RoutingProfile("low", "medium", "high", "medium", "high"),
        "deep": RoutingProfile("medium", "high", "high", "high", "high"),
    }[mode]
    if effort_overrides is None and model_overrides is None:
        return defaults
    values = asdict(defaults)
    if effort_overrides is not None:
        values.update(
            {
                role: effort
                for role, effort in asdict(effort_overrides).items()
                if effort is not None
            }
        )
    values["recovery_explicitly_requested"] = bool(
        (effort_overrides is not None and effort_overrides.recovery is not None)
        or (model_overrides is not None and model_overrides.recovery is not None)
    )
    return RoutingProfile(**values)


def route(
    mode: Mode,
    role: Role,
    risk: Risk = "routine",
    *,
    effort_overrides: EffortOverrides | None = None,
    model_overrides: ModelOverrides | None = None,
) -> Route:
    profile = resolve_profile(
        mode,
        effort_overrides=effort_overrides,
        model_overrides=model_overrides,
    )
    if role not in {
        "implementer",
        "debugger",
        "recovery",
        "reviewer",
    }:
        raise ValueError(f"unsupported role: {role}")
    if risk not in {"routine", "high"}:
        raise ValueError(f"unsupported risk: {risk}")

    if role == "reviewer":
        profile_field = "high_risk_review" if risk == "high" else "routine_review"
    else:
        profile_field = role
    effort = getattr(profile, profile_field)
    model = (
        getattr(model_overrides, profile_field)
        if model_overrides is not None
        else None
    )

    return Route(
        mode=mode,
        role=role,
        reasoning_effort=effort,
        model=model,
    )


def failure_route(
    classification: FailureClass,
    *,
    mode: Mode = "balanced",
    independent_contract_design_evidence: bool = False,
    effort_overrides: EffortOverrides | None = None,
    model_overrides: ModelOverrides | None = None,
) -> CorrectiveRoute:
    """Map a classified failure to the next policy route."""
    if mode not in {"fast", "balanced", "deep"}:
        raise ValueError(f"unsupported mode: {mode}")
    if classification == "environment failure":
        return "report"
    if classification == "missing-context failure":
        return "context_continuation"
    if classification == "local deterministic implementation defect":
        return "semantic_correction"
    if classification == "implementation-reasoning defect":
        return "debugger"
    if classification == "contract/design defect":
        profile = resolve_profile(
            mode,
            effort_overrides=effort_overrides,
            model_overrides=model_overrides,
        )
        if mode == "fast" and not profile.recovery_explicitly_requested:
            return "stop"
        return "recovery" if independent_contract_design_evidence else "stop"
    raise ValueError(f"unsupported failure classification: {classification}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["fast", "balanced", "deep"], default="balanced")
    parser.add_argument(
        "--role",
        choices=[
            "implementer",
            "debugger",
            "recovery",
            "reviewer",
        ],
        required=True,
    )
    parser.add_argument("--risk", choices=["routine", "high"], default="routine")
    parser.add_argument(
        "--effort",
        action="append",
        default=[],
        metavar="ROLE=EFFORT",
        help="override implementer, routine-review, high-risk-review, debugger, or recovery",
    )
    parser.add_argument(
        "--model",
        action="append",
        default=[],
        metavar="ROLE=MODEL_ID",
        help="override implementer, routine-review, high-risk-review, debugger, or recovery",
    )
    args = parser.parse_args()
    try:
        overrides = parse_effort_assignments(args.effort)
    except ValueError as error:
        parser.error(f"--effort {error}")
    try:
        model_overrides = parse_model_assignments(args.model)
    except ValueError as error:
        parser.error(f"--model {error}")
    print(
        json.dumps(
            asdict(
                route(
                    args.mode,
                    args.role,
                    args.risk,
                    effort_overrides=overrides,
                    model_overrides=model_overrides,
                )
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
