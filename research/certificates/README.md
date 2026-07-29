# Full-range witness certificates

The authoritative bundle is `eg58_witness_certificates.zip`:

- size: 20,545,969 bytes;
- SHA-256:
  `721221d5d59ceafcb7cfc11ce704e49f17d34586529eb315d800fee6bb1b597e`;
- format: `EG58CER1`;
- theorem-supporting streams: 66; and
- compatibility streams: 1.

The detached digest is in `eg58_witness_certificates.zip.sha256`.
`eg58_witness_certificates.json` records every member's size, digest,
counters, and role.

## Coverage

For incidence side size \(v\), the graph order is \(2v\). The bundle contains
the one available root orbit at \(v=7\), two at \(v=8\), and all three at
every \(v=9,\ldots,29\). These \(1+2+21\cdot3=66\) streams cover the full
theorem range. The extra side-16 stream is a compatibility check and is not
needed for the theorem.

Across the 66 streams, the checker reconstructs 1,160,270 states and
101,430,148 attempted candidates. It validates 66,966,950 \(C_8\) witnesses
and 26,007,625 \(C_{16}\) witnesses; no branch reaches a completed
configuration.

## Check

From the repository root:

```sh
make verify-certificate
```

The separately written checker regenerates states and candidates, validates
positive cycle witnesses, reconciles all counters, and rejects malformed,
truncated, trailing, tampered, or unexpectedly completing streams. It does
not trust a production executable, a production cycle oracle, or stored
negative cycle assertions.

To rebuild the bundle:

```sh
make generate-certificates
```

The remaining trust boundary is the mathematical root normalization and
restricted-growth coverage proof in Proposition 10; see
`research/docs/completeness_argument.md`. The implementation-independent
binary specification is [`FORMAT.md`](FORMAT.md).
