# CS982 Big Data Technologies - Pettan Battle Card Analysis

This project analyses a structured dataset of Dragon Ball Z Pettan Battle cards using a reproducible data science workflow: data cleaning, feature engineering, statistical testing, unsupervised clustering and supervised classification.

The project is framed as a compact big-data technologies case study. The dataset is not large in volume, so the emphasis is on disciplined analytical engineering: clear data preparation, leakage-aware modelling, validation, interpretable outputs and honest limitations.

## Research Questions

| Question | Approach |
|---|---|
| Do Gold and Platinum cards have significantly higher HP and Attack than Silver and Bronze cards? | Mann-Whitney U tests, median differences and rarity-level visualisation. |
| Can cards be grouped into intuitive archetypes using only HP and Attack? | Standardised K-Means clustering, inertia and silhouette diagnostics. |
| Can high-tier rarity be predicted from card statistics alone? | Median-imputation and scaling pipeline with class-balanced logistic regression, stratified cross-validation and holdout evaluation. |

## Repository Structure

```text
cs982-dragon-ball-pettan-big-data/
|-- data/
|   |-- README.md
|   `-- processed/
|       `-- pettan_cards_clean.csv
|-- notebooks/
|   `-- 01_pettan_big_data_analysis.ipynb
|-- reports/
|   |-- final_metrics.json
|   `-- methodology_report.md
|-- src/
|   |-- __init__.py
|   `-- pettan_utils.py
|-- requirements.txt
|-- environment.yml
|-- .gitignore
`-- README.md
```

## Results Summary

| Component | Result |
|---|---|
| Dataset size | 295 cards, 22 source columns |
| Rarity distribution | 119 bronze, 97 silver, 63 gold, 16 platinum |
| HP tier comparison | High-tier median `8700` vs low-tier median `4100` |
| Attack tier comparison | High-tier median `7350` vs low-tier median `3200` |
| Statistical test | Mann-Whitney p-values below `2e-39` for both HP and Attack |
| Clustering | K-Means selected `k = 5` by silhouette score |
| Supervised model | Logistic regression pipeline reached perfect CV and holdout scores using HP and Attack |

The perfect supervised scores are interpreted cautiously: rarity tier appears strongly encoded by HP and Attack ranges in this dataset. The model is therefore useful as a transparent validation of the data structure, not as proof that the task is intrinsically difficult.

## Setup

```bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
python -m ipykernel install --user --name cs982-pettan-big-data --display-name "CS982 Pettan Big Data"
jupyter lab
```

Open:

```text
notebooks/01_pettan_big_data_analysis.ipynb
```

## Data and Reproducibility Note

The repository includes only the cleaned tabular dataset and technical analysis files. It excludes private spreadsheets, PDFs, screenshots and card images.

Dragon Ball and related names are trademarks of their respective owners. This project is an educational data analysis exercise and is not affiliated with Bandai, Toei Animation or the Dragon Ball franchise.
