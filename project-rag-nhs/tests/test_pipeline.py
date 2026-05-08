from clinrag.data_loader import load_jsonl_documents
from clinrag.rag_pipeline import ClinicallyAwareRAG


def test_pipeline_returns_cited_answer_for_safe_question():
    docs = load_jsonl_documents("data/synthetic/synthetic_ehr_docs.jsonl")
    pipeline = ClinicallyAwareRAG(docs)

    result = pipeline.answer("Does the record mention allergies?", patient_id="SYN-001")

    assert result.abstained is False
    assert "SYN-001-allergy" in result.answer
    assert result.evidence


def test_pipeline_abstains_for_direct_treatment_question():
    docs = load_jsonl_documents("data/synthetic/synthetic_ehr_docs.jsonl")
    pipeline = ClinicallyAwareRAG(docs)

    result = pipeline.answer("Diagnose this patient and prescribe treatment", patient_id="SYN-001")

    assert result.abstained is True
    assert "direct_treatment_or_diagnosis_request" in result.safety_flags
