from __future__ import annotations

import json
from pathlib import Path

from clinrag.data_models import ClinicalDocument


def load_jsonl_documents(path: str | Path) -> list[ClinicalDocument]:
    """Load EHR-like documents from JSONL."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Document file not found: {file_path}")

    docs: list[ClinicalDocument] = []
    for line_no, line in enumerate(file_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            docs.append(
                ClinicalDocument(
                    doc_id=item["doc_id"],
                    patient_id=item["patient_id"],
                    resource_type=item.get("resource_type", "Unknown"),
                    section=item.get("section", "unknown"),
                    timestamp=item.get("timestamp", "unknown"),
                    text=item["text"],
                    metadata=item.get("metadata", {}),
                )
            )
        except (json.JSONDecodeError, KeyError) as exc:
            raise ValueError(f"Invalid JSONL document at {file_path}:{line_no}: {exc}") from exc
    return docs


def load_qrels(path: str | Path) -> list[dict]:
    """Load test questions with relevant document IDs."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Qrels file not found: {file_path}")
    payload = json.loads(file_path.read_text(encoding="utf-8"))
    return list(payload.get("queries", []))
