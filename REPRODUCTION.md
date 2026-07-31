# Reproduction

## Requirements

- Python 3.11 or newer;
- a C++17 compiler;
- GNU Make;
- NetworkX 3.6.1 for positive controls; and
- pdfTeX with PGF/TikZ for the paper build.

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

In a Git checkout, this also requires the manifest file set to equal
`git ls-files`. In a downloaded source archive, it validates every
manifest-listed path and digest without requiring `.git`.

## Primary triangle-rooted certificate

```sh
make verify-certificate
```

This verifies the two members of
`research/certificates/eg58_triangle_universal_two_streams.zip`. The checker
uses 29 as a cap and rejects a completed configuration immediately, including
one using fewer than 29 points. It therefore excludes every side size at most
29 with two streams.

The command also:

- regenerates both raw streams byte-for-byte;
- verifies the 45 conventional per-side triangle streams;
- reconstructs exactly 337 depth-19 states;
- checks explicit point and block bijections to six kernel representatives;
- checks that each kernel's compatible-pair graph is triangle-free; and
- exercises malformed and tampered certificate cases.

The independent byte specification is
`research/certificates/TRIANGLE_FORMAT.md`.

To rerun both triangle-rooted search implementations for every
$v=7,\ldots,29$, compare all counters and transcript hashes, and perform
every certificate and kernel check:

```sh
make verify-triangle
```

## Stronger arbitrary-root certificate

The earlier computation excludes the larger class without assuming a Berge
triangle. Verify its 66 theorem-supporting streams with:

```sh
make verify-arbitrary-certificate
```

This compiles `research/src/verify_eg_certificate.cpp`, verifies
`research/certificates/eg58_witness_certificates.zip`, reconciles its counters
with `research/results/frontier_counts.tsv`, and runs its tampering tests. Its
byte specification is `research/certificates/FORMAT.md`.

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
$v=7,\ldots,29$. `verify-transcripts` compares their deterministic
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
  $v=7,\ldots,13$. It uses `NAUTY_BIN_DIR` when supplied; otherwise it
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
| `make verify-certificate` | 6 s | 127 MiB |
| `make verify-triangle-search` | 37 s | 117 MiB |
| `make verify-triangle` | 43 s | 127 MiB |
| `make verify-arbitrary-certificate` | 16 s | 127 MiB |
| `make verify-v29` | 62 s | 141 MiB |
| `make verify-full` | 99 s | 114 MiB |
| `make verify-transcripts` | 153 s | 117 MiB |
| `make generate-certificates` | 78 s | 127 MiB |
| `make verify-positive` | 6 s | 39 MiB |
| `make verify-genbg` | 58 s | 524 MiB |
| `make verify-unreduced` | 78 s | 111 MiB |

Times are from the reference machine and have no logical role.
