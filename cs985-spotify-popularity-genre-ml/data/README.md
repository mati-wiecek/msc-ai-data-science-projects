# Data directory

Raw CSV files are not included in this public repository.

Place the four dataset files in `data/raw/` using these neutral filenames:

| Required filename | Purpose |
|---|---|
| `spotify_regression_train.csv` | labelled training data for popularity regression |
| `spotify_regression_test.csv` | unlabelled test data for popularity regression |
| `spotify_classification_train.csv` | labelled training data for genre classification |
| `spotify_classification_test.csv` | unlabelled test data for genre classification |

The `.gitignore` file prevents CSV files in `data/raw/` from being committed.
