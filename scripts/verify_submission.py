#!/usr/bin/env python3
"""Verify a directory-submission ZIP against the reviewed plugin snapshot."""

from __future__ import annotations

import argparse
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
import package_submission


def verify(archive_path: Path, plugin: Path = package_submission.PLUGIN) -> list[str]:
    expected_files = package_submission.reviewed_files(plugin)
    expected = {
        f"adaptive-effort/{path.relative_to(plugin).as_posix()}": path
        for path in expected_files
    }
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise ValueError("duplicate archive entry")
        if names != sorted(names):
            raise ValueError("archive entries are not sorted")
        if set(names) != set(expected):
            raise ValueError("archive membership does not match the reviewed plugin snapshot")
        for info in infos:
            if "\\" in info.filename:
                raise ValueError(f"unsafe archive path: {info.filename!r}")
            posix = PurePosixPath(info.filename)
            if (
                posix.is_absolute()
                or ".." in posix.parts
                or len(posix.parts) < 2
                or posix.parts[0] != "adaptive-effort"
                or posix.as_posix() != info.filename
            ):
                raise ValueError(f"unsafe archive path: {info.filename}")
            rel_posix = PurePosixPath(*posix.parts[1:])
            package_submission.validate_relative_path(rel_posix, raw="/".join(posix.parts[1:]))
            if info.is_dir() or not stat.S_ISREG(info.external_attr >> 16):
                raise ValueError(f"unsupported archive entry type: {info.filename}")
            if info.date_time != package_submission.FIXED_TIMESTAMP:
                raise ValueError(f"unexpected archive timestamp: {info.filename}")
            if info.compress_type != zipfile.ZIP_DEFLATED or info.create_system != 3:
                raise ValueError(f"unexpected archive encoding metadata: {info.filename}")
            expected_mode = package_submission.SUBMISSION_MODES[rel_posix.as_posix()]
            actual_mode = (info.external_attr >> 16) & 0o777
            if actual_mode != expected_mode:
                raise ValueError(f"unexpected archive mode: {info.filename}")
            rel = Path(*rel_posix.parts)
            reason = package_submission.forbidden_reason(rel)
            if reason:
                raise ValueError(f"forbidden archive content ({reason}): {info.filename}")
            if archive.read(info) != expected[info.filename].read_bytes():
                raise ValueError(f"archive content differs from reviewed snapshot: {info.filename}")
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    names = verify(args.archive)
    print(f"PASS: verified {len(names)} submission entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
