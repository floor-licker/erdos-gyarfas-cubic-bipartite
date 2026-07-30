# `EG58TRI1` triangle-rooted certificate format

This format records the two triangle-rooted restricted-growth trees used by
`eg58_triangle_universal_two_streams.zip`. All integers larger than one byte
are unsigned 64-bit little-endian values.

## Header

Each stream begins with a 60-byte header:

| Offset | Bytes | Meaning |
| ---: | ---: | --- |
| 0 | 8 | ASCII magic `EG58TRI1` |
| 8 | 1 | maximum side size |
| 9 | 1 | triangle-root orbit, 1 or 2 |
| 10 | 1 | flags: bit 0 is $C_8$, bit 1 is $C_{16}$ |
| 11 | 1 | reserved; must be zero |
| 12 | 8 | recursive states |
| 20 | 8 | attempted blocks |
| 28 | 8 | structural rejections |
| 36 | 8 | $C_8$ rejections |
| 44 | 8 | $C_{16}$ rejections |
| 52 | 8 | completed configurations |

The universal proof uses side size 29 and both flags.

## Root and traversal

The checker installs the Berge triangle

```text
{0,1,3}, {1,2,4}, {0,2,5}
```

and then one of:

```text
orbit 1: {0,4,6}
orbit 2: {0,6,7}
```

It reconstructs every later candidate in deterministic restricted-growth
order. Degree-three and repeated-pair failures are recomputed and consume no
record. Every other candidate consumes one record:

| Byte | Payload | Meaning |
| ---: | --- | --- |
| `08` | three old-block indices | reject by a $C_8$ witness |
| `10` | endpoint-pair code and seven old-block indices | reject by a $C_{16}$ witness |
| `20` | none | install the block and recursively verify the child |

There are no explicit recursion or termination markers. The regenerated
candidate schedule determines when a child returns.

For a `08` record, the candidate and the three indexed old blocks must form
four distinct blocks with four distinct consecutive intersection points.

For a `10` record, endpoint codes 0, 1, and 2 denote respectively the first
and second, first and third, or second and third points of the candidate. The
seven distinct old blocks must form a simple 14-edge incidence path between
those endpoints.

Whenever every introduced point has degree three, the checker treats the
state as a completed configuration immediately, even if fewer points than the
header cap have been introduced. It rejects such a stream. This is why two
cap-29 streams cover every side size at most 29.

Acceptance also requires exact agreement with all header counters, immediate
end-of-file after the reconstructed tree, and zero completions. Malformed,
truncated, trailing, counter-tampered, and witness-tampered streams are
rejected.

## Implementations

- Generator: `research/src/generate_triangle_certificate.cpp`
- Streaming checker:
  `research/src/verify_triangle_universal_certificate.cpp`
- State-dumping checker:
  `research/src/verify_triangle_universal_dump.cpp`
- Python reproduction:
  `research/scripts/reproduce_triangle_rooted.py`

The certificate does not formalize the Moore reduction, the two-root
normalization, or restricted-growth completeness. Those remain mathematical
parts of the proof.
