#!/usr/bin/env python3
"""Generate or verify the repository-root SHA-256 manifest."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "SHA256SUMS"


def inside_git_checkout() -> bool:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=ROOT,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except OSError:
        return False
    if result.returncode != 0:
        return False
    return Path(result.stdout.strip()).resolve() == ROOT.resolve()


def tracked_files() -> list[str]:
    if not inside_git_checkout():
        raise RuntimeError("tracked-file enumeration requires a Git checkout")
    payload = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    return sorted(
        os.fsdecode(raw)
        for raw in payload.split(b"\0")
        if raw and os.fsdecode(raw) != "SHA256SUMS"
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def generate() -> None:
    if not inside_git_checkout():
        raise RuntimeError("manifest generation requires a Git checkout")
    lines = [f"{sha256(ROOT / relative)}  {relative}\n" for relative in tracked_files()]
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=ROOT,
        prefix=".SHA256SUMS.",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        handle.writelines(lines)
    os.replace(temporary, MANIFEST)
    print(f"WROTE: {MANIFEST}")


def validate_manifest_path(relative: str, line_number: int) -> str:
    if not relative or relative == ".":
        raise RuntimeError(f"empty manifest path on line {line_number}")
    if "\0" in relative or "\\" in relative:
        raise RuntimeError(f"invalid manifest path on line {line_number}: {relative}")

    posix = PurePosixPath(relative)
    windows = PureWindowsPath(relative)
    if posix.is_absolute() or windows.is_absolute() or windows.drive:
        raise RuntimeError(f"absolute manifest path on line {line_number}: {relative}")
    if ".." in posix.parts:
        raise RuntimeError(
            f"parent traversal in manifest path on line {line_number}: {relative}"
        )
    if posix.as_posix() != relative:
        raise RuntimeError(
            f"noncanonical manifest path on line {line_number}: {relative}"
        )
    if relative == MANIFEST.name:
        raise RuntimeError(f"manifest must not list itself on line {line_number}")
    return relative


def parse_manifest(text: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line_number, raw in enumerate(text.splitlines(), 1):
        if len(raw) < 67 or raw[64:66] != "  ":
            raise RuntimeError(f"invalid manifest line {line_number}: {raw}")
        digest = raw[:64]
        relative = validate_manifest_path(raw[66:], line_number)
        if len(digest) != 64 or any(
            character not in "0123456789abcdef" for character in digest
        ):
            raise RuntimeError(f"invalid SHA-256 on manifest line {line_number}")
        if relative in entries:
            raise RuntimeError(f"duplicate manifest entry: {relative}")
        entries[relative] = digest
    if not entries:
        raise RuntimeError("manifest is empty")
    return entries


def read_manifest() -> dict[str, str]:
    return parse_manifest(MANIFEST.read_text(encoding="utf-8"))


def check() -> None:
    entries = read_manifest()
    git_mode = inside_git_checkout()
    if git_mode:
        tracked = set(tracked_files())
        listed = set(entries)
        if tracked != listed:
            missing = sorted(tracked - listed)
            extra = sorted(listed - tracked)
            raise RuntimeError(
                f"manifest file-set mismatch; missing={missing}, extra={extra}"
            )

    for relative in sorted(entries):
        target = ROOT.joinpath(*PurePosixPath(relative).parts)
        if target.is_symlink():
            raise RuntimeError(f"manifest entry is a symbolic link: {relative}")
        if not target.is_file():
            raise RuntimeError(f"manifest file is missing: {relative}")
        actual = sha256(target)
        if actual != entries[relative]:
            raise RuntimeError(f"checksum mismatch: {relative}")
        print(f"{relative}: OK")
    mode = "Git checkout" if git_mode else "source archive"
    print(f"VERIFIED: {len(entries)} files from SHA256SUMS ({mode}).")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("generate", "check"))
    arguments = parser.parse_args()
    if arguments.action == "generate":
        generate()
    else:
        check()


if __name__ == "__main__":
    main()
