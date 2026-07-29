#!/usr/bin/env python3
"""Independent exact cycle verifier using subset-state transfer dynamic programming.

For a fixed start vertex s and target length ell, the DP state is
(current vertex, visited-vertex bitset, number of used edges).  Restricting internal
vertices to labels >= s assigns every simple cycle to its unique minimum vertex.
This is algorithmically independent of the generator's incremental new-block oracle.
"""
from __future__ import annotations

import argparse
import json
from functools import lru_cache
from pathlib import Path

from verify_configurations_johnson import incidence_graph, read_configurations, verify_graph


def has_simple_cycle_of_length(graph, length: int) -> bool:
    n = graph.number_of_nodes()
    adjacency = [tuple(sorted(graph.neighbors(v))) for v in range(n)]

    for start in range(n):
        start_bit = 1 << start

        @lru_cache(maxsize=None)
        def extend(current: int, visited: int, used_edges: int) -> bool:
            if used_edges == length - 1:
                return start in adjacency[current]
            # Even with maximum one new vertex per edge, enough unused vertices must remain.
            for nxt in adjacency[current]:
                if nxt == start:
                    continue
                # Every cycle is handled only at its minimum-labelled vertex.
                if nxt < start:
                    continue
                bit = 1 << nxt
                if visited & bit:
                    continue
                if extend(nxt, visited | bit, used_edges + 1):
                    return True
            return False

        for first in adjacency[start]:
            if first < start:
                continue
            if extend(first, start_bit | (1 << first), 1):
                return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    configurations = read_configurations(args.input)
    if args.limit:
        configurations = configurations[: args.limit]

    records = []
    for index, blocks in enumerate(configurations, 1):
        graph = incidence_graph(blocks)
        verify_graph(graph, len(blocks))
        result = {length: has_simple_cycle_of_length(graph, length)
                  for length in (4, 8, 16)}
        if result != {4: False, 8: False, 16: True}:
            raise AssertionError(f"configuration {index}: {result}")
        records.append({"configuration": index, "v": len(blocks),
                        "has_C4": result[4], "has_C8": result[8],
                        "has_C16": result[16]})

    summary = {
        "method": "exact subset-state transfer DP",
        "configurations_verified": len(records),
        "all_avoid_C4_C8": True,
        "all_contain_C16": True,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.json:
        args.json.write_text(json.dumps({"summary": summary, "records": records}, indent=2,
                                        sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
