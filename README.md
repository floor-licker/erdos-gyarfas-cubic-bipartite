# Erdős–Gyárfás conjecture for cubic bipartite graphs

This repository contains the paper, source code, exact outputs, and
full-range witness certificates for the following computer-assisted theorem:

> Every simple cubic bipartite graph on at most 58 vertices contains a
> simple cycle of length 4, 8, or 16.

Consequently, any cubic bipartite counterexample to the Erdős–Gyárfás
conjecture has at least 60 vertices.

This does not prove the full Erdős–Gyárfás conjecture and does not exclude a
counterexample on 60 vertices.

## Paper

- PDF:
  [`paper/Tranquilli_2026_Erdos-Gyarfas_60-Vertex_Lower_Bound.pdf`](paper/Tranquilli_2026_Erdos-Gyarfas_60-Vertex_Lower_Bound.pdf)
- LaTeX source: [`paper/main.tex`](paper/main.tex)
- Public review snapshot: branch `main`
- Planned immutable artifact: release `v1.0.0`, after its Zenodo DOI is
  reserved

## Fastest independent check

```sh
make verify-certificate
```

This compiles the separately written streaming checker and verifies all 66
witness streams covering every normalized root orbit for
\(v=7,\ldots,29\). On the reference machine this takes about 16 seconds.

| Claim | Status |
| --- | --- |
| Every cubic bipartite graph on at most \(58\) vertices has \(C_4\), \(C_8\), or \(C_{16}\) | Proved by exhaustive computation and a full-range witness certificate |
| Any cubic-bipartite counterexample has at least \(60\) vertices | Corollary |
| No counterexample exists on \(60\) vertices | Not claimed |
| The full Erdős–Gyárfás conjecture is true | Not claimed |
| Search-tree coverage follows from Proposition 10 | Mathematical completeness argument; external audit welcomed |

## Three reproduction levels

1. Verify the existing static certificate:

   ```sh
   make verify-certificate
   ```

2. Rebuild the two principal searches over \(v=7,\ldots,29\) and compare
   their decision transcripts:

   ```sh
   make reproduce-search
   ```

3. Run the complete audit, including the third implementation, tamper tests,
   the `genbg` overlap, positive controls, manifest verification, and paper
   build:

   ```sh
   make verify-all
   ```

See [`REPRODUCTION.md`](REPRODUCTION.md) for expected output, software
requirements, and approximate resource use.

## Certificate and trust boundary

The 20,545,969-byte bundle
[`research/certificates/eg58_witness_certificates.zip`](research/certificates/eg58_witness_certificates.zip)
contains one stream for each of the 66 available normalized root orbits in
the full range. Every cycle-based rejection carries either an explicit
\(C_8\) witness or a simple old length-14 path witnessing the newly closed
\(C_{16}\). The checker regenerates all states and candidate blocks, checks
the witnesses, reconciles counters, rejects malformed or trailing data, and
fails if an expanded branch reaches a completed configuration.

The certificate removes the production generators and cycle oracles from
the computational trust base. It does not replace the mathematical
root-normalization and restricted-growth coverage argument in Proposition 10
of the paper. That remaining boundary is documented in
[`research/docs/completeness_argument.md`](research/docs/completeness_argument.md).

## Repository map

- `paper/` — manuscript source, generated tables, and circulation PDF.
- `research/src/` — search programs, certificate generator and checker, and
  positive-control implementations.
- `research/scripts/` — Python reproduction, validation, and packaging
  commands.
- `research/certificates/` — the certificate bundle, metadata, checksum, and
  format documentation.
- `research/results/` — primary counters, transcript hashes, canonical graph
  sets, and positive-control outputs.
- `research/logs/` — retained full-range, frontier, and certificate logs.
- `research/tests/` — certificate-tampering and positive-control tests.
- `research/docs/` — claim ledger, proof audit, environment, and known
  limitations.
- `research/archive/` — clearly marked superseded and diagnostic material.
- `environment/` — recorded tool versions and third-party checksums.

All retained project orchestration is Python; the exact search and
certificate programs are C++17. The Makefile is only a short command index.
There are no project-specific Bash scripts.

## Provenance and responsibility

Julius Tranquilli is the sole author of the paper. OpenAI ChatGPT and OpenAI
Codex materially assisted the research, implementation, audit, and
manuscript preparation. The detailed activity-level disclosure is in
[`PROVENANCE.md`](PROVENANCE.md). The retained source, outputs, certificates,
and mathematical arguments—not an AI assertion—are the evidence for the
result.

## Licensing

- Code is available under the MIT License.
- Certificates and primary machine-readable results are dedicated under
  CC0 1.0 Universal.
- Repository documentation is available under CC BY 4.0.
- The paper remains copyright Julius Tranquilli; see
  [`LICENSES/LICENSE-PAPER`](LICENSES/LICENSE-PAPER).

The scope of each license is recorded in [`LICENSES/README.md`](LICENSES/README.md).

## Citation

Use [`CITATION.cff`](CITATION.cff) for repository metadata. Until `v1.0.0`
is archived, cite the full `main` commit used. For mathematical claims, cite
the paper rather than only the software repository.
