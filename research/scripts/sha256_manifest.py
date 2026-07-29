#!/usr/bin/env python3
"""Generate or verify the repository-root SHA-256 manifest."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "SHA256SUMS"


def tracked_files() -> list[str]:
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


def read_manifest() -> dict[str, str]:
    entries: dict[str, str] = {}
    for line_number, raw in enumerate(
        MANIFEST.read_text(encoding="utf-8").splitlines(), 1
    ):
        try:
            digest, relative = raw.split("  ", 1)
        except ValueError as error:
            raise RuntimeError(f"invalid manifest line {line_number}: {raw}") from error
        if len(digest) != 64 or any(
            character not in "0123456789abcdef" for character in digest
        ):
            raise RuntimeError(f"invalid SHA-256 on manifest line {line_number}")
        if relative in entries:
            raise RuntimeError(f"duplicate manifest entry: {relative}")
        entries[relative] = digest
    return entries


def check() -> None:
    entries = read_manifest()
    tracked = set(tracked_files())
    listed = set(entries)
    if tracked != listed:
        missing = sorted(tracked - listed)
        extra = sorted(listed - tracked)
        raise RuntimeError(
            f"manifest file-set mismatch; missing={missing}, extra={extra}"
        )
    for relative in sorted(entries):
        actual = sha256(ROOT / relative)
        if actual != entries[relative]:
            raise RuntimeError(f"checksum mismatch: {relative}")
        print(f"{relative}: OK")


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
