# Claim ledger

This ledger separates theorem claims, computational evidence, and matters
that are explicitly not claimed.

| Identifier | Claim | Evidence | Trust boundary |
| --- | --- | --- | --- |
| T1 | Every simple cubic bipartite graph on at most 58 vertices has a \(C_4\), \(C_8\), or \(C_{16}\) | Proposition 10 coverage argument; 66 accepted certificate streams; zero completed leaves | Mathematical root normalization and restricted-growth completeness |
| C1 | Any cubic-bipartite counterexample to the Erdős–Gyárfás conjecture has at least 60 vertices | T1 plus equality of the two bipartition sizes, hence even order | Ordinary graph-theoretic deduction |
| E1 | Full-range production search has zero completions for \(v=7,\ldots,29\) | `frontier_counts.tsv`; two exact implementations | Build/runtime environment |
| E2 | The production implementations make the same ordered decisions | 69 rows in `transcript_hashes.tsv` | Shared restricted-growth schedule and transcript specification |
| E3 | Every generated cycle rejection has a valid positive witness | Static certificate bundle and separately written checker | Checker implementation and certificate-format specification |
| E4 | Restricted-growth generation agrees with a different generator through \(v=13\) | Exact color-preserving canonical graph6 set comparison with nauty `genbg` | Scope ends at \(v=13\) |
| E5 | The two different \(C_{16}\) oracle formulations detect known cycles | Johnson-graph, subset-DP, and permutation-pair positive controls | Positive-control scope |
| N1 | The applicable published lower bound was 30 and the newest public computational bound was 32 | Dated literature audit in the paper and `status_of_literature.md` | Qualified by “to my knowledge” |

## Not claimed

- The theorem does not exclude a counterexample on 60 vertices.
- It does not prove the Erdős–Gyárfás conjecture for every cubic bipartite
  graph.
- It does not prove the full conjecture.
- The search is not isomorph-free; its state counters are not counts of
  nonisomorphic graphs.
- The certificate is not a proof-assistant object or an LRAT proof.
- The `genbg` overlap does not establish independent coverage at
  \(v=14,\ldots,29\).
