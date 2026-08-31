#!/usr/bin/env python3
"""Emit a deterministic classified failure for public routing review cases."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FIELDS = ("fingerprint", "classification", "boundary", "invariant", "expected", "actual")


def load_fixture(path: Path) -> dict[str, str]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load review fixture: {exc}") from exc
    if not isinstance(value, dict) or set(value) != set(FIELDS):
        raise ValueError(f"review fixture fields must be exactly: {', '.join(FIELDS)}")
    if not all(isinstance(value[field], str) and value[field] for field in FIELDS):
        raise ValueError("review fixture values must be non-empty strings")
    return {field: value[field] for field in FIELDS}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args()
    try:
        fixture = load_fixture(args.fixture)
    except ValueError as exc:
        print(f"REVIEW FIXTURE ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(fixture, sort_keys=True, separators=(",", ":")))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
