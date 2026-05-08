# Project plan

## Working title

Clinically-Aware Retrieval-Augmented Generation (RAG) Systems for NHS Electronic Health Records.

## Project purpose

Build and evaluate a research prototype that answers EHR-grounded questions by retrieving relevant record evidence and producing cautious, cited responses. The project should compare a baseline RAG system with clinically-aware improvements such as structured clinical context, patient-specific filtering, provenance, abstention and safety controls.

## Proposed deliverables

1. Literature review on RAG, EHR question answering, clinical NLP and AI safety in health records.
2. Data plan using synthetic data first, then an approved public/de-identified dataset if permitted.
3. Baseline RAG implementation.
4. Clinically-aware RAG implementation.
5. Evaluation dataset and metrics.
6. Risk, ethics and governance discussion.
7. Technical report and reproducible repository.

## Step-by-step plan

### Phase 1 — Scoping and governance

- Confirm exact academic requirements, marking criteria, deadline and expected artefacts.
- Confirm whether the project is expected to be purely research, software engineering, experimental evaluation, or a mixed research prototype.
- Define what “clinically-aware” means in measurable terms.
- Decide what data can be used: synthetic data, public EHR data, MIMIC-IV/MIMIC demo, FHIR demo, or another approved dataset.
- Confirm ethics and information governance requirements before any real or restricted data is accessed.

### Phase 2 — Literature and baseline design

- Review RAG for healthcare and EHR question answering.
- Review clinical safety, hallucination, provenance, abstention and evaluation methods.
- Implement a transparent baseline: lexical retrieval plus deterministic cited answer generation.
- Define baseline metrics: Precision@k, Recall@k, MRR, answer faithfulness, citation coverage and abstention accuracy.

### Phase 3 — Data representation

- Create a small synthetic dataset for fast iteration.
- Map documents to clinically meaningful sections: problems, medications, allergies, results, observations, procedures and encounters.
- Add structured metadata such as patient ID, timestamp, resource type and section.
- If approved, create loaders for public/de-identified EHR datasets.

### Phase 4 — Clinically-aware retrieval

- Add patient-specific filtering.
- Add section-aware ranking, e.g. medication questions prioritise medication sections.
- Add temporal ranking, e.g. latest active medications should rank higher than old entries.
- Add clinical entity extraction or coding if feasible.
- Compare lexical, dense and hybrid retrieval.

### Phase 5 — Clinically-aware generation

- Require every answer to cite retrieved evidence.
- Add abstention when evidence is weak or contradictory.
- Separate record summarisation from clinical recommendation.
- Add clear uncertainty language.
- Add a safety gate for direct diagnosis, prescribing or dosing requests.

### Phase 6 — Evaluation

- Build a gold set of questions with relevant document IDs.
- Evaluate retrieval quality.
- Evaluate answer faithfulness and citation accuracy.
- Evaluate unsafe query handling.
- Compare baseline RAG with clinically-aware RAG.
- Analyse failure cases: missing evidence, wrong patient, wrong timeline, hallucinated answer, unsafe recommendation.

### Phase 7 - Report and final artefacts

- Write methodology and experiment results.
- Discuss ethical, legal and NHS deployment constraints.
- Prepare diagrams, tables and reproducibility instructions.
- Clean GitHub history and check that no sensitive data is committed.
- Prepare defence presentation and likely viva questions.

## Suggested milestone checklist

- [ ] Research question and scope are confirmed.
- [ ] Data source confirmed.
- [ ] Ethics/governance path confirmed.
- [ ] Baseline pipeline working.
- [ ] Evaluation set drafted.
- [ ] Clinically-aware features implemented.
- [ ] Experiments run and results saved.
- [ ] Error analysis completed.
- [ ] Technical report draft ready.
- [ ] GitHub repository cleaned and documented.
