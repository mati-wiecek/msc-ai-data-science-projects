# Methodology Report

## Aim

This project analyses a structured dataset of Dragon Ball Z Pettan Battle cards as a compact big-data workflow case study. The aim is to test whether rarity corresponds to measurable differences in card statistics, whether cards form interpretable stat-based segments, and whether high-tier rarity can be predicted from HP and Attack.

## Research Questions

| Question | Method |
|---|---|
| Do Gold and Platinum cards have higher HP and Attack than Silver and Bronze cards? | Mann-Whitney U tests, median differences and rarity-level boxplots. |
| Can cards be grouped into stat-based archetypes? | Standardised K-Means clustering with silhouette and inertia diagnostics. |
| Can high-tier rarity be predicted from card statistics? | Leakage-aware scikit-learn pipeline with median imputation, scaling, class-balanced logistic regression, stratified cross-validation and holdout evaluation. |

## Data Preparation

The raw HP and Attack fields are re-parsed into `hp_for_model` and `attack_for_model`. The parser extracts the final numeric token from each value and falls back to existing numeric columns if needed. This keeps the modelling features explicit and avoids using rarity-derived information as an input to the supervised model.

The binary target `is_high` is defined as:

```text
1 = gold or platinum
0 = silver or bronze
```

The final cleaned dataset contains 295 rows. The rarity distribution is imbalanced: 119 bronze, 97 silver, 63 gold and 16 platinum cards.

## Key Results

- High-tier cards have a median HP of `8700`, compared with `4100` for low-tier cards.
- High-tier cards have a median Attack of `7350`, compared with `3200` for low-tier cards.
- Mann-Whitney p-values are below `2e-39` for both HP and Attack, indicating a very strong separation between high-tier and low-tier cards.
- K-Means selects `k = 5` by silhouette score, separating low-stat, mid-stat, high-stat and extreme-stat card archetypes.
- A leakage-aware logistic regression pipeline reaches perfect cross-validation and holdout scores using only HP and Attack.

## Interpretation

The supervised result should be interpreted as evidence that rarity tier is strongly encoded in the HP and Attack ranges of this dataset, rather than as evidence of a complex predictive model. The technical value of the workflow is in the validation design: imputation and scaling are fitted inside the pipeline, class imbalance is handled explicitly, and model performance is reported with precision, recall, F1 and ROC-AUC rather than accuracy alone.

## Limitations

The dataset is small and contains only a limited number of numerical modelling features. The strong classification performance may not generalise to later releases if the card design rules change. Release-date fields also contain missingness and should be validated against primary sources before being used for temporal analysis.

## Future Work

Natural extensions include direct multi-class rarity prediction, comparison against tree-based models, density-based clustering, release-series analysis, and validation on cards released after the current dataset snapshot.
