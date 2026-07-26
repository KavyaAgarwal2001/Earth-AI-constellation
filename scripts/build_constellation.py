#!/usr/bin/env python3
"""Embed, project, cluster, and export the static website dataset."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from umap import UMAP


def name_clusters(texts: list[str], labels: np.ndarray, count: int) -> dict[int, str]:
    vectorizer = TfidfVectorizer(stop_words=list(ENGLISH_STOP_WORDS), max_features=2000, ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(texts)
    terms = np.array(vectorizer.get_feature_names_out())
    names = {}
    for label in range(count):
        rows = np.where(labels == label)[0]
        scores = np.asarray(matrix[rows].mean(axis=0)).ravel()
        names[label] = " · ".join(terms[scores.argsort()[-2:][::-1]]).title()
    return names


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/processed/classified_papers.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("public/data"))
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--clusters", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    papers = json.loads(args.input.read_text(encoding="utf-8"))
    texts = [f"{paper.get('title', '')}. {paper.get('abstract', '')}" for paper in papers]
    embeddings = SentenceTransformer(args.model).encode(texts, show_progress_bar=True, normalize_embeddings=True)
    coordinates = UMAP(n_components=2, metric="cosine", random_state=args.seed, n_neighbors=20, min_dist=0.12).fit_transform(embeddings)
    labels = KMeans(n_clusters=args.clusters, random_state=args.seed, n_init=10).fit_predict(embeddings)
    names = name_clusters(texts, labels, args.clusters)
    x = (coordinates[:, 0] - coordinates[:, 0].mean()) / (coordinates[:, 0].std() or 1) * 36
    y = (coordinates[:, 1] - coordinates[:, 1].mean()) / (coordinates[:, 1].std() or 1) * 36
    exported = []
    for index, paper in enumerate(papers):
        exported.append({
            "id": paper["id"], "title": paper["title"], "abstract": paper.get("abstract", ""),
            "year": paper.get("year"), "authors": paper.get("authors", []), "domain": paper["domain"],
            "aiMethod": paper["aiMethod"], "aiRole": paper["aiRole"], "physicsIntegration": paper["physicsIntegration"],
            "confidence": paper["confidence"], "evidence": paper["evidence"]["method"],
            "x": round(float(x[index]), 3), "y": round(float(y[index]), 3),
            "cluster": names[int(labels[index])], "url": paper.get("url") or paper["id"], "demo": False,
        })
    clusters = []
    for label, name in names.items():
        rows = np.where(labels == label)[0]
        clusters.append({"name": name, "x": round(float(x[rows].mean()), 3), "y": round(float(y[rows].mean()), 3)})
    years = [paper["year"] for paper in exported if paper.get("year")]
    summary = {"demo": False, "generatedAt": date.today().isoformat(), "paperCount": len(exported), "yearRange": [min(years), max(years)]}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, payload in [("papers.json", exported), ("clusters.json", clusters), ("summary.json", summary)]:
        (args.output_dir / filename).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Exported {len(exported)} papers and {len(clusters)} cluster labels to {args.output_dir}")


if __name__ == "__main__":
    main()
