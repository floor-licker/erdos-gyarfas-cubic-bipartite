# Research and AI provenance

This document records the material human and AI contributions to the
research artifact and manuscript. It is an activity-level account: the
earliest development record does not support reliable line-by-line
attribution within the original source package.

## Author and project direction

Julius Tranquilli selected the problem and claimed result, directed the scope
of the project, supplied the original dated research package for audit, and
is the sole author of the report. He accepts responsibility for the claims,
code, computations, citations, and final text.

The reported programs were executed or reproduced in Julius Tranquilli's
local workspace. In many cases, commands were invoked through an AI system's
local tool interface. The retained source, deterministic outputs, logs,
cross-checks, and mathematical arguments—not statements made by an AI
system—constitute the evidence for the result.

## Initial research phase: OpenAI ChatGPT

OpenAI ChatGPT materially assisted the initial research process. Its
contributions included:

- proposing computational and structural approaches;
- helping develop portions of the incidence-based search and verification
  code;
- running and interpreting computations in the author's workspace;
- drafting preliminary mathematical arguments and the proof architecture;
- helping interpret the computational result; and
- conducting an initial literature audit.

This assistance predates the later artifact audit. The original dated package
does not contain a complete turn-by-turn development transcript, so a more
granular division between human-written and ChatGPT-generated lines in those
early files cannot be reconstructed reliably.

## Audit and manuscript phase: OpenAI Codex

OpenAI Codex subsequently assisted with:

- unpacking, organizing, and auditing the supplied research artifact;
- rebuilding programs, reproducing computations, and checking manuscript
  tables against primary results;
- expanding and editing the incidence, root-orbit, and restricted-growth
  completeness arguments;
- auditing and qualifying the literature comparison;
- adding and running the independent nauty `genbg` canonical-set comparison;
- identifying and exactly reproducing the historical unreduced-root
  generation mode;
- replacing fixed meet-in-the-middle half-path stores with dynamically sized
  vectors and rerunning the full range;
- implementing deterministic SHA-256 search-transcript hashes and comparing
  every supported side size and root orbit across the implementations;
- designing and implementing the full-range witness-certificate generator,
  the separately written streaming checker, and the deterministic
  certificate bundle;
- drafting and editing the LaTeX report, documentation, scripts, and release
  materials;
- preparing the clean public-repository structure, certificate-format
  specification, tamper-test suite, CI workflows, and release manifest.

Codex generated or modified portions of the manuscript and auxiliary source
code during this phase and invoked the reported local reproduction commands.

## Verification and responsibility

The AI systems are tools, not authors: they cannot accept responsibility for
the work. The artifact is designed so that the central computational claims
can be checked from source and exact outputs without relying on AI testimony.
Julius Tranquilli is responsible for making any personal checks required by
the target venue and approving the final archived version.

This disclosure should be updated if additional human or AI contributions
materially affect a later release.
