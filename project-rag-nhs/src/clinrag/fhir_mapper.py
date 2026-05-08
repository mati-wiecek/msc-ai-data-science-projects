from __future__ import annotations

from typing import Any

from clinrag.data_models import ClinicalDocument


def document_to_minimal_fhir_like_resource(doc: ClinicalDocument) -> dict[str, Any]:
    """Map a synthetic document to a minimal FHIR-inspired dictionary.

    This is not a full FHIR implementation. It is a placeholder for later work using
    proper FHIR libraries, profiles and validation.
    """
    return {
        "resourceType": doc.resource_type,
        "id": doc.doc_id,
        "subject": {"reference": f"Patient/{doc.patient_id}"},
        "meta": {
            "tag": [
                {"system": "https://example.org/clinrag/section", "code": doc.section},
                {"system": "https://example.org/clinrag/source", "code": "synthetic"},
            ]
        },
        "effectiveDateTime": doc.timestamp,
        "text": {"status": "generated", "div": doc.text},
    }
