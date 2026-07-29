# Erdős–Gyárfás conjecture for cubic bipartite graphs

This repository is the reproducibility artifact for the following
computer-assisted theorem:

> Every simple cubic bipartite graph on at most 58 vertices contains a
> simple cycle of length 4, 8, or 16.

Consequently, any cubic-bipartite counterexample to the Erdős–Gyárfás
conjecture has at least 60 vertices. This does not exclude a counterexample
on 60 vertices or prove the full conjecture.

## Verify

With Python 3 and a C++17 compiler:

```sh
make verify-certificate
```

This checks all 66 normalized root-orbit witness streams for side sizes
\(v=7,\ldots,29\), their digests and counters, and the certificate-tampering
tests. It takes about 16 seconds on the reference machine.

| Claim or check | Status |
| --- | --- |
| Orders through 58 contain \(C_4\), \(C_8\), or \(C_{16}\) | Exhaustive computation and full-range witness certificate |
| Counterexample lower bound | 60 vertices |
| Production implementations | Matching counters and decision transcripts |
| Different-generator overlap | Exact `genbg` set agreement through \(v=13\) |
| Order 60 | Not claimed |

Certificate verification still relies on the mathematical root normalization
and restricted-growth coverage proof (Proposition 10). A focused audit guide
is in
[`research/docs/completeness_argument.md`](research/docs/completeness_argument.md).

## Reproduce

| Command | Purpose |
| --- | --- |
| `make verify-certificate` | Verify the static certificate |
| `make reproduce-search` | Rerun the two principal searches and transcript comparison |
| `make verify-v29` | Compare all three implementations at the frontier |
| `make verify-genbg` | Compare canonical graph sets through \(v=13\) |
| `make verify-all` | Run the complete audit and rebuild the paper |

See [`REPRODUCTION.md`](REPRODUCTION.md) for requirements, expected behavior,
and resource use.

## Contents

- `paper/` — LaTeX source and
  [PDF](paper/Tranquilli_2026_Erdos-Gyarfas_60-Vertex_Lower_Bound.pdf).
- `research/src/` — C++ search, certificate, and checking programs.
- `research/scripts/` — Python reproduction and validation commands.
- `research/certificates/` — certificate bundle, metadata, and
  [format specification](research/certificates/FORMAT.md).
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

Citation metadata is in [`CITATION.cff`](CITATION.cff). Until the immutable
`v1.0.0` release is archived, cite the full `main` commit used.
