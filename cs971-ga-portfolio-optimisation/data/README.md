# Data

Raw market data is not stored in this repository.

The analysis downloads adjusted close prices locally using the R `quantmod` package and Yahoo Finance as the data source. The same ticker universes and date windows are defined in the notebook and in `src/run_analysis.R`.

## Reproducing the Local Dataset

From the repository root, run:

```bash
Rscript src/run_analysis.R
```

or render the notebook:

```bash
R -e "rmarkdown::render('notebooks/01_portfolio_optimisation_genetic_algorithms.Rmd')"
```

The scripts create local cache files under `data/raw/` and generated tables/figures under `outputs/` and `figures/`. These files are ignored by version control so that the repository contains code and documentation only.

## Expected Data Fields

For each ticker, the downloaded time series contains daily adjusted close prices. The analysis converts prices to daily log returns and then applies the following split:

- Training window: 2021-01-01 to 2024-12-31
- Holdout window: 2025-01-01 to 2025-12-31
