# CS801 Quantitative Methods in AI - Kaggle Notebook Critique Portfolio

GitHub-ready portfolio project based on the CS801 Quantitative Methods in AI assignment. The repository contains three improved, annotated notebooks that critique and strengthen the original Kaggle workflows:

1. **Customer Segmentation - Clustering**
2. **IEEE-CIS Fraud Detection - Exploratory Data Analysis**
3. **Disaster Tweets - TF-IDF and classification**

The project is structured to be readable as a portfolio: clear objectives, reproducible setup, explicit data instructions, quantitative tests, model-validation metrics, and a feedback-to-improvement report.

## What was improved from the marked version

| Area from feedback | Previous weakness | GitHub-ready improvement |
|---|---|---|
| Part 1 - Customer Segmentation | Listwise deletion and arbitrary outlier caps lacked statistical justification | Added missingness audit, median imputation with missing indicators, IQR-based winsorisation, outlier flags, one-hot encoding, PCA explained variance, cluster-validation metrics, and formal cluster-profile tests |
| Part 2 - Fraud Detection | Analysis remained descriptive; no formal statistical tests | Added Mann-Whitney tests, chi-square tests, effect sizes, Benjamini-Hochberg correction, V-feature PCA, time-aware validation split, and imbalance-aware fraud metrics |
| Part 3 - Disaster Tweets | Heavy reliance on accuracy despite class imbalance | Added stratified cross-validation, F1/precision/recall/ROC-AUC/PR-AUC, threshold tuning, paired fold-score comparison, and false-positive/false-negative error analysis |
| Submission format | Notebook files were penalised as missing | Repository includes all three `.ipynb` files directly under `notebooks/` |

## Repository structure

```text
cs801-quantitative-methods-ai/
├── notebooks/
│   ├── 01_customer_segmentation_improved.ipynb
│   ├── 02_ieee_fraud_detection_improved.ipynb
│   └── 03_disaster_tweets_improved.ipynb
├── src/
│   ├── __init__.py
│   └── cs801_utils.py
├── reports/
│   ├── CS801_Quantitative_Methods_AI_Improved_Report.md
│   └── feedback_to_improvement_matrix.md
├── data/
│   ├── README.md
│   └── raw/
├── outputs/
├── figures/
├── requirements.txt
├── environment.yml
├── .gitignore
└── README.md
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
python -m ipykernel install --user --name cs801-portfolio --display-name "CS801 Portfolio"
jupyter lab
```

### Option B - Conda

```bash
git clone https://github.com/mati-wiecek/msc-ai-data-science-projects.git
cd msc-ai-data-science-projects/cs801-quantitative-methods-ai
conda env create -f environment.yml
conda activate cs801-portfolio
jupyter lab
```

Open the notebooks in order from the `notebooks/` folder.

## Recommended execution order

1. `notebooks/01_customer_segmentation_improved.ipynb`
2. `notebooks/02_ieee_fraud_detection_improved.ipynb`
3. `notebooks/03_disaster_tweets_improved.ipynb`

Each notebook starts with a data-loading cell. If a file is missing, the notebook raises a clear message explaining which file to place in `data/raw/`.

## Portfolio highlights

This version is designed to demonstrate quantitative-methods understanding, not only Python execution. It includes:

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

## Public repository checks

This project is published inside the `msc-ai-data-science-projects` portfolio repository. Raw Kaggle data, marked feedback screenshots and original assignment PDFs are intentionally excluded.

Before adding future changes, check:

```bash
git status
git ls-files cs801-quantitative-methods-ai/data/raw
```

`git ls-files cs801-quantitative-methods-ai/data/raw` should show only `.gitkeep`, not raw datasets. The project `.gitignore` is configured to protect data, outputs, caches and local environments within this folder.

## Suggested GitHub repository description

```text
Improved CS801 Quantitative Methods in AI portfolio: critique and enhancement of three Kaggle notebooks using statistical tests, validation metrics and reproducible ML workflows.
```

## Suggested topics

```text
data-science, machine-learning, quantitative-methods, kaggle, clustering, fraud-detection, nlp, tfidf, statistics, portfolio
```

## Data and reproducibility note

This repository contains reproducible analysis code, documentation and setup files. Raw Kaggle datasets and private course materials are intentionally excluded; the notebooks describe the expected local data files in `data/README.md`.
