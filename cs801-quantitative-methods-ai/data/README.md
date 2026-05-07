# Data folder

Place raw data files in `data/raw/`. They are ignored by git to avoid uploading large or restricted Kaggle files.

## Required files

### Part 1 - Customer Segmentation

Expected file:

```text
data/raw/marketing_campaign.csv
```

The notebook expects the tab-separated marketing campaign/customer personality dataset used in the original Kaggle customer segmentation notebook.

### Part 2 - IEEE-CIS Fraud Detection

Expected files:

```text
data/raw/fraud_train_transaction.csv
data/raw/fraud_train_identity.csv
```

Optional files for unlabeled train/test distribution checks:

```text
data/raw/fraud_test_transaction.csv
data/raw/fraud_test_identity.csv
```

The improved notebook uses test files only for optional unlabeled covariate-shift diagnostics. It does not use test labels or test data for supervised model selection.

### Part 3 - Disaster Tweets

Expected file:

```text
data/raw/NLP_train.csv
```

Optional file for generating a submission:

```text
data/raw/NLP_test.csv
```

## Why data is not committed

The `.gitignore` file excludes `data/raw/*`, generated outputs and caches. This keeps the repository lightweight and avoids redistribution issues.
