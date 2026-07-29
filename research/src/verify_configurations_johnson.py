#!/usr/bin/env python3
"""Independent positive-control verifier using NetworkX's Johnson-style cycle generator.

Input is the restricted-growth configuration format produced by the generator.
For each symmetric v_3 configuration, the incidence graph has point vertices 0..v-1
and block vertices v..2v-1.  The verifier checks graph invariants and enumerates every
simple cycle of length at most 16 with networkx.simple_cycles.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Iterable

import networkx as nx


def read_configurations(path: Path) -> list[list[tuple[int, int, int]]]:
    records: list[list[tuple[int, int, int]]] = []
    current: list[tuple[int, int, int]] | None = None
    expected = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("SOLUTION"):
            if current is not None:
                if len(current) != expected:
                    raise ValueError(f"expected {expected} blocks, found {len(current)}")
                records.append(current)
            expected = int(line.rsplit("=", 1)[1])
            current = []
        else:
            if current is None:
                raise ValueError("block before SOLUTION header")
            block = tuple(map(int, line.split()))
            if len(block) != 3 or len(set(block)) != 3:
                raise ValueError(f"invalid block: {line}")
            current.append(tuple(sorted(block)))
    if current is not None:
        if len(current) != expected:
            raise ValueError(f"expected {expected} blocks, found {len(current)}")
        records.append(current)
    return records


def incidence_graph(blocks: list[tuple[int, int, int]]) -> nx.Graph:
    v = len(blocks)
    graph = nx.Graph()
    graph.add_nodes_from(range(2 * v))
    for j, block in enumerate(blocks):
        for point in block:
            if point < 0 or point >= v:
                raise ValueError(f"point {point} outside 0..{v-1}")
            graph.add_edge(point, v + j)
    return graph


def verify_graph(graph: nx.Graph, v: int) -> None:
    if graph.number_of_nodes() != 2 * v or graph.number_of_edges() != 3 * v:
        raise AssertionError("wrong incidence graph size")
    if any(graph.degree(x) != 3 for x in graph):
        raise AssertionError("graph is not cubic")
    if not nx.is_connected(graph):
        raise AssertionError("graph is disconnected")
    if not nx.is_bipartite(graph):
        raise AssertionError("graph is not bipartite")
    left = set(range(v))
    right = set(range(v, 2 * v))
    if any((u in left) == (w in left) for u, w in graph.edges()):
        raise AssertionError("declared bipartition is invalid")
    if set(graph) != left | right:
        raise AssertionError("wrong vertex set")


def bounded_cycle_spectrum(graph: nx.Graph, bound: int = 16) -> Counter[int]:
    counts: Counter[int] = Counter()
    # NetworkX uses an elementary-circuit algorithm for undirected graphs and emits
    # each undirected simple cycle once.  Self-loops and 2-cycles are absent here.
    for cycle in nx.simple_cycles(graph, length_bound=bound):
        if len(cycle) >= 3:
            counts[len(cycle)] += 1
    return counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--limit", type=int, default=0,
                        help="verify only this many configurations (0 = all)")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    configurations = read_configurations(args.input)
    if args.limit:
        configurations = configurations[: args.limit]
    report = []
    for index, blocks in enumerate(configurations, 1):
        graph = incidence_graph(blocks)
        verify_graph(graph, len(blocks))
        spectrum = bounded_cycle_spectrum(graph, 16)
        if spectrum[4] or spectrum[8]:
            raise AssertionError(f"configuration {index} has a C4 or C8: {spectrum}")
        if not spectrum[16]:
            raise AssertionError(f"configuration {index} has no C16")
        report.append({"configuration": index,
                       "v": len(blocks),
                       "cycle_counts_through_16": dict(sorted(spectrum.items()))})

    summary = {
        "method": "networkx.simple_cycles (Johnson-style elementary circuit enumeration)",
        "networkx_version": nx.__version__,
        "configurations_verified": len(report),
        "all_avoid_C4_C8": True,
        "all_contain_C16": True,
        "first": report[0] if report else None,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.json:
        args.json.write_text(json.dumps({"summary": summary, "records": report}, indent=2,
                                        sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
