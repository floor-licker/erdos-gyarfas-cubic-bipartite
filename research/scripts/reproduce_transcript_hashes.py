#!/usr/bin/env python3
"""Reproduce and compare deterministic search-transcript hashes for v=7,...,29."""

from __future__ import annotations

import csv
import os
from pathlib import Path
import re
import subprocess
import tempfile

RESEARCH = Path(__file__).resolve().parents[1]
RESULT = RESEARCH / "results" / "transcript_hashes.tsv"
COUNTERS = re.compile(
    r"ORBIT (\d+) states=(\d+) attempted=(\d+) pair=(\d+) "
    r"c8=(\d+) c16=(\d+) completions=(\d+)"
)
TRANSCRIPT = re.compile(
    r"TRANSCRIPT orbit=(\d+) states=(\d+) candidates=(\d+) " r"sha256=([0-9a-f]{64})"
)
FIELDS = ("states", "attempted", "pair", "c8", "c16", "completions")


def checked(command: list[str]) -> str:
    return subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout


def parse_output(text: str, expected_orbit: int) -> tuple[tuple[int, ...], str]:
    counter_match = COUNTERS.search(text)
    transcript_match = TRANSCRIPT.search(text)
    if counter_match is None or transcript_match is None:
        raise RuntimeError(f"missing counter or transcript line:\n{text}")
    counter_orbit = int(counter_match.group(1))
    transcript_orbit = int(transcript_match.group(1))
    if counter_orbit != expected_orbit or transcript_orbit != expected_orbit:
        raise RuntimeError(
            f"expected orbit {expected_orbit}, got "
            f"{counter_orbit} and {transcript_orbit}"
        )
    counters = tuple(map(int, counter_match.groups()[1:]))
    transcript_states = int(transcript_match.group(2))
    transcript_candidates = int(transcript_match.group(3))
    if (transcript_states, transcript_candidates) != counters[:2]:
        raise RuntimeError(
            "transcript event counts differ from search counters: "
            f"{(transcript_states, transcript_candidates)} != {counters[:2]}"
        )
    return counters, transcript_match.group(4)


def expected_totals() -> dict[int, tuple[int, ...]]:
    with (RESEARCH / "results" / "frontier_counts.tsv").open(
        newline="", encoding="utf-8"
    ) as handle:
        return {
            int(row["v"]): tuple(int(row[field]) for field in FIELDS)
            for row in csv.DictReader(handle, delimiter="\t")
        }


def main() -> None:
    cxx = os.environ.get("CXX", "g++")
    clangxx = os.environ.get("CLANGXX", "clang++")
    common = [
        "-O3",
        "-std=c++17",
        "-Wall",
        "-Wextra",
        "-Wpedantic",
        "-Werror",
    ]
    expected = expected_totals()
    rows: list[dict[str, str | int]] = []

    with tempfile.TemporaryDirectory(prefix="eg-transcript-") as temporary:
        build = Path(temporary)
        self_test = build / "sha256_self_test"
        subprocess.run(
            [
                cxx,
                *common,
                str(RESEARCH / "src" / "test_transcript_sha256.cpp"),
                "-o",
                str(self_test),
            ],
            check=True,
        )
        checked([str(self_test)])

        for side in range(7, 30):
            programs = {
                "canonical": (
                    cxx,
                    RESEARCH / "src" / "canonical_root_orbit_search.cpp",
                ),
                "independent_mitm": (
                    cxx,
                    RESEARCH / "src" / "independent_mitm_root_orbit_search.cpp",
                ),
            }
            if side >= 9:
                programs["vector_mitm"] = (
                    clangxx,
                    RESEARCH / "src" / "vector_mitm_root_orbit_verifier.cpp",
                )

            executables: dict[str, Path] = {}
            for method, (compiler, source) in programs.items():
                executable = build / f"{method}_{side}"
                subprocess.run(
                    [
                        compiler,
                        *common,
                        f"-DSIDE={side}",
                        str(source),
                        "-o",
                        str(executable),
                    ],
                    check=True,
                )
                executables[method] = executable

            side_totals = [0] * len(FIELDS)
            for orbit in (1, 2, 3):
                observations = {
                    method: parse_output(checked([str(executable), str(orbit)]), orbit)
                    for method, executable in executables.items()
                }
                reference_counters, reference_hash = observations["canonical"]
                for method, observation in observations.items():
                    if observation != (reference_counters, reference_hash):
                        raise RuntimeError(
                            f"transcript mismatch at v={side}, orbit={orbit}: "
                            f"{method}={observation}, "
                            f"canonical={(reference_counters, reference_hash)}"
                        )
                side_totals = [
                    total + value
                    for total, value in zip(side_totals, reference_counters)
                ]
                rows.append(
                    {
                        "v": side,
                        "orbit": orbit,
                        "states": reference_counters[0],
                        "attempted": reference_counters[1],
                        "sha256": reference_hash,
                        "implementations": len(observations),
                    }
                )

            if tuple(side_totals) != expected[side]:
                raise RuntimeError(
                    f"counter mismatch at v={side}: "
                    f"{tuple(side_totals)} != {expected[side]}"
                )
            print(
                f"v={side}: transcript hashes agree across "
                f"{len(executables)} implementations"
            )

    with RESULT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "v",
                "orbit",
                "states",
                "attempted",
                "sha256",
                "implementations",
            ),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    print(
        f"VERIFIED: wrote {len(rows)} matching transcript hashes to "
        "research/results/transcript_hashes.tsv"
    )


if __name__ == "__main__":
    main()
