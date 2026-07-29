# `EG58CER1` certificate format

This document specifies the raw member format inside
`eg58_witness_certificates.zip`. It is intended to be sufficient for writing
an independent verifier without reading the certificate generator.

## Primitive representation

All values are unsigned. Single-byte fields are exactly one octet. Every
64-bit counter is encoded in little-endian order. No padding, alignment, or
native C++ object representation occurs in a stream.

ZIP is only a transport container. Each member is verified as a separate raw
stream; an independent implementation need not use ZIP if the raw members
and metadata are supplied another way.

## Header

The fixed header is 60 bytes:

| Offset | Width | Meaning |
| ---: | ---: | --- |
| 0 | 8 | ASCII magic `EG58CER1` |
| 8 | 1 | side size \(v\), from 7 through 29 |
| 9 | 1 | root orbit: 1, 2, or 3; 0 only for the compatibility stream |
| 10 | 1 | cycle flags: bit 0 enables \(C_8\), bit 1 enables \(C_{16}\) |
| 11 | 1 | reserved; must be zero |
| 12 | 8 | states |
| 20 | 8 | attempted candidates |
| 28 | 8 | structural/pair rejections |
| 36 | 8 | \(C_8\) rejections |
| 44 | 8 | \(C_{16}\) rejections |
| 52 | 8 | completed configurations |

The theorem-supporting streams require flags `0x03`. Root orbit 1 is
available for every supported side, orbit 2 requires \(v\geq8\), and orbit 3
requires \(v\geq9\). Orbit 0 is reserved for the side-16 compatibility
stream and requires flags `0x01`.

Header counters are claims, not trusted input. A verifier must recompute and
compare them after checking the proof.

## Initial state

Point labels range from 0 through \(v-1\). The verifier installs the rooted
star, in this order:

```text
{0,1,2}
{0,3,4}
{0,5,6}
```

For a theorem-supporting stream it then installs one normalized first block:

```text
orbit 1: {1,3,5}
orbit 2: {1,3,7}
orbit 3: {1,7,8}
```

The compatibility orbit starts from only the rooted star and invokes the
unreduced-root, \(C_8\)-only traversal.

## Deterministic candidate traversal

At each recursive state:

1. Increment the state counter.
2. Advance to the least introduced point `p` whose degree is below three.
3. If `p == v` and exactly \(v\) blocks are installed, reject the
   certificate because it expanded to a complete configuration.
4. Form the ordered `possible` list from:
   - old labels `q > p` having degree below three and not already paired with
     `p`;
   - the next fresh label, when below \(v\); and
   - the following fresh label, when below \(v\).
5. Enumerate index pairs from that list in lexicographic order.
6. Disallow use of the second fresh label unless the first fresh label is in
   the same proposed block.
7. When continuing through the same point, enforce a strict lexicographic
   lower bound from the previously installed block through that point.

Every surviving pair defines candidate `{p,q,r}` and increments the
attempted counter. Degree or repeated-pair failure is recomputed directly,
increments the structural counter, and consumes no proof byte.

## Record types

A structurally valid candidate consumes one record.

### `0x08`: \(C_8\) rejection

The tag is followed by three one-byte indices into the current ordered block
list. The three indices must be distinct and in range. Together with the
candidate, the four blocks must meet consecutively in four distinct points.
This is the Berge quadrilateral witnessing a simple \(C_8\).

Total width: 4 bytes.

### `0x10`: \(C_{16}\) rejection

The tag is followed by:

- one endpoint-pair code;
- seven one-byte indices into the current ordered block list.

Endpoint-pair codes refer to the candidate's sorted entries:

```text
0: entries (0,1)
1: entries (0,2)
2: entries (1,2)
```

The seven block indices must be distinct and in range. The first old block
must contain the stated start point, the last must contain the finish point,
and consecutive old blocks must meet in six distinct intermediate points.
Together with the endpoints, these eight point vertices must all be
distinct. The record therefore describes a simple old 14-edge incidence
path, which the new block closes to a simple \(C_{16}\).

Total width: 9 bytes.

### `0x20`: expansion

There is no payload. Install the candidate, update the first-unused label,
and recursively consume the complete child stream. On return, uninstall the
candidate and continue with the next candidate in the parent's deterministic
order.

Total width: 1 byte plus the recursively nested records.

There are no explicit end-state, return, or termination markers; deterministic
reconstruction determines those boundaries.

## Successful termination

After the root traversal returns, a verifier must require:

- recomputed counters exactly equal the header counters;
- the recomputed completion count is zero; and
- the next input operation reaches end-of-file.

Empty suffixes, ignored suffixes, and concatenated streams are invalid.

## Required failure behavior

A verifier must reject at least:

- bad magic, unsupported side/orbit/flags, or a nonzero reserved byte;
- truncated header, record, witness, or child stream;
- an unknown record tag;
- an out-of-range or repeated witness block index;
- an invalid endpoint-pair code;
- a witness that does not establish the claimed simple cycle;
- a stream that expands to a completed configuration;
- any header-counter disagreement; and
- any byte after the reconstructed root traversal.

The regression cases in `research/tests/certificate_tampering/` exercise
these boundaries.
