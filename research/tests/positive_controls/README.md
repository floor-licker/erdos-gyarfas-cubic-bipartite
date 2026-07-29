# Positive controls

Run `make verify-positive`.

The command checks the 128 retained symmetric \(19_3\) configurations with
two exact cycle detectors:

- NetworkX elementary-cycle enumeration on the Johnson graph; and
- an exact subset-state dynamic program.

It also runs the normalized permutation-pair verifier on the first retained
configuration. The expected semantic JSON outputs are under
`research/results/`.
