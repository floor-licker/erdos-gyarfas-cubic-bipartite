# Certificate tampering tests

`test_tampering.py` extracts three genuine members from the release bundle,
requires each to verify, and then requires nonzero checker exits for:

1. an unknown/malformed record;
2. a truncated stream;
3. trailing data;
4. a tampered header counter;
5. a tampered \(C_8\) witness;
6. a tampered \(C_{16}\) witness; and
7. a proof that expands to an unexpected completed configuration.

The \(C_{16}\) test locates a reachable `0x10` record in the small
`v=19, orbit=1` member by requiring the checker to identify the deliberately
invalid endpoint code. The unexpected-completion test replaces the
side-size-7 rejection with conservative expansions; the checker must stop as
soon as a complete configuration is reached.

These mutations are generated in a temporary directory so large corrupt
binary fixtures are not committed.
