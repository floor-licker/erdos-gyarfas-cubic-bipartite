# Reproduction

## Requirements

- Python 3.11 or newer;
- a C++17 compiler;
- GNU Make;
- NetworkX 3.6.1 for positive controls; and
- pdfTeX for the paper build.

Install the Python dependency with:

```sh
python3 -m pip install -r requirements.txt
```

The retained run used a 10-core Apple M5 MacBook Pro with 16 GB RAM,
macOS 26.4, Apple Clang 21.0.0, Python 3.11.8, nauty 2.9.3, and
TeX Live 2025. Exact versions are recorded in `environment/versions.txt`.
All search decisions use exact integer, set, array, and bit-mask operations.

First verify the tracked-file manifest:

```sh
make verify-manifest
```

## Certificate

```sh
make verify-certificate
```

This compiles only `research/src/verify_eg_certificate.cpp` and verifies the
66 theorem-supporting members of
`research/certificates/eg58_witness_certificates.zip`. It checks every raw
digest, regenerates the search schedule, validates each positive \(C_8\) or
\(C_{16}\) witness, reconciles counters with
`research/results/frontier_counts.tsv`, and requires zero completions. It
also checks the side-16 compatibility stream and seven tampering cases.

The checker does not invoke a production search or trust a stored negative
cycle assertion. The independent byte specification is
`research/certificates/FORMAT.md`.

To regenerate the deterministic bundle:

```sh
make generate-certificates
```

## Search cross-checks

```sh
make verify-full
make verify-transcripts
make verify-v29
```

`verify-full` runs the two principal implementations for every
\(v=7,\ldots,29\). `verify-transcripts` compares their deterministic
decision-level hashes, including the third implementation where available.
`verify-v29` compares all three programs in every frontier root orbit.
Expected counters and hashes are in:

- `research/results/frontier_counts.tsv`;
- `research/results/transcript_hashes.tsv`; and
- `research/results/v29_orbits.tsv`.

Every retained completion count is zero.

## Additional checks

```sh
make verify-positive
make verify-genbg
make verify-unreduced
```

- `verify-positive` runs the Johnson-graph, subset-DP, and normalized
  permutation-pair cycle checks.
- `verify-genbg` compares exact color-preserving canonical graph sets for
  \(v=7,\ldots,13\). It uses `NAUTY_BIN_DIR` when supplied; otherwise it
  downloads nauty 2.9.3 and verifies the pinned archive digest before
  building.
- `verify-unreduced` reproduces the superseded unreduced-root counters. They
  are diagnostic only.

Run every check and rebuild the paper with:

```sh
make verify-all
```

Build or audit the paper separately with:

```sh
make paper
make validate-paper-data
```

The data audit checks all displayed exhaustive-search counters against the
retained tables and logs.

## Approximate resource use

| Command | Wall time | Peak RSS |
| --- | ---: | ---: |
| `make verify-certificate` | 16 s | 127 MiB |
| `make verify-v29` | 62 s | 141 MiB |
| `make verify-full` | 99 s | 114 MiB |
| `make verify-transcripts` | 153 s | 117 MiB |
| `make generate-certificates` | 78 s | 127 MiB |
| `make verify-positive` | 6 s | 39 MiB |
| `make verify-genbg` | 58 s | 524 MiB |
| `make verify-unreduced` | 78 s | 111 MiB |

Times are from the reference machine and have no logical role.
