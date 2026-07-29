# Tests

- `certificate_tampering/` verifies that the genuine certificate members
  succeed and seven classes of altered stream fail.
- `positive_controls/` documents the retained known-valid configuration
  inputs exercised by `make verify-positive`.
- `expected_outputs/` records the stable final status lines used by release
  and CI checks.

Tests construct temporary altered certificate streams at runtime. Deliberate
20 MB or 500 MB corrupt copies are not committed.
