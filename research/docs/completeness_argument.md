# Restricted-growth completeness audit

This note isolates the principal nonmechanical trust boundary of the
certificate. The full proof is Proposition 10 of the paper.

## Objects

A connected cubic bipartite graph with bipartition \((X,Y)\) corresponds to
an indexed family \((B_y)_{y\in Y}\) of triples on \(X\). Cubicity gives
\(|X|=|Y|=v\), every block has size three, and every point occurs three
times. If there is no \(C_4\), no point pair occurs in two blocks.

## Root normalization

Choose a point labelled 0. Linearity permits its three incident blocks to be
labelled

```text
{0,1,2}, {0,3,4}, {0,5,6}.
```

The rooted-star stabilizer fixes 0 and 1, preserves the star, may exchange
the last two blocks, and may swap their nonroot points. Among the two
uninserted blocks through 1, choose one using the most old points. Repeated
pairs exclude 2 and exclude using both points from either remaining root
pair. The possibilities—two old points, one old point, or no old
points—normalize respectively to:

```text
{1,3,5}, {1,3,7}, {1,7,8}.
```

The same stabilizer and first-occurrence labelling make the representative
the lexicographically first uninserted block through 1.

## Induction invariant

Before processing point \(p\):

1. every target block with least-labelled point below \(p\) is inserted;
2. inserted target blocks through \(p\) form a lexicographic initial
   segment; and
3. introduced labels are exactly \(0,\ldots,m-1\), in first-occurrence
   order.

The normalized root establishes the invariant. Let \(B\) be the first
missing target block through \(p\). Any block containing \(p\) and a smaller
point was inserted earlier, so the other entries of \(B\) exceed \(p\).
Old entries pass the degree and repeated-pair filters because \(B\) belongs
to the target. New entries receive the next unused label or two labels.
Thus the generator proposes \(B\) in the required order.

The target contains no forbidden cycle, so this branch is not pruned. Once
\(p\) has degree three, advancing to the least unfinished introduced point
preserves the invariant. Connectedness ensures that every target point is
eventually introduced: a proper introduced subset closed under incident
blocks would be a union of components.

The argument proves coverage, not uniqueness. Multiple labelled branches
may represent the same unlabelled graph; surjectivity is sufficient for a
zero-completion result.

As a computational overlap, the restricted-growth generator and nauty
`genbg` produce identical color-preserving canonical graph sets for
\(v=7,\ldots,13\). This checks a nontrivial range but does not replace the
argument through \(v=29\).
