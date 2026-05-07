# Evolutionary Optimisation of a Long/Cash Trading Strategy

This project develops and evaluates a genetic-algorithm-optimised trading strategy for GOOG daily OHLCV data. The system combines MACD trend following, RSI mean reversion, ADX regime detection, ATR-based risk management, transaction costs, slippage, position sizing and out-of-sample validation.

The central research question is whether evolutionary search can produce a defensible active timing rule, not merely a high in-sample backtest. The final strategy is deliberately long/cash rather than long/short because short exposure was not supported by the cost and borrow assumptions in the available backtest.

## Research Questions

| Question | Method |
|---|---|
| Can a genetic algorithm optimise a complete trading-system parameter vector? | GA search over 15 parameters controlling indicators, thresholds, stops, holding period and risk fraction. |
| Does the strategy survive out-of-sample evaluation? | Chronological train/test split with optimisation ending in 2021 and testing from 2022 onward. |
| Is the GA useful compared with simpler alternatives? | Comparison against fixed parameters, random parameter search and buy-and-hold. |
| What is the economically honest interpretation? | Evaluate profit, return, Sharpe ratio, drawdown, trades and win rate rather than raw return alone. |

## Strategy Design

- Asset: `GOOG`
- Data source: Yahoo Finance via `quantmod`
- Sample: 2015-01-01 to 2024-12-31
- Training window: through 2021-12-31
- Test window: from 2022-01-01
- Execution assumption: signal at close on day `t`, execution at open on day `t + 1`
- Trading mode: long/cash
- Costs: flat commission plus slippage
- Risk management: ATR stop, ATR trailing stop, maximum holding period and capped risk fraction

## Results Summary

| Test-period strategy | Net profit | Total return | Sharpe | Max drawdown | Trades |
|---|---:|---:|---:|---:|---:|
| GA optimised | GBP 750.21 | 7.50% | 0.29 | 9.99% | 14 |
| Fixed baseline | GBP -104.70 | -1.05% | -0.10 | 3.97% | 7 |
| Best random solution | GBP 764.03 | 7.64% | 0.35 | 6.75% | 10 |
| Buy and hold | GBP 3,305.17 | 33.05% | 0.45 | 43.51% | 0 |
| Mean random solution | GBP 108.89 | n/a | 0.03 | n/a | n/a |

The GA strategy remains profitable out of sample and clearly improves on the fixed baseline and the mean random solution. It does not dominate buy-and-hold on raw return, and the best random draw remains competitive. The strongest defensible claim is therefore narrower and more useful: the GA produced a lower-drawdown active timing rule with positive out-of-sample performance, but not a universally superior trading strategy.

## Repository Structure

```text
genetic-algorithms-portfolio-optimisation/
|-- strategy_evaluation.Rmd
|-- src/
|   `-- algorithmic_trading_strategy.R
|-- results/
|   |-- ga_regime_strategy_results.rds
|   |-- best_parameters.csv
|   |-- train_comparison.csv
|   |-- test_comparison.csv
|   |-- random_search_results.csv
|   |-- random_summary.csv
|   |-- train_trade_log_ga.csv
|   `-- test_trade_log_ga.csv
|-- figures/
|   |-- 01_price_split.png
|   |-- 02_train_equity_curves.png
|   |-- 03_test_equity_curves.png
|   `-- 04_random_search_train_fitness.png
|-- reports/
|   `-- methodology_report.md
|-- requirements.R
|-- .gitignore
`-- README.md
```

## Reproducibility

The report uses cached results in `results/ga_regime_strategy_results.rds` so it can be rendered quickly. To regenerate the full optimisation from scratch, install the R dependencies and run:

```r
source("src/algorithmic_trading_strategy.R")
rmarkdown::render("strategy_evaluation.Rmd")
```

The full GA rerun downloads data from Yahoo Finance and may take longer than rendering the cached report.

## Notes

This repository contains the technical strategy, report source, cached results and figures. Private collaboration notes, local documents and original PDFs are intentionally excluded.
