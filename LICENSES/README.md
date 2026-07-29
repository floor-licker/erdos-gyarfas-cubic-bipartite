# License map

Copyright © 2026 Julius Tranquilli.

The repository uses separate licenses because software, research data, and
the manuscript have different reuse needs:

- `research/src/`, `research/scripts/`, `research/tests/`, the root
  `Makefile`, and other executable build or validation files:
  [`LICENSE-CODE`](LICENSE-CODE), MIT.
- `research/certificates/`, `research/results/`, and retained machine
  outputs under `research/logs/`:
  [`LICENSE-DATA`](LICENSE-DATA), CC0 1.0 Universal.
- Markdown documentation outside `paper/`:
  [`LICENSE-DOCUMENTATION`](LICENSE-DOCUMENTATION), CC BY 4.0.
- `paper/`, including its LaTeX source and PDF:
  [`LICENSE-PAPER`](LICENSE-PAPER), all rights reserved unless a later
  release or publication record states otherwise.

Third-party software is not redistributed except where explicitly noted.
The `genbg` comparison downloads nauty from its authoritative distribution
site and verifies the pinned archive digest.
