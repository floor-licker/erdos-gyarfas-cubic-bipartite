# Reproduction record

The public-review snapshot was reproduced on 29 July 2026 on a 10-core Apple
M5 MacBook Pro with 16 GB RAM, macOS 26.4 (Darwin 25.4.0), Apple Clang
21.0.0, and Python 3.11.8.

The principal search programs require a C++17 compiler. The orchestration is
implemented in Python and does not require Bash. The positive-control command
requires NetworkX; the generator comparison either uses `genbg` and `labelg`
from `NAUTY_BIN_DIR` or downloads and builds the pinned nauty release.

From the repository root, verify the tracked-file manifest with:

```sh
make verify-manifest
```

## Full side-size range

```sh
make verify-full
```

Expected final line:

```text
VERIFIED: full-range integer counters agree.
```

The script compiles the two principal programs for every side size
`v=7,...,29`, requires their six integer counters to agree, and compares the
result with `research/results/frontier_counts.tsv`. It writes the retained
tables to `research/logs/full_range/`; every completion count is zero.

## Full-range static witness certificate

```sh
make verify-certificate
```

Expected output:

```text
VERIFIED: 66 witness streams exhaust every normalized root orbit for v=7,...,29.
VERIFIED: all proof-stream totals match frontier_counts.tsv and all completion counts are zero.
VERIFIED: the compatibility stream reproduces the former v=16 C4/C8 certificate counters.
VERIFIED: malformed, truncated, trailing, counter-tampered, C8-witness-tampered, C16-witness-tampered, and unexpected-completion streams are rejected.
```

The command compiles only
`research/src/verify_eg_certificate.cpp`. It then checks every member of
`research/certificates/eg58_witness_certificates.zip`, verifies each raw
SHA-256 digest against
`research/certificates/eg58_witness_certificates.json`, and requires the
per-side-size sums to equal the primary counter table. The 66 proof streams
cover the one available root orbit at `v=7`, two at `v=8`, and all three at
each `v=9,...,29`. The additional compatibility stream semantically
reproduces the former text certificate at `v=16`: 1,207 states, 30,152
candidates, 4,172 structural rejections, 24,774 `C8` rejections, 1,206
expansions, and zero solutions.

Each raw stream begins with the eight bytes `EG58CER1`, followed by the side
size, root orbit, enabled-cycle flags, one reserved byte, and six
little-endian 64-bit counters. The checker reconstructs every partial block
family and candidate in deterministic depth-first restricted-growth order.
A structurally invalid candidate consumes no proof byte. Every other
candidate has one of three records:

- `0x08`, followed by three old-block indices witnessing a `C8`;
- `0x10`, followed by an endpoint-pair code and seven old-block indices
  witnessing the old simple length-14 path closed into a `C16`; or
- `0x20`, directing the checker to expand that candidate recursively.

The checker validates only positive cycle witnesses. It does not need to
trust a negative cycle-oracle answer: expanding an extra forbidden branch is
conservative, and the checker fails if any expanded branch reaches a
complete configuration. It also rejects an invalid witness, a truncated
stream, an unknown record, inconsistent header counters, trailing bytes, or
an expanded branch reaching a completed configuration.
Thus the certificate removes the production generators and both production
cycle oracles from the computational trust base. It does not remove the
mathematical obligation to audit the root normalization and
restricted-growth completeness argument.

To rebuild the deterministic ZIP and its metadata:

```sh
make generate-certificates
```

This recompiles the generator at every side size, generates and immediately
checks every raw stream, checks all totals, and packages the streams with
fixed ZIP metadata and DEFLATE level 9.

## Three-implementation frontier

```sh
make verify-v29
```

Expected summary:

```text
VERIFIED: all three implementations have identical counters and search-transcript hashes for all v=29 root orbits.
1 (3286, 286790, 22001, 141678, 119826, 0)
2 (23607, 2167611, 148504, 1489941, 505560, 0)
3 (504300, 48634099, 3352944, 32467272, 12309584, 0)
```

The script runs all three implementations in every root orbit at `v=29`,
checks counters and transcript hashes against
`research/results/v29_orbits.tsv`. Its logs are retained in
`research/logs/v29/`. The static certificate has its own separate command
above.

Both meet-in-the-middle programs use dynamically sized vectors and retain
every enumerated half-path; there is no fixed global or per-midpoint
capacity.

## Decision-level transcript comparison

```sh
make verify-transcripts
```

The script first tests the portable SHA-256 implementation against the
standard empty-string and `abc` vectors. It then compares the two principal
implementations for `v=7,8` and all three implementations for
`v=9,...,29`, separately for each root orbit. It also requires each
side-size sum to equal `research/results/frontier_counts.tsv`. The expected
final line is:

```text
VERIFIED: wrote 69 matching transcript hashes to research/results/transcript_hashes.tsv
```

The versioned transcript begins with the bytes `E G T R`, format version 1,
the side size, and the root orbit. In deterministic depth-first order it
then records:

- each recursive state and its ordered block family;
- each candidate block and its outcome: structural, `C8`, or `C16`
  rejection, or accepted augmentation;
- each terminal event; and
- each recursive return.

Each executable checks that state and candidate event counts equal the
ordinary search counters. The complete byte format is implemented in
`research/src/transcript_sha256.hpp`; its self-test is
`research/src/test_transcript_sha256.cpp`. Digest agreement is stronger than
aggregate-counter agreement, but is not a static proof certificate and does
not independently validate the shared completeness argument.

## Positive controls

```sh
make verify-positive
```

This reruns the NetworkX elementary-cycle check and the exact subset-state
dynamic program on all 128 retained symmetric `19_3` configurations, then
runs the normalized permutation-pair check on the first configuration. It
compares the substantive JSON output with the files in `research/results/`.
The recorded NetworkX run used version 3.6.1; the verifier reports but
deliberately excludes the installed package-version string from the semantic
comparison.

## Set-level nauty comparison

```sh
make verify-genbg
```

Expected final line:

```text
VERIFIED: restricted-growth and genbg canonical C4-free sets agree for v=7,...,13.
```

The script compares actual color-preserving canonical graph6 sets generated
by the restricted-growth program and nauty 2.9.3 `genbg`. The common counts
are `1, 1, 3, 10, 31, 229, 2036`. The graph sets and their SHA-256 hashes are
in `research/results/genbg_crosscheck/`. Unless `NAUTY_BIN_DIR` supplies
existing `genbg` and `labelg` executables, the script downloads the official
nauty 2.9.3 archive and verifies its pinned hash before building it.

## Historical generation-mode check

```sh
make verify-unreduced
```

Expected final line:

```text
VERIFIED: --unreduced-root reproduces every v=7,...,28 historical counter.
```

The larger counters from the initial research package came from starting
directly with the fixed root star, before quotienting the first additional
block through point 1 by the root stabilizer. Both principal implementations
reproduce the canonical historical table in
`research/results/unreduced_root_counts.tsv`. This diagnostic mode is not
primary evidence for the theorem.

## Report build and data audit

```sh
make paper
make validate-paper-data
```

The paper build regenerates both LaTeX tables from their primary TSV files
before compiling
`paper/Tranquilli_2026_Erdos-Gyarfas_60-Vertex_Lower_Bound.pdf`. The data
audit cross-checks the paper tables, retained full-range and frontier logs,
transcript table, historical diagnostic table, and stored `genbg` sets.

## Approximate resources

| Command | Wall time | Peak RSS |
| --- | ---: | ---: |
| `make verify-v29` | 62 s | 141 MiB |
| `make verify-full` | 99 s | 114 MiB |
| `make verify-transcripts` | 153 s | 117 MiB |
| `make verify-certificate` | 16 s | 127 MiB |
| `make generate-certificates` | 78 s | 127 MiB |
| `make verify-positive` | 6 s | 39 MiB |
| `make verify-genbg` | 58 s | 524 MiB |
| `make verify-unreduced` | 78 s | 111 MiB |

The `genbg` measurement includes a clean nauty download, configuration, and
build. Times vary by machine and have no logical role.
