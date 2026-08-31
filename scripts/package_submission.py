#!/usr/bin/env python3
"""Build the deterministic Universal Plugins Directory submission archive."""
from __future__ import annotations
import argparse
import hashlib
import stat
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath
ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "adaptive-effort"
FORBIDDEN_PARTS = {"__pycache__", ".pytest_cache", ".git", "app", "apps", "mcp", "mcps", "screenshot", "screenshots", "hook", "hooks"}
FORBIDDEN_SUFFIXES = {".pyc", ".zip", ".sha256", ".toml"}
FIXED_TIMESTAMP = (2026, 8, 30, 0, 0, 0)
SUBMISSION_MANIFEST = (
    (".codex-plugin/plugin.json", 0o644),
    ("README.md", 0o644),
    ("assets/adaptive-effort-small.svg", 0o644),
    ("assets/adaptive-effort.svg", 0o644),
    ("skills/adaptive-effort/SKILL.md", 0o644),
    ("skills/adaptive-effort/agents/openai.yaml", 0o644),
    ("skills/adaptive-effort/references/compatibility.md", 0o644),
    ("skills/adaptive-effort/references/escalation-policy.md", 0o644),
    ("skills/adaptive-effort/references/handoff-templates.md", 0o644),
    ("skills/adaptive-effort/references/routing-policy.md", 0o644),
    ("skills/adaptive-effort/references/superpowers-integration.md", 0o644),
    ("skills/adaptive-effort/scripts/doctor.py", 0o644),
    ("skills/adaptive-effort/scripts/policy.py", 0o644),
)
SUBMISSION_MODES = dict(SUBMISSION_MANIFEST)
SUBMISSION_FILES = frozenset(SUBMISSION_MODES)
SUBMISSION_DIRECTORIES = frozenset(
    parent.as_posix()
    for relative in SUBMISSION_FILES
    for parent in PurePosixPath(relative).parents
    if parent.as_posix() != "."
)
WINDOWS_RESERVED_NAMES = {
    "con", "prn", "aux", "nul",
    *(f"com{number}" for number in range(1, 10)),
    *(f"lpt{number}" for number in range(1, 10)),
}


def validate_relative_path(relative: PurePosixPath, *, raw: str | None = None) -> None:
    value = relative.as_posix() if raw is None else raw
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise ValueError(f"unsafe or ambiguous path: {value!r}")
    if raw is not None and relative.as_posix() != raw:
        raise ValueError(f"unsafe or ambiguous path: {value!r}")
    for part in relative.parts:
        folded_stem = part.split(".", 1)[0].casefold()
        if (
            part in {"", ".", ".."}
            or "\\" in part
            or ":" in part
            or any(ord(character) < 32 or ord(character) == 127 for character in part)
            or part != part.strip()
            or part.endswith(".")
            or unicodedata.normalize("NFC", part) != part
            or folded_stem in WINDOWS_RESERVED_NAMES
        ):
            raise ValueError(f"unsafe or ambiguous path: {value!r}")

def forbidden_reason(rel: Path) -> str | None:
    lowered_parts = {part.lower() for part in rel.parts}
    name = rel.name.lower()
    if lowered_parts & FORBIDDEN_PARTS:
        return "forbidden app, MCP, screenshot, hook, VCS, or cache path"
    if rel.suffix.lower() in FORBIDDEN_SUFFIXES:
        return "forbidden cache, archive, checksum, or custom-agent file"
    if name.endswith(":zone.identifier"):
        return "forbidden zone identifier"
    if name in {"app.json", "mcp.json"} or ".app." in name or ".mcp." in name:
        return "forbidden app or MCP file"
    return None


def _validate_plugin_root(plugin: Path) -> None:
    if plugin.is_symlink():
        raise ValueError(f"symlink is not allowed: {plugin}")
    try:
        mode = plugin.lstat().st_mode
    except OSError as exc:
        raise ValueError(f"cannot inspect plugin root: {plugin}: {exc}") from exc
    if not stat.S_ISDIR(mode):
        raise ValueError(f"plugin root is not a directory: {plugin}")


def reviewed_files(plugin: Path = PLUGIN) -> list[Path]:
    """Return only the checked-in submission manifest, independent of tree additions."""
    _validate_plugin_root(plugin)
    files: list[Path] = []
    checked_directories: set[Path] = set()
    for relative, _mode in SUBMISSION_MANIFEST:
        rel = PurePosixPath(relative)
        validate_relative_path(rel, raw=relative)
        for parent in reversed(rel.parents):
            if parent.as_posix() == ".":
                continue
            directory = plugin.joinpath(*parent.parts)
            if directory in checked_directories:
                continue
            checked_directories.add(directory)
            try:
                directory_mode = directory.lstat().st_mode
            except OSError as exc:
                raise ValueError(f"missing reviewed submission directory: {parent}") from exc
            if stat.S_ISLNK(directory_mode):
                raise ValueError(f"symlink is not allowed: {parent}")
            if not stat.S_ISDIR(directory_mode):
                raise ValueError(f"reviewed submission directory has unsupported type: {parent}")
        path = plugin.joinpath(*rel.parts)
        try:
            file_mode = path.lstat().st_mode
        except OSError as exc:
            raise ValueError(f"missing reviewed submission file: {relative}") from exc
        if stat.S_ISLNK(file_mode):
            raise ValueError(f"symlink is not allowed: {relative}")
        if not stat.S_ISREG(file_mode):
            raise ValueError(f"reviewed submission file has unsupported type: {relative}")
        files.append(path)
    return files


def collect_files(plugin: Path = PLUGIN) -> list[Path]:
    _validate_plugin_root(plugin)
    files: dict[str, Path] = {}
    for path in sorted(plugin.rglob("*"), key=lambda item: item.relative_to(plugin).as_posix()):
        rel = path.relative_to(plugin)
        posix = PurePosixPath(rel.as_posix())
        validate_relative_path(posix, raw=rel.as_posix())
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise ValueError(f"symlink is not allowed: {rel}")
        reason = forbidden_reason(rel)
        if reason:
            raise ValueError(f"forbidden submission content ({reason}): {rel}")
        relative = posix.as_posix()
        if stat.S_ISDIR(mode):
            if relative not in SUBMISSION_DIRECTORIES:
                raise ValueError(f"unreviewed submission path: {rel}")
            continue
        if not stat.S_ISREG(mode):
            raise ValueError(f"special file is not allowed: {rel}")
        if relative not in SUBMISSION_FILES:
            raise ValueError(f"unreviewed submission path: {rel}")
        files[relative] = path
    missing = SUBMISSION_FILES - files.keys()
    if missing:
        raise ValueError(f"missing reviewed submission paths: {sorted(missing)}")
    return [files[relative] for relative, _mode in SUBMISSION_MANIFEST]

def build(output: Path, plugin: Path = PLUGIN) -> tuple[Path, Path, str]:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in collect_files(plugin):
            relative = path.relative_to(plugin).as_posix()
            rel = PurePosixPath("adaptive-effort") / relative
            info = zipfile.ZipInfo(rel.as_posix(), date_time=FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            mode = SUBMISSION_MODES[relative]
            info.external_attr = (stat.S_IFREG | mode) << 16
            archive.writestr(info, path.read_bytes())
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    checksum = output.with_suffix(output.suffix + ".sha256")
    checksum.write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    return output, checksum, digest

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for value in build(args.output):
        print(value)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
