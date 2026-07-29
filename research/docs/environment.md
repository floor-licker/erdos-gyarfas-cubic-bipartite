# Reproduction environment

The retained release computations were reproduced on 29 July 2026 using:

- 10-core Apple M5 MacBook Pro;
- 16 GB RAM;
- macOS 26.4, Darwin 25.4.0, arm64;
- Apple Clang 21.0.0;
- Python 3.11.8;
- NetworkX 3.6.1 for the Johnson-graph positive control;
- nauty 2.9.3 for the `genbg` comparison; and
- pdfTeX 1.40.27 from TeX Live 2025 for the public-repository paper build.

Exact correctness does not depend on timing or floating-point behavior. The
searches and certificate checks use integer, array, set, and bit-mask
operations. `REPRODUCTION.md` lists approximate wall time and peak memory.

The Python scripts are intended to remain compatible with current Python 3
releases. GitHub Actions provides Linux checks in addition to the recorded
macOS reproduction.
