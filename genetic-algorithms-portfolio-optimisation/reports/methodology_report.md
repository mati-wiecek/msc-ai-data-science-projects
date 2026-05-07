# Methodology Report

## Aim

This project evaluates whether a genetic algorithm can optimise a complete long/cash trading strategy for GOOG while maintaining out-of-sample credibility. The strategy combines regime detection, technical indicators, execution assumptions, transaction costs and risk management into one decision system.

## Search Space

The chromosome contains 15 parameters:

- MACD fast, slow and signal windows
- RSI, ADX, ATR and SMA lookback windows
- ADX regime threshold
- RSI buy, sell and exit thresholds
- Initial stop and trailing stop distances in ATR multiples
- Maximum holding period
- Fraction of equity risked per trade

Repair logic enforces sensible parameter ordering, such as `MACD slow > MACD fast` and `RSI sell > RSI buy`.

## Validation Design

The strategy is optimised on data ending 2021-12-31 and tested from 2022 onward. Signals are generated from information available at close on day `t`, while orders execute at the open of day `t + 1`. This reduces look-ahead bias and makes the backtest more realistic than same-close execution.

## Benchmarks

The GA strategy is compared against:

- a fixed-parameter baseline;
- the best random parameter draw;
- the mean random parameter result;
- buy-and-hold exposure over the same test window.

All strategies use the same cost and slippage assumptions where applicable.

## Key Finding

The GA improves substantially over the fixed baseline and the mean random strategy out of sample. However, buy-and-hold still earns more raw profit over the test window, while the best random draw is slightly ahead of the GA. The strongest interpretation is therefore that evolutionary search produced a profitable, lower-drawdown active timing rule, not a dominant trading system that beats all benchmarks.

## Limitations

The evidence comes from one asset, one train/test split and daily bars. The strategy does not model taxes, borrow frictions, liquidity constraints beyond simple costs, or intraday execution risk. Future work should add walk-forward validation, multi-asset testing and a richer transaction-cost model.
