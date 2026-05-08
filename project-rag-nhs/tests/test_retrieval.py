from clinrag.data_loader import load_jsonl_documents
from clinrag.retrieval import TfidfRetriever


def test_tfidf_retrieves_medication_doc_for_patient_syn_001():
    docs = load_jsonl_documents("data/synthetic/synthetic_ehr_docs.jsonl")
    retriever = TfidfRetriever()
    retriever.fit(docs)

    results = retriever.search("What medications is patient SYN-001 taking?", patient_id="SYN-001", top_k=3)

    assert results
    assert results[0].doc.doc_id == "SYN-001-meds"
    assert all(result.doc.patient_id == "SYN-001" for result in results)
