#!/usr/bin/env python3
"""Generate the manuscript's exhaustive-search tables from primary TSV data."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIELDS = ("states", "attempted", "pair", "c8", "c16", "completions")


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


def main() -> None:
    result_root = ROOT / "research/results"
    table_root = ROOT / "paper/tables"
    table_root.mkdir(parents=True, exist_ok=True)

    frontier_rows = read_rows(result_root / "frontier_counts.tsv")
    orbit_rows = read_rows(result_root / "v29_orbits.tsv")
    if [int(row["v"]) for row in frontier_rows] != list(range(7, 30)):
        raise ValueError("frontier table must contain exactly v=7,...,29")
    if [row["orbit"] for row in orbit_rows] != ["1", "2", "3"]:
        raise ValueError("orbit table must contain exactly root orbits 1,2,3")

    (table_root / "frontier_counts.tex").write_text(
        frontier_table(frontier_rows), encoding="utf-8"
    )
    (table_root / "v29_orbits.tex").write_text(
        orbit_table(orbit_rows), encoding="utf-8"
    )
    print("WROTE: paper tables from research/results primary TSV files.")


if __name__ == "__main__":
    main()
