# Contributing

Audit reports, independent reproductions, and narrowly scoped corrections
are welcome. The highest-value contributions are:

- an independent audit of Proposition 10's root normalization and
  restricted-growth completeness argument;
- a full-frontier reproduction using a substantially different generator or
  encoding;
- an independent implementation of the certificate format in
  `research/certificates/FORMAT.md`; and
- reproducible extensions of the `genbg` overlap.

Please open an issue before undertaking a change that alters the theorem
statement, certificate format, or primary result tables. A pull request
should identify the claim it affects, include a deterministic reproduction
command, and update expected outputs and checksums where applicable.

Do not edit generated tables or primary result files by hand. Regenerate
them from the source command documented in `REPRODUCTION.md`.

Use Conventional Commits for commit and pull-request titles, for example
`fix: correct certificate metadata`.

By contributing code, you agree that it may be distributed under the MIT
License. Documentation contributions are accepted under CC BY 4.0, and
machine-readable result contributions under CC0 1.0, unless a pull request
states otherwise and is accepted explicitly.
