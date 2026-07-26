#!/usr/bin/env python3
"""Fetch a balanced, cached Earth/planetary AI corpus from OpenAlex.

OpenAlex requires an API key as of February 2026. Set OPENALEX_API_KEY in the
environment; the key is never written to disk.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import time
from collections import defaultdict
from pathlib import Path

import requests
from dotenv import load_dotenv

API = "https://api.openalex.org/works"
USER_AGENT = "earth-ai-constellation/1.0 (open-source research visualization)"

DOMAIN_QUERIES = {
    "Weather and climate": [
        "weather forecasting machine learning",
        "climate deep learning",
        "precipitation neural network",
        "tropical cyclone artificial intelligence",
        "atmospheric transformer forecasting",
        "climate model machine learning",
    ],
    "Oceans and coasts": [
        "ocean machine learning",
        "coastal deep learning",
        "sea surface temperature neural network",
        "ocean circulation artificial intelligence",
        "shoreline change machine learning",
        "wave forecasting deep learning",
    ],
    "Earth observation and remote sensing": [
        "earth observation deep learning",
        "remote sensing machine learning",
        "satellite image convolutional neural network",
        "land cover random forest",
        "remote sensing transformer",
        "geospatial foundation model",
    ],
    "Solid Earth and geophysics": [
        "geophysics machine learning",
        "seismology deep learning",
        "earthquake detection neural network",
        "geophysical inversion machine learning",
        "volcanic artificial intelligence",
        "subsurface neural network",
    ],
    "Planetary science": [
        "planetary science machine learning",
        "Mars crater deep learning",
        "lunar remote sensing machine learning",
        "planetary geomorphology artificial intelligence",
        "exoplanet machine learning",
        "asteroid neural network",
    ],
}

AI_RE = re.compile(
    r"\b(machine learning|deep learning|artificial intelligence|neural networks?|"
    r"random forests?|support vector machines?|transformers?|foundation models?|"
    r"reinforcement learning|neural operators?|large language models?|CNNs?|LSTMs?|"
    r"U[- ]?Nets?|XGBoost|Gaussian processes?)\b",
    re.IGNORECASE,
)
DOMAIN_RELEVANCE = {
    "Weather and climate": re.compile(
        r"\b(weather|climate|climatic|climatology|atmospheric|atmosphere|"
        r"precipitation|rainfall|tropical cyclone|hurricane|monsoon|"
        r"meteorological|weather prediction|climate model)\b",
        re.IGNORECASE,
    ),
    "Oceans and coasts": re.compile(
        r"\b(ocean|oceanographic|coastal|coastline|marine|sea surface|"
        r"shoreline|estuary|estuarine|coral reef|ocean circulation|wave forecasting)\b",
        re.IGNORECASE,
    ),
    "Earth observation and remote sensing": re.compile(
        r"\b(remote sensing|earth observation|satellite imag(?:e|ery)|"
        r"land cover|hyperspectral|multispectral|synthetic aperture radar|"
        r"geospatial|Sentinel[- ]?[123]|Landsat)\b",
        re.IGNORECASE,
    ),
    "Solid Earth and geophysics": re.compile(
        r"\b(geophysic|seismic|seismolog|earthquake|subsurface|volcan(?:o|ic)|"
        r"tectonic|geothermal|geologic|geology|mineral exploration|"
        r"ground penetrating radar|full[- ]waveform inversion)\b",
        re.IGNORECASE,
    ),
    "Planetary science": re.compile(
        r"\b(planetary science|planetary surface|mars|martian|lunar|moon|"
        r"asteroid|exoplanet|venusian|mercury|jupiter|saturn|"
        r"crater detection|space telescope)\b",
        re.IGNORECASE,
    ),
}
DOMAIN_EXCLUSIONS = {
    "Weather and climate": re.compile(r"\b(wind turbine|HVAC|stock market)\b", re.IGNORECASE),
    "Oceans and coasts": re.compile(r"\b(materials science|structural health monitoring)\b", re.IGNORECASE),
    "Earth observation and remote sensing": re.compile(r"$^"),
    "Solid Earth and geophysics": re.compile(r"\b(green concrete|reinforcing bars?)\b", re.IGNORECASE),
    "Planetary science": re.compile(r"\b(planetary gear|planetary gearbox|bearing fault)\b", re.IGNORECASE),
}


def reconstruct_abstract(index: dict | None) -> str:
    if not index:
        return ""
    words = sorted((position, word) for word, positions in index.items() for position in positions)
    return " ".join(word for _, word in words)


def compact(work: dict, domain: str, query: str) -> dict:
    primary = work.get("primary_location") or {}
    source = primary.get("source") or {}
    topics = work.get("topics") or []
    keywords = work.get("keywords") or []
    return {
        "id": work.get("id"),
        "doi": work.get("doi"),
        "title": work.get("display_name") or work.get("title") or "",
        "abstract": reconstruct_abstract(work.get("abstract_inverted_index")),
        "year": work.get("publication_year"),
        "authors": [
            item.get("author", {}).get("display_name")
            for item in work.get("authorships", [])
            if item.get("author", {}).get("display_name")
        ],
        "venue": source.get("display_name"),
        "cited_by_count": work.get("cited_by_count", 0),
        "topics": [topic.get("display_name") for topic in topics if topic.get("display_name")],
        "keywords": [keyword.get("display_name") for keyword in keywords if keyword.get("display_name")],
        "type": work.get("type"),
        "language": work.get("language"),
        "url": primary.get("landing_page_url") or work.get("doi") or work.get("id"),
        "query_domain": domain,
        "matched_domains": [domain],
        "matched_queries": [query],
    }


def cache_path(cache: Path, domain: str, query: str) -> Path:
    slug = re.sub(r"[^a-z0-9]+", "_", domain.lower()).strip("_")[:28]
    digest = hashlib.sha1(query.encode("utf-8")).hexdigest()[:10]
    return cache / f"{slug}_{digest}.json"


def request_page(session: requests.Session, params: dict, retries: int = 4) -> dict:
    for attempt in range(retries):
        response = session.get(API, params=params, timeout=60)
        if response.status_code in {401, 403}:
            raise RuntimeError(
                f"OpenAlex authentication failed ({response.status_code}). "
                "Check OPENALEX_API_KEY in the gitignored .env file."
            )
        if response.status_code not in {429, 500, 502, 503, 504}:
            if not response.ok:
                raise RuntimeError(f"OpenAlex request failed with HTTP {response.status_code}.")
            return response.json()
        if attempt == retries - 1:
            response.raise_for_status()
        delay = min(12, 1.5 * (2**attempt))
        print(f"OpenAlex returned {response.status_code}; retrying in {delay:.1f}s")
        time.sleep(delay)
    raise RuntimeError("OpenAlex request failed after retries")


def fetch_query(
    domain: str,
    query: str,
    target: int,
    api_key: str,
    cache: Path,
    refresh: bool,
) -> list[dict]:
    cached = cache_path(cache, domain, query)
    if cached.exists() and not refresh:
        print(f"Using cache: {cached.name}")
        return json.loads(cached.read_text(encoding="utf-8"))

    results: list[dict] = []
    cursor: str | None = "*"
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    while len(results) < target and cursor:
        params = {
            "api_key": api_key,
            "search": query,
            "filter": (
                "from_publication_date:2015-01-01,"
                "has_abstract:true,"
                "is_retracted:false,"
                "language:en,"
                "type:article|preprint"
            ),
            "select": (
                "id,doi,display_name,abstract_inverted_index,publication_year,"
                "authorships,primary_location,cited_by_count,topics,keywords,"
                "type,language,is_retracted"
            ),
            "per_page": min(100, target - len(results)),
            "cursor": cursor,
        }
        payload = request_page(session, params)
        page = payload.get("results", [])
        results.extend(compact(work, domain, query) for work in page)
        cursor = payload.get("meta", {}).get("next_cursor")
        if not page:
            break
        time.sleep(0.12)

    cached.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{domain} · {query}: {len(results)}")
    return results


def merge_records(records: list[dict]) -> list[dict]:
    merged: dict[str, dict] = {}
    for record in records:
        work_id = record.get("id")
        if not work_id:
            continue
        if work_id not in merged:
            merged[work_id] = record
            continue
        current = merged[work_id]
        current["matched_domains"] = sorted(set(current["matched_domains"] + record["matched_domains"]))
        current["matched_queries"] = sorted(set(current["matched_queries"] + record["matched_queries"]))
    return list(merged.values())


def select_balanced(records: list[dict], target: int) -> list[dict]:
    relevant: list[dict] = []
    for record in records:
        title = record.get("title", "")
        abstract = record.get("abstract", "")
        text = f"{title}. {abstract}"
        if not AI_RE.search(text):
            continue
        scores: dict[str, int] = {}
        for domain in record.get("matched_domains", [record["query_domain"]]):
            pattern = DOMAIN_RELEVANCE[domain]
            title_hits = len(pattern.findall(title))
            abstract_hits = len(pattern.findall(abstract))
            scores[domain] = title_hits * 4 + min(abstract_hits, 4)
            if DOMAIN_EXCLUSIONS[domain].search(text):
                scores[domain] -= 6
        best_domain = max(scores, key=scores.get)
        if scores[best_domain] < 2:
            continue
        record["query_domain"] = best_domain
        record["domain_relevance_score"] = scores[best_domain]
        relevant.append(record)
    buckets: dict[str, list[dict]] = defaultdict(list)
    for record in relevant:
        buckets[record["query_domain"]].append(record)
    for bucket in buckets.values():
        bucket.sort(key=lambda item: (-int(item.get("cited_by_count") or 0), item["id"]))

    selected: list[dict] = []
    selected_ids: set[str] = set()
    domains = list(DOMAIN_QUERIES)
    index = 0
    while len(selected) < target:
        added = False
        for domain in domains:
            bucket = buckets[domain]
            if index < len(bucket) and bucket[index]["id"] not in selected_ids:
                selected.append(bucket[index])
                selected_ids.add(bucket[index]["id"])
                added = True
                if len(selected) == target:
                    break
        if not added:
            break
        index += 1
    return selected


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=1500, help="Maximum selected corpus size")
    parser.add_argument("--output", type=Path, default=Path("data/raw/openalex_papers.json"))
    parser.add_argument("--refresh", action="store_true", help="Ignore cached query responses")
    args = parser.parse_args()

    api_key = os.getenv("OPENALEX_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(
            "OPENALEX_API_KEY is required. Get a free key at "
            "https://openalex.org/settings/api and export it in your shell."
        )

    cache = args.output.parent / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    query_count = sum(len(queries) for queries in DOMAIN_QUERIES.values())
    per_query = max(20, math.ceil(args.target / query_count * 1.6))
    fetched = [
        record
        for domain, queries in DOMAIN_QUERIES.items()
        for query in queries
        for record in fetch_query(domain, query, per_query, api_key, cache, args.refresh)
    ]
    merged = merge_records(fetched)
    selected = select_balanced(merged, args.target)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(selected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = defaultdict(int)
    for record in selected:
        counts[record["query_domain"]] += 1
    print(f"Wrote {len(selected)} selected OpenAlex records to {args.output}")
    print("Domain counts:", dict(counts))


if __name__ == "__main__":
    main()
