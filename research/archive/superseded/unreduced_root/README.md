# Superseded unreduced-root counters

`unreduced_root_counts.tsv` contains the historical \(v=7,\ldots,28\)
counters generated before root-stabilizer reduction of the first additional
block through point 1.

They differ from the primary counters because the initial augmentation
traverses symmetric copies. They use the same degree, pair, \(C_8\), and
\(C_{16}\) tests, and all completion counts are zero. Run:

```sh
make verify-unreduced
```

to reproduce the table with both principal implementations. These counters
are retained only for provenance and regression testing.
