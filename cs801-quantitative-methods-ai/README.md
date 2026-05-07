# CS801 Quantitative Methods in AI - Comparative ML Workflow Analysis

This project analyses three public Kaggle-style machine learning workflows through the lens of quantitative methods, statistical validity and reproducible evaluation. The repository contains annotated notebooks covering:

1. **Customer Segmentation - Clustering**
2. **IEEE-CIS Fraud Detection - Exploratory Data Analysis**
3. **Disaster Tweets - TF-IDF and classification**

The project is structured as a reproducible research artefact: each notebook defines an objective, motivates the methodological choices, applies appropriate statistical tests or validation metrics, and documents the assumptions required to run the analysis locally.

## Research Questions and Methods

| Case study | Research question | Quantitative methods |
|---|---|---|
| Customer Segmentation | Can customer groups be identified in a way that is statistically defensible and interpretable? | Missingness audit, median imputation with missing indicators, IQR-based winsorisation, one-hot encoding, PCA explained variance, cluster-validation metrics, Kruskal-Wallis tests and chi-square tests for cluster profiles. |
| IEEE-CIS Fraud Detection | Which transaction and identity features show measurable association with fraud, and how should rare-event evaluation be framed? | Mann-Whitney tests, chi-square tests, effect sizes, Benjamini-Hochberg correction, V-feature PCA, time-aware validation split, PR-AUC, F1, recall and threshold analysis. |
| Disaster Tweets | How should disaster-tweet classifiers be evaluated when class balance and false-negative cost matter? | Stratified cross-validation, precision, recall, F1, ROC-AUC, PR-AUC, threshold tuning, paired fold-score comparison and false-positive/false-negative error analysis. |

## Repository structure

```text
cs801-quantitative-methods-ai/
|-- notebooks/
|   |-- 01_customer_segmentation_analysis.ipynb
|   |-- 02_ieee_fraud_detection_analysis.ipynb
|   `-- 03_disaster_tweets_analysis.ipynb
|-- src/
|   |-- __init__.py
|   `-- cs801_utils.py
|-- reports/
|   |-- CS801_Quantitative_Methods_AI_Methodology_Report.md
|   |-- CS801_Quantitative_Methods_AI_Methodology_Report.pdf
|   `-- methodology_revision_matrix.md
|-- data/
|   |-- README.md
|   `-- raw/
|-- outputs/
|-- figures/
|-- requirements.txt
|-- environment.yml
|-- .gitignore
`-- README.md
```

## Data

Raw Kaggle data is **not included** in the repository because competition and dataset files can be large and may have redistribution restrictions. Place the files in `data/raw/` using the names below:

| Notebook | Required file names |
|---|---|
| Customer Segmentation | `marketing_campaign.csv` |
| IEEE-CIS Fraud Detection | `fraud_train_transaction.csv`, `fraud_train_identity.csv`, optionally `fraud_test_transaction.csv`, `fraud_test_identity.csv` |
| Disaster Tweets | `NLP_train.csv`, optionally `NLP_test.csv` |

See [`data/README.md`](data/README.md) for exact instructions.

## Quick start

### Option A - Python virtual environment

```bash
git clone https://github.com/mati-wiecek/msc-ai-data-science-projects.git
cd msc-ai-data-science-projects/cs801-quantitative-methods-ai

python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name cs801-methods --display-name "CS801 Methods"
jupyter lab
```

### Option B - Conda

```bash
git clone https://github.com/mati-wiecek/msc-ai-data-science-projects.git
cd msc-ai-data-science-projects/cs801-quantitative-methods-ai
conda env create -f environment.yml
conda activate cs801-methods
jupyter lab
```

Open the notebooks in order from the `notebooks/` folder.

## Recommended execution order

1. `notebooks/01_customer_segmentation_analysis.ipynb`
2. `notebooks/02_ieee_fraud_detection_analysis.ipynb`
3. `notebooks/03_disaster_tweets_analysis.ipynb`

Each notebook starts with a data-loading cell. If a file is missing, the notebook raises a clear message explaining which file to place in `data/raw/`.

## Methodological Highlights

The project emphasises quantitative reasoning rather than notebook execution alone. It includes:

- missingness diagnostics and imputation reasoning;
- IQR-based outlier treatment instead of arbitrary caps;
- one-hot encoding for nominal categories;
- PCA explained-variance analysis;
- silhouette, Calinski-Harabasz and Davies-Bouldin cluster validation;
- chi-square tests, Mann-Whitney tests and effect sizes;
- false-discovery-rate adjustment;
- time-aware validation for fraud detection;
- precision-recall analysis and PR-AUC for imbalanced classification;
- threshold tuning and error analysis for disaster-tweet classification.

## Version Control and Data Policy

Raw Kaggle data, local outputs and private course materials are intentionally excluded.

Before adding future changes, check:

```bash
git status
git ls-files cs801-quantitative-methods-ai/data/raw
```

`git ls-files cs801-quantitative-methods-ai/data/raw` should show only `.gitkeep`, not raw datasets. The project `.gitignore` is configured to protect data, outputs, caches and local environments within this folder.

## Data and reproducibility note

This repository contains reproducible analysis code, documentation and setup files. Raw Kaggle datasets and private course materials are intentionally excluded; the notebooks describe the expected local data files in `data/README.md`.
