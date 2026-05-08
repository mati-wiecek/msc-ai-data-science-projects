# Portfolio Optimisation with Genetic Algorithms

This project investigates how genetic algorithms can be used for long-only equity portfolio optimisation and automated asset selection. The analysis compares evolved portfolio weights against equal-weight and random portfolio baselines, then extends the experiment to a larger asset universe where a binary genetic algorithm selects the asset subset and a nested real-valued genetic algorithm optimises weights.

## Research Objective

The objective is to evaluate whether evolutionary search can identify portfolios with stronger out-of-sample risk-adjusted performance than simple benchmark allocations. The project focuses on three questions:

1. Can a genetic algorithm optimise long-only portfolio weights for a diversified 10-asset equity basket?
2. How does the evolved portfolio perform on a later holdout period compared with equal-weight and random long-only portfolios?
3. Can a nested genetic algorithm jointly select assets and optimise weights from a larger candidate universe?

## Methodology

The workflow uses adjusted close prices, converts them to daily log returns, and applies a strict chronological split:

- Training window: 2021-01-01 to 2024-12-31
- Holdout window: 2025-01-01 to 2025-12-31

The main optimisation methods are:

- Real-valued genetic algorithm for portfolio weights.
- Sharpe ratio objective for the main long-only allocation experiment.
- Equal-weight portfolio as a simple baseline.
- Random long-only portfolios as a distributional benchmark.
- Risk-return preference sweep using `lambda * return - (1 - lambda) * risk`, where `lambda` ranges from 0 to 1.
- Binary genetic algorithm for asset selection from a 50-stock universe.
- Nested asset-selection approach where the outer GA selects assets and the inner GA optimises weights for each candidate subset.

## Dataset

The project uses publicly available historical market data downloaded locally from Yahoo Finance through the R `quantmod` package. No raw market data is stored in this repository.

The manual 10-asset universe combines growth, defensive, financial, energy, and consumer exposures. The larger universe contains 50 liquid large-cap US equities used for the asset-selection experiment.

## Repository Structure

```text
.
|-- README.md
|-- environment.yml
|-- .gitignore
|-- notebooks/
|   `-- 01_portfolio_optimisation_genetic_algorithms.Rmd
|-- src/
|   |-- data_utils.R
|   |-- metrics.R
|   |-- ga_portfolio.R
|   |-- plotting.R
|   `-- run_analysis.R
|-- data/
|   |-- README.md
|   `-- raw/
|       `-- .gitkeep
|-- reports/
|   |-- methodology_report.md
|   `-- model_evaluation.md
|-- figures/
|   `-- .gitkeep
`-- outputs/
    `-- .gitkeep
```

## Setup

Create the conda environment:

```bash
conda env create -f environment.yml
conda activate ga-portfolio-optimisation
```

Alternatively, install the required R packages manually:

```r
install.packages(c(
  "quantmod",
  "GA",
  "xts",
  "knitr",
  "rmarkdown"
))
```

## Running the Project

Render the analysis notebook from the repository root:

```bash
R -e "rmarkdown::render('notebooks/01_portfolio_optimisation_genetic_algorithms.Rmd')"
```

Run the scripted pipeline and save tables/figures locally:

```bash
Rscript src/run_analysis.R
```

Generated files are written to `outputs/` and `figures/`. These directories are intentionally excluded from version control except for placeholder files.

## Evaluation

The evaluation uses annualised return, annualised volatility, Sharpe ratio, empirical percentile rank against random portfolios, and holdout-period cumulative growth. The baseline comparisons are designed to separate in-sample optimisation performance from holdout-period generalisation.

A representative experimental run showed that the evolved 10-asset portfolio improved training Sharpe relative to the equal-weight baseline, remained competitive on the holdout window, and ranked above most random 10-asset subsets in the asset-selection experiment. Detailed metric tables are documented in `reports/model_evaluation.md`.

## Data and Reproducibility

Raw price data is not included. To reproduce the dataset locally, run the notebook or `src/run_analysis.R`; both use the same ticker lists and date windows and download adjusted close prices from Yahoo Finance through `quantmod`.

Reproducibility controls:

- Fixed random seed for genetic algorithm runs.
- Explicit train/holdout split.
- Long-only fully invested weight normalisation.
- Local cache files are ignored by version control.
- Output tables and generated figures are reproducible from the source scripts.

## Limitations

This project is a research prototype rather than an investment system. The analysis assumes zero transaction costs, no taxes, no slippage, no liquidity constraints, and no rebalancing cost. Results are sensitive to the selected assets, historical window, optimiser settings, and market regime.

## Future Work

Potential extensions include walk-forward validation, transaction-cost-aware objectives, turnover constraints, alternative risk measures such as maximum drawdown or CVaR, multi-start stability analysis, and comparison with convex optimisation baselines.
