# Witness certificates

## Triangle-rooted proof

The primary bundle is `eg58_triangle_universal_two_streams.zip`:

- size: 218,728 bytes;
- SHA-256:
  `ce772c8cc5175fa5754129cef95c80a80ac96dec2eccd751c80de5a604e99b67`;
- format: `EG58TRI1`; and
- theorem-supporting streams: 2.

The streams represent the two normalized Berge-triangle root orbits. Side
size 29 is a cap: the checker rejects a completed configuration as soon as
all introduced points are cubic, including completions on fewer than 29
points. The two streams therefore cover every $v\leq29$.

The detached digest and machine-readable metadata accompany the ZIP. The
binary format is specified in [`TRIANGLE_FORMAT.md`](TRIANGLE_FORMAT.md).

From the repository root:

```sh
make verify-certificate
```

This regenerates both raw streams byte-for-byte, verifies every positive
cycle witness, reconstructs the 337 depth-19 states, checks their explicit
maps to six kernels, proves each kernel's compatible-pair graph
triangle-free, and thereby excludes a further block on the existing
29-point set. It also runs tampering tests.

`eg58_triangle_witness_certificates.zip` contains 45 conventional per-side
triangle-rooted streams as a cross-check.

## Stronger arbitrary-root cross-check

`eg58_witness_certificates.zip` is the earlier, stronger arbitrary-root
bundle:

- size: 20,545,969 bytes;
- SHA-256:
  `721221d5d59ceafcb7cfc11ce704e49f17d34586529eb315d800fee6bb1b597e`;
- format: `EG58CER1`; and
- theorem-supporting streams: 66.

It excludes all connected linear candidates through $v=29$, without
assuming a Berge triangle. Verify it with:

```sh
make verify-arbitrary-certificate
```

To rebuild the bundle:

```sh
make generate-certificates
```

That command rebuilds the arbitrary-root bundle; its format is
[`FORMAT.md`](FORMAT.md). Both certificate families retain a mathematical
trust boundary in their root normalization and restricted-growth coverage
arguments.
