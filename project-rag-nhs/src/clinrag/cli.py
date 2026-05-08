from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinrag.config import load_config
from clinrag.data_loader import load_jsonl_documents, load_qrels
from clinrag.evaluation import evaluate_retrieval
from clinrag.rag_pipeline import ClinicallyAwareRAG


def build_pipeline(config_path: str | Path = "configs/default.yaml") -> ClinicallyAwareRAG:
    config = load_config(config_path)
    documents = load_jsonl_documents(config.synthetic_docs_path)
    return ClinicallyAwareRAG(
        documents,
        min_score=config.retrieval.min_score,
        top_k=config.retrieval.top_k,
    )


def _cmd_demo(args: argparse.Namespace) -> int:
    pipeline = build_pipeline(args.config)
    patient_id = args.patient_id or "SYN-001"
    result = pipeline.answer(args.question, patient_id=patient_id)
    print(result.answer)
    print("\nEvidence ranking:")
    for item in result.evidence:
        print(f"  {item.rank}. {item.doc.doc_id} score={item.score:.3f}")
    if result.safety_flags:
        print(f"\nSafety flags: {', '.join(result.safety_flags)}")
    return 0


def _cmd_query(args: argparse.Namespace) -> int:
    pipeline = build_pipeline(args.config)
    result = pipeline.answer(args.question, patient_id=args.patient_id)
    payload = {
        "question": result.question,
        "patient_id": result.patient_id,
        "answer": result.answer,
        "abstained": result.abstained,
        "safety_flags": result.safety_flags,
        "evidence": [
            {
                "rank": item.rank,
                "doc_id": item.doc.doc_id,
                "score": item.score,
                "section": item.doc.section,
                "timestamp": item.doc.timestamp,
            }
            for item in result.evidence
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0


def _cmd_evaluate(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    pipeline = build_pipeline(args.config)
    qrels = load_qrels(config.qrels_path)
    metrics = evaluate_retrieval(pipeline, qrels, k=args.k)
    print(json.dumps(metrics, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Clinically-aware RAG research prototype")
    parser.add_argument("--config", default="configs/default.yaml", help="Path to YAML config")
    subparsers = parser.add_subparsers(required=True)

    demo_parser = subparsers.add_parser("demo", help="Run a simple text demo")
    demo_parser.add_argument("question")
    demo_parser.add_argument("--patient-id", default="SYN-001")
    demo_parser.set_defaults(func=_cmd_demo)

    query_parser = subparsers.add_parser("query", help="Return a JSON answer")
    query_parser.add_argument("--patient-id", default=None)
    query_parser.add_argument("--question", required=True)
    query_parser.set_defaults(func=_cmd_query)

    eval_parser = subparsers.add_parser("evaluate", help="Evaluate retrieval on synthetic qrels")
    eval_parser.add_argument("--k", type=int, default=3)
    eval_parser.set_defaults(func=_cmd_evaluate)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
