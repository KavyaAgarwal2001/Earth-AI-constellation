#!/usr/bin/env python3
"""Generate a deterministic synthetic corpus for interface development.

These records are invented and must never be presented as real publications.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

SEED = 42
COUNT = 108
OUT = Path(__file__).resolve().parents[1] / "public" / "data"

CLUSTERS = [
    ("Weather forecasting", -58, 43, "Weather and climate"),
    ("Satellite image segmentation", 20, 48, "Earth observation and remote sensing"),
    ("Coastal-change detection", 55, 11, "Oceans and coasts"),
    ("Seismic-event classification", -48, -35, "Solid Earth and geophysics"),
    ("Physical-model emulation", 2, -12, "Weather and climate"),
    ("Planetary geomorphology", 52, -43, "Planetary science"),
]

METHODS = {
    "Weather forecasting": ["Transformers", "Recurrent networks", "Graph neural networks", "Classical statistical models"],
    "Satellite image segmentation": ["CNNs", "Foundation models", "Random forests and tree models", "Support vector machines"],
    "Coastal-change detection": ["CNNs", "Random forests and tree models", "Recurrent networks", "Method unclear"],
    "Seismic-event classification": ["CNNs", "Support vector machines", "Random forests and tree models", "Physics-informed neural networks"],
    "Physical-model emulation": ["Neural operators", "Physics-informed neural networks", "Transformers", "Reinforcement learning"],
    "Planetary geomorphology": ["CNNs", "Foundation models", "Random forests and tree models", "AI discussed but not implemented"],
}

ROLES = {
    "Weather forecasting": ["Forecasting", "Estimation", "Data assimilation"],
    "Satellite image segmentation": ["Segmentation", "Classification", "Detection"],
    "Coastal-change detection": ["Detection", "Estimation", "Forecasting"],
    "Seismic-event classification": ["Classification", "Detection", "Inverse modeling"],
    "Physical-model emulation": ["Simulator emulation", "Inverse modeling", "Control and optimization", "Scientific discovery"],
    "Planetary geomorphology": ["Detection", "Classification", "Segmentation"],
}

PHYSICS = [
    "Purely data-driven",
    "Physical variables used as inputs",
    "Physical consistency evaluated",
    "Physics included in the loss",
    "Physics encoded in the architecture",
    "Coupled with a simulator",
    "Emulator of a simulator",
    "Physics relationship unclear",
]

AUTHORS = [
    "Maya Chen", "Amir Okafor", "Sofia Alvarez", "Jonas Lind", "Leila Rahman",
    "Noah Williams", "Priya Nair", "Elena Petrova", "Kwame Mensah", "Ana Torres",
]

OBJECTS = {
    "Weather forecasting": ["atmospheric rivers", "regional precipitation", "tropical cyclone tracks", "subseasonal temperature"],
    "Satellite image segmentation": ["flood extent", "forest disturbance", "glacier boundaries", "urban land cover"],
    "Coastal-change detection": ["shoreline retreat", "harmful algal blooms", "wave fields", "wetland loss"],
    "Seismic-event classification": ["microseismic events", "subsurface velocity", "earthquake phases", "volcanic tremor"],
    "Physical-model emulation": ["ocean circulation", "cloud microphysics", "land-surface fluxes", "fluid transport"],
    "Planetary geomorphology": ["Martian craters", "lunar boulders", "dune morphology", "icy moon fractures"],
}

METHOD_PHRASES = {
    "Classical statistical models": "a regularized statistical learning model",
    "Random forests and tree models": "a random forest classifier",
    "Support vector machines": "a support vector machine",
    "CNNs": "a convolutional neural network",
    "Recurrent networks": "a recurrent neural network",
    "Transformers": "a transformer architecture",
    "Graph neural networks": "a graph neural network",
    "Physics-informed neural networks": "a physics-informed neural network with governing-equation residuals",
    "Neural operators": "a Fourier neural operator trained as a simulator emulator",
    "Foundation models": "a pretrained remote-sensing foundation model",
    "Reinforcement learning": "a reinforcement-learning controller",
    "Large language models": "a large language model",
    "Method unclear": "an unspecified AI approach",
    "AI discussed but not implemented": "AI as a proposed future direction",
}

SPECIALS = [
    {
        "title": "Convolutional Networks for Pixel-Level Flood Segmentation in Multispectral Imagery",
        "cluster": "Satellite image segmentation", "method": "CNNs", "role": "Segmentation",
        "physics": "Purely data-driven", "evidence": "U-Net convolutional network segments inundated pixels",
    },
    {
        "title": "Random Forest Mapping of Continental Land-Cover Classes",
        "cluster": "Satellite image segmentation", "method": "Random forests and tree models", "role": "Classification",
        "physics": "Physical variables used as inputs", "evidence": "random forest trained on spectral and terrain variables",
    },
    {
        "title": "A Transformer for Medium-Range Global Weather Forecasting",
        "cluster": "Weather forecasting", "method": "Transformers", "role": "Forecasting",
        "physics": "Physical variables used as inputs", "evidence": "transformer forecasts atmospheric state variables",
    },
    {
        "title": "Physics-Informed Neural Networks for Regional Ocean Circulation",
        "cluster": "Physical-model emulation", "method": "Physics-informed neural networks", "role": "Estimation",
        "physics": "Physics included in the loss", "evidence": "Navier–Stokes residuals enter the training loss",
    },
    {
        "title": "Neural Operators as Fast Emulators of an Earth-System Simulator",
        "cluster": "Physical-model emulation", "method": "Neural operators", "role": "Simulator emulation",
        "physics": "Emulator of a simulator", "evidence": "Fourier neural operator emulates simulator outputs",
    },
    {
        "title": "Reinforcement Learning for Adaptive Reservoir Release Control",
        "cluster": "Physical-model emulation", "method": "Reinforcement learning", "role": "Control and optimization",
        "physics": "Coupled with a simulator", "evidence": "policy learns release actions through simulator rewards",
    },
    {
        "title": "Learning a Nonlinear Operator for Seismic Geophysical Inversion",
        "cluster": "Seismic-event classification", "method": "Neural operators", "role": "Inverse modeling",
        "physics": "Physical consistency evaluated", "evidence": "learned inverse map evaluated against wave-equation constraints",
    },
    {
        "title": "Automated Mars Crater Detection with Deep Convolutional Features",
        "cluster": "Planetary geomorphology", "method": "CNNs", "role": "Detection",
        "physics": "Purely data-driven", "evidence": "convolutional features detect crater rims",
    },
    {
        "title": "A Foundation Model for Multisensor Earth Observation",
        "cluster": "Satellite image segmentation", "method": "Foundation models", "role": "Classification",
        "physics": "Physical variables used as inputs", "evidence": "pretrained foundation model transfers across sensors",
    },
    {
        "title": "Artificial Intelligence Opportunities for Future Climate Services",
        "cluster": "Weather forecasting", "method": "AI discussed but not implemented", "role": "Role unclear",
        "physics": "Physics relationship unclear", "evidence": "AI appears in discussion; no implemented method is named",
    },
    {
        "title": "Agent-Based Modeling of Coastal Community Adaptation",
        "cluster": "Coastal-change detection", "method": "Method unclear", "role": "Estimation",
        "physics": "Coupled with a simulator", "evidence": "agent-based model refers to simulated households, not an AI agent",
    },
    {
        "title": "Language Models for Automated Earth-Science Metadata Workflows",
        "cluster": "Satellite image segmentation", "method": "Large language models", "role": "Workflow automation",
        "physics": "Physics relationship unclear", "evidence": "large language model extracts and harmonizes dataset metadata",
    },
]


def domain_for(cluster: str) -> str:
    return next(item[3] for item in CLUSTERS if item[0] == cluster)


def position(cluster: str, index: int, rng: random.Random) -> tuple[float, float]:
    _, cx, cy, _ = next(item for item in CLUSTERS if item[0] == cluster)
    angle = rng.random() * math.tau
    radius = 4 + (index % 9) * 1.25 + rng.random() * 5
    return round(cx + math.cos(angle) * radius * 1.35, 3), round(cy + math.sin(angle) * radius, 3)


def make_record(index: int, spec: dict, rng: random.Random) -> dict:
    cluster = spec["cluster"]
    method = spec["method"]
    role = spec["role"]
    physics = spec["physics"]
    obj = rng.choice(OBJECTS[cluster])
    title = spec.get("title") or f"{method.replace('CNNs', 'Deep Networks')} for {role} of {obj.title()}"
    evidence = spec.get("evidence") or f"{METHOD_PHRASES[method]} is used for {role.lower()}"
    abstract = (
        f"This synthetic demonstration study investigates {obj} in {domain_for(cluster).lower()}. "
        f"We use {METHOD_PHRASES[method]} for {role.lower()} and report evaluation on held-out observations. "
        f"The physics relationship is categorized as {physics.lower()}. This record is invented for interface testing."
    )
    x, y = position(cluster, index, rng)
    confidence = 0.52 if method in ("Method unclear", "AI discussed but not implemented") else min(0.98, 0.71 + rng.random() * 0.27)
    return {
        "id": f"demo-{index + 1:03d}", "title": title, "abstract": abstract,
        "year": 2015 + (index * 7 + index // 9) % 11,
        "authors": rng.sample(AUTHORS, 2 + index % 3), "domain": domain_for(cluster),
        "aiMethod": method, "aiRole": role, "physicsIntegration": physics,
        "confidence": round(confidence, 2), "evidence": evidence, "x": x, "y": y,
        "cluster": cluster, "url": f"https://openalex.org/demo-{index + 1:03d}", "demo": True,
    }


def main() -> None:
    rng = random.Random(SEED)
    specs = list(SPECIALS)
    while len(specs) < COUNT:
        cluster = CLUSTERS[len(specs) % len(CLUSTERS)][0]
        method = METHODS[cluster][(len(specs) // len(CLUSTERS)) % len(METHODS[cluster])]
        role = ROLES[cluster][len(specs) % len(ROLES[cluster])]
        physics = PHYSICS[(len(specs) * 3 + len(specs) // 5) % len(PHYSICS)]
        specs.append({"cluster": cluster, "method": method, "role": role, "physics": physics})

    papers = [make_record(i, spec, rng) for i, spec in enumerate(specs)]
    clusters = [{"name": name, "x": x, "y": y} for name, x, y, _ in CLUSTERS]
    summary = {"demo": True, "generatedAt": "2026-07-25", "paperCount": len(papers), "yearRange": [2015, 2025]}
    OUT.mkdir(parents=True, exist_ok=True)
    for filename, payload in [("papers.json", papers), ("clusters.json", clusters), ("summary.json", summary)]:
        (OUT / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(papers)} synthetic demo papers to {OUT}")


if __name__ == "__main__":
    main()
