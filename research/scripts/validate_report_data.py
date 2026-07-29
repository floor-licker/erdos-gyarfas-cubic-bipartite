#!/usr/bin/env python3
"""Cross-check every displayed exhaustive-search counter in the report."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
FIELDS = ("states", "attempted", "pair", "c8", "c16", "completions")


def parse_tsv(path: Path) -> dict[int, tuple[int, ...]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = csv.DictReader(handle, delimiter="\t")
        return {
            int(row["v"]): tuple(int(row[field]) for field in FIELDS) for row in rows
        }


def parse_orbit_tsv(path: Path) -> dict[str, tuple[int, ...]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = csv.DictReader(handle, delimiter="\t")
        return {
            row["orbit"]: tuple(int(row[field]) for field in FIELDS) for row in rows
        }


def parse_frontier_tex(path: Path) -> dict[int, tuple[int, ...]]:
    row_re = re.compile(
        r"^(\d+)\s*&\s*([\d,]+)\s*&\s*([\d,]+)\s*&\s*"
        r"([\d,]+)\s*&\s*([\d,]+)\s*&\s*([\d,]+)\s*&\s*"
        r"([\d,]+)\\\\$"
    )
    result: dict[int, tuple[int, ...]] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        match = row_re.match(raw.strip())
        if match:
            values = tuple(int(value.replace(",", "")) for value in match.groups())
            result[values[0]] = values[1:]
    return result


def parse_orbit_tex(path: Path) -> dict[str, tuple[int, ...]]:
    row_re = re.compile(
        r"^(1|2|3|Total)\s*&\s*([\d,]+)\s*&\s*([\d,]+)\s*&\s*"
        r"([\d,]+)\s*&\s*([\d,]+)\s*&\s*([\d,]+)\s*&\s*"
        r"([\d,]+)\\\\$"
    )
    result: dict[str, tuple[int, ...]] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        match = row_re.match(raw.strip())
        if match:
            result[match.group(1)] = tuple(
                int(value.replace(",", "")) for value in match.groups()[1:]
            )
    return result


def parse_frontier_log(path: Path) -> dict[str, tuple[int, ...]]:
    orbit_re = re.compile(
        r"^ORBIT ([123]) "
        r"states=(\d+) attempted=(\d+) pair=(\d+) c8=(\d+) "
        r"c16=(\d+) completions=(\d+)$"
    )
    total_re = re.compile(
        r"^TOTAL V=29 "
        r"states=(\d+) attempted=(\d+) pair=(\d+) c8=(\d+) "
        r"c16=(\d+) completions=(\d+)"
    )
    result: dict[str, tuple[int, ...]] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if match := orbit_re.match(raw):
            result[match.group(1)] = tuple(map(int, match.groups()[1:]))
        elif match := total_re.match(raw):
            result["Total"] = tuple(map(int, match.groups()))
    return result


def parse_transcript_log(path: Path) -> dict[int, tuple[int, int, str]]:
    transcript_re = re.compile(
        r"^TRANSCRIPT orbit=([123]) states=(\d+) candidates=(\d+) "
        r"sha256=([0-9a-f]{64})$"
    )
    result: dict[int, tuple[int, int, str]] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if match := transcript_re.match(raw):
            result[int(match.group(1))] = (
                int(match.group(2)),
                int(match.group(3)),
                match.group(4),
            )
    return result


def main() -> None:
    fresh_discovery = parse_tsv(
        ROOT / "research/logs/full_range/discovery.tsv"
    )
    fresh_independent = parse_tsv(
        ROOT / "research/logs/full_range/independent.tsv"
    )
    report_frontier = parse_frontier_tex(ROOT / "paper/tables/frontier_counts.tex")
    primary_frontier = parse_tsv(ROOT / "research/results/frontier_counts.tsv")

    assert fresh_discovery == fresh_independent
    assert report_frontier == primary_frontier == fresh_discovery
    assert set(report_frontier) == set(range(7, 30))
    assert all(row[-1] == 0 for row in report_frontier.values())

    report_orbits = parse_orbit_tex(ROOT / "paper/tables/v29_orbits.tex")
    primary_orbits = parse_orbit_tsv(ROOT / "research/results/v29_orbits.tsv")
    assert {key: report_orbits[key] for key in ("1", "2", "3")} == primary_orbits
    reproduced_v29_root = ROOT / "research/logs/v29"
    for method in ("discovery", "independent", "verifier_b"):
        observed: dict[str, tuple[int, ...]] = {}
        for orbit in ("1", "2", "3"):
            parsed = parse_frontier_log(
                reproduced_v29_root / f"{method}_o{orbit}.log"
            )
            observed[orbit] = parsed[orbit]
        assert observed == primary_orbits
        assert tuple(sum(row[i] for row in observed.values()) for i in range(6)) == (
            report_orbits["Total"]
        )

    with (ROOT / "research/results/transcript_hashes.tsv").open(
        encoding="utf-8", newline=""
    ) as handle:
        transcript_rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(transcript_rows) == 69
    assert {(int(row["v"]), int(row["orbit"])) for row in transcript_rows} == {
        (v, orbit) for v in range(7, 30) for orbit in (1, 2, 3)
    }
    assert all(
        int(row["implementations"]) == (2 if int(row["v"]) < 9 else 3)
        for row in transcript_rows
    )
    assert all(re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) for row in transcript_rows)
    for v in range(7, 30):
        rows = [row for row in transcript_rows if int(row["v"]) == v]
        assert sum(int(row["states"]) for row in rows) == primary_frontier[v][0]
        assert sum(int(row["attempted"]) for row in rows) == primary_frontier[v][1]

    expected_v29_transcripts = {
        int(row["orbit"]): (int(row["states"]), int(row["attempted"]), row["sha256"])
        for row in transcript_rows
        if int(row["v"]) == 29
    }
    for name in (
        "discovery_o1.log",
        "discovery_o2.log",
        "discovery_o3.log",
        "independent_o1.log",
        "independent_o2.log",
        "independent_o3.log",
        "verifier_b_o1.log",
        "verifier_b_o2.log",
        "verifier_b_o3.log",
    ):
        orbit = int(re.search(r"_o([123])\.log$", name).group(1))
        assert parse_transcript_log(reproduced_v29_root / name) == {
            orbit: expected_v29_transcripts[orbit]
        }

    unreduced = parse_tsv(
        ROOT / "research/results/unreduced_root_counts.tsv"
    )
    assert set(unreduced) == set(range(7, 29))
    assert all(row[-1] == 0 for row in unreduced.values())
    assert any(unreduced[v] != fresh_discovery[v] for v in range(7, 29))

    genbg_root = ROOT / "research/results/genbg_crosscheck"
    with (genbg_root / "summary.tsv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert [int(row["v"]) for row in rows] == list(range(7, 14))
    assert [int(row["canonical_graphs"]) for row in rows] == [
        1,
        1,
        3,
        10,
        31,
        229,
        2036,
    ]
    for row in rows:
        graph_path = genbg_root / f"v{row['v']}.graph6"
        payload = graph_path.read_bytes()
        assert len(payload.splitlines()) == int(row["canonical_graphs"])
        assert hashlib.sha256(payload).hexdigest() == row["sha256"]

    certificate_root = ROOT / "research/certificates"
    metadata = json.loads(
        (certificate_root / "eg58_witness_certificates.json").read_text(
            encoding="utf-8"
        )
    )
    archive_path = certificate_root / metadata["bundle"]
    assert hashlib.sha256(archive_path.read_bytes()).hexdigest() == (
        metadata["bundle_sha256"]
    )
    entries = metadata["entries"]
    proof_entries = [entry for entry in entries if entry["role"] == "proof"]
    compatibility_entries = [
        entry for entry in entries if entry["role"] == "compatibility"
    ]
    assert metadata["certificate_format"] == "EG58CER1"
    assert len(proof_entries) == metadata["proof_certificate_count"] == 66
    assert (
        len(compatibility_entries)
        == metadata["compatibility_certificate_count"]
        == 1
    )
    expected_orbits = {
        side: ({1} if side == 7 else {1, 2} if side == 8 else {1, 2, 3})
        for side in range(7, 30)
    }
    certificate_fields = (
        "states",
        "attempted",
        "structural",
        "c8",
        "c16",
        "completions",
    )
    expected_root_events = {
        (int(row["v"]), int(row["orbit"])): (
            int(row["states"]),
            int(row["attempted"]),
        )
        for row in transcript_rows
    }
    for side in range(7, 30):
        side_entries = [
            entry for entry in proof_entries if int(entry["side"]) == side
        ]
        assert {int(entry["orbit"]) for entry in side_entries} == (
            expected_orbits[side]
        )
        assert tuple(
            sum(int(entry[field]) for entry in side_entries)
            for field in certificate_fields
        ) == primary_frontier[side]
        assert all(
            (int(entry["states"]), int(entry["attempted"]))
            == expected_root_events[(side, int(entry["orbit"]))]
            for entry in side_entries
        )
    assert tuple(
        int(compatibility_entries[0][field]) for field in certificate_fields
    ) == (1207, 30152, 4172, 24774, 0, 0)
    with ZipFile(archive_path, "r") as archive:
        assert set(archive.namelist()) == {
            str(entry["name"]) for entry in entries
        }

    print(
        "VERIFIED: report and primary full-range table match both fresh implementations."
    )
    print("VERIFIED: report v=29 orbit table matches all three fresh log sets.")
    print("VERIFIED: transcript table and fresh v=29 transcript logs agree.")
    print("VERIFIED: every displayed completion count is zero.")
    print("VERIFIED: canonical unreduced-root diagnostic table is internally valid.")
    print("VERIFIED: stored genbg canonical-set counts and SHA-256 hashes.")
    print("VERIFIED: full-range certificate metadata and archive member set.")


if __name__ == "__main__":
    main()
