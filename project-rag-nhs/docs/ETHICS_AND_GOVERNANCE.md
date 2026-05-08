# Ethics and governance notes

This project sits in a high-risk domain because Electronic Health Records may contain sensitive health data and because generated clinical text may influence decisions. Even for a research prototype, governance must be visible in the design.

## Current safe starting position

- Use synthetic data in the public GitHub repository.
- Do not process real patient data without written approval.
- Do not send any patient-identifiable data to external APIs.
- Treat all EHR-like text as sensitive during design and testing.
- Keep outputs grounded in retrieved evidence and clearly non-clinical.

## UK/NHS governance themes to discuss

### 1. Data protection

Health data is special category data under UK data protection law and requires additional protection and a valid lawful basis/condition before processing.

Project implication: the public prototype should explain why it uses synthetic data and why any restricted EHR data must stay outside the repository.

### 2. NHS digital technology assessment

Digital health technologies entering NHS and social care contexts are assessed against areas such as clinical safety, data protection, technical security, interoperability, usability and accessibility.

Project implication: even if this is only a research prototype, the architecture can map risks and mitigations to these categories.

### 3. Clinical safety standards

NHS clinical risk management standards distinguish between manufacturers/developers of health IT and health organisations deploying health IT.

Project implication: this prototype should include a risk register, hazard thinking, evidence constraints and clear non-clinical-use boundaries.

### 4. Data Security and Protection Toolkit

Organisations with access to NHS patient data and systems use the Data Security and Protection Toolkit to demonstrate data security and information governance performance.

Project implication: this project should not claim compliance, but can reference relevant categories as part of the governance discussion.

### 5. Evidence standards for digital health technologies

NICE evidence standards help evaluators and decision makers assess digital health technologies.

Project implication: the evaluation should not only measure accuracy; it should also discuss evidence quality, intended use, risks and generalisability.

## Safety requirements for the prototype

- Patient-specific filtering to reduce wrong-patient retrieval.
- Evidence citations in every answer.
- Abstention when retrieved evidence is insufficient.
- Safety gate for direct treatment, diagnosis, dosing or prescribing requests.
- Logs without sensitive content where possible.
- No hidden prompts containing patient information.
- No GitHub commits containing real patient data.

## Ethics application discussion points

Open governance questions:

1. Is formal university ethics approval required if only synthetic/public de-identified data is used?
2. Does use of MIMIC-IV require separate approval or only credentialed access/training?
3. Are cloud LLM APIs allowed for any data source?
4. Is clinician review part of the project, and would that require additional ethics approval?
5. What wording should be used to state that the prototype is not for clinical deployment?

## Public repository statement

Recommended public safety statement:

> This repository contains a research prototype using synthetic data. It is not a clinical tool, not a medical device and not intended for use in patient care. No real patient-identifiable data should be committed to this repository.
