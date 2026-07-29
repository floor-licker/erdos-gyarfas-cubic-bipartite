#!/usr/bin/env python3
"""Reproduce the retained cycle-oracle positive controls."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

RESEARCH = Path(__file__).resolve().parents[1]
SOURCE = RESEARCH / "src"
RESULTS = RESEARCH / "results"
INPUT = RESULTS / "all_19_3_no4_no8.txt"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run(script: str, output: Path, *arguments: str) -> None:
    subprocess.run(
        [
            sys.executable,
            str(SOURCE / script),
            str(INPUT),
            *arguments,
            "--json",
            str(output),
        ],
        check=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        stdout=subprocess.DEVNULL,
    )


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="eg-positive-") as temporary:
        generated = Path(temporary)
        johnson_path = generated / "johnson.json"
        subset_path = generated / "subset.json"
        permutation_path = generated / "permutation.json"

        run("verify_configurations_johnson.py", johnson_path)
        run("verify_configurations_subset_dp.py", subset_path)
        run(
            "permutation_model_verifier.py",
            permutation_path,
            "--index",
            "1",
        )

        johnson = load(johnson_path)
        expected_johnson = load(RESULTS / "johnson_19_all.json")
        observed_version = johnson["summary"].pop("networkx_version")
        recorded_version = expected_johnson["summary"].pop("networkx_version")
        if johnson != expected_johnson:
            raise RuntimeError("NetworkX positive-control results differ")

        if load(subset_path) != load(RESULTS / "subset_dp_19_all.json"):
            raise RuntimeError("subset-state positive-control results differ")
        if load(permutation_path) != load(
            RESULTS / "permutation_model_first19.json"
        ):
            raise RuntimeError("permutation-model positive-control result differs")

    print(
        "VERIFIED: 128 NetworkX and subset-state positive controls agree "
        "with retained results."
    )
    print(
        "VERIFIED: normalized permutation-model positive control agrees "
        "with its retained result."
    )
    print(
        f"NetworkX version: installed {observed_version}; "
        f"recorded {recorded_version}."
    )


if __name__ == "__main__":
    main()
