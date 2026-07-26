#!/usr/bin/env python3
"""Fetch a selected, cached Earth/planetary AI corpus from OpenAlex."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import requests

API = "https://api.openalex.org/works"
DOMAINS = {
    "Weather and climate": "climate weather machine learning",
    "Oceans and coasts": "ocean coastal machine learning",
    "Earth observation and remote sensing": "remote sensing earth observation deep learning",
    "Solid Earth and geophysics": "geophysics seismology machine learning",
    "Planetary science": "planetary Mars lunar machine learning",
}


def reconstruct_abstract(index: dict | None) -> str:
    if not index:
        return ""
    words = sorted(((position, word) for word, positions in index.items() for position in positions))
    return " ".join(word for _, word in words)


def compact(work: dict, domain: str) -> dict:
    primary = work.get("primary_location") or {}
    return {
        "id": work.get("id"), "doi": work.get("doi"), "title": work.get("title") or "",
        "abstract": reconstruct_abstract(work.get("abstract_inverted_index")),
        "year": work.get("publication_year"), "authors": [
            item.get("author", {}).get("display_name") for item in work.get("authorships", []) if item.get("author")
        ], "venue": (primary.get("source") or {}).get("display_name"),
        "cited_by_count": work.get("cited_by_count", 0),
        "topics": [topic.get("display_name") for topic in work.get("topics", [])],
        "url": primary.get("landing_page_url") or work.get("doi") or work.get("id"),
        "query_domain": domain,
    }


def fetch_domain(domain: str, query: str, target: int, mailto: str, cache: Path) -> list[dict]:
    cached = cache / f"{domain.lower().replace(' ', '_').replace('/', '_')}.json"
    if cached.exists():
        print(f"Using cache: {cached.name}")
        return json.loads(cached.read_text(encoding="utf-8"))
    results, cursor = [], "*"
    session = requests.Session()
    while len(results) < target and cursor:
        params = {
            "search": query, "filter": "from_publication_date:2015-01-01,has_abstract:true",
            "select": "id,doi,title,abstract_inverted_index,publication_year,authorships,primary_location,cited_by_count,topics",
            "per-page": min(200, target - len(results)), "cursor": cursor, "mailto": mailto,
        }
        response = session.get(API, params=params, timeout=45)
        response.raise_for_status()
        payload = response.json()
        results.extend(compact(work, domain) for work in payload.get("results", []))
        cursor = payload.get("meta", {}).get("next_cursor")
        print(f"{domain}: {len(results)}/{target}")
        time.sleep(0.15)
    cached.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=1500, help="Approximate total corpus size")
    parser.add_argument("--output", type=Path, default=Path("data/raw/openalex_papers.json"))
    parser.add_argument("--refresh", action="store_true", help="Ignore cached domain responses")
    args = parser.parse_args()
    mailto = os.getenv("OPENALEX_MAILTO", "earth-ai-constellation@example.com")
    cache = args.output.parent / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    if args.refresh:
        for item in cache.glob("*.json"):
            item.unlink()
    per_domain = max(1, args.target // len(DOMAINS))
    records = [record for domain, query in DOMAINS.items() for record in fetch_domain(domain, query, per_domain, mailto, cache)]
    unique = {record["id"]: record for record in records if record.get("id")}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(list(unique.values()), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(unique)} selected OpenAlex records to {args.output}")


if __name__ == "__main__":
    main()
