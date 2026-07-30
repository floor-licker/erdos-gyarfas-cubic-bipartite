#!/usr/bin/env python3
"""Verify the triangle-rooted searches, certificates, and six kernels."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research" / "src"
RESULTS = ROOT / "research" / "results"
CERTIFICATES = ROOT / "research" / "certificates"
TESTS = ROOT / "research" / "tests" / "certificate_tampering"

COUNT_FIELDS = ("states", "attempted", "pair", "c8", "c16", "completions")
CERTIFICATE_FIELDS = (
    "states",
    "attempted",
    "structural",
    "c8",
    "c16",
    "completions",
)
ORBIT_RE = re.compile(
    r"^ORBIT ([12]) states=(\d+) attempted=(\d+) pair=(\d+) "
    r"c8=(\d+) c16=(\d+) completions=(\d+)$",
    re.MULTILINE,
)
TRANSCRIPT_RE = re.compile(
    r"^TRANSCRIPT orbit=([12]) states=(\d+) candidates=(\d+) "
    r"sha256=([0-9a-f]{64})$",
    re.MULTILINE,
)
CHECKER_HEADER_RE = re.compile(
    r"^VERIFIED EG58TRI1-UNIVERSAL side=(\d+) orbit=(\d+)$",
    re.MULTILINE,
)
CHECKER_FIELD_RE = re.compile(
    r"^(states|attempted|structural|C8|C16|solutions) (\d+)$",
    re.MULTILINE,
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_text(command: list[str]) -> str:
    result = subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(command)}\n"
            f"{result.stdout}{result.stderr}"
        )
    return result.stdout


def compile_cpp(
    compiler: str,
    source: Path,
    output: Path,
    *,
    side: int | None = None,
) -> None:
    command = [
        compiler,
        "-O3",
        "-std=c++17",
        "-Wall",
        "-Wextra",
        "-Wpedantic",
        "-Werror",
    ]
    if side is not None:
        command.append(f"-DSIDE={side}")
    command.extend((str(source), "-o", str(output)))
    run_text(command)


def load_frontier() -> dict[int, tuple[int, ...]]:
    with (RESULTS / "triangle_frontier_counts.tsv").open(
        encoding="utf-8", newline=""
    ) as handle:
        return {
            int(row["v"]): tuple(int(row[field]) for field in COUNT_FIELDS)
            for row in csv.DictReader(handle, delimiter="\t")
        }


def load_transcripts() -> dict[tuple[int, int], tuple[int, int, str]]:
    with (RESULTS / "triangle_transcript_hashes.tsv").open(
        encoding="utf-8", newline=""
    ) as handle:
        return {
            (int(row["v"]), int(row["orbit"])): (
                int(row["states"]),
                int(row["candidates"]),
                row["sha256"],
            )
            for row in csv.DictReader(handle, delimiter="\t")
        }


def parse_search(
    text: str,
) -> tuple[
    dict[int, tuple[int, ...]],
    dict[int, tuple[int, int, str]],
]:
    counts = {
        int(match.group(1)): tuple(int(value) for value in match.groups()[1:])
        for match in ORBIT_RE.finditer(text)
    }
    transcripts = {
        int(match.group(1)): (
            int(match.group(2)),
            int(match.group(3)),
            match.group(4),
        )
        for match in TRANSCRIPT_RE.finditer(text)
    }
    if set(counts) != {1, 2} or set(transcripts) != {1, 2}:
        raise RuntimeError(f"unexpected triangle-search output:\n{text}")
    return counts, transcripts


def verify_searches(compiler: str, build: Path) -> None:
    frontier = load_frontier()
    expected_transcripts = load_transcripts()
    if set(frontier) != set(range(7, 30)):
        raise RuntimeError("triangle frontier table does not cover v=7,...,29")
    if set(expected_transcripts) != {
        (side, orbit) for side in range(7, 30) for orbit in (1, 2)
    }:
        raise RuntimeError("triangle transcript table has the wrong key set")

    search_a = build / "triangle_search_dfs"
    search_b = build / "triangle_search_mitm"
    for side in range(7, 30):
        compile_cpp(
            compiler,
            SOURCE / "triangle_root_universal_search.cpp",
            search_a,
            side=side,
        )
        compile_cpp(
            compiler,
            SOURCE / "triangle_root_universal_mitm.cpp",
            search_b,
            side=side,
        )
        counts_a, transcripts_a = parse_search(run_text([str(search_a)]))
        counts_b, transcripts_b = parse_search(run_text([str(search_b)]))
        if counts_a != counts_b or transcripts_a != transcripts_b:
            raise RuntimeError(f"triangle implementations disagree at v={side}")

        total = tuple(
            sum(counts_a[orbit][column] for orbit in (1, 2))
            for column in range(len(COUNT_FIELDS))
        )
        if total != frontier[side]:
            raise RuntimeError(f"triangle frontier counters differ at v={side}")
        for orbit in (1, 2):
            if transcripts_a[orbit] != expected_transcripts[(side, orbit)]:
                raise RuntimeError(
                    f"triangle transcript differs at v={side}, orbit={orbit}"
                )

    print(
        "VERIFIED: two triangle-rooted implementations agree on all counters "
        "and transcripts for v=7,...,29."
    )


def parse_detached_digest(path: Path, expected_name: str) -> str:
    parts = path.read_text(encoding="utf-8").strip().split()
    if len(parts) != 2 or parts[1] != expected_name:
        raise RuntimeError(f"malformed detached digest: {path}")
    if re.fullmatch(r"[0-9a-f]{64}", parts[0]) is None:
        raise RuntimeError(f"invalid detached digest: {path}")
    return parts[0]


def archive_members(path: Path) -> dict[str, bytes]:
    with ZipFile(path, "r") as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise RuntimeError(f"duplicate ZIP member in {path}")
        if any(
            not name
            or name.startswith("/")
            or "\\" in name
            or ".." in Path(name).parts
            or name.endswith("/")
            for name in names
        ):
            raise RuntimeError(f"unsafe or non-file ZIP member in {path}")
        return {name: archive.read(name) for name in names}


def parse_checker(text: str) -> dict[str, int]:
    header = CHECKER_HEADER_RE.search(text)
    if header is None:
        raise RuntimeError(f"checker did not report acceptance:\n{text}")
    fields = {
        name.lower(): int(value)
        for name, value in CHECKER_FIELD_RE.findall(text)
    }
    if set(fields) != {
        "states",
        "attempted",
        "structural",
        "c8",
        "c16",
        "solutions",
    }:
        raise RuntimeError("checker output has an unexpected counter set")
    fields["side"] = int(header.group(1))
    fields["orbit"] = int(header.group(2))
    fields["completions"] = fields.pop("solutions")
    return fields


def expected_certificate_counts(entry: dict[str, object]) -> tuple[int, ...]:
    return tuple(int(entry[field]) for field in CERTIFICATE_FIELDS)


def observed_certificate_counts(observed: dict[str, int]) -> tuple[int, ...]:
    return tuple(observed[field] for field in CERTIFICATE_FIELDS)


def write_member(build: Path, name: str, payload: bytes) -> Path:
    target = build / name
    target.write_bytes(payload)
    return target


def verify_universal_bundle(
    compiler: str,
    build: Path,
    checker: Path,
    dump_checker: Path,
) -> tuple[Path, Path]:
    metadata_path = (
        CERTIFICATES / "eg58_triangle_universal_two_streams.json"
    )
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    archive_path = CERTIFICATES / str(metadata["bundle"])
    detached_path = archive_path.with_suffix(archive_path.suffix + ".sha256")
    expected_sha = str(metadata["bundle_sha256"])
    if sha256_file(archive_path) != expected_sha:
        raise RuntimeError("universal triangle archive SHA-256 differs")
    if parse_detached_digest(detached_path, archive_path.name) != expected_sha:
        raise RuntimeError("universal triangle detached digest differs")
    if archive_path.stat().st_size != int(metadata["bundle_bytes"]):
        raise RuntimeError("universal triangle archive size differs")

    members = archive_members(archive_path)
    entries = list(metadata["entries"])
    if set(members) != {str(entry["name"]) for entry in entries}:
        raise RuntimeError("universal triangle archive member set differs")
    if len(entries) != 2 or int(metadata["proof_certificate_count"]) != 2:
        raise RuntimeError("universal triangle stream count differs")

    generator = build / "generate_triangle_certificate"
    compile_cpp(
        compiler,
        SOURCE / "generate_triangle_certificate.cpp",
        generator,
        side=29,
    )

    certificate_paths: dict[int, Path] = {}
    dump_paths: dict[int, Path] = {}
    for entry in entries:
        name = str(entry["name"])
        orbit = int(entry["orbit"])
        payload = members[name]
        if len(payload) != int(entry["raw_bytes"]):
            raise RuntimeError(f"raw stream size differs: {name}")
        if sha256_bytes(payload) != str(entry["raw_sha256"]):
            raise RuntimeError(f"raw stream SHA-256 differs: {name}")
        certificate = write_member(build, name, payload)
        certificate_paths[orbit] = certificate

        observed = parse_checker(run_text([str(checker), str(certificate)]))
        if (observed["side"], observed["orbit"]) != (29, orbit):
            raise RuntimeError(f"wrong universal stream identity: {name}")
        if observed_certificate_counts(observed) != expected_certificate_counts(
            entry
        ):
            raise RuntimeError(f"universal stream counters differ: {name}")

        regenerated = build / f"regenerated_o{orbit}.cert"
        run_text([str(generator), str(regenerated), str(orbit)])
        if regenerated.read_bytes() != payload:
            raise RuntimeError(f"universal stream is not reproducible: {name}")

        dump = build / f"triangle_o{orbit}.states"
        dump_paths[orbit] = dump
        dump_observed = parse_checker(
            run_text([str(dump_checker), str(certificate), str(dump)])
        )
        if dump_observed != observed:
            raise RuntimeError(f"dump checker counters differ: {name}")

    expected_lines = []
    for line in (RESULTS / "triangle_depth19_states.txt").read_text(
        encoding="utf-8"
    ).splitlines():
        _, remainder = line.split(" ", 1)
        expected_lines.append(remainder)
    actual_lines = []
    for orbit in (1, 2):
        actual_lines.extend(
            line.rstrip(";")
            for line in dump_paths[orbit].read_text(
                encoding="utf-8"
            ).splitlines()
        )
    if actual_lines != expected_lines or len(actual_lines) != 337:
        raise RuntimeError("depth-19 state stream differs")

    print(
        "VERIFIED: two universal cap-29 streams, exact regeneration, and "
        "337 depth-19 states."
    )
    return certificate_paths[1], certificate_paths[2]


def verify_conventional_bundle(
    build: Path,
    checker: Path,
) -> None:
    metadata = json.loads(
        (
            CERTIFICATES / "eg58_triangle_witness_certificates.json"
        ).read_text(encoding="utf-8")
    )
    archive_path = CERTIFICATES / "eg58_triangle_witness_certificates.zip"
    expected_sha = str(metadata["sha256"])
    if sha256_file(archive_path) != expected_sha:
        raise RuntimeError("conventional triangle archive SHA-256 differs")
    detached_path = archive_path.with_suffix(archive_path.suffix + ".sha256")
    if parse_detached_digest(detached_path, archive_path.name) != expected_sha:
        raise RuntimeError("conventional triangle detached digest differs")
    if archive_path.stat().st_size != int(metadata["compressed_bytes"]):
        raise RuntimeError("conventional triangle archive size differs")

    entries = list(metadata["counts"])
    members = archive_members(archive_path)
    expected_names = {
        f"tri_v{int(entry['v'])}_o{int(entry['orbit'])}.cert"
        for entry in entries
    }
    if set(members) != expected_names:
        raise RuntimeError("conventional triangle archive member set differs")
    if len(entries) != 45 or int(metadata["streams"]) != 45:
        raise RuntimeError("conventional triangle stream count differs")

    by_side: dict[int, list[tuple[int, ...]]] = {}
    for entry in entries:
        side = int(entry["v"])
        orbit = int(entry["orbit"])
        name = f"tri_v{side}_o{orbit}.cert"
        payload = members[name]
        if len(payload) != int(entry["bytes"]):
            raise RuntimeError(f"conventional stream size differs: {name}")
        certificate = write_member(build, f"conventional_{name}", payload)
        observed = parse_checker(run_text([str(checker), str(certificate)]))
        if (observed["side"], observed["orbit"]) != (side, orbit):
            raise RuntimeError(f"wrong conventional stream identity: {name}")
        counts = observed_certificate_counts(observed)
        if counts != expected_certificate_counts(entry):
            raise RuntimeError(f"conventional stream counters differ: {name}")
        by_side.setdefault(side, []).append(counts)

    frontier = load_frontier()
    if set(by_side) != set(range(7, 30)):
        raise RuntimeError("conventional streams do not cover v=7,...,29")
    for side, rows in by_side.items():
        total = tuple(
            sum(row[column] for row in rows)
            for column in range(len(CERTIFICATE_FIELDS))
        )
        expected = (
            frontier[side][0],
            frontier[side][1],
            frontier[side][2],
            frontier[side][3],
            frontier[side][4],
            frontier[side][5],
        )
        if total != expected:
            raise RuntimeError(
                f"conventional certificate totals differ at v={side}"
            )

    print("VERIFIED: 45 conventional per-side triangle streams.")


def verify_classification_and_tampering(
    checker: Path,
    orbit1: Path,
    orbit2: Path,
) -> None:
    classification = run_text(
        [
            sys.executable,
            str(SOURCE / "verify_triangle_kernel_classification.py"),
            str(RESULTS / "triangle_kernel_classes.json"),
            str(RESULTS / "triangle_depth19_states.txt"),
            str(RESULTS / "triangle_kernel_isomorphism_certificate.txt"),
        ]
    )
    print(classification.strip())
    tampering = run_text(
        [
            sys.executable,
            str(
                TESTS / "test_triangle_certificate_tampering.py"
            ),
            str(checker),
            str(orbit1),
            str(orbit2),
        ]
    )
    print(tampering.strip())


def verify_certificates(compiler: str, build: Path) -> None:
    checker = build / "verify_triangle_universal_certificate"
    dump_checker = build / "verify_triangle_universal_dump"
    compile_cpp(
        compiler,
        SOURCE / "verify_triangle_universal_certificate.cpp",
        checker,
    )
    compile_cpp(
        compiler,
        SOURCE / "verify_triangle_universal_dump.cpp",
        dump_checker,
    )
    orbit1, orbit2 = verify_universal_bundle(
        compiler, build, checker, dump_checker
    )
    verify_conventional_bundle(build, checker)
    verify_classification_and_tampering(checker, orbit1, orbit2)
    print("ALL TRIANGLE-ROOTED CERTIFICATE CHECKS PASSED")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=("certificate", "search", "all"),
        nargs="?",
        default="all",
    )
    arguments = parser.parse_args()
    compiler = os.environ.get("CXX", "c++")
    if shutil.which(compiler) is None:
        raise RuntimeError(f"C++ compiler not found: {compiler}")

    with tempfile.TemporaryDirectory(prefix="eg-triangle-") as temporary:
        build = Path(temporary)
        if arguments.action in {"certificate", "all"}:
            verify_certificates(compiler, build)
        if arguments.action in {"search", "all"}:
            verify_searches(compiler, build)
    print("ALL TRIANGLE-ROOTED CHECKS PASSED")


if __name__ == "__main__":
    main()
