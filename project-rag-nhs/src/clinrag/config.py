from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class RetrievalConfig:
    strategy: str = "tfidf"
    top_k: int = 3
    min_score: float = 0.05


@dataclass(frozen=True)
class SafetyConfig:
    block_direct_treatment_advice: bool = True
    flag_phi_patterns: bool = True
    require_uncertainty_statement: bool = True


@dataclass(frozen=True)
class AppConfig:
    synthetic_docs_path: Path = Path("data/synthetic/synthetic_ehr_docs.jsonl")
    qrels_path: Path = Path("data/synthetic/synthetic_qrels.json")
    retrieval: RetrievalConfig = RetrievalConfig()
    safety: SafetyConfig = SafetyConfig()


def load_config(path: str | Path = "configs/default.yaml") -> AppConfig:
    """Load a lightweight YAML config.

    Defaults are deliberately safe: synthetic data only and clinical-use disabled.
    """
    config_path = Path(path)
    if not config_path.exists():
        return AppConfig()

    raw: dict[str, Any] = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    data = raw.get("data", {})
    retrieval = raw.get("retrieval", {})
    safety = raw.get("safety", {})

    return AppConfig(
        synthetic_docs_path=Path(data.get("synthetic_docs_path", "data/synthetic/synthetic_ehr_docs.jsonl")),
        qrels_path=Path(data.get("qrels_path", "data/synthetic/synthetic_qrels.json")),
        retrieval=RetrievalConfig(
            strategy=retrieval.get("strategy", "tfidf"),
            top_k=int(retrieval.get("top_k", 3)),
            min_score=float(retrieval.get("min_score", 0.05)),
        ),
        safety=SafetyConfig(
            block_direct_treatment_advice=bool(safety.get("block_direct_treatment_advice", True)),
            flag_phi_patterns=bool(safety.get("flag_phi_patterns", True)),
            require_uncertainty_statement=bool(safety.get("require_uncertainty_statement", True)),
        ),
    )
