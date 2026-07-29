# Proof and computation audit

## Central proof chain

1. Translate a connected cubic bipartite component into a symmetric indexed
   triple system.
2. Use \(C_4\)-freeness to enforce linearity.
3. Normalize a rooted star and one of three root-stabilizer orbits.
4. Apply the restricted-growth completeness argument to cover every target.
5. Reject a new block exactly when it violates structure or closes a
   \(C_8\) or \(C_{16}\).
6. Verify, for all side sizes \(7\leq v\leq29\), that no normalized branch
   reaches a completed configuration.
7. Convert side size \(v\leq29\) to graph order at most 58; use parity to
   obtain the next possible counterexample order 60.

## Independent or partially independent checks

| Check | Independence gained | Correlation retained |
| --- | --- | --- |
| DFS path oracle vs. meet-in-the-middle oracle | Different \(C_{16}\) algorithms | Same high-level generator |
| Third frontier implementation | Separately written program | Same restricted-growth mathematics |
| Decision transcript hashes | Equality of every ordered state/candidate outcome | Same transcript format |
| Static witness checker | Does not trust production executables or negative oracle answers | Reimplements the restricted-growth schedule |
| nauty `genbg` sets through \(v=13\) | Different generator and canonicalization path | Only an overlapping finite range |
| Positive controls | Detects known cycle witnesses by different exact methods | Does not establish full search coverage |

## Static-certificate audit

Run `make verify-certificate`. Confirm that:

- exactly 66 theorem-supporting members are present;
- their raw SHA-256 digests match the metadata;
- their per-side counters sum to `frontier_counts.tsv`;
- every completion count is zero;
- the compatibility stream reproduces its stated counters; and
- every tampered stream exits nonzero for the expected reason.

An independent checker should be written from
`research/certificates/FORMAT.md`, not translated line-by-line from the
included checker.

## Highest-value next audits

1. A line-by-line external review of the root-orbit lemma and induction
   invariant in Proposition 10.
2. A full \(v=29\) reproduction using normalized permutation pairs,
   canonical augmentation, or SAT/SMS.
3. A second implementation of `EG58CER1` from the format document.
4. Extension of the exact `genbg` set overlap beyond \(v=13\), subject to
   resources.
