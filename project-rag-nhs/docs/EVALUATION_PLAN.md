# Evaluation plan

## Evaluation goal

Show whether clinically-aware retrieval and safety controls improve record-grounded answer quality compared with a baseline RAG system.

## Retrieval metrics

For each question, define one or more relevant document IDs.

- **Precision@k:** proportion of retrieved documents in top k that are relevant.
- **Recall@k:** proportion of all relevant documents retrieved in top k.
- **MRR:** mean reciprocal rank of the first relevant document.
- **nDCG@k:** optional if graded relevance labels are added.

## Generation metrics

- **Faithfulness:** answer claims are supported by retrieved evidence.
- **Citation coverage:** every clinical claim has a citation.
- **Answer relevance:** answer addresses the question.
- **Abstention accuracy:** system abstains when evidence is insufficient or unsafe.
- **Contradiction handling:** system avoids selecting one claim when evidence conflicts.

## Safety metrics

- Wrong-patient retrieval rate.
- Unsupported clinical claim rate.
- Unsafe recommendation rate.
- PHI leakage rate in logs/outputs.
- Direct diagnosis/prescribing request handling.

## Example experiment table

| System | Retrieval | Clinical awareness | Generator | Key metrics |
|---|---|---|---|---|
| Baseline A | TF-IDF | Patient filter only | Template | P@k, R@k, MRR |
| Baseline B | BM25 | Patient filter only | Template or LLM | P@k, R@k, MRR, faithfulness |
| System C | Dense | Patient + section metadata | LLM | P@k, R@k, citation accuracy |
| System D | Hybrid + reranking | Patient + section + time + safety | LLM | all metrics + safety |

## Suggested question categories

1. Medication list questions.
2. Allergy questions.
3. Abnormal lab/result questions.
4. Timeline questions.
5. Problem-list questions.
6. Conflicting evidence questions.
7. Insufficient evidence questions.
8. Unsafe clinical instruction questions.

## Failure analysis template

For every failed query, record:

- question;
- expected evidence;
- retrieved evidence;
- generated answer;
- failure category;
- likely cause;
- mitigation.
