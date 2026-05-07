# Feedback-to-improvement matrix

This file records how the marked feedback was translated into concrete project changes.

| Feedback item | Concrete change in this repository | Where implemented |
|---|---|---|
| Part 1: "Outlier caps and listwise deletion lack statistical justification" | Replaced row dropping with a missingness audit, median imputation and missingness indicators. Replaced hard caps with IQR-based winsorisation and outlier flags. | `notebooks/01_customer_segmentation_improved.ipynb`, cells `MW-IMPROVED #03` to `#06` |
| Part 1: "Missing concrete follow-through of remedies" | Added full replacement pipeline: one-hot encoding, robust scaling, PCA explained variance, cluster validation, and statistical profile tests. | `notebooks/01_customer_segmentation_improved.ipynb`, cells `MW-IMPROVED #06` to `#11` |
| Part 2: "No formal statistical test to confirm significance" | Added Mann-Whitney tests for numeric fraud/non-fraud feature differences and chi-square tests for categorical features, with Cramer's V and FDR-adjusted p-values. | `notebooks/02_ieee_fraud_detection_improved.ipynb`, cells `MW-IMPROVED #17` to `#19` |
| Part 2: "Analysis remains descriptive" | Added time-aware validation, a class-weighted baseline model, PR curve, F1 threshold tuning and V-feature PCA. | `notebooks/02_ieee_fraud_detection_improved.ipynb`, cells `MW-IMPROVED #20` to `#23` |
| Part 3: "Heavy reliance on accuracy despite class imbalance" | Added stratified cross-validation and metrics: precision, recall, F1, ROC-AUC, average precision/PR-AUC and balanced accuracy. | `notebooks/03_disaster_tweets_improved.ipynb`, cells `MW-IMPROVED #26` to `#31` |
| Part 3: "Analysis remains descriptive" | Added hyperparameter tuning against F1, threshold tuning, paired fold-score comparison and error analysis. | `notebooks/03_disaster_tweets_improved.ipynb`, cells `MW-IMPROVED #30` to `#33` |
| Penalty: no `.ipynb` submitted | All three improved notebook files are included directly in the repository. | `notebooks/` |
| GitHub readiness | Added README, requirements, conda environment, `.gitignore`, data instructions, reusable helper functions and outputs/figures folders. | Repository root |
