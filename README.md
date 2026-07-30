# Erdős–Gyárfás conjecture for cubic bipartite graphs

This repository is the reproducibility artifact for the following
computer-assisted theorem:

> Every simple cubic bipartite graph on at most 58 vertices contains a
> simple cycle of length 4, 8, or 16.

Consequently, any cubic-bipartite counterexample to the Erdős–Gyárfás
conjecture has at least 60 vertices. This does not exclude a counterexample
on 60 vertices or prove the full conjecture.

Earlier arbitrary-root review artifact:
[`v1.0.0-rc1`](https://github.com/floor-licker/erdos-gyarfas-cubic-bipartite/releases/tag/v1.0.0-rc1).

Preprint DOI:
[`10.5281/zenodo.21695513`](https://doi.org/10.5281/zenodo.21695513).

## Verify

With Python 3 and a C++17 compiler:

```sh
make verify-certificate
```

The primary proof first uses the cubic Moore bound to force a 6-cycle, then
normalizes the corresponding Berge triangle. `make verify-certificate`
checks the resulting two universal cap-29 streams, reconstructs their 337
deepest states, verifies explicit maps to six cap-29 terminal kernels, checks
the kernel obstruction, and runs tampering tests. It takes about 6 seconds
on the reference machine.

| Claim or check | Status |
| --- | --- |
| Orders through 58 contain a 4-, 8-, or 16-cycle | Triangle-rooted exhaustive computation and two-stream witness certificate |
| Counterexample lower bound | 60 vertices |
| Triangle-rooted implementations | Matching counters and decision transcripts through $v=29$ |
| Terminal classification | 337 depth-19 states map explicitly to six kernels |
| Stronger arbitrary-root check | 66-stream certificate retained |
| Different-generator overlap | Exact `genbg` set agreement through $v=13$ |
| Order 60 | Not claimed |

Certificate verification still relies on the mathematical root normalization
and restricted-growth coverage proofs. A focused audit guide for the stronger
arbitrary-root search and its triangle-rooted specialization is in
[`research/docs/completeness_argument.md`](research/docs/completeness_argument.md).

## Reproduce

| Command | Purpose |
| --- | --- |
| `make verify-certificate` | Verify the two-stream triangle proof and six kernels |
| `make verify-triangle` | Rerun both triangle searches and every triangle check |
| `make verify-arbitrary-certificate` | Verify the stronger 66-stream arbitrary-root certificate |
| `make reproduce-search` | Rerun the two principal searches and transcript comparison |
| `make verify-v29` | Compare all three implementations at the frontier |
| `make verify-genbg` | Compare canonical graph sets through $v=13$ |
| `make verify-all` | Run the complete audit and rebuild the paper |

See [`REPRODUCTION.md`](REPRODUCTION.md) for requirements, expected behavior,
and resource use.

## Contents

- `paper/` — LaTeX source and
  [PDF](paper/Tranquilli_2026_Erdos-Gyarfas_60-Vertex_Lower_Bound.pdf).
- `research/src/` — C++ search, certificate, and checking programs.
- `research/scripts/` — Python reproduction and validation commands.
- `research/certificates/` — certificate bundles, metadata, and
  [format specifications](research/certificates/README.md).
- `research/results/` and `research/logs/` — retained exact outputs.
- `research/tests/` — certificate-tampering tests.
- `research/archive/` — superseded diagnostic data, not primary evidence.
- `environment/` — recorded tool versions and third-party checksums.

## Project information

Julius Tranquilli is the sole author of the paper. OpenAI ChatGPT, OpenAI
Codex, and a custom closed-source coding/formalization harness built on a
fork of Codex materially assisted the research, implementation, audit, and
writing; see [`PROVENANCE.md`](PROVENANCE.md).

Code is MIT-licensed, machine-readable data is CC0, documentation is
CC BY 4.0, and the paper remains copyright Julius Tranquilli. See
[`LICENSES/README.md`](LICENSES/README.md).

Citation metadata is in [`CITATION.cff`](CITATION.cff). Cite the paper using
the preprint DOI above and identify the exact Git commit used. The immutable
`v1.0.0-rc1` release covers the earlier arbitrary-root artifact.
