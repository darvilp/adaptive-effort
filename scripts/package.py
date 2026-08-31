#!/usr/bin/env python3
"""Create a deterministic ZIP, internal manifest, and adjacent SHA-256 file."""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIRECTORIES = (".agents", ".github", "docs", "plugins", "scripts", "submission", "tests")
PACKAGE_ROOT_FILES = {
    ".gitignore",
    "CHANGELOG.md",
    "DESIGN.md",
    "LICENSE",
    "Makefile",
    "MANIFEST.sha256",
    "PRIVACY.md",
    "README.md",
    "SECURITY.md",
    "SOURCES.md",
    "TEST_DRIVE.md",
    "TEST_RESULTS.md",
}
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".zip"}


def _is_package_file(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    return (
        path.is_file()
        and not any(part in EXCLUDED_PARTS for part in rel.parts)
        and path.suffix not in EXCLUDED_SUFFIXES
        and not path.name.endswith(":Zone.Identifier")
    )


def files_to_package() -> list[Path]:
    result = [ROOT / name for name in PACKAGE_ROOT_FILES if _is_package_file(ROOT / name)]
    for directory in PACKAGE_DIRECTORIES:
        root = ROOT / directory
        if root.exists():
            result.extend(path for path in root.rglob("*") if _is_package_file(path))
    return sorted(result, key=lambda item: item.relative_to(ROOT).as_posix())


def write_manifest() -> Path:
    manifest_path = ROOT / "MANIFEST.sha256"
    lines: list[str] = []
    for path in files_to_package():
        if path == manifest_path:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(ROOT).as_posix()}")
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest_path


def write_zip(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    root_name = ROOT.name
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files_to_package():
            rel = Path(root_name) / path.relative_to(ROOT)
            info = zipfile.ZipInfo(rel.as_posix(), date_time=(2026, 8, 22, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = 0o755 if os.access(path, os.X_OK) else 0o644
            info.external_attr = (mode & 0xFFFF) << 16
            archive.writestr(info, path.read_bytes())


def run_check_commands(commands: list[list[str]], cwd: Path = ROOT) -> int:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    for command in commands:
        result = subprocess.run(command, cwd=cwd, env=environment, check=False)
        if result.returncode:
            return result.returncode
    return 0


def run_checks() -> int:
    return run_check_commands([
        [sys.executable, str(ROOT / "scripts" / "validate.py")],
        [sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-v"],
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()

    write_manifest()
    if not args.skip_tests:
        result = run_checks()
        if result:
            return result

    write_zip(args.output)
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    checksum_path = args.output.with_suffix(args.output.suffix + ".sha256")
    checksum_path.write_text(f"{digest}  {args.output.name}\n", encoding="utf-8")
    print(args.output)
    print(checksum_path)
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
