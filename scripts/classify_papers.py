#!/usr/bin/env python3
"""Transparent pattern-based classifier for titles and abstracts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

METHODS = [
    ("Physics-informed neural networks", r"\bphysics[- ]informed neural network|\bPINNs?\b"),
    ("Neural operators", r"\b(?:fourier|deep|graph) neural operator|\bneural operator"),
    ("Foundation models", r"\bfoundation model|self-supervised pretrain"),
    ("Large language models", r"\blarge language model|\bLLMs?\b"),
    ("Reinforcement learning", r"\breinforcement learning|\bdeep Q[- ]network|\bpolicy gradient"),
    ("Transformers", r"\btransformer (?:model|architecture|network)|\bvision transformer|\bViT\b"),
    ("Graph neural networks", r"\bgraph neural network|\bGNNs?\b"),
    ("CNNs", r"\bconvolutional neural network|\bCNNs?\b|\bU[- ]?Net\b"),
    ("Recurrent networks", r"\brecurrent neural network|\bLSTMs?\b|\bGRUs?\b"),
    ("Random forests and tree models", r"\brandom forests?\b|\bgradient[- ]boosted trees?\b|\bXGBoost\b"),
    ("Support vector machines", r"\bsupport vector (?:machine|regression)|\bSVMs?\b"),
    ("Classical statistical models", r"\blinear regression|\bgaussian process|\bkriging\b"),
]
ROLES = [
    ("Segmentation", r"\bsegment(?:ation|ing)?\b|\bpixel[- ]wise\b"),
    ("Inverse modeling", r"\binvers(?:e|ion)\b|\bparameter retrieval\b"),
    ("Simulator emulation", r"\bemulat(?:e|or|ion)\b|\bsurrogate model\b"),
    ("Data assimilation", r"\bdata assimilation\b"),
    ("Control and optimization", r"\bcontrol\b|\boptim(?:ize|isation|ization)\b"),
    ("Forecasting", r"\bforecast(?:ing|s)?\b|\bprediction horizon\b"),
    ("Detection", r"\bdetect(?:ion|ing)?\b|\blocali[sz]ation\b"),
    ("Classification", r"\bclassif(?:y|ier|ication)\b"),
    ("Estimation", r"\bestimat(?:e|ion)\b|\bretrieval\b"),
    ("Scientific discovery", r"\bdiscover(?:y|ing)?\b|\bpattern discovery\b"),
    ("Workflow automation", r"\bworkflow\b|\bmetadata extraction\b"),
]
PHYSICS = [
    ("Physics included in the loss", r"\bphysics[- ]informed\b|\bgoverning equation residual|\bphysics loss\b"),
    ("Physics encoded in the architecture", r"\bequivariant\b|\bconservation layer\b|\bphysics[- ]encoded architecture\b"),
    ("Emulator of a simulator", r"\bemulat(?:e|or) (?:a |the )?(?:simulator|model)|\bsurrogate (?:for|of)\b"),
    ("Coupled with a simulator", r"\bcoupled (?:to|with) (?:a |the )?(?:simulator|model)\b|\bin[- ]the[- ]loop simulator\b"),
    ("Physical consistency evaluated", r"\bphysical consistency\b|\bconservation (?:evaluated|tested|error)\b"),
    ("Physical variables used as inputs", r"\bphysical variables?\b|\bmeteorological inputs?\b|\boceanographic inputs?\b"),
    ("Purely data-driven", r"\bpurely data[- ]driven\b|\bdata[- ]driven model\b"),
]


def first_match(text: str, patterns: list[tuple[str, str]], unclear: str) -> tuple[str, float, str]:
    for label, pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            sentence = next((s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if match.group(0).lower() in s.lower()), match.group(0))
            future = bool(re.search(r"\b(future work|could be|may be|we propose to|potential for)\b", sentence, re.I))
            if future:
                continue
            return label, 0.88, sentence[:240]
    return unclear, 0.45, "No sufficiently specific implementation phrase was detected."


def classify(record: dict) -> dict:
    text = f"{record.get('title', '')}. {record.get('abstract', '')}"
    method, method_conf, method_evidence = first_match(text, METHODS, "Method unclear")
    if re.search(r"\bAI\b|\bartificial intelligence\b", text, re.I) and method == "Method unclear":
        method, method_conf = "AI discussed but not implemented", 0.55
    role, role_conf, role_evidence = first_match(text, ROLES, "Role unclear")
    physics, physics_conf, physics_evidence = first_match(text, PHYSICS, "Physics relationship unclear")
    return {
        **record, "domain": record.get("query_domain", "Unclear"),
        "aiMethod": method, "aiRole": role, "physicsIntegration": physics,
        "confidence": round((method_conf + role_conf + physics_conf) / 3, 2),
        "evidence": {"method": method_evidence, "role": role_evidence, "physics": physics_evidence},
        "automaticallyClassified": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/raw/openalex_papers.json"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/classified_papers.json"))
    args = parser.parse_args()
    records = json.loads(args.input.read_text(encoding="utf-8"))
    classified = [classify(record) for record in records]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(classified, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Classified {len(classified)} papers → {args.output}")


if __name__ == "__main__":
    main()
