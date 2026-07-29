#!/usr/bin/env python3
"""Reproduce all three implementations in every v=29 root orbit."""

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
LOGS = RESEARCH / "logs" / "v29"
FIELDS = ("states", "attempted", "pair", "c8", "c16", "completions")
COUNTER = re.compile(
    r"^ORBIT ([123]) states=(\d+) attempted=(\d+) pair=(\d+) "
    r"c8=(\d+) c16=(\d+) completions=(\d+)$",
    re.MULTILINE,
)
TRANSCRIPT = re.compile(
    r"^TRANSCRIPT orbit=([123]) states=(\d+) candidates=(\d+) "
    r"sha256=([0-9a-f]{64})$",
    re.MULTILINE,
)


def compile_search(compiler: str, source: Path, output: Path) -> None:
    subprocess.run(
        [
            compiler,
            "-O3",
            "-std=c++17",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            "-Werror",
            "-DSIDE=29",
            str(source),
            "-o",
            str(output),
        ],
        check=True,
    )


def run_output(command: list[str]) -> str:
    return subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout


def parse_search_output(
    text: str, expected_orbit: int
) -> tuple[tuple[int, ...], tuple[int, int, str]]:
    counter_match = COUNTER.search(text)
    transcript_match = TRANSCRIPT.search(text)
    if counter_match is None or transcript_match is None:
        raise RuntimeError("search output lacks a counter or transcript line")
    if int(counter_match.group(1)) != expected_orbit:
        raise RuntimeError("counter line has the wrong root orbit")
    if int(transcript_match.group(1)) != expected_orbit:
        raise RuntimeError("transcript line has the wrong root orbit")

    counters = tuple(map(int, counter_match.groups()[1:]))
    transcript = (
        int(transcript_match.group(2)),
        int(transcript_match.group(3)),
        transcript_match.group(4),
    )
    if transcript[:2] != counters[:2]:
        raise RuntimeError("transcript event counts differ from search counters")
    return counters, transcript


def deterministic_log(text: str) -> str:
    lines = [
        line
        for line in text.splitlines()
        if line.startswith("ORBIT ") or line.startswith("TRANSCRIPT ")
    ]
    if len(lines) != 2:
        raise RuntimeError("unexpected search-log structure")
    return "\n".join(lines) + "\n"


def expected_counters() -> dict[int, tuple[int, ...]]:
    with (RESULTS / "v29_orbits.tsv").open(encoding="utf-8", newline="") as handle:
        return {
            int(row["orbit"]): tuple(int(row[field]) for field in FIELDS)
            for row in csv.DictReader(handle, delimiter="\t")
        }


def expected_transcripts() -> dict[int, tuple[int, int, str]]:
    with (RESULTS / "transcript_hashes.tsv").open(
        encoding="utf-8", newline=""
    ) as handle:
        return {
            int(row["orbit"]): (
                int(row["states"]),
                int(row["attempted"]),
                row["sha256"],
            )
            for row in csv.DictReader(handle, delimiter="\t")
            if int(row["v"]) == 29
        }


def atomic_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
    os.replace(temporary, path)


def main() -> None:
    cxx = os.environ.get("CXX", "g++")
    clangxx = os.environ.get("CLANGXX", "clang++")
    counters = expected_counters()
    transcripts = expected_transcripts()
    logs: dict[str, str] = {}
    observations: dict[str, dict[int, tuple[int, ...]]] = {}

    with tempfile.TemporaryDirectory(prefix="eg-v29-") as temporary:
        build = Path(temporary)
        programs = {
            "discovery": (
                cxx,
                SOURCE / "canonical_root_orbit_search.cpp",
            ),
            "independent": (
                cxx,
                SOURCE / "independent_mitm_root_orbit_search.cpp",
            ),
            "verifier_b": (
                clangxx,
                SOURCE / "vector_mitm_root_orbit_verifier.cpp",
            ),
        }
        executables: dict[str, Path] = {}
        for method, (compiler, source) in programs.items():
            executable = build / method
            compile_search(compiler, source, executable)
            executables[method] = executable

        for method, executable in executables.items():
            observations[method] = {}
            for orbit in (1, 2, 3):
                text = run_output([str(executable), str(orbit)])
                observed_counters, observed_transcript = parse_search_output(
                    text, orbit
                )
                if observed_counters != counters[orbit]:
                    raise RuntimeError(
                        f"{method} counters differ in root orbit {orbit}"
                    )
                if observed_transcript != transcripts[orbit]:
                    raise RuntimeError(
                        f"{method} transcript differs in root orbit {orbit}"
                    )
                observations[method][orbit] = observed_counters
                logs[f"{method}_o{orbit}.log"] = deterministic_log(text)

    for name, payload in logs.items():
        atomic_write(LOGS / name, payload)

    print(
        "VERIFIED: all three implementations have identical counters and "
        "search-transcript hashes for all v=29 root orbits."
    )
    for orbit in (1, 2, 3):
        print(orbit, observations["discovery"][orbit])
    print(f"Reproduction completed: {LOGS}")


if __name__ == "__main__":
    main()
