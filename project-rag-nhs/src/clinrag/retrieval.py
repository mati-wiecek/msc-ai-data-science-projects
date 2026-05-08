from __future__ import annotations

import re
from typing import Protocol

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from clinrag.data_models import ClinicalDocument, RetrievalResult
from clinrag.preprocessing import filter_by_patient


class Retriever(Protocol):
    def fit(self, documents: list[ClinicalDocument]) -> None: ...

    def search(
        self,
        query: str,
        *,
        patient_id: str | None = None,
        top_k: int = 3,
    ) -> list[RetrievalResult]: ...


def _normalise_query(query: str) -> str:
    """Remove administrative identifiers that should be handled by filters, not ranking."""
    query = re.sub(r"\bSYN-\d+\b", " ", query, flags=re.IGNORECASE)
    query = re.sub(r"\bpatient\b", " ", query, flags=re.IGNORECASE)
    return " ".join(query.split())


class TfidfRetriever:
    """Lexical baseline retriever.

    This is intentionally simple and reproducible. It gives the project a working
    baseline before adding BM25, dense retrieval, hybrid retrieval or clinical reranking.
    """

    def __init__(self) -> None:
        self._documents: list[ClinicalDocument] = []
        self._vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        self._matrix = None

    def fit(self, documents: list[ClinicalDocument]) -> None:
        if not documents:
            raise ValueError("Cannot fit retriever with an empty document list.")
        self._documents = documents
        self._matrix = self._vectorizer.fit_transform([doc.searchable_text() for doc in documents])

    def search(
        self,
        query: str,
        *,
        patient_id: str | None = None,
        top_k: int = 3,
    ) -> list[RetrievalResult]:
        if self._matrix is None:
            raise RuntimeError("Retriever must be fitted before search().")
        if not query.strip():
            return []

        candidate_docs = filter_by_patient(self._documents, patient_id)
        if not candidate_docs:
            return []

        # Compute over the full matrix, then filter. This keeps the implementation simple.
        query_vector = self._vectorizer.transform([_normalise_query(query)])
        scores = cosine_similarity(query_vector, self._matrix).ravel()

        allowed_doc_ids = {doc.doc_id for doc in candidate_docs}
        ranked_pairs = sorted(
            [
                (doc, float(score))
                for doc, score in zip(self._documents, scores, strict=True)
                if doc.doc_id in allowed_doc_ids
            ],
            key=lambda pair: pair[1],
            reverse=True,
        )[:top_k]

        return [RetrievalResult(doc=doc, score=score, rank=i + 1) for i, (doc, score) in enumerate(ranked_pairs)]
