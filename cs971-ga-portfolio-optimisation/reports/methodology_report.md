# Methodology Report

## Research Objective

The objective is to evaluate whether genetic algorithms can produce long-only equity portfolios with competitive out-of-sample risk-adjusted performance. The study combines portfolio weight optimisation, benchmark comparison, risk-return preference analysis, and automated asset selection.

## Dataset

The analysis uses adjusted close prices downloaded locally from Yahoo Finance through the R `quantmod` package. Daily log returns are computed from adjusted prices.

The chronological split is:

- Training window: 2021-01-01 to 2024-12-31
- Holdout window: 2025-01-01 to 2025-12-31

No raw price data is included in the repository. Running the notebook or script recreates the dataset locally.

## Manual Asset Universe

The 10-asset universe is designed to combine multiple sources of equity exposure:

| Ticker | Sector | Role |
|---|---|---|
| GOOGL | Communication Services | Growth / technology exposure |
| NVDA | Information Technology | Growth / technology exposure |
| META | Communication Services | Growth / technology exposure |
| XOM | Energy | Energy exposure |
| NEE | Utilities | Defensive utility exposure |
| JPM | Financials | Cyclical financial exposure |
| MA | Financials | Quality financial exposure |
| WMT | Consumer Staples | Defensive consumer exposure |
| PG | Consumer Staples | Defensive consumer exposure |
| EL | Consumer Staples | Consumer discretionary tilt |

The training correlation matrix is used as a quick diversification diagnostic before optimisation.

## Optimisation Design

### Weight Optimisation

A real-valued genetic algorithm searches over non-negative asset weights. Weights are normalised so the portfolio is fully invested and long-only. The primary objective is training-period Sharpe ratio with a zero risk-free-rate assumption.

### Baselines

The evolved portfolio is compared against:

- Equal-weight allocation.
- Random long-only portfolios sampled from positive random draws and normalised to sum to one.
- Random 10-stock subsets for the larger asset-selection experiment.

### Risk-Return Preference Sweep

A preference grid is used to generate different portfolios under the objective:

```text
fitness(w) = lambda * return(w) - (1 - lambda) * risk(w)
```

`lambda` ranges from 0 to 1. Low values prioritise risk reduction, while high values prioritise return.

### Asset Selection

The larger 50-stock universe is evaluated using two methods:

1. Proxy selection: a binary GA selects a subset and evaluates it with equal weights.
2. Integrated selection: a binary GA selects assets while an inner GA optimises weights for each candidate subset.

The integrated method uses a cache to avoid repeated evaluation of the same subset.

## Reproducibility Controls

- Fixed random seed for stochastic runs.
- Explicit chronological train/holdout split.
- Clear ticker lists in source code.
- Local data caches excluded from version control.
- Generated figures and output tables recreated from source scripts.
