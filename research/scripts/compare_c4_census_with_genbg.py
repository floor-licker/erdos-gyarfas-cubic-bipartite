#!/usr/bin/env python3
"""Compare restricted-growth and nauty genbg canonical graph sets."""

from __future__ import annotations

import csv
import hashlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request

RESEARCH = Path(__file__).resolve().parents[1]
SOURCE = RESEARCH / "src"
BUILD = RESEARCH / "build_genbg_crosscheck"
RESULTS = RESEARCH / "results" / "genbg_crosscheck"
NAUTY_VERSION = "2_9_3"
NAUTY_ARCHIVE = f"nauty{NAUTY_VERSION}.tar.gz"
NAUTY_URLS = (
    "https://pallini.di.uniroma1.it/" + NAUTY_ARCHIVE,
    "https://users.cecs.anu.edu.au/~bdm/nauty/" + NAUTY_ARCHIVE,
)
NAUTY_SHA256 = "9fc4edae04f88a0f5883985be3b39cf7f898fd6cc96e96b9ee25452743cc1b5b"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_executable(path: Path) -> bool:
    return path.is_file() and os.access(path, os.X_OK)


def download_nauty(archive: Path) -> None:
    temporary = archive.with_name(f".{archive.name}.download")
    failures: list[str] = []
    for url in NAUTY_URLS:
        temporary.unlink(missing_ok=True)
        try:
            print(f"Downloading pinned nauty archive from {url}", file=sys.stderr)
            with urllib.request.urlopen(url, timeout=90) as response:
                with temporary.open("wb") as output:
                    shutil.copyfileobj(response, output)
            os.replace(temporary, archive)
            return
        except (OSError, urllib.error.URLError) as error:
            failures.append(f"{url}: {error}")
        finally:
            temporary.unlink(missing_ok=True)
    raise RuntimeError(
        "could not download the pinned nauty archive:\n"
        + "\n".join(failures)
    )


def extract_nauty(archive: Path, destination: Path) -> None:
    destination_resolved = destination.resolve()
    with tarfile.open(archive, mode="r:gz") as bundle:
        for member in bundle.getmembers():
            target = (destination / member.name).resolve()
            if (
                target != destination_resolved
                and destination_resolved not in target.parents
            ):
                raise RuntimeError(f"unsafe path in nauty archive: {member.name}")
        bundle.extractall(destination)


def nauty_programs() -> tuple[Path, Path]:
    supplied = os.environ.get("NAUTY_BIN_DIR")
    if supplied:
        binary_dir = Path(supplied).expanduser().resolve()
        genbg = binary_dir / "genbg"
        labelg = binary_dir / "labelg"
    else:
        BUILD.mkdir(parents=True, exist_ok=True)
        archive = BUILD / NAUTY_ARCHIVE
        source = BUILD / f"nauty{NAUTY_VERSION}"
        if not archive.is_file():
            download_nauty(archive)
        actual_hash = sha256(archive)
        if actual_hash != NAUTY_SHA256:
            raise RuntimeError(f"nauty archive checksum mismatch: {actual_hash}")
        if not source.is_dir():
            extract_nauty(archive, BUILD)

        genbg = source / "genbg"
        labelg = source / "labelg"
        if not is_executable(genbg) or not is_executable(labelg):
            subprocess.run(["./configure"], cwd=source, check=True)
            subprocess.run(["make", "genbg", "labelg"], cwd=source, check=True)

    if not is_executable(genbg) or not is_executable(labelg):
        raise RuntimeError("genbg and labelg must be executable")
    return genbg, labelg


def compile_census(compiler: str, side: int, output: Path) -> None:
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
            str(SOURCE / "restricted_growth_c4_census.cpp"),
            "-o",
            str(output),
        ],
        check=True,
    )


def run_to_file(command: list[str], output: Path) -> None:
    with output.open("wb") as handle:
        subprocess.run(command, check=True, stdout=handle)


def sorted_unique_records(path: Path) -> bytes:
    records = sorted(set(path.read_bytes().splitlines()))
    if not records:
        return b""
    return b"\n".join(records) + b"\n"


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="wb",
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
    os.replace(temporary, path)


def main() -> None:
    compiler = os.environ.get("CXX", "c++")
    genbg, labelg = nauty_programs()
    generated_sets: dict[int, bytes] = {}
    summary_rows: list[tuple[int, int, int, str]] = []

    with tempfile.TemporaryDirectory(prefix="eg-genbg-work-") as temporary:
        work = Path(temporary)
        for side in range(7, 14):
            census = work / f"restricted_growth_census_{side}"
            raw = work / f"restricted_{side}.raw.graph6"
            labelled = work / f"restricted_{side}.labelled.graph6"
            genbg_raw = work / f"genbg_{side}.graph6"
            compile_census(compiler, side, census)
            run_to_file([str(census)], raw)
            subprocess.run(
                [
                    str(labelg),
                    "-q",
                    f"-f{'a' * side}{'b' * side}",
                    str(raw),
                    str(labelled),
                ],
                check=True,
            )
            subprocess.run(
                [
                    str(genbg),
                    "-clq",
                    "-Z1",
                    "-d3:3",
                    "-D3:3",
                    str(side),
                    str(side),
                    str(3 * side),
                    str(genbg_raw),
                ],
                check=True,
            )

            restricted_set = sorted_unique_records(labelled)
            genbg_set = sorted_unique_records(genbg_raw)
            if restricted_set != genbg_set:
                raise RuntimeError(f"canonical graph sets differ at side size {side}")

            rooted_count = len(raw.read_bytes().splitlines())
            canonical_count = len(restricted_set.splitlines())
            canonical_hash = hashlib.sha256(restricted_set).hexdigest()
            generated_sets[side] = restricted_set
            summary_rows.append((side, rooted_count, canonical_count, canonical_hash))

    RESULTS.mkdir(parents=True, exist_ok=True)
    for side, payload in generated_sets.items():
        atomic_write(RESULTS / f"v{side}.graph6", payload)

    summary = io.StringIO(newline="")
    writer = csv.writer(summary, delimiter="\t", lineterminator="\n")
    writer.writerow(("v", "rooted_labelled", "canonical_graphs", "sha256"))
    writer.writerows(summary_rows)
    atomic_write(RESULTS / "summary.tsv", summary.getvalue().encode())
    print(
        "VERIFIED: restricted-growth and genbg canonical C4-free sets "
        "agree for v=7,...,13."
    )


if __name__ == "__main__":
    main()
