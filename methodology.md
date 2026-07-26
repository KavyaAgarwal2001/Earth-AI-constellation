# Methodology

This repository currently ships with a **synthetic demonstration corpus**. The records in `public/data/papers.json` are invented, visibly labeled as demo data, and exist only to make the interface testable before a real corpus is generated. They support no scientific conclusions.

## Corpus selection

The real-data pipeline queries the OpenAlex Works API across five broad query groups: weather and climate, oceans and coasts, Earth observation and remote sensing, solid Earth and geophysics, and planetary science. Each query includes machine-learning-related language, requires an abstract, and currently selects work published from 2015 onward.

This produces a selected, convenience corpus—not a systematic review and not every relevant paper. Query terms, OpenAlex coverage, abstract availability, language, and the target sample size all shape what appears.

Raw API responses are compacted and cached under `data/raw/cache/`. Duplicate OpenAlex work IDs are removed before classification.

## Classification

`scripts/classify_papers.py` applies ordered, human-readable regular-expression patterns to each title and abstract. It produces:

- a detected AI method;
- a scientific role;
- a physics-integration category;
- a confidence score;
- matched evidence text; and
- an `automaticallyClassified` flag.

Specific phrases are tested before broad ones. For example, “physics-informed neural network” takes precedence over “neural network.” Patterns require phrases such as “reinforcement learning” rather than the word “reinforcement,” and “transformer model” rather than “transform.” “Agent-based model” is not treated as an LLM agent. Sentences framed as future work or unrealized potential do not count as implementation evidence.

The classifier deliberately supports `Method unclear`, `Role unclear`, and `Physics relationship unclear`. Confidence represents the strength and specificity of textual evidence, not scientific quality and not a calibrated probability that a label is correct.

## Embeddings and semantic layout

`scripts/build_constellation.py` joins each paper’s title and abstract, embeds that text with `sentence-transformers/all-MiniLM-L6-v2`, and normalizes the vectors. UMAP reduces the vectors to two dimensions with cosine distance and a fixed random seed (`42` by default) for reproducibility.

The two-dimensional position is an approximate visual aid. Local neighborhoods can reveal shared language, but axes have no intrinsic meaning and distances should not be interpreted as precise semantic measurements.

K-means assigns a small number of display clusters. Cluster names come from the two highest-weight TF–IDF terms within each cluster. These labels are navigational summaries, not scientific taxonomies.

## Static export

The processed records are written to:

- `public/data/papers.json`
- `public/data/clusters.json`
- `public/data/summary.json`

The React application loads these files directly. No backend or database is required.

## Limitations

- This is a selected corpus, not every Earth-science paper.
- OpenAlex metadata and abstracts may be missing or incomplete.
- Automated labels can be wrong and should be audited before publication.
- Scientific fields overlap; one domain label simplifies multidisciplinary work.
- UMAP positions are approximate and depend on text, model, and parameters.
- Mentioning a method is not necessarily the same as implementing it.
- Abstract-only classification misses details found in full text.
- Citation count reflects many factors and does not represent scientific quality.
- Automatically generated cluster names may be awkward or overly broad.
