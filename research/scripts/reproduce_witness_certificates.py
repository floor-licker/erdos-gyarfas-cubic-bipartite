#!/usr/bin/env python3
"""Generate or verify the full-range witness-certificate bundle."""

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
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research"
SOURCE = RESEARCH / "src"
RESULTS = RESEARCH / "results"
CERTIFICATES = RESEARCH / "certificates"
ARCHIVE = CERTIFICATES / "eg58_witness_certificates.zip"
METADATA = CERTIFICATES / "eg58_witness_certificates.json"
DETACHED_SHA256 = CERTIFICATES / "eg58_witness_certificates.zip.sha256"
FORMAT = "EG58CER1"
FIELDS = ("states", "attempted", "structural", "c8", "c16", "completions")
GENERATOR_LINE = re.compile(
    r"^CERT EG58CER1 side=(\d+) orbit=(\d+) flags=(\d+) "
    r"states=(\d+) attempted=(\d+) structural=(\d+) c8=(\d+) "
    r"c16=(\d+) completions=(\d+) bytes=(\d+) seconds=([0-9.eE+-]+)$"
)
CHECKER_HEADER = re.compile(
    r"^VERIFIED EG58CER1 side=(\d+) orbit=(\d+)$", re.MULTILINE
)
CHECKER_FIELD = re.compile(
    r"^(states|attempted|structural|C8|C16|solutions) (\d+)$",
    re.MULTILINE,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compile_cpp(
    compiler: str,
    source: Path,
    output: Path,
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
    subprocess.run(command, check=True)


def run_text(command: list[str]) -> str:
    return subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout


def frontier_rows() -> dict[int, tuple[int, ...]]:
    with (RESULTS / "frontier_counts.tsv").open(
        encoding="utf-8", newline=""
    ) as handle:
        return {
            int(row["v"]): (
                int(row["states"]),
                int(row["attempted"]),
                int(row["pair"]),
                int(row["c8"]),
                int(row["c16"]),
                int(row["completions"]),
            )
            for row in csv.DictReader(handle, delimiter="\t")
        }


def root_event_rows() -> dict[tuple[int, int], tuple[int, int]]:
    with (RESULTS / "transcript_hashes.tsv").open(
        encoding="utf-8", newline=""
    ) as handle:
        return {
            (int(row["v"]), int(row["orbit"])): (
                int(row["states"]),
                int(row["attempted"]),
            )
            for row in csv.DictReader(handle, delimiter="\t")
        }


def valid_orbits(side: int) -> tuple[int, ...]:
    if side == 7:
        return (1,)
    if side == 8:
        return (1, 2)
    return (1, 2, 3)


def parse_generator(text: str) -> dict[str, int | float]:
    match = GENERATOR_LINE.fullmatch(text.strip())
    if match is None:
        raise RuntimeError(f"unexpected generator output: {text!r}")
    values = match.groups()
    return {
        "side": int(values[0]),
        "orbit": int(values[1]),
        "flags": int(values[2]),
        "states": int(values[3]),
        "attempted": int(values[4]),
        "structural": int(values[5]),
        "c8": int(values[6]),
        "c16": int(values[7]),
        "completions": int(values[8]),
        "bytes": int(values[9]),
        "seconds": float(values[10]),
    }


def parse_checker(text: str) -> dict[str, int]:
    header = CHECKER_HEADER.search(text)
    if header is None:
        raise RuntimeError(f"checker did not verify the stream: {text!r}")
    observed = {
        name.lower(): int(value)
        for name, value in CHECKER_FIELD.findall(text)
    }
    expected_names = {
        "states",
        "attempted",
        "structural",
        "c8",
        "c16",
        "solutions",
    }
    if set(observed) != expected_names:
        raise RuntimeError("checker output has an unexpected counter set")
    observed["side"] = int(header.group(1))
    observed["orbit"] = int(header.group(2))
    observed["completions"] = observed.pop("solutions")
    return observed


def deterministic_zip_info(name: str) -> ZipInfo:
    info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def add_file_to_zip(archive: ZipFile, name: str, source: Path) -> None:
    info = deterministic_zip_info(name)
    with source.open("rb") as input_handle:
        with archive.open(info, mode="w", force_zip64=True) as output_handle:
            shutil.copyfileobj(input_handle, output_handle, 1024 * 1024)


def proof_entry_name(side: int, orbit: int) -> str:
    return f"proof/v{side:02d}/orbit{orbit}.cert"


def compile_checker(compiler: str, build: Path) -> Path:
    checker = build / "verify_eg_certificate"
    compile_cpp(
        compiler,
        SOURCE / "verify_eg_certificate.cpp",
        checker,
    )
    return checker


def check_raw_certificate(checker: Path, certificate: Path) -> dict[str, int]:
    return parse_checker(run_text([str(checker), str(certificate)]))


def make_entry(
    raw: Path,
    name: str,
    generated: dict[str, int | float],
    compatibility: bool = False,
) -> dict[str, object]:
    return {
        "name": name,
        "side": generated["side"],
        "orbit": generated["orbit"],
        "flags": generated["flags"],
        "states": generated["states"],
        "attempted": generated["attempted"],
        "structural": generated["structural"],
        "c8": generated["c8"],
        "c16": generated["c16"],
        "completions": generated["completions"],
        "raw_bytes": raw.stat().st_size,
        "raw_sha256": sha256_file(raw),
        "role": "compatibility" if compatibility else "proof",
    }


def generate() -> None:
    compiler = os.environ.get("CXX", "c++")
    expected = frontier_rows()
    expected_root_events = root_event_rows()
    entries: list[dict[str, object]] = []
    per_side: dict[int, list[tuple[int, ...]]] = {}

    CERTIFICATES.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="eg-certificates-") as temporary:
        build = Path(temporary)
        checker = compile_checker(compiler, build)
        temporary_archive = build / ARCHIVE.name

        with ZipFile(
            temporary_archive,
            mode="w",
            compression=ZIP_DEFLATED,
            compresslevel=9,
            allowZip64=True,
        ) as archive:
            for side in range(7, 30):
                generator = build / f"generate_v{side}"
                compile_cpp(
                    compiler,
                    SOURCE / "generate_eg_certificate.cpp",
                    generator,
                    side=side,
                )
                per_side[side] = []
                for orbit in valid_orbits(side):
                    raw = build / f"v{side:02d}-orbit{orbit}.cert"
                    generated = parse_generator(
                        run_text([str(generator), str(raw), str(orbit)])
                    )
                    checked = check_raw_certificate(checker, raw)
                    for field in ("side", "orbit", *FIELDS):
                        if checked[field] != generated[field]:
                            raise RuntimeError(
                                f"generator/checker mismatch at v={side}, "
                                f"orbit={orbit}, field={field}"
                            )
                    if (
                        int(generated["states"]),
                        int(generated["attempted"]),
                    ) != expected_root_events[(side, orbit)]:
                        raise RuntimeError(
                            f"root-event counts differ at v={side}, "
                            f"orbit={orbit}"
                        )
                    counters = tuple(int(generated[field]) for field in FIELDS)
                    per_side[side].append(counters)
                    name = proof_entry_name(side, orbit)
                    entries.append(make_entry(raw, name, generated))
                    add_file_to_zip(archive, name, raw)

            compatibility_raw = build / "v16-unreduced-c4-c8.cert"
            generator_v16 = build / "generate_v16"
            compatibility = parse_generator(
                run_text(
                    [
                        str(generator_v16),
                        str(compatibility_raw),
                        "c8-only",
                    ]
                )
            )
            checked = check_raw_certificate(checker, compatibility_raw)
            for field in ("side", "orbit", *FIELDS):
                if checked[field] != compatibility[field]:
                    raise RuntimeError(
                        f"compatibility generator/checker mismatch: {field}"
                    )
            compatibility_expected = (1207, 30152, 4172, 24774, 0, 0)
            if tuple(int(compatibility[field]) for field in FIELDS) != (
                compatibility_expected
            ):
                raise RuntimeError(
                    "v=16 compatibility certificate no longer reproduces "
                    "the former certificate's semantic counters"
                )
            compatibility_name = (
                "compatibility/v16-unreduced-c4-c8.cert"
            )
            entries.append(
                make_entry(
                    compatibility_raw,
                    compatibility_name,
                    compatibility,
                    compatibility=True,
                )
            )
            add_file_to_zip(
                archive, compatibility_name, compatibility_raw
            )

        for side, rows in per_side.items():
            total = tuple(
                sum(row[index] for row in rows)
                for index in range(len(FIELDS))
            )
            if total != expected[side]:
                raise RuntimeError(
                    f"certificate counters differ from the primary table "
                    f"at v={side}: {total} != {expected[side]}"
                )

        archive_sha256 = sha256_file(temporary_archive)
        os.replace(temporary_archive, ARCHIVE)

    metadata = {
        "bundle": ARCHIVE.name,
        "bundle_sha256": archive_sha256,
        "certificate_format": FORMAT,
        "bundle_version": 1,
        "created": "2026-07-29",
        "compression": "ZIP DEFLATE level 9",
        "claim": (
            "For every side size v=7,...,29, every normalized "
            "restricted-growth root branch is exhausted after positive "
            "C8/C16 witness checks, with zero complete configurations."
        ),
        "proof_certificate_count": sum(
            entry["role"] == "proof" for entry in entries
        ),
        "compatibility_certificate_count": sum(
            entry["role"] == "compatibility" for entry in entries
        ),
        "entries": entries,
    }
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=CERTIFICATES,
        prefix=f".{METADATA.name}.",
        delete=False,
    ) as handle:
        temporary_metadata = Path(handle.name)
        json.dump(metadata, handle, indent=2)
        handle.write("\n")
    os.replace(temporary_metadata, METADATA)
    os.chmod(METADATA, 0o644)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=CERTIFICATES,
        prefix=f".{DETACHED_SHA256.name}.",
        delete=False,
    ) as handle:
        temporary_digest = Path(handle.name)
        handle.write(f"{archive_sha256}  {ARCHIVE.name}\n")
    os.replace(temporary_digest, DETACHED_SHA256)
    os.chmod(DETACHED_SHA256, 0o644)
    print(
        f"GENERATED: {ARCHIVE} "
        f"({ARCHIVE.stat().st_size} compressed bytes)"
    )
    print(
        f"GENERATED: {len(entries) - 1} full-range proof streams and "
        "1 compatibility stream"
    )


def extract_and_hash(
    archive: ZipFile,
    name: str,
    destination: Path,
) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with archive.open(name, "r") as input_handle:
        with destination.open("wb") as output_handle:
            while chunk := input_handle.read(1024 * 1024):
                output_handle.write(chunk)
                digest.update(chunk)
                size += len(chunk)
    return size, digest.hexdigest()


def verify() -> None:
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    if metadata["certificate_format"] != FORMAT:
        raise RuntimeError("metadata names an unsupported certificate format")
    if metadata["bundle"] != ARCHIVE.name:
        raise RuntimeError("metadata names the wrong archive")
    if sha256_file(ARCHIVE) != metadata["bundle_sha256"]:
        raise RuntimeError("certificate-bundle SHA-256 mismatch")
    expected_detached = (
        f"{metadata['bundle_sha256']}  {ARCHIVE.name}\n"
    )
    if DETACHED_SHA256.read_text(encoding="utf-8") != expected_detached:
        raise RuntimeError("detached certificate-bundle digest mismatch")

    entries = metadata["entries"]
    named_entries = {entry["name"]: entry for entry in entries}
    if len(named_entries) != len(entries):
        raise RuntimeError("metadata repeats a certificate member name")

    compiler = os.environ.get("CXX", "c++")
    expected = frontier_rows()
    expected_root_events = root_event_rows()
    observed: dict[int, list[tuple[int, ...]]] = {
        side: [] for side in range(7, 30)
    }

    with tempfile.TemporaryDirectory(
        prefix="eg-certificate-check-"
    ) as temporary:
        build = Path(temporary)
        checker = compile_checker(compiler, build)
        raw = build / "current.cert"
        with ZipFile(ARCHIVE, "r") as archive:
            if set(archive.namelist()) != set(named_entries):
                raise RuntimeError(
                    "archive member set differs from the metadata"
                )
            bad_member = archive.testzip()
            if bad_member is not None:
                raise RuntimeError(f"ZIP CRC failure: {bad_member}")

            for name in archive.namelist():
                entry = named_entries[name]
                size, digest = extract_and_hash(archive, name, raw)
                if size != entry["raw_bytes"]:
                    raise RuntimeError(f"raw size mismatch: {name}")
                if digest != entry["raw_sha256"]:
                    raise RuntimeError(f"raw SHA-256 mismatch: {name}")
                checked = check_raw_certificate(checker, raw)
                for field in ("side", "orbit", *FIELDS):
                    if checked[field] != entry[field]:
                        raise RuntimeError(
                            f"checker/metadata mismatch for {name}: {field}"
                        )
                if entry["role"] == "proof":
                    side = int(entry["side"])
                    orbit = int(entry["orbit"])
                    if (
                        checked["states"],
                        checked["attempted"],
                    ) != expected_root_events[(side, orbit)]:
                        raise RuntimeError(
                            f"root-event counts differ for {name}"
                        )
                    observed[side].append(
                        tuple(checked[field] for field in FIELDS)
                    )

        tamper_result = subprocess.run(
            [
                sys.executable,
                str(
                    RESEARCH
                    / "tests"
                    / "certificate_tampering"
                    / "test_tampering.py"
                ),
                str(checker),
                str(ARCHIVE),
            ],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )

    for side in range(7, 30):
        expected_orbit_set = set(valid_orbits(side))
        actual_orbit_set = {
            int(entry["orbit"])
            for entry in entries
            if entry["role"] == "proof" and entry["side"] == side
        }
        if actual_orbit_set != expected_orbit_set:
            raise RuntimeError(
                f"wrong root-orbit coverage at side size {side}"
            )
        total = tuple(
            sum(row[index] for row in observed[side])
            for index in range(len(FIELDS))
        )
        if total != expected[side]:
            raise RuntimeError(
                f"proof-stream totals differ at side size {side}"
            )

    print(
        "VERIFIED: 66 witness streams exhaust every normalized root orbit "
        "for v=7,...,29."
    )
    print(
        "VERIFIED: all proof-stream totals match frontier_counts.tsv and "
        "all completion counts are zero."
    )
    print(
        "VERIFIED: the compatibility stream reproduces the former v=16 "
        "C4/C8 certificate counters."
    )
    print(tamper_result.stdout.strip())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("generate", "verify"))
    arguments = parser.parse_args()
    if arguments.action == "generate":
        generate()
    else:
        verify()


if __name__ == "__main__":
    main()
