# Methodology

This repository currently ships with a processed snapshot of **1,172 selected OpenAlex works** published from 2015–2026. It was generated on July 25, 2026. The corpus and automatic labels are exploratory and support no causal or evaluative scientific claims.

## Corpus selection

The pipeline queries the OpenAlex Works API across five broad groups: weather and climate, oceans and coasts, Earth observation and remote sensing, solid Earth and geophysics, and planetary science. Six queries per group combine domain language with machine-learning terminology. The collector requires an English abstract, excludes retracted works, limits records to articles and preprints, and selects work published from 2015 onward.

Candidate records must also pass a local title-weighted domain-relevance check and contain recognizable AI terminology. Explicit exclusion patterns remove recurring false matches such as planetary gears, wind-turbine monitoring, structural-health monitoring, and green concrete. Results are interleaved across domain buckets before the target is applied. The current release contains 330 Earth-observation papers, 311 weather-and-climate papers, 205 ocean-and-coast papers, 189 solid-Earth papers, and 137 planetary-science papers.

This remains a selected, convenience corpus—not a systematic review and not every relevant paper. Query terms, OpenAlex ranking, English-language and abstract requirements, citation-based ordering within domain buckets, and the target sample size all shape what appears.

Raw API responses are compacted and cached under `data/raw/cache/`. Duplicate OpenAlex work IDs are merged before classification. OpenAlex requires a free API key; the key is read from the gitignored `.env` file and is never included in exported data.

## Classification

`scripts/classify_papers.py` (classifier `rules-v2`) applies ordered, human-readable regular-expression patterns to each title and abstract. It produces:

- a detected AI method;
- a scientific role;
- a physics-integration category;
- a confidence score;
- matched evidence text; and
- an `automaticallyClassified` flag.

Specific phrases are tested before broad ones. For example, “physics-informed neural network” takes precedence over more general neural-network language. Patterns require phrases such as “reinforcement learning” rather than “reinforcement,” and “transformer model” rather than “transform.” “Agent-based model” is not treated as an LLM agent. Sentences framed as future work or unrealized potential do not count as implementation evidence. Reviews and perspectives without implementation cues are labeled “AI discussed but not implemented.”

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
