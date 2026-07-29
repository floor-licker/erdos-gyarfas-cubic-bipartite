#!/usr/bin/env python3
"""Require genuine certificate members to pass and altered members to fail."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import tempfile
from zipfile import ZipFile

HEADER_BYTES = 60


def run_checker(checker: Path, certificate: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(checker), str(certificate)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def require_success(checker: Path, path: Path, label: str) -> None:
    result = run_checker(checker, path)
    if result.returncode != 0:
        raise RuntimeError(
            f"checker rejected genuine {label}: {result.stderr.strip()}"
        )


def require_failure(
    checker: Path,
    path: Path,
    payload: bytes,
    label: str,
    expected_error: str,
) -> None:
    path.write_bytes(payload)
    result = run_checker(checker, path)
    if result.returncode == 0:
        raise RuntimeError(f"checker accepted {label} certificate data")
    if expected_error not in result.stderr:
        raise RuntimeError(
            f"{label} failed for the wrong reason: {result.stderr.strip()}"
        )


def find_c16_endpoint_mutation(
    checker: Path,
    path: Path,
    payload: bytes,
) -> bytes:
    expected = "C16 witness has an invalid endpoint code"
    for offset in range(HEADER_BYTES, len(payload) - 1):
        if payload[offset] != 0x10:
            continue
        altered = bytearray(payload)
        altered[offset + 1] = 0xFF
        path.write_bytes(altered)
        result = run_checker(checker, path)
        if result.returncode != 0 and expected in result.stderr:
            return bytes(altered)
    raise RuntimeError("could not locate a reachable C16 record for tampering")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("checker", type=Path)
    parser.add_argument("bundle", type=Path)
    arguments = parser.parse_args()

    checker = arguments.checker.resolve()
    bundle = arguments.bundle.resolve()
    if not checker.is_file():
        raise FileNotFoundError(checker)
    if not bundle.is_file():
        raise FileNotFoundError(bundle)

    with ZipFile(bundle, "r") as archive:
        v7 = archive.read("proof/v07/orbit1.cert")
        v19 = archive.read("proof/v19/orbit1.cert")
        compatibility = archive.read(
            "compatibility/v16-unreduced-c4-c8.cert"
        )

    with tempfile.TemporaryDirectory(prefix="eg58-tampering-") as temporary:
        current = Path(temporary) / "current.cert"
        for label, payload in (
            ("v=7 orbit 1", v7),
            ("v=19 orbit 1", v19),
            ("v=16 compatibility", compatibility),
        ):
            current.write_bytes(payload)
            require_success(checker, current, label)

        require_failure(
            checker,
            current,
            v7[:HEADER_BYTES] + b"\xff",
            "malformed",
            "unknown certificate record",
        )
        require_failure(
            checker,
            current,
            compatibility[:-1],
            "truncated",
            "unexpected end of certificate",
        )
        require_failure(
            checker,
            current,
            compatibility + b"\x00",
            "trailing",
            "trailing bytes after proof stream",
        )

        counter_tampered = bytearray(compatibility)
        counter_tampered[12] ^= 1
        require_failure(
            checker,
            current,
            bytes(counter_tampered),
            "counter-tampered",
            "header counts do not match",
        )

        c8_tampered = bytearray(v7)
        if c8_tampered[HEADER_BYTES] != 0x08:
            raise RuntimeError("v=7 regression stream no longer begins with C8")
        c8_tampered[HEADER_BYTES + 1] = 0xFF
        require_failure(
            checker,
            current,
            bytes(c8_tampered),
            "C8-witness-tampered",
            "C8 witness has an invalid block index",
        )

        c16_tampered = find_c16_endpoint_mutation(
            checker, current, v19
        )
        require_failure(
            checker,
            current,
            c16_tampered,
            "C16-witness-tampered",
            "C16 witness has an invalid endpoint code",
        )

        require_failure(
            checker,
            current,
            v7[:HEADER_BYTES] + bytes((0x20,)) * 100,
            "unexpected-completion",
            "certificate expands to a complete configuration",
        )

    print(
        "VERIFIED: malformed, truncated, trailing, counter-tampered, "
        "C8-witness-tampered, C16-witness-tampered, and "
        "unexpected-completion streams are rejected."
    )


if __name__ == "__main__":
    main()
