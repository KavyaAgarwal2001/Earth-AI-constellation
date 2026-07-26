#!/usr/bin/env python3
"""Transparent, evidence-preserving classifier for titles and abstracts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

METHODS = [
    ("Physics-informed neural networks", r"\bphysics[- ]informed neural networks?\b|\bPINNs?\b"),
    ("Neural operators", r"\b(?:fourier|deep|graph) neural operators?\b|\bneural operators?\b"),
    ("Foundation models", r"\bfoundation models?\b|\bself[- ]supervised pretrain(?:ing|ed)?\b"),
    ("Large language models", r"\blarge language models?\b|\bLLMs?\b|\bGPT[- ]?[234]\b"),
    ("Reinforcement learning", r"\breinforcement learning\b|\bdeep Q[- ]networks?\b|\bpolicy gradient\b"),
    ("Transformers", r"\btransformer (?:models?|architectures?|networks?)\b|\bvision transformers?\b|\bViTs?\b"),
    ("Graph neural networks", r"\bgraph neural networks?\b|\bGNNs?\b"),
    ("CNNs", r"\bconvolutional neural networks?\b|\bCNNs?\b|\bU[- ]?Nets?\b|\bResNets?\b"),
    ("Recurrent networks", r"\brecurrent neural networks?\b|\bLSTMs?\b|\bGRUs?\b"),
    ("Random forests and tree models", r"\brandom forests?\b|\bgradient[- ]boost(?:ed|ing) trees?\b|\bXGBoost\b"),
    ("Support vector machines", r"\bsupport vector (?:machines?|regression)\b|\bSVMs?\b"),
    ("Classical statistical models", r"\blinear regression\b|\bgaussian processes?\b|\bkriging\b"),
]
ROLES = [
    ("Segmentation", r"\bsegment(?:ation|ing)?\b|\bpixel[- ]wise\b"),
    ("Inverse modeling", r"\binverse model(?:ing|ling)?\b|\bgeophysical inversion\b|\bparameter retrieval\b"),
    ("Simulator emulation", r"\bemulat(?:e|or|ion)\b|\bsurrogate models?\b"),
    ("Data assimilation", r"\bdata assimilation\b"),
    ("Control and optimization", r"\b(?:adaptive |optimal )?control\b|\boptim(?:ize|ise|ization|isation)\b"),
    ("Forecasting", r"\bforecast(?:ing|s|ed)?\b|\bprediction horizon\b"),
    ("Detection", r"\bdetect(?:ion|ing|ed)?\b|\blocali[sz]ation\b"),
    ("Classification", r"\bclassif(?:y|ies|ied|ier|iers|ication)\b"),
    ("Estimation", r"\bestimat(?:e|es|ed|ion)\b|\bretrieval\b|\bdownscal(?:e|ing)\b"),
    ("Scientific discovery", r"\bdiscover(?:y|ing|ed)?\b|\bpattern discovery\b"),
    ("Workflow automation", r"\bworkflow automation\b|\bmetadata extraction\b|\binformation extraction\b"),
]
PHYSICS = [
    ("Physics included in the loss", r"\bphysics[- ]informed\b|\bgoverning[- ]equation residuals?\b|\bphysics loss\b"),
    ("Physics encoded in the architecture", r"\b(?:rotation|translation|permutation)[- ]equivariant\b|\bconservation layers?\b|\bphysics[- ]encoded architecture\b"),
    ("Emulator of a simulator", r"\bemulat(?:e|or) (?:a |the )?(?:simulator|physical model|numerical model)\b|\bsurrogate (?:for|of) (?:a |the )?(?:simulator|model)\b"),
    ("Coupled with a simulator", r"\bcoupled (?:to|with) (?:a |the )?(?:simulator|physical model|numerical model)\b|\bin[- ]the[- ]loop simulator\b"),
    ("Physical consistency evaluated", r"\bphysical consistency\b|\bconservation (?:evaluated|tested|error|constraint)\b"),
    ("Physical variables used as inputs", r"\bphysical variables?\b|\bmeteorological (?:inputs?|variables?)\b|\boceanographic (?:inputs?|variables?)\b"),
    ("Purely data-driven", r"\bpurely data[- ]driven\b|\bdata[- ]driven (?:model|approach|method)\b"),
]
DOMAIN_PATTERNS = {
    "Weather and climate": r"\b(weather|climat(?:e|ic|ology)|atmospher(?:e|ic)|precipitation|rainfall|tropical cyclone|temperature forecast)\b",
    "Oceans and coasts": r"\b(ocean|coast(?:al|line)?|marine|sea surface|wave height|shoreline|estuar(?:y|ine))\b",
    "Earth observation and remote sensing": r"\b(remote sensing|earth observation|satellite imag(?:e|ery)|land cover|hyperspectral|multispectral|synthetic aperture radar)\b",
    "Solid Earth and geophysics": r"\b(geophysic|seismic|seismolog|earthquake|subsurface|volcan|tectonic|geothermal)\b",
    "Planetary science": r"\b(planetary|mars|martian|lunar|moon|asteroid|exoplanet|venus|mercury|jupiter|saturn)\b",
}

IMPLEMENTATION_RE = re.compile(
    r"\b(we (?:use|apply|train|develop|implement|propose|introduce|present)|"
    r"this (?:study|work|paper) (?:uses|applies|develops|presents)|"
    r"(?:is|are|was|were) (?:trained|applied|implemented|used)|"
    r"our (?:model|method|framework|approach))\b",
    re.IGNORECASE,
)
NON_IMPLEMENTATION_RE = re.compile(
    r"\b(future work|could be|may be|might be|we propose to|potential for|"
    r"opportunities for|promising direction|remains to be explored)\b",
    re.IGNORECASE,
)
REVIEW_TITLE_RE = re.compile(r"\b(review|survey|perspective|opportunities|challenges|roadmap|overview)\b", re.IGNORECASE)


def sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def find_match(title: str, abstract: str, patterns: list[tuple[str, str]], unclear: str) -> tuple[str, float, str, bool]:
    for source_name, source_text in (("title", title), ("abstract", abstract)):
        for label, pattern in patterns:
            match = re.search(pattern, source_text, re.IGNORECASE)
            if not match:
                continue
            sentence = next((item for item in sentences(source_text) if re.search(pattern, item, re.I)), match.group(0))
            if NON_IMPLEMENTATION_RE.search(sentence):
                continue
            implemented = source_name == "title" or bool(IMPLEMENTATION_RE.search(sentence))
            confidence = 0.94 if source_name == "title" else (0.89 if implemented else 0.72)
            return label, confidence, sentence[:260], implemented
    return unclear, 0.4, "No sufficiently specific implementation phrase was detected.", False


def classify_domain(record: dict, text: str) -> tuple[str, float]:
    scores = {
        domain: len(re.findall(pattern, text, re.IGNORECASE))
        for domain, pattern in DOMAIN_PATTERNS.items()
    }
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return record.get("query_domain", "Unclear"), 0.55
    confidence = min(0.96, 0.68 + scores[best] * 0.04)
    return best, confidence


def classify(record: dict) -> dict:
    title = record.get("title", "")
    abstract = record.get("abstract", "")
    text = f"{title}. {abstract}"
    domain, domain_conf = classify_domain(record, text)
    method, method_conf, method_evidence, implemented = find_match(title, abstract, METHODS, "Method unclear")
    if method != "Method unclear" and REVIEW_TITLE_RE.search(title) and not implemented:
        method, method_conf = "AI discussed but not implemented", 0.63
    elif method == "Method unclear" and re.search(r"\bAI\b|\bartificial intelligence\b", text, re.I):
        method, method_conf = "AI discussed but not implemented", 0.55
    role, role_conf, role_evidence, _ = find_match(title, abstract, ROLES, "Role unclear")
    physics, physics_conf, physics_evidence, _ = find_match(
        title, abstract, PHYSICS, "Physics relationship unclear"
    )
    return {
        **record,
        "domain": domain,
        "aiMethod": method,
        "aiRole": role,
        "physicsIntegration": physics,
        "confidence": round((domain_conf + method_conf + role_conf + physics_conf) / 4, 2),
        "evidence": {
            "method": method_evidence,
            "role": role_evidence,
            "physics": physics_evidence,
        },
        "methodImplemented": implemented,
        "automaticallyClassified": True,
        "classifierVersion": "rules-v2",
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
    unclear = sum(item["aiMethod"] in {"Method unclear", "AI discussed but not implemented"} for item in classified)
    print(f"Classified {len(classified)} papers → {args.output}")
    print(f"Unclear/unimplemented methods: {unclear} ({unclear / max(1, len(classified)):.1%})")


if __name__ == "__main__":
    main()
