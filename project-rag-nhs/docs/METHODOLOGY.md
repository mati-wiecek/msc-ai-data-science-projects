# Methodology draft

## 1. Problem definition

Electronic Health Records contain structured and unstructured clinical information. A RAG system may help answer record-grounded questions by retrieving relevant evidence and then generating a natural-language response. However, in clinical contexts, ordinary RAG can fail by retrieving the wrong patient, ignoring time, omitting allergies or medications, hallucinating unsupported claims, or providing unsafe recommendations.

## 2. Baseline system

The initial baseline consists of:

1. synthetic EHR-like documents;
2. TF-IDF retrieval over document text and metadata;
3. patient-specific filtering;
4. deterministic answer generation from retrieved snippets;
5. citation of document IDs.

This baseline is intentionally simple so later improvements can be measured.

## 3. Clinically-aware extensions

Potential clinically-aware extensions:

- section-aware ranking: medication questions prioritise medication resources;
- temporal ranking: recent active entries rank higher than outdated entries;
- clinical entity matching: conditions, medications, allergies, labs;
- FHIR-inspired metadata: resource type, section, timestamp, subject;
- safety-aware prompting/generation;
- abstention when evidence is insufficient;
- provenance and citation checks.

## 4. Experimental design

Compare at least two systems:

- Baseline RAG: lexical retrieval + grounded answer.
- Clinically-aware RAG: baseline plus selected clinical context and safety features.

Possible additional systems:

- Dense retrieval baseline.
- Hybrid lexical+dense retrieval.
- Clinically reranked retrieval.

## 5. Evaluation dimensions

- Retrieval relevance: Precision@k, Recall@k, MRR, nDCG.
- Grounding: answer statements supported by retrieved evidence.
- Citation quality: whether cited documents actually support the answer.
- Safety: unsafe query refusal/abstention, wrong-patient evidence, overconfident answer rate.
- Usability: clarity, traceability and uncertainty communication.

## 6. Expected limitations

- Synthetic data may not reflect real EHR complexity.
- Public de-identified data may not represent NHS workflows.
- LLM-based evaluation can be biased and must be treated cautiously.
- Clinical review may be unavailable within the project timeline.
- A research prototype cannot demonstrate readiness for NHS deployment.
