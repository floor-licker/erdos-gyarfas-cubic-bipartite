#!/usr/bin/env python3
"""Convert a cubic bipartite incidence graph to three normalized matchings.

The script independently checks simplicity, connectedness, pairwise alternating
cycles, and arbitrary C4/C8/C16 cycles by reduced color-word simulation.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Iterable, Sequence

import networkx as nx

from verify_configurations_johnson import incidence_graph, read_configurations, verify_graph
from verify_configurations_subset_dp import has_simple_cycle_of_length


def three_perfect_matchings(graph: nx.Graph, v: int) -> list[list[int]]:
    work = graph.copy()
    maps: list[list[int]] = []
    left = set(range(v))
    for color in range(3):
        matching = nx.algorithms.bipartite.maximum_matching(work, top_nodes=left)
        if any(x not in matching for x in left):
            raise AssertionError(f"color {color}: no perfect matching")
        mapping = [matching[x] - v for x in range(v)]
        if sorted(mapping) != list(range(v)):
            raise AssertionError("matching is not bijective")
        maps.append(mapping)
        work.remove_edges_from((x, matching[x]) for x in range(v))
    if work.number_of_edges() != 0:
        raise AssertionError("matchings do not partition the edges")
    return maps


def inverse(permutation: Sequence[int]) -> list[int]:
    out = [-1] * len(permutation)
    for x, y in enumerate(permutation):
        out[y] = x
    if any(x < 0 for x in out):
        raise ValueError("not a permutation")
    return out


def compose(left: Sequence[int], right: Sequence[int]) -> list[int]:
    """Return left o right."""
    return [left[right[x]] for x in range(len(left))]


def normalize(maps: Sequence[Sequence[int]]) -> list[list[int]]:
    # Relabel a right vertex r by the unique x with pi_0(x)=r.
    relabel_right = inverse(maps[0])
    normalized = [compose(relabel_right, p) for p in maps]
    if normalized[0] != list(range(len(normalized[0]))):
        raise AssertionError("normalization failed")
    return normalized


def cycle_type(permutation: Sequence[int]) -> list[int]:
    seen = [False] * len(permutation)
    lengths: list[int] = []
    for start in range(len(permutation)):
        if seen[start]:
            continue
        cur = start
        length = 0
        while not seen[cur]:
            seen[cur] = True
            cur = permutation[cur]
            length += 1
        lengths.append(length)
    return sorted(lengths, reverse=True)


def is_transitive(sigma: Sequence[int], tau: Sequence[int]) -> bool:
    generators = [list(sigma), list(tau), inverse(sigma), inverse(tau)]
    orbit = {0}
    frontier = [0]
    while frontier:
        x = frontier.pop()
        for g in generators:
            y = g[x]
            if y not in orbit:
                orbit.add(y)
                frontier.append(y)
    return len(orbit) == len(sigma)


def reduced_color_words(length: int) -> Iterable[tuple[int, ...]]:
    for first in range(3):
        word = [first]

        def extend() -> Iterable[tuple[int, ...]]:
            if len(word) == length:
                if word[-1] != word[0]:
                    yield tuple(word)
                return
            for color in range(3):
                if color == word[-1]:
                    continue
                word.append(color)
                yield from extend()
                word.pop()

        yield from extend()


def simulate_word(permutations: Sequence[Sequence[int]],
                  inverses: Sequence[Sequence[int]], start: int,
                  word: Sequence[int]) -> list[tuple[int, int]] | None:
    # side 0 = left, side 1 = right in normalized labels.
    current = (0, start)
    path = [current]
    seen = {current}
    for index, color in enumerate(word):
        side, label = current
        if side == 0:
            nxt = (1, permutations[color][label])
        else:
            nxt = (0, inverses[color][label])
        final = index + 1 == len(word)
        if final:
            if nxt == path[0]:
                return path + [nxt]
            return None
        if nxt in seen:
            return None
        seen.add(nxt)
        path.append(nxt)
        current = nxt
    return None


def find_cycle_word(permutations: Sequence[Sequence[int]], length: int):
    invs = [inverse(p) for p in permutations]
    for word in reduced_color_words(length):
        for start in range(len(permutations[0])):
            path = simulate_word(permutations, invs, start, word)
            if path is not None:
                return {"word": list(word), "start_left": start,
                        "normalized_bipartite_path": [list(x) for x in path]}
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--index", type=int, default=1)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    configurations = read_configurations(args.input)
    blocks = configurations[args.index - 1]
    v = len(blocks)
    graph = incidence_graph(blocks)
    verify_graph(graph, v)

    raw_maps = three_perfect_matchings(graph, v)
    permutations = normalize(raw_maps)
    identity, sigma, tau = permutations
    sigma_inv_tau = compose(inverse(sigma), tau)

    simplicity = all(len({identity[i], sigma[i], tau[i]}) == 3 for i in range(v))
    transitive = is_transitive(sigma, tau)
    if not simplicity or not transitive:
        raise AssertionError("normalized pair fails graph conditions")

    graph_dp = {length: has_simple_cycle_of_length(graph, length)
                for length in (4, 8, 16)}
    word_witnesses = {length: find_cycle_word(permutations, length)
                      for length in (4, 8, 16)}
    word_exists = {length: word_witnesses[length] is not None
                   for length in (4, 8, 16)}
    if graph_dp != word_exists:
        raise AssertionError(f"graph/word disagreement: {graph_dp} vs {word_exists}")

    report = {
        "configuration": args.index,
        "v": v,
        "normalized_matchings": {
            "pi0": identity,
            "sigma": sigma,
            "tau": tau,
        },
        "simple": simplicity,
        "connected_via_transitive_group": transitive,
        "pairwise_permutation_cycle_types": {
            "sigma": cycle_type(sigma),
            "tau": cycle_type(tau),
            "sigma_inverse_tau": cycle_type(sigma_inv_tau),
        },
        "graph_subset_dp": graph_dp,
        "color_word_exists": word_exists,
        "witnesses": word_witnesses,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.json:
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")


if __name__ == "__main__":
    main()
