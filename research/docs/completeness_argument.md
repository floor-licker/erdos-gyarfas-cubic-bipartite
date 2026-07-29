# Restricted-growth completeness audit guide

This note isolates the mathematical coverage argument behind Proposition 10
of the paper. It is the principal remaining nonmechanical trust boundary of
the certificate.

## Objects being covered

A connected simple cubic bipartite graph with fixed bipartition \((X,Y)\)
corresponds to a connected indexed family \((B_y)_{y\in Y}\) of triples on
\(X\). Cubicity gives \(|X|=|Y|=v\), every block has size three, and every
point occurs in three indexed blocks. Absence of a \(C_4\) makes the triple
system linear: no point pair occurs twice.

The coverage claim concerns connected, linear, 3-uniform, 3-regular indexed
incidence structures whose Levi graphs contain neither \(C_8\) nor
\(C_{16}\).

## Root normalization

Choose any point and label it 0. Linearity makes the six other points in its
three blocks distinct, so relabel those blocks as:

```text
{0,1,2}, {0,3,4}, {0,5,6}.
```

The permitted stabilizer fixes 0 and 1, preserves this rooted star, may
exchange the last two rooted blocks, and may swap the nonroot points within
either rooted block.

Among the two target blocks through point 1 not already inserted, select one
with the largest number of old rooted-star points. It cannot use 2, use both
of 3 and 4, or use both of 5 and 6, because each would repeat a rooted-star
pair. Its other entries therefore fall into exactly three cases:

1. two old points, one from each remaining root pair;
2. one old and one new point;
3. two new points.

The root stabilizer and first-occurrence labels send these cases to,
respectively:

```text
{1,3,5}, {1,3,7}, {1,7,8}.
```

The selection by greatest old-point count and the remaining stabilizer
freedom ensure that the representative can be the lexicographically first
uninserted block through point 1. The three cases are distinct because they
have different numbers of old points.

Audit questions:

- Does the allowed permutation preserve every rooted-star incidence and fix
  the designated point 1?
- Is every forbidden old-entry pattern excluded by an already used pair?
- Can the selected target block always be made first in the generator's
  lexicographic order?

## Induction invariant

Labels already introduced are exactly \(0,\ldots,m-1\). Immediately before
processing point \(p\):

1. every target block whose least-labelled point is less than \(p\) has been
   inserted;
2. the target blocks already inserted through \(p\) form a lexicographically
   initial segment of all target blocks through \(p\); and
3. introduced labels occur in first-occurrence order.

The normalized root and selected first block establish the invariant at
\(p=1\).

Let \(B\) be the first target block through \(p\) not yet inserted. Every
block containing \(p\) and a smaller point was inserted when that smaller
point was processed, so the other two entries of \(B\) are larger than
\(p\). Old entries meet the generator's degree and pair filters because
\(B\) belongs to the target. New target points receive the next unused
labels; two new points receive the next two labels in a fixed order. Hence
the proposal appears in the generator's ordered candidate list and follows
the previously inserted block through \(p\).

The target's linearity and absence of \(C_8,C_{16}\) ensure that none of its
blocks is pruned. When the degree of \(p\) reaches three, advancing to the
least unfinished introduced point converts the completed initial segment at
\(p\) into the first invariant condition for the next point.

Connectedness guarantees eventual introduction of every target point. A
proper introduced subset closed under all incident blocks would be a union
of components, contradicting connectedness.

## What completeness does and does not say

The induction constructs at least one labeled branch for each target.
It does not claim uniqueness. Multiple roots or labelings of the same
unrooted incidence graph may survive. For a zero-completion theorem,
surjectivity onto targets is sufficient.

## Independent computational overlap

For \(v=7,\ldots,13\), the same restricted-growth generator with only
linearity filtering emits completed Levi graphs that are canonically labeled
with the color classes fixed. The exact canonical graph6 sets agree with
nauty `genbg`, not merely in cardinality. This is a substantially different
generator-level check of the argument over the overlapping range, but it
does not replace the proof at larger \(v\).
