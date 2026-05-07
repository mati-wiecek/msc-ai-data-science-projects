# Methodology Revision Matrix

This file summarises the methodological decisions used across the three case studies and links each decision to its implementation in the notebooks.

| Case study | Methodological risk | Research-oriented response | Where implemented |
|---|---|---|---|
| Customer Segmentation | Missing values and outliers can bias cluster structure if handled by deletion or arbitrary thresholds. | Audit missingness, preserve rows with median imputation and missingness indicators, use IQR-based winsorisation, and retain outlier flags as potential signal. | `notebooks/01_customer_segmentation_analysis.ipynb`, cells `MW-METHOD #03` to `#06` |
| Customer Segmentation | Nominal categories and dimensionality reduction can distort distance-based clustering if not justified. | Use one-hot encoding, robust scaling, PCA explained variance, cluster validation, and statistical profile tests. | `notebooks/01_customer_segmentation_analysis.ipynb`, cells `MW-METHOD #06` to `#11` |
| IEEE-CIS Fraud Detection | Visual EDA alone does not quantify whether fraud and non-fraud transactions differ meaningfully. | Apply Mann-Whitney tests for numeric differences and chi-square tests for categorical associations, with effect sizes and FDR-adjusted p-values. | `notebooks/02_ieee_fraud_detection_analysis.ipynb`, cells `MW-METHOD #17` to `#19` |
| IEEE-CIS Fraud Detection | Rare-event fraud modelling requires validation and metrics aligned with class imbalance and time structure. | Use time-aware validation, a class-weighted baseline model, PR curve analysis, F1 threshold tuning and V-feature PCA. | `notebooks/02_ieee_fraud_detection_analysis.ipynb`, cells `MW-METHOD #20` to `#23` |
| Disaster Tweets | Accuracy can be misleading when class proportions and false-negative cost matter. | Evaluate with stratified cross-validation and precision, recall, F1, ROC-AUC, PR-AUC and balanced accuracy. | `notebooks/03_disaster_tweets_analysis.ipynb`, cells `MW-METHOD #26` to `#31` |
| Disaster Tweets | A single model split does not fully support claims about text-classification performance. | Add hyperparameter tuning against F1, decision-threshold analysis, paired fold-score comparison and false-positive/false-negative error analysis. | `notebooks/03_disaster_tweets_analysis.ipynb`, cells `MW-METHOD #30` to `#33` |
| Repository design | Reproducibility depends on clear setup instructions and reusable helper code. | Include notebooks, data placement instructions, environment files, helper functions, and placeholder folders for local outputs and figures. | Repository root |
