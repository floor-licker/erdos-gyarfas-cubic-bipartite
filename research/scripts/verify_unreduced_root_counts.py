#!/usr/bin/env python3
"""Reproduce the historical unreduced-root counters with two programs."""

from __future__ import annotations

import csv
import os
from pathlib import Path
import re
import subprocess
import tempfile

RESEARCH = Path(__file__).resolve().parents[1]
SOURCE = RESEARCH / "src"
EXPECTED = RESEARCH / "results" / "unreduced_root_counts.tsv"
FIELDS = ("v", "states", "attempted", "pair", "c8", "c16", "completions")
TOTAL = re.compile(
    r"^TOTAL V=(\d+) states=(\d+) attempted=(\d+) pair=(\d+) "
    r"c8=(\d+) c16=(\d+) completions=(\d+)",
    re.MULTILINE,
)


def compile_program(compiler: str, source: Path, output: Path, side: int) -> None:
    subprocess.run(
        [
            compiler,
            "-O3",
            "-std=c++17",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            "-Werror",
            f"-DSIDE={side}",
            str(source),
            "-o",
            str(output),
        ],
        check=True,
    )


def run_total(executable: Path) -> tuple[int, ...]:
    completed = subprocess.run(
        [str(executable), "--unreduced-root"],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    match = TOTAL.search(completed.stdout)
    if match is None:
        raise RuntimeError(f"missing TOTAL line in output from {executable}")
    return tuple(map(int, match.groups()))


def expected_rows() -> list[tuple[int, ...]]:
    with EXPECTED.open(encoding="utf-8", newline="") as handle:
        return [
            tuple(int(row[field]) for field in FIELDS)
            for row in csv.DictReader(handle, delimiter="\t")
        ]


def main() -> None:
    compiler = os.environ.get("CXX", "c++")
    discovery_rows: list[tuple[int, ...]] = []
    independent_rows: list[tuple[int, ...]] = []

    with tempfile.TemporaryDirectory(prefix="eg-unreduced-") as temporary:
        build = Path(temporary)
        for side in range(7, 29):
            discovery = build / f"discovery_{side}"
            independent = build / f"independent_{side}"
            compile_program(
                compiler,
                SOURCE / "canonical_root_orbit_search.cpp",
                discovery,
                side,
            )
            compile_program(
                compiler,
                SOURCE / "independent_mitm_root_orbit_search.cpp",
                independent,
                side,
            )
            discovery_rows.append(run_total(discovery))
            independent_rows.append(run_total(independent))

    expected = expected_rows()
    if discovery_rows != expected:
        raise RuntimeError("discovery program differs from unreduced_root_counts.tsv")
    if independent_rows != expected:
        raise RuntimeError("independent program differs from unreduced_root_counts.tsv")
    print("VERIFIED: --unreduced-root reproduces every v=7,...,28 historical counter.")


if __name__ == "__main__":
    main()
