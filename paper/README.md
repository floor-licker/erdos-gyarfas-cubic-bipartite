# Paper

The circulation PDF is
[`Tranquilli_2026_Erdos-Gyarfas_60-Vertex_Lower_Bound.pdf`](Tranquilli_2026_Erdos-Gyarfas_60-Vertex_Lower_Bound.pdf).
Its source is [`main.tex`](main.tex).

From the repository root, regenerate the tables and build the PDF with:

```sh
make paper
```

The generated tables in `tables/` are derived from
`research/results/frontier_counts.tsv` and
`research/results/v29_orbits.tsv`. Run `make validate-paper-data` to
cross-check every displayed exhaustive-search counter against the retained
primary results and logs.

The paper is solely authored by Julius Tranquilli. Its AI acknowledgement
and the fuller repository-level [`PROVENANCE.md`](../PROVENANCE.md) describe
material assistance from OpenAI ChatGPT and OpenAI Codex.
