from __future__ import annotations

from statistics import mean

from clinrag.data_models import RetrievalResult
from clinrag.rag_pipeline import ClinicallyAwareRAG


def precision_at_k(results: list[RetrievalResult], relevant_doc_ids: set[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    retrieved = [result.doc.doc_id for result in results[:k]]
    if not retrieved:
        return 0.0
    hits = sum(1 for doc_id in retrieved if doc_id in relevant_doc_ids)
    return hits / min(k, len(retrieved))


def recall_at_k(results: list[RetrievalResult], relevant_doc_ids: set[str], k: int) -> float:
    if not relevant_doc_ids:
        return 0.0
    retrieved = [result.doc.doc_id for result in results[:k]]
    hits = sum(1 for doc_id in retrieved if doc_id in relevant_doc_ids)
    return hits / len(relevant_doc_ids)


def reciprocal_rank(results: list[RetrievalResult], relevant_doc_ids: set[str]) -> float:
    for result in results:
        if result.doc.doc_id in relevant_doc_ids:
            return 1.0 / result.rank
    return 0.0


def evaluate_retrieval(pipeline: ClinicallyAwareRAG, qrels: list[dict], *, k: int = 3) -> dict[str, float]:
    rows: list[dict[str, float]] = []
    for item in qrels:
        relevant = set(item["relevant_doc_ids"])
        results = pipeline.retriever.search(
            item["question"],
            patient_id=item.get("patient_id"),
            top_k=k,
        )
        rows.append(
            {
                "precision_at_k": precision_at_k(results, relevant, k),
                "recall_at_k": recall_at_k(results, relevant, k),
                "reciprocal_rank": reciprocal_rank(results, relevant),
            }
        )

    if not rows:
        return {"precision_at_k": 0.0, "recall_at_k": 0.0, "mrr": 0.0}

    return {
        "precision_at_k": mean(row["precision_at_k"] for row in rows),
        "recall_at_k": mean(row["recall_at_k"] for row in rows),
        "mrr": mean(row["reciprocal_rank"] for row in rows),
    }
