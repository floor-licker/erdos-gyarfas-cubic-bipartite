#!/usr/bin/env python3
"""Generate the manuscript's exhaustive-search tables from primary TSV data."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIELDS = ("states", "attempted", "pair", "c8", "c16", "completions")
CERTIFICATE_FIELDS = (
    "states",
    "attempted",
    "structural",
    "c8",
    "c16",
    "completions",
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def formatted_values(row: dict[str, str]) -> list[str]:
    return [f"{int(row[field]):,}" for field in FIELDS]


def frontier_table(rows: list[dict[str, str]]) -> str:
    lines = [
        r"\begin{longtable}{rrrrrrr}",
        r"\caption{Fresh exact restricted-growth search counts regenerated from the",
        r"included source. The graph order is $2v$.}\label{tab:frontier-counts}\\",
        r"\toprule",
        r"$v$ & states & attempted & pair/$C_4$ & $C_8$ & $C_{16}$ & completions\\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"$v$ & states & attempted & pair/$C_4$ & $C_8$ & $C_{16}$ & completions\\",
        r"\midrule",
        r"\endhead",
    ]
    for row in rows:
        values = " & ".join(formatted_values(row))
        lines.append(f"{int(row['v'])} & {values}" + r"\\")
    lines.extend([r"\bottomrule", r"\end{longtable}"])
    return "\n".join(lines) + "\n"


def orbit_table(rows: list[dict[str, str]]) -> str:
    totals = {
        field: sum(int(row[field]) for row in rows)
        for field in FIELDS
    }
    lines = [
        r"\begin{table}[ht]",
        r"\centering",
        r"\caption{Side size $v=29$ (graph order $58$), split by the three root-stabilizer orbits.}",
        r"\label{tab:v29-orbits}",
        r"\begin{tabular}{rrrrrrr}",
        r"\toprule",
        r"orbit & states & attempted & pair/$C_4$ & $C_8$ & $C_{16}$ & completions\\",
        r"\midrule",
    ]
    for row in rows:
        values = " & ".join(formatted_values(row))
        lines.append(f"{row['orbit']} & {values}" + r"\\")
    total_values = " & ".join(f"{totals[field]:,}" for field in FIELDS)
    lines.extend(
        [
            r"\midrule",
            f"Total & {total_values}" + r"\\",
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
        ]
    )
    return "\n".join(lines) + "\n"


def triangle_orbit_table(entries: list[dict[str, object]]) -> str:
    totals = {
        field: sum(int(entry[field]) for entry in entries)
        for field in CERTIFICATE_FIELDS
    }
    lines = [
        r"\begin{table}[ht]",
        r"\centering",
        r"\small",
        r"\caption{Universal cap-$29$ triangle-rooted search, split by root orbit.}",
        r"\label{tab:triangle-orbits}",
        r"\begin{tabular}{rrrrrrr}",
        r"\toprule",
        r"orbit & states & attempted & structural & $C_8$ & $C_{16}$ & completions\\",
        r"\midrule",
    ]
    for entry in entries:
        values = " & ".join(
            f"{int(entry[field]):,}" for field in CERTIFICATE_FIELDS
        )
        lines.append(f"{int(entry['orbit'])} & {values}" + r"\\")
    total_values = " & ".join(
        f"{totals[field]:,}" for field in CERTIFICATE_FIELDS
    )
    lines.extend(
        [
            r"\midrule",
            f"Total & {total_values}" + r"\\",
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
        ]
    )
    return "\n".join(lines) + "\n"


def triangle_kernel_table(entries: list[dict[str, object]]) -> str:
    compatible_graph = {
        1: r"$3K_{1,2}$",
        2: r"$K_2\sqcup2K_{1,2}$",
        3: r"$K_2\sqcup2K_{1,2}$",
        4: r"$2K_{1,2}$",
        5: r"$K_{1,2}$",
        6: r"$K_{1,2}$",
    }
    lines = [
        r"\begin{table}[ht]",
        r"\centering",
        r"\small",
        r"\caption{The six color-preserving classes among the deepest triangle-rooted states.}",
        r"\label{tab:triangle-kernels}",
        r"\begin{tabular}{rrrr}",
        r"\toprule",
        r"kernel & labelled occurrences & deficient points & compatible-pair graph\\",
        r"\midrule",
    ]
    for entry in entries:
        klass = int(entry["class"])
        lines.append(
            f"$K_{klass}$ & {int(entry['size']):,} & "
            f"{len(entry['unfinished'])} & {compatible_graph[klass]}" + r"\\"
        )
    lines.extend(
        [
            r"\midrule",
            r"Total & 337 & &\\",
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    result_root = ROOT / "research/results"
    table_root = ROOT / "paper/tables"
    table_root.mkdir(parents=True, exist_ok=True)

    frontier_rows = read_rows(result_root / "frontier_counts.tsv")
    orbit_rows = read_rows(result_root / "v29_orbits.tsv")
    triangle_metadata = json.loads(
        (
            ROOT
            / "research/certificates/eg58_triangle_universal_two_streams.json"
        ).read_text(encoding="utf-8")
    )
    triangle_entries = list(triangle_metadata["entries"])
    triangle_kernels = json.loads(
        (result_root / "triangle_kernel_classes.json").read_text(
            encoding="utf-8"
        )
    )
    if [int(row["v"]) for row in frontier_rows] != list(range(7, 30)):
        raise ValueError("frontier table must contain exactly v=7,...,29")
    if [row["orbit"] for row in orbit_rows] != ["1", "2", "3"]:
        raise ValueError("orbit table must contain exactly root orbits 1,2,3")
    if [int(entry["orbit"]) for entry in triangle_entries] != [1, 2]:
        raise ValueError("triangle table must contain exactly root orbits 1,2")
    if [int(entry["class"]) for entry in triangle_kernels] != list(
        range(1, 7)
    ):
        raise ValueError("triangle kernel table must contain exactly K1,...,K6")

    (table_root / "frontier_counts.tex").write_text(
        frontier_table(frontier_rows), encoding="utf-8"
    )
    (table_root / "v29_orbits.tex").write_text(
        orbit_table(orbit_rows), encoding="utf-8"
    )
    (table_root / "triangle_orbits.tex").write_text(
        triangle_orbit_table(triangle_entries), encoding="utf-8"
    )
    (table_root / "triangle_kernels.tex").write_text(
        triangle_kernel_table(triangle_kernels), encoding="utf-8"
    )
    print("WROTE: paper tables from research/results primary TSV files.")


if __name__ == "__main__":
    main()
