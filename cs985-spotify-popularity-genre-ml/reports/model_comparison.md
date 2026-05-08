# Model comparison and implementation review

## Executive summary

This project solves two related tasks using song metadata and audio-style features:

- popularity regression, evaluated with RMSE;
- genre classification, evaluated with accuracy.

The final public benchmark results were:

| Task | Public benchmark metric | Result | Public rank |
|---|---:|---:|---:|
| Popularity regression | RMSE | **6.52657** | **2** |
| Genre classification | Accuracy | **0.57142** | **16** |

The workflow is structured so that the modelling choices are easy to read, rerun and discuss. Raw data and generated submissions are excluded from version control.

## Local validation comparison

The table below comes from `reports/local_validation_metrics.csv` and uses a reproducible split with `RANDOM_STATE = 42`.

| Task | Model | Train metric | Validation metric | Interpretation |
|---|---|---:|---:|---|
| Regression | Dummy mean | 13.0033 RMSE | 15.1609 RMSE | Sanity-check baseline; too weak for final use. |
| Regression | Linear regression | 8.3823 RMSE | 11.6012 RMSE | Captures simple linear relationships but does not handle categorical complexity well. |
| Regression | Ridge regression | 9.0030 RMSE | 11.1708 RMSE | More stable than ordinary linear regression because of regularisation. |
| Regression | Random forest | 4.8161 RMSE | 10.9514 RMSE | Better validation RMSE than linear baselines, but train/validation gap suggests overfitting risk. |
| Classification | Dummy most frequent | 0.1698 acc | 0.1750 acc | Shows the strength of the majority-class baseline. |
| Classification | Linear SVC balanced | 1.0000 acc | 0.5875 acc | Best default classification model; matches the validated prediction file exactly. |
| Classification | Random forest | 0.4560 acc | 0.4250 acc | Underperforms Linear SVC on the validation split. |
| Classification | TF-IDF text SVC | n/a | 0.4875 acc | Optional text experiment; lower validation accuracy, so not used as the default. |

The CatBoost regression model used by the experiment runner reported quick-mode validation RMSE of **9.8633**, which is better than the lightweight baselines above. The public benchmark RMSE was **6.52657**, which is based on a separate hidden/public split and is therefore not directly comparable to the local validation split.

## Implementation audit

Two classification variants were reviewed. The validated prediction file matched the tabular Linear SVC pipeline for **113/113** rows. The TF-IDF text variant did not match that prediction file and had lower validation accuracy (**0.4875** versus **0.5875**), so the final public workflow keeps the tabular Linear SVC as the default and leaves the text model as an optional experiment.

## Engineering notes

- Added a modular `src/` package with reusable functions for loading, feature engineering, evaluation and modelling.
- Added explicit train/validation comparisons for each task.
- Added public benchmark metrics and an explanation of why local validation and hidden/public benchmark scores can differ.
- Added figures, local validation metrics, tests, `requirements.txt`, `pyproject.toml`, `.gitignore`, `data/README.md` and `outputs/README.md`.

## Main limitations

The dataset is small and the genre classification target has many rare labels. This creates unstable validation estimates and makes the classification task sensitive to individual songs in the split. The regression task is also affected by high-cardinality categorical variables, especially artist and genre.

## Future work

The next improvements would be nested cross-validation, richer rare-class error analysis, safer target/frequency encoding for high-cardinality categories, and a calibrated ensemble for the classification task.
