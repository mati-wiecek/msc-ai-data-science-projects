from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ClinicalDocument:
    """A small, retrievable EHR-like document.

    The scaffold intentionally keeps the model simple. Later, this can be replaced
    with richer FHIR resource objects or a database-backed document store.
    """

    doc_id: str
    patient_id: str
    resource_type: str
    section: str
    timestamp: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def searchable_text(self) -> str:
        """Return text used by retrievers."""
        # Patient IDs are deliberately excluded from retrieval text. The pipeline filters
        # by patient_id before ranking; including IDs in the vector space can dominate
        # similarity and hide clinically relevant terms.
        return " ".join(
            [
                self.resource_type,
                self.section.replace("_", " "),
                self.timestamp,
                self.text,
            ]
        )


@dataclass(frozen=True)
class RetrievalResult:
    doc: ClinicalDocument
    score: float
    rank: int


@dataclass(frozen=True)
class RAGAnswer:
    question: str
    patient_id: str | None
    answer: str
    evidence: list[RetrievalResult]
    safety_flags: list[str]
    abstained: bool = False
