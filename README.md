# What Does “AI” Mean in Earth Science?

### An interactive constellation of AI across Earth and planetary research

[![Deploy to GitHub Pages](https://github.com/OWNER/earth-ai-constellation/actions/workflows/deploy.yml/badge.svg)](https://github.com/OWNER/earth-ai-constellation/actions/workflows/deploy.yml)

> **Demo status:** the repository currently ships with 108 clearly marked synthetic paper records. They are for interface development only and support no scientific conclusions.

> **Screenshot placeholder:** add a capture of the deployed constellation here before launch.

**Live site:** `https://OWNER.github.io/earth-ai-constellation/` (replace `OWNER` after publishing)

## Research question

When Earth scientists say “AI,” what are they actually doing?

This project maps a selected corpus of Earth and planetary science papers by semantic similarity. Each point is a paper. Its position stays fixed while the color lens changes, making it possible to compare scientific domain, AI method, research role, physics integration, publication year, and classification confidence on the same landscape.

## Features

- WebGL-rendered semantic paper constellation with zoom, pan, hover, and selection
- Six color lenses with accessible categorical and continuous legends
- Title search and filters for year, domain, method, role, and physics integration
- Detailed paper drawer with abstract, authors, labels, confidence, and evidence
- Limited cluster labels that stay readable over the map
- Interactive summary charts with counts and percentages
- Loading, empty, and error states
- Responsive dark, scientific visual design
- Reproducible synthetic dataset and real OpenAlex processing pipeline
- Fully static GitHub Pages deployment

## Technology

- React + TypeScript + Vite
- deck.gl for the WebGL constellation
- Recharts for analytical summaries
- Python, OpenAlex, sentence-transformers, UMAP, and scikit-learn for data processing
- Static JSON data files; no server, database, authentication, or paid API

## Run locally

Requires Node.js 20+ and Python 3.10+.

```bash
npm install
npm run generate:demo
npm run dev
```

Open the local URL printed by Vite.

To verify a production build:

```bash
npm run build
npm run preview
```

## Demo data

Regenerate the same 108 deterministic synthetic records at any time:

```bash
npm run generate:demo
```

The generator writes `papers.json`, `clusters.json`, and `summary.json` to `public/data/`. It includes representative examples such as CNN segmentation, random forests, transformers, PINNs, neural operators, reinforcement learning, geophysical inversion, Mars crater detection, remote-sensing foundation models, unclear “AI” claims, and an agent-based model that is not mislabeled as an AI agent.

## Build a real corpus

Create and activate a Python environment, then install the pipeline dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
```

Optionally identify yourself to the OpenAlex polite pool:

```bash
export OPENALEX_MAILTO="you@example.org"
```

Fetch a manageable selected corpus, classify it, and build the semantic map:

```bash
python scripts/fetch_papers.py --target 1500
python scripts/classify_papers.py
python scripts/build_constellation.py
```

The fetcher caches per-domain responses and deduplicates OpenAlex IDs. The classifier uses inspectable patterns and saves labels, confidence, evidence, and whether each classification was automatic. The final script creates sentence-transformer embeddings, uses seeded UMAP for a reproducible two-dimensional projection, creates lightweight cluster names, and replaces the demo files in `public/data/`.

Review automated classifications before presenting the corpus as research output.

## GitHub Pages deployment

One setting controls the repository base path. In `.github/workflows/deploy.yml`, change:

```yaml
VITE_REPOSITORY_NAME: earth-ai-constellation
```

to the exact GitHub repository name.

Then:

1. Create a GitHub repository and push this project to its `main` branch.
2. In the repository, open **Settings → Pages**.
3. Under **Build and deployment**, choose **GitHub Actions** as the source.
4. Push to `main` or run the workflow manually from the **Actions** tab.

The workflow installs dependencies, builds with the repository base path, uploads `dist/`, and deploys it through GitHub Pages. Application assets and JSON fetch paths use Vite’s base URL, so they work both locally and under `https://OWNER.github.io/REPOSITORY/`.

## Data methodology

The real pipeline:

1. Queries five broad Earth and planetary research groups in OpenAlex.
2. Keeps a selected recent corpus with abstracts and machine-learning-related language.
3. Applies transparent title-and-abstract patterns to classify method, role, and physics integration.
4. Embeds title + abstract with `all-MiniLM-L6-v2`.
5. Projects embeddings with UMAP using a fixed random seed.
6. Exports static JSON loaded directly by the browser.

See [methodology.md](methodology.md) for pattern behavior, confidence semantics, layout details, and limitations.

## Limitations

- The included dataset is synthetic.
- A generated real corpus is selected, not exhaustive.
- OpenAlex abstracts can be absent or incomplete.
- Automated labels can be wrong; scientific fields overlap.
- UMAP neighborhoods are approximate, not exact distances.
- Mentioning a method does not prove implementation.
- Citation counts do not represent scientific quality.

## Repository map

```text
src/                    React interface and visualization
public/data/            Static demo or processed paper JSON
scripts/                Collection, classification, and layout pipeline
methodology.md          Detailed methodology and limitations
.github/workflows/      GitHub Pages deployment
```

## Future ideas

- Human-reviewed validation set and per-label precision estimates
- Multi-label scientific domains and roles
- Corpus snapshots with versioned selection queries
- Citation and venue facets (without treating citations as quality)
- Comparison across time periods or disciplines
- Exportable filtered paper lists

## License

MIT for the project code. OpenAlex metadata remains subject to its source terms; document any additional dataset terms before redistributing a generated corpus.
