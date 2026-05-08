# Data handling plan

## Allowed in this repository

- Synthetic EHR-style records created for demonstration.
- Public documentation and code.
- Configuration templates without secrets.
- Evaluation scripts and toy question sets.

## Not allowed in this repository

- Real patient records.
- NHS extracts.
- Restricted MIMIC files if redistribution is not permitted.
- API keys or cloud credentials.
- Private meeting notes containing sensitive information.
- Any text that could identify a patient, clinician or institution without permission.

## Data source options

### Option 1 — synthetic-only

Best for the earliest stage and public GitHub. Lowest governance burden, but weaker realism.

### Option 2 — MIMIC-IV demo/FHIR demo

Potentially useful for FHIR-style prototyping and small-scale experiments. Confirm licence and redistribution restrictions before committing any data.

### Option 3 — MIMIC-IV full access

More realistic and widely used in clinical NLP research, but access requires credentialing and data-use rules. Keep data outside GitHub.

### Option 4 — NHS data

Highest realism, but highest governance burden. Do not plan around NHS data unless a viable, approved route is confirmed.

## Local folder pattern

```text
project-root/
├── data/synthetic/      # committed toy data
├── data/raw/            # ignored placeholder only
├── data/private/        # ignored local-only folder
└── outputs/             # ignored generated outputs
```

## Pre-commit checklist

- [ ] `git status` reviewed.
- [ ] No `.env` file staged.
- [ ] No raw clinical data staged.
- [ ] No private notes staged.
- [ ] No generated vector store containing restricted text staged.
- [ ] Tests pass on synthetic data.
