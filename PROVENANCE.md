# Research and AI provenance

Julius Tranquilli selected the problem and claimed result, directed the
project, supplied the original research package for audit, and is the sole
author of the paper. He accepts responsibility for the final claims, code,
computations, citations, and text.

OpenAI ChatGPT materially assisted the initial research by:

- proposing computational and structural approaches;
- helping develop the incidence search and verification code;
- running and interpreting computations in the author's workspace;
- drafting preliminary arguments and the proof architecture; and
- conducting an initial literature audit.

OpenAI Codex subsequently assisted by:

- organizing and auditing the artifact and reproducing its computations;
- strengthening the mathematical presentation and literature comparison;
- implementing the `genbg` comparison, dynamic half-path storage, and
  decision-transcript hashes;
- resolving the historical unreduced-root discrepancy;
- developing the full-range witness certificates, streaming checker, and
  tamper tests; and
- drafting and editing the manuscript, documentation, and public release.

A custom closed-source coding/formalization harness built on a fork of Codex
was also used during the later research and verification work. It provided
an agentic environment for portions of the coding, mathematical
formalization, artifact audit, and tool-driven checks, including development
of the triangle-rooted universal search, two-stream certificate, and
six-kernel classification. The harness is not included in this public
artifact and is not treated as independent evidence.

On 30 July 2026, the author supplied the triangle-rooted research package
`eg_triangle_rooted_research_2026-07-30.zip`, with SHA-256
`d2cb1ec5fb755011e81fc4026e1434fa9b4a8c26458ecdd960dd0600928e9108`.
Codex checked its manifest, rebuilt and reran its verification from source,
audited the universal completion semantics, replaced its Bash wrapper with
the retained Python reproduction command, integrated the primary files, and
revised the manuscript and public documentation.

Work performed through ChatGPT, Codex, and the custom harness generated or
modified portions of code and text and invoked commands through local tool
interfaces. The early package does not preserve enough turn-level history
for reliable line-by-line attribution.

These systems are tools rather than authors and cannot accept responsibility.
The retained public source, exact outputs, certificates, cross-checks, and
mathematical arguments—not AI testimony or the closed-source harness—are the
evidence for the result. This record should be updated if later releases
receive material additional human or AI contributions.
