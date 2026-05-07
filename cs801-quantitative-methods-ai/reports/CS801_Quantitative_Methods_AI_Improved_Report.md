# CS801 Quantitative Methods in AI - Improved Report

## Introduction

This report accompanies three improved notebook copies prepared as a GitHub-ready portfolio project. The assignment objective is to critique three Kaggle notebooks and demonstrate how quantitative methods support understanding, evaluation and criticism of AI/ML workflows. The improved notebooks use stable cell labels in the format `MW-IMPROVED #xx`, allowing this report to reference the relevant notebook locations without relying on Jupyter execution numbers.

The marked feedback indicated three main weaknesses: insufficient statistical justification in Part 1, descriptive-only analysis in Part 2, and over-reliance on accuracy in Part 3. The revised notebooks address those points by adding formal tests, effect sizes, validation metrics, class-imbalance-aware evaluation and clearer reproducibility controls.

---

## Part 1 - Customer Segmentation: Clustering

### Objective and success

The primary objective is to segment customers into meaningful groups using demographic and purchasing variables. The original notebook broadly addressed this objective through feature engineering, PCA and clustering, but several methodological choices were not sufficiently justified. The improved version retains the business objective but makes success criteria more quantitative: preprocessing decisions should be defensible, the number of retained PCA components should be supported by explained variance, the cluster count should be validated with multiple metrics, and final customer profiles should be tested statistically rather than described only visually.

### Quantitative methods used

`MW-IMPROVED #03` audits missingness rather than immediately deleting rows. This is important because listwise deletion assumes that missingness is ignorable. The revised notebook tests whether `Income` missingness differs across variables such as education, marital status or household indicators using chi-square tests and reports Cramer's V as an effect size. The modelling pipeline then uses median imputation and missingness indicators, preserving sample size while acknowledging that missingness itself can be informative.

`MW-IMPROVED #05` replaces arbitrary outlier caps with Tukey IQR bounds. Instead of dropping observations based on hard-coded thresholds, it winsorises extreme values and creates outlier indicator variables. This gives a clearer statistical justification and reduces the risk that rare but meaningful high-value customers are removed from the segmentation.

`MW-IMPROVED #06` uses one-hot encoding for nominal variables and robust scaling for numerical variables. This fixes the original risk of label encoding, which can impose a false ordinal relationship on categories and distort Euclidean distances used in PCA and clustering. Scaling is essential because distance-based methods are sensitive to feature magnitude.

`MW-IMPROVED #07` reports PCA explained variance and uses cumulative variance to justify dimensionality reduction. This is stronger than selecting three principal components only because they are easy to visualise. The notebook keeps a 3D projection for plots but uses enough components for modelling to retain a chosen variance threshold.

`MW-IMPROVED #08` evaluates candidate cluster solutions with silhouette score, Calinski-Harabasz index and Davies-Bouldin score. This makes the selected number of clusters more defensible than relying on a single elbow plot. `MW-IMPROVED #11` then tests whether cluster profiles differ significantly using Kruskal-Wallis tests for numerical variables and chi-square tests for categorical variables, including effect sizes and Benjamini-Hochberg p-value correction.

### Limitations and remedies

The original notebook's most important limitations were listwise deletion, arbitrary outlier rules, ordinal encoding of nominal variables, insufficient PCA justification and qualitative-only cluster profiling. The revised notebook supplies concrete remedies for each issue. A remaining limitation is that unsupervised segmentation has no single ground-truth label, so the final cluster interpretation still requires business judgement. However, the revised workflow ensures that this judgement is supported by validation scores, statistical tests and transparent preprocessing choices.

---

## Part 2 - IEEE-CIS Fraud Detection: EDA

### Objective and success

The objective is to explore a large fraud-detection dataset, understand the distribution of the binary `isFraud` target and identify feature groups that may help detect fraudulent transactions. The original notebook successfully highlighted time structure, class imbalance and several visually interesting feature patterns, but the marked feedback correctly noted that the analysis remained mostly descriptive. The improved version turns the EDA into a quantitatively supported analysis and links it to a lightweight baseline model.

### Quantitative methods used

`MW-IMPROVED #15` quantifies class imbalance and explicitly states why accuracy is not a sufficient metric for rare-event fraud detection. This connects the empirical fraud prevalence to evaluation choices such as precision, recall, F1, ROC-AUC and PR-AUC.

`MW-IMPROVED #16` creates a chronological validation split. This is important because the dataset is time-structured: random splits can overestimate performance when the future distribution differs from the past. A time-aware split better reflects the competition setting and reduces leakage risk.

`MW-IMPROVED #17` applies Mann-Whitney U tests to numeric features such as transaction amount, distance-like variables and `C`/`D` feature groups. The Mann-Whitney test is appropriate because many transaction features are skewed and not normally distributed. Rank-biserial correlation is reported as an effect size, so the analysis does not rely only on p-values.

`MW-IMPROVED #18` applies chi-square tests to categorical features including `ProductCD`, card variables, email-domain variables, `M` indicators and identity features when available. Cramer's V is included to assess strength of association. P-values are adjusted using the Benjamini-Hochberg procedure because many feature tests are performed.

`MW-IMPROVED #20` improves treatment of the high-dimensional `V` features by applying PCA rather than reducing the entire block to a simple row-wise mean. This retains a clearer view of the underlying variance structure. `MW-IMPROVED #21` and `#22` connect EDA to modelling through a class-weighted logistic-regression baseline, average precision/PR-AUC and threshold tuning from the precision-recall curve.

### Limitations and remedies

The original EDA used plots effectively but did not confirm whether observed differences were statistically meaningful. The revised notebook remedies this with formal tests, effect sizes and false-discovery-rate correction. It also avoids using test data for supervised decisions. A remaining limitation is that the baseline model is intentionally simple and is not intended to maximise Kaggle performance. Its purpose is to demonstrate how EDA findings can guide evaluation and modelling. Stronger production fraud detection would require more extensive feature engineering, model comparison and temporal monitoring.

---

## Part 3 - Disaster Tweets: TF-IDF and classification

### Objective and success

The objective is to classify tweets as real disaster-related messages or not. The original notebook built a range of text features and classifiers, but the feedback identified an over-reliance on accuracy despite class imbalance. The improved notebook keeps the NLP classification objective but shifts the evaluation framework to metrics that are more appropriate for alerting and risk-classification tasks.

### Quantitative methods used

`MW-IMPROVED #26` reports the class distribution and explains why accuracy can be misleading. In disaster detection, false negatives can be particularly costly, so recall, F1 and PR-AUC are more informative than raw accuracy alone.

`MW-IMPROVED #27` implements a reproducible cleaning function. It removes URLs, mentions and punctuation while preserving negation words such as `not`, `no` and `nor`, because negation can reverse meaning. This is a quantitative issue because cleaning decisions change token frequencies and therefore alter TF-IDF weights and classifier coefficients.

`MW-IMPROVED #28` uses a stratified holdout split and stratified k-fold cross-validation. Stratification preserves class proportions in each fold, which reduces sampling bias when estimating generalisation performance.

`MW-IMPROVED #29` compares models using multiple metrics: accuracy, balanced accuracy, precision, recall, F1, ROC-AUC and average precision. This makes model comparison more robust than a single accuracy score. `MW-IMPROVED #30` tunes a TF-IDF Logistic Regression model using F1 as the objective, aligning hyperparameter selection with the task requirements.

`MW-IMPROVED #31` tunes the probability threshold using the precision-recall curve. This is important because the default 0.5 threshold is not always optimal for imbalanced classification. `MW-IMPROVED #32` adds a paired Wilcoxon comparison of fold F1 scores as supporting evidence when comparing the best cross-validated model with a baseline. `MW-IMPROVED #33` performs error analysis by inspecting false negatives and false positives.

### Limitations and remedies

The original notebook's main limitation was that it treated accuracy as the dominant indicator of success and used a fragmented preprocessing workflow. The improved notebook addresses this with stratified cross-validation, class-imbalance-aware metrics, threshold tuning and a simpler reproducible cleaning pipeline. A remaining limitation is that the improved notebook intentionally avoids heavy external embedding libraries to improve reproducibility. A future portfolio extension could compare this TF-IDF baseline with transformer embeddings or fine-tuned language models, provided that the same F1/PR-AUC-focused evaluation discipline is maintained.

---

## Overall conclusion

Across all three parts, the revised project strengthens the quantitative-methods critique by moving from descriptive observations to tested, validated and reproducible analysis. Part 1 now justifies preprocessing and cluster selection, Part 2 supports fraud-pattern claims with formal significance tests and imbalance-aware evaluation, and Part 3 evaluates NLP models using metrics aligned with the task. These changes directly address the marked feedback and make the repository more suitable as a public data-science portfolio.
