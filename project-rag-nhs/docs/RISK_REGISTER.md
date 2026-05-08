# Risk register

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---:|---:|---|
| R1 | Real patient data accidentally committed to GitHub | Medium | Very high | Use synthetic data only in repo, `.gitignore`, pre-commit review, no raw data folder tracking. |
| R2 | Data access delays prevent realistic experiments | High | Medium | Start with synthetic data and public demo data; design methods independent of a single dataset. |
| R3 | RAG system hallucinates unsupported clinical claims | High | High | Require citations, faithfulness checks, abstention and deterministic baseline. |
| R4 | Wrong-patient retrieval | Medium | High | Patient-specific filtering and evaluation of wrong-patient retrieval rate. |
| R5 | Unsafe output gives diagnosis, treatment or dosing advice | Medium | High | Safety gate for direct treatment questions; non-clinical-use wording; output limited to evidence summary. |
| R6 | Scope becomes too broad | High | Medium | Define a minimum viable research contribution and prioritise one clear evaluation path. |
| R7 | LLM API privacy/cost constraints | Medium | Medium | Keep baseline local; use LLM only after data governance is confirmed. |
| R8 | Evaluation lacks credibility | Medium | High | Build gold qrels, document metrics, add expert review if feasible. |
| R9 | Public dataset differs from NHS records | High | Medium | State limitation clearly; use NHS as motivation rather than claiming deployment readiness. |
| R10 | Clinical terminology complexity reduces retrieval quality | Medium | Medium | Use structured metadata, synonyms and section-aware ranking as planned extensions. |
