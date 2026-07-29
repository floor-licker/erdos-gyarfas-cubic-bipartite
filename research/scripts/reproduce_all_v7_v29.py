#!/usr/bin/env python3
"""Reproduce the two-implementation counter table for v=7,...,29."""

from __future__ import annotations

import csv
import os
from pathlib import Path
import re
import subprocess
import tempfile

RESEARCH = Path(__file__).resolve().parents[1]
SOURCE = RESEARCH / "src"
RESULTS = RESEARCH / "results"
LOGS = RESEARCH / "logs" / "full_range"
FIELDS = ("states", "attempted", "pair", "c8", "c16", "completions")
HEADER = ("v", *FIELDS)
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
        [str(executable)],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    match = TOTAL.search(completed.stdout)
    if match is None:
        raise RuntimeError(f"missing TOTAL line in output from {executable}")
    return tuple(map(int, match.groups()))


def read_expected() -> list[tuple[int, ...]]:
    with (RESULTS / "frontier_counts.tsv").open(encoding="utf-8", newline="") as handle:
        return [
            tuple(int(row[field]) for field in HEADER)
            for row in csv.DictReader(handle, delimiter="\t")
        ]


def write_table(path: Path, rows: list[tuple[int, ...]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(HEADER)
        writer.writerows(rows)
    os.replace(temporary, path)


def main() -> None:
    compiler = os.environ.get("CXX", "g++")
    discovery_rows: list[tuple[int, ...]] = []
    independent_rows: list[tuple[int, ...]] = []

    with tempfile.TemporaryDirectory(prefix="eg-full-range-") as temporary:
        build = Path(temporary)
        for side in range(7, 30):
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

    expected = read_expected()
    if discovery_rows != independent_rows:
        raise RuntimeError("the two full-range counter tables differ")
    if discovery_rows != expected:
        raise RuntimeError("fresh counters differ from results/frontier_counts.tsv")

    write_table(LOGS / "discovery.tsv", discovery_rows)
    write_table(LOGS / "independent.tsv", independent_rows)
    print("VERIFIED: full-range integer counters agree.")


if __name__ == "__main__":
    main()
