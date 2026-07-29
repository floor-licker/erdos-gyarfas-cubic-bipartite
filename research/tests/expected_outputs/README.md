# Expected terminal status

The stable success lines for the principal commands are:

```text
make verify-certificate
VERIFIED: 66 witness streams exhaust every normalized root orbit for v=7,...,29.

make verify-full
VERIFIED: full-range integer counters agree.

make verify-transcripts
VERIFIED: wrote 69 matching transcript hashes to research/results/transcript_hashes.tsv

make verify-v29
VERIFIED: all three implementations have identical counters and search-transcript hashes for all v=29 root orbits.

make verify-genbg
VERIFIED: restricted-growth and genbg canonical C4-free sets agree for v=7,...,13.

make verify-unreduced
VERIFIED: --unreduced-root reproduces every v=7,...,28 historical counter.
```
