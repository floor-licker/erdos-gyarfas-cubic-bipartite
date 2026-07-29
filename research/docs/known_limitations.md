# Known limitations

- The result is finite: it reaches graph order 58 and gives a lower bound of
  60. It makes no claim at order 60.
- The certificate is a domain-specific witness stream, not a proof-assistant
  formalization and not an LRAT-style proof.
- The checker still implements the normalized restricted-growth traversal.
  Search-space coverage ultimately relies on Proposition 10.
- The three search programs are separately written but share the same
  mathematical generation framework.
- The generator-level `genbg` comparison ends at side size 13.
- Transcript equality shows identical ordered decisions but is not an
  independent coverage proof.
- The search is not isomorph-free, so state counts must not be interpreted as
  numbers of nonisomorphic configurations.
- The historical unreduced-root counters are diagnostic and are not primary
  evidence.
- The literature novelty statement is qualified by “to my knowledge” and an
  audit date; unpublished or uncatalogued computations may exist.
