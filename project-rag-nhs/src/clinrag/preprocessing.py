from __future__ import annotations

import re

from clinrag.data_models import ClinicalDocument

# These are deliberately simple development-time guards, not a complete de-identification system.
NHS_NUMBER_RE = re.compile(r"\b\d{3}[ -]?\d{3}[ -]?\d{4}\b")
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", flags=re.IGNORECASE)
UK_POSTCODE_RE = re.compile(
    r"\b([A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})\b",
    flags=re.IGNORECASE,
)


def detect_phi_like_patterns(text: str) -> list[str]:
    """Return simple flags for potentially identifying information."""
    flags: list[str] = []
    if NHS_NUMBER_RE.search(text):
        flags.append("possible_nhs_number")
    if EMAIL_RE.search(text):
        flags.append("possible_email")
    if UK_POSTCODE_RE.search(text):
        flags.append("possible_uk_postcode")
    return flags


def redact_phi_like_patterns(text: str) -> str:
    """Redact obvious identifiers for safer local experiments."""
    text = NHS_NUMBER_RE.sub("[REDACTED_NHS_NUMBER]", text)
    text = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = UK_POSTCODE_RE.sub("[REDACTED_POSTCODE]", text)
    return text


def filter_by_patient(documents: list[ClinicalDocument], patient_id: str | None) -> list[ClinicalDocument]:
    if patient_id is None:
        return documents
    return [doc for doc in documents if doc.patient_id == patient_id]


def chunk_documents(documents: list[ClinicalDocument]) -> list[ClinicalDocument]:
    """Placeholder for clinically meaningful chunking.

    Current synthetic notes are already small. Future work should chunk by EHR section,
    clinical concept, timestamp and provenance rather than arbitrary character windows.
    """
    return documents
