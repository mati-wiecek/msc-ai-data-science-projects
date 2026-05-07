# CS801 Quantitative Methods in AI - Methodology Report

## Introduction

This report accompanies three annotated notebooks that examine machine learning workflows from a quantitative-methods perspective. The aim is to show how statistical testing, validation design, effect-size reporting and reproducibility controls can make applied AI analysis more defensible.

The three case studies cover unsupervised customer segmentation, rare-event fraud detection and binary text classification. Together, they illustrate how modelling decisions should be connected to the structure of the data, the assumptions behind the method and the costs of different evaluation errors.

---

## Part 1 - Customer Segmentation: Clustering

### Objective and success criteria

The objective is to segment customers into interpretable groups using demographic and purchasing variables. A useful clustering workflow should preserve the sample where possible, avoid arbitrary preprocessing rules, justify dimensionality reduction, validate candidate cluster solutions and support final cluster interpretations with statistical evidence.

### Quantitative methods used

`MW-METHOD #03` audits missingness before preprocessing. This matters because listwise deletion can change the sample composition when missingness is associated with household, education or response variables. The notebook checks whether `Income` missingness differs across selected categorical variables using chi-square tests and reports Cramer's V as an effect size. The modelling pipeline then uses median imputation and missingness indicators so that missingness is handled explicitly rather than hidden.

`MW-METHOD #05` treats outliers with Tukey IQR bounds. Extreme values are winsorised and outlier indicator variables are retained. This reduces the influence of extreme observations on distance-based methods while keeping potentially meaningful high-value customers in the analysis.

`MW-METHOD #06` uses one-hot encoding for nominal variables and robust scaling for numeric variables. This avoids imposing artificial ordinal structure on categories and keeps distance-based PCA and clustering from being dominated by high-magnitude features.

`MW-METHOD #07` reports PCA explained variance and uses cumulative variance to choose the representation used for clustering. A lower-dimensional projection is retained for visualisation, while the modelling representation is selected according to retained variance.

`MW-METHOD #08` evaluates candidate cluster solutions using silhouette score, Calinski-Harabasz index and Davies-Bouldin score. `MW-METHOD #11` then tests whether final cluster profiles differ using Kruskal-Wallis tests for numerical variables and chi-square tests for categorical variables, with effect sizes and Benjamini-Hochberg correction.

### Limitations

Unsupervised segmentation has no single ground-truth label, so the final interpretation still requires domain judgement. The quantitative workflow reduces arbitrariness, but cluster labels should be treated as analytical hypotheses rather than fixed customer personas.

---

## Part 2 - IEEE-CIS Fraud Detection: Exploratory Analysis and Baseline Modelling

### Objective and success criteria

The objective is to investigate a large fraud-detection dataset, identify feature groups associated with fraudulent transactions and evaluate a simple baseline under class imbalance. Because fraud is a rare-event problem with temporal structure, success should be measured using time-aware validation and metrics such as precision, recall, F1 and PR-AUC rather than accuracy alone.

### Quantitative methods used

`MW-METHOD #15` quantifies class imbalance and connects the fraud prevalence to metric choice. Accuracy is not sufficient when the negative class dominates, so the analysis uses precision, recall, F1, ROC-AUC and PR-AUC.

`MW-METHOD #16` creates a chronological validation split. This reflects the temporal nature of transaction data and reduces the risk of overestimating performance through random splitting when future transactions may differ from past transactions.

`MW-METHOD #17` applies Mann-Whitney U tests to numeric transaction features. This non-parametric test is appropriate for skewed transaction variables. Rank-biserial correlation is reported so that differences are interpreted with an effect-size estimate rather than p-values alone.

`MW-METHOD #18` applies chi-square tests to categorical features such as product code, card variables, email domains, `M` indicators and identity features when present. Cramer's V is used as an association measure, and Benjamini-Hochberg correction controls the false-discovery rate across many feature tests.

`MW-METHOD #20` analyses the high-dimensional `V` feature block using PCA. `MW-METHOD #21` and `MW-METHOD #22` connect the exploratory findings to a class-weighted logistic-regression baseline, PR-AUC and threshold tuning from the precision-recall curve.

### Limitations

The baseline model is deliberately simple. It is intended to demonstrate how quantitative EDA can inform modelling and evaluation, not to maximise benchmark performance. A production-oriented fraud model would require broader feature engineering, model comparison, drift monitoring and careful operational threshold selection.

---

## Part 3 - Disaster Tweets: TF-IDF and Classification

### Objective and success criteria

The objective is to classify tweets as disaster-related or not. Because the task can involve asymmetric error costs, evaluation should consider recall, precision, F1 and PR-AUC alongside accuracy. The text pipeline should also be reproducible so that preprocessing decisions can be inspected and repeated.

### Quantitative methods used

`MW-METHOD #26` reports class balance and motivates the use of metrics beyond accuracy. In an alerting context, false negatives may be especially costly, so recall and PR-AUC provide important complementary views of performance.

`MW-METHOD #27` implements a reproducible text-cleaning function. It removes URLs, mentions and punctuation while preserving negation words such as `not`, `no` and `nor`, because negation can change meaning and therefore affect TF-IDF weights and classifier coefficients.

`MW-METHOD #28` uses a stratified holdout split and stratified k-fold cross-validation. Stratification preserves class proportions in each split, reducing sampling bias when estimating generalisation performance.

`MW-METHOD #29` compares models using accuracy, balanced accuracy, precision, recall, F1, ROC-AUC and average precision. `MW-METHOD #30` tunes a TF-IDF Logistic Regression model using F1 as the objective. `MW-METHOD #31` tunes the decision threshold using the precision-recall curve, and `MW-METHOD #33` inspects false negatives and false positives.

### Limitations

The notebook favours lightweight scikit-learn models for reproducibility. A natural extension would compare the TF-IDF baseline with transformer embeddings or fine-tuned language models while keeping the same cross-validation and PR-AUC/F1-focused evaluation discipline.

---

## Overall conclusion

Across the three case studies, the project shows how applied AI workflows become more defensible when modelling decisions are paired with statistical tests, effect sizes, validation design and transparent data-handling assumptions. The analysis moves beyond visual inspection by quantifying uncertainty, checking associations, selecting metrics that match the task and documenting reproducible execution requirements.
