# Evolutionary optimisation of a long/cash MACD/RSI/ADX strategy for GOOG
# Standalone implementation used to regenerate cached results and figures.

# Title: Evolutionary optimisation of a regime-switching technical
#        trading strategy for GOOG using quantmod + TTR
#
# Strategy summary

# 1) Download daily GOOG data from Yahoo Finance with quantmod.
# 2) Build a regime-switching strategy using:
#       - MACD for trend-following entries/exits,
#       - RSI for mean-reversion entries/exits,
#       - ADX to decide whether the market is trending or ranging,
#       - ATR for stop distance and volatility-aware position sizing,
#       - SMA as an additional trend filter.
# 3) Use a Genetic Algorithm (GA package) to optimise the indicator
#    windows and trading-rule thresholds on the training set only.
# 4) Evaluate the best strategy on a reserved out-of-sample test set.
# 5) Compare the optimised strategy with:
#       - a fixed, hand-chosen baseline strategy,
#       - buy-and-hold,
#       - random parameter solutions.
#
# Notes
# -----
# * Signals are generated using information available at close on day t.
# * Orders are executed at the OPEN on day t+1 to avoid look-ahead bias.
# * Initial notional capital is fixed at GBP 10,000 for every experiment.
# * A flat commission and slippage assumption is included.


# 0. Package setup

required_packages <- c("quantmod", "TTR", "GA")
missing_packages <- required_packages[!sapply(required_packages, requireNamespace, quietly = TRUE)]

if (length(missing_packages) > 0) {
  cran_repo <- "https://cloud.r-project.org"
  install.packages(missing_packages, repos = cran_repo)
}

still_missing <- required_packages[!sapply(required_packages, requireNamespace, quietly = TRUE)]
if (length(still_missing) > 0) {
  stop(
    "The following packages are still missing after installation was attempted: ",
    paste(still_missing, collapse = ", "),
    "."
  )
}

library(quantmod)
library(TTR)
library(GA)

set.seed(123)
options(stringsAsFactors = FALSE)

# Create output folders so that the script can save tables, figures and an
# RDS object containing all final results for later reuse in a report.
dir.create("figures", showWarnings = FALSE)
dir.create("results", showWarnings = FALSE)


# 1. Global configuration

symbol            <- "GOOG"
start_date        <- "2015-01-01"
end_date          <- "2024-12-31"
train_end_date    <- as.Date("2021-12-31")
test_start_date   <- as.Date("2022-01-01")
initial_capital   <- 10000
commission_gbp    <- 5         # flat commission paid on every entry and exit
slippage_bps      <- 5         # 5 basis points on every fill
max_capital_frac  <- 0.95      # never allocate more than 95% of equity
random_baseline_n <- 200       # number of random solutions used for comparison
allow_short_positions <- FALSE # bearish signals flatten the book instead of opening shorts

# Helper formatting functions that are also convenient inside an R Markdown
# report if this script is sourced there.
fmt_gbp <- function(x) paste0("GBP ", format(round(x, 2), nsmall = 2, big.mark = ","))
fmt_pct <- function(x) paste0(format(round(100 * x, 2), nsmall = 2), "%")
fmt_num <- function(x, digits = 2) format(round(x, digits), nsmall = digits, big.mark = ",")


# 2. Download data

# quantmod returns an xts object with Open, High, Low, Close, Volume and
# Adjusted columns.
price_xts <- suppressWarnings(
  getSymbols(Symbols = symbol,
             src = "yahoo",
             from = start_date,
             to   = end_date,
             auto.assign = FALSE)
)

price_xts <- na.omit(price_xts)

# 3. Data summary function

make_data_summary <- function(px, train_end) {
  adj <- Ad(px)
  ret <- na.omit(dailyReturn(adj, type = "log"))

  data.frame(
    symbol                 = symbol,
    start                  = as.character(start(px)),
    end                    = as.character(end(px)),
    observations           = nrow(px),
    train_observations     = sum(index(px) <= train_end),
    test_observations      = sum(index(px) > train_end),
    first_adjusted_close   = as.numeric(first(adj)),
    last_adjusted_close    = as.numeric(last(adj)),
    mean_daily_log_return  = mean(as.numeric(ret), na.rm = TRUE),
    sd_daily_log_return    = sd(as.numeric(ret), na.rm = TRUE),
    annualised_volatility  = sd(as.numeric(ret), na.rm = TRUE) * sqrt(252),
    min_daily_log_return   = min(as.numeric(ret), na.rm = TRUE),
    max_daily_log_return   = max(as.numeric(ret), na.rm = TRUE),
    median_volume          = median(as.numeric(Vo(px)), na.rm = TRUE)
  )
}

data_summary <- make_data_summary(price_xts, train_end_date)
write.csv(data_summary, "results/data_summary.csv", row.names = FALSE)


# 4. Parameter repair / decode

# The GA package works with real-valued chromosomes. This helper converts the
# raw chromosome into a valid parameter list and repairs any ordering issues.
repair_params <- function(x) {
  p <- list(
    macd_fast   = as.integer(round(x[1])),
    macd_slow   = as.integer(round(x[2])),
    macd_signal = as.integer(round(x[3])),
    rsi_n       = as.integer(round(x[4])),
    adx_n       = as.integer(round(x[5])),
    atr_n       = as.integer(round(x[6])),
    sma_n       = as.integer(round(x[7])),
    adx_regime  = as.numeric(x[8]),
    rsi_buy     = as.numeric(x[9]),
    rsi_sell    = as.numeric(x[10]),
    rsi_exit    = as.numeric(x[11]),
    stop_atr    = as.numeric(x[12]),
    trail_atr   = as.numeric(x[13]),
    max_hold    = as.integer(round(x[14])),
    risk_frac   = as.numeric(x[15])
  )

  # Hard bounds
  p$macd_fast   <- min(max(p$macd_fast, 4), 20)
  p$macd_slow   <- min(max(p$macd_slow, p$macd_fast + 2), 60)
  p$macd_signal <- min(max(p$macd_signal, 3), 15)
  p$rsi_n       <- min(max(p$rsi_n, 5), 30)
  p$adx_n       <- min(max(p$adx_n, 5), 30)
  p$atr_n       <- min(max(p$atr_n, 5), 30)
  p$sma_n       <- min(max(p$sma_n, 50), 250)
  p$adx_regime  <- min(max(p$adx_regime, 10), 35)
  p$rsi_buy     <- min(max(p$rsi_buy, 10), 45)
  p$rsi_sell    <- min(max(p$rsi_sell, p$rsi_buy + 10), 90)
  p$rsi_exit    <- min(max(p$rsi_exit, p$rsi_buy + 5), p$rsi_sell - 5)
  p$stop_atr    <- min(max(p$stop_atr, 1.0), 5.0)
  p$trail_atr   <- min(max(p$trail_atr, 1.0), 7.0)
  p$max_hold    <- min(max(p$max_hold, 3), 40)
  p$risk_frac   <- min(max(p$risk_frac, 0.005), 0.03)

  p
}

# Lower and upper bounds used directly by GA::ga(). The repair function above
# still acts as a final safety net.
ga_lower <- c(4,  21, 3,  5,  5,  5,  50, 10, 10, 55, 45, 1.0, 1.0, 3, 0.005)
ga_upper <- c(20, 60, 15, 30, 30, 30, 250, 35, 45, 90, 60, 5.0, 7.0, 40, 0.030)

# A sensible non-evolved baseline using standard technical-analysis settings.
fixed_baseline_params <- list(
  macd_fast   = 12,
  macd_slow   = 26,
  macd_signal = 9,
  rsi_n       = 14,
  adx_n       = 14,
  atr_n       = 14,
  sma_n       = 200,
  adx_regime  = 20,
  rsi_buy     = 30,
  rsi_sell    = 70,
  rsi_exit    = 50,
  stop_atr    = 2.0,
  trail_atr   = 3.0,
  max_hold    = 15,
  risk_frac   = 0.02
)


# 5. Build indicator data

# This function computes all indicator series needed by the strategy.
build_indicator_data <- function(px, p) {
  macd_obj <- MACD(Cl(px),
                   nFast = p$macd_fast,
                   nSlow = p$macd_slow,
                   nSig  = p$macd_signal,
                   maType = "EMA")

  rsi_vec <- RSI(Cl(px), n = p$rsi_n)
  adx_obj <- ADX(HLC(px), n = p$adx_n)
  atr_obj <- ATR(HLC(px), n = p$atr_n)
  sma_vec <- SMA(Cl(px), n = p$sma_n)

  indicators <- merge(
    macd_obj[, "macd"],
    macd_obj[, "signal"],
    macd_obj[, "macd"] - macd_obj[, "signal"],
    rsi_vec,
    adx_obj[, "ADX"],
    atr_obj[, "atr"],
    sma_vec
  )
  colnames(indicators) <- c("macd", "signal", "hist", "rsi", "adx", "atr", "sma")

  out <- merge(px, indicators)

  # Remove the initial warm-up rows where long indicator windows are not yet
  # available.
  out <- na.omit(out)
  out
}

# 6. Utility: equity metrics

compute_equity_metrics <- function(equity_curve,
                                   trade_log,
                                   initial_capital,
                                   final_equity) {
  eq <- as.numeric(equity_curve)
  eq <- eq[is.finite(eq)]

  # Daily equity returns.
  if (length(eq) > 1) {
    ret <- diff(eq) / head(eq, -1)
    ret <- ret[is.finite(ret)]
  } else {
    ret <- numeric(0)
  }

  total_return <- final_equity / initial_capital - 1
  ann_return <- if (length(eq) > 1) {
    (final_equity / initial_capital)^(252 / (length(eq) - 1)) - 1
  } else {
    NA_real_
  }

  sharpe <- if (length(ret) > 1 && sd(ret, na.rm = TRUE) > 0) {
    sqrt(252) * mean(ret, na.rm = TRUE) / sd(ret, na.rm = TRUE)
  } else {
    0
  }

  peak <- cummax(eq)
  dd_gbp <- peak - eq
  dd_pct <- eq / peak - 1

  max_dd_gbp <- max(dd_gbp, na.rm = TRUE)
  max_dd_pct <- abs(min(dd_pct, na.rm = TRUE))

  closed_trade_mask <- trade_log$event %in% c("LONG_EXIT", "SHORT_EXIT", "FINAL_LONG_EXIT", "FINAL_SHORT_EXIT")
  closed_trades <- trade_log[closed_trade_mask, , drop = FALSE]
  n_trades <- nrow(closed_trades)

  win_rate <- if (n_trades > 0) {
    mean(closed_trades$trade_pnl > 0, na.rm = TRUE)
  } else {
    0
  }

  net_profit <- final_equity - initial_capital

  # Profit-based fitness with a drawdown penalty and a penalty for trivially
  # inactive strategies. Profit remains the dominant term.
  inactivity_penalty <- if (n_trades < 5) 250 else 0
  fitness <- net_profit - 0.30 * max_dd_gbp - inactivity_penalty

  data.frame(
    final_equity   = final_equity,
    net_profit     = net_profit,
    total_return   = total_return,
    annual_return  = ann_return,
    sharpe         = sharpe,
    max_dd_gbp     = max_dd_gbp,
    max_dd_pct     = max_dd_pct,
    trades         = n_trades,
    win_rate       = win_rate,
    fitness        = fitness
  )
}


# 7. Core backtest

# This is the most important function in the script. It implements all trading
# logic using only information available at time t and executes orders at the
# next open (t + 1).
backtest_strategy <- function(data,
                              p,
                              initial_capital = 10000,
                              commission = 5,
                              slippage_bps = 5,
                              max_capital_frac = 0.95) {

  n <- nrow(data)
  if (n < 30) {
    empty_equity <- xts(rep(initial_capital, n), order.by = index(data))
    empty_log <- data.frame()
    metrics <- data.frame(
      final_equity = initial_capital,
      net_profit   = 0,
      total_return = 0,
      annual_return = 0,
      sharpe = 0,
      max_dd_gbp = 0,
      max_dd_pct = 0,
      trades = 0,
      win_rate = 0,
      fitness = -1e9
    )
    return(list(equity = empty_equity, trade_log = empty_log, metrics = metrics))
  }

  opn  <- as.numeric(Op(data))
  cls  <- as.numeric(Cl(data))
  hist <- as.numeric(data$hist)
  rsi  <- as.numeric(data$rsi)
  adx  <- as.numeric(data$adx)
  atr  <- as.numeric(data$atr)
  sma  <- as.numeric(data$sma)
  dts  <- index(data)

  # Slippage converter.
  slip <- slippage_bps / 10000

  # State variables for the current portfolio.
  cash          <- initial_capital
  position      <- 0L     # 1 = long, -1 = short, 0 = flat
  shares        <- 0L
  entry_price   <- NA_real_
  entry_atr     <- NA_real_
  entry_date    <- as.Date(NA)
  entry_style   <- NA_character_
  bars_held     <- 0L
  highest_close <- NA_real_
  lowest_close  <- NA_real_

  # A simple list that will later be converted to a data.frame trade log.
  trade_log_list <- list()
  trade_row <- 0L

  # Daily equity curve valued at the close of each bar.
  equity <- rep(initial_capital, n)

  # Helper used repeatedly to add a row to the trade log.
  append_trade <- function(date, event, direction, shares, price, reason, trade_pnl, cash_after) {
    trade_row <<- trade_row + 1L
    trade_log_list[[trade_row]] <<- data.frame(
      date       = as.character(date),
      event      = event,
      direction  = direction,
      shares     = shares,
      price      = price,
      reason     = reason,
      trade_pnl  = trade_pnl,
      cash_after = cash_after,
      stringsAsFactors = FALSE
    )
  }

  # Start at row 2 because some signals use the previous day's indicator value.
  # End at n - 1 because all orders are executed at the next day's open.
  for (i in 2:(n - 1)) {

    current_close  <- cls[i]
    next_open      <- opn[i + 1]
    current_equity <- cash + position * shares * current_close

    # If a position is already open, update holding duration and trailing state
    # using today's close.
    current_stop <- NA_real_
    if (position != 0L) {
      bars_held <- bars_held + 1L

      if (position == 1L) {
        highest_close <- if (is.na(highest_close)) current_close else max(highest_close, current_close)
        current_stop  <- max(entry_price - p$stop_atr * entry_atr,
                             highest_close - p$trail_atr * atr[i])
      }

      if (position == -1L) {
        lowest_close <- if (is.na(lowest_close)) current_close else min(lowest_close, current_close)
        current_stop <- min(entry_price + p$stop_atr * entry_atr,
                            lowest_close + p$trail_atr * atr[i])
      }
    }

    # Record close-to-close equity BEFORE any action scheduled for tomorrow's open.
    equity[i] <- current_equity


    # Entries

    trend_regime <- adx[i] >= p$adx_regime

    trend_long_entry  <- trend_regime  && hist[i - 1] <= 0 && hist[i] > 0 && current_close > sma[i]
    trend_short_entry <- allow_short_positions &&
      trend_regime && hist[i - 1] >= 0 && hist[i] < 0 && current_close < sma[i]

    # In the ranging regime we wait for RSI to move back out of an extreme,
    # which avoids buying a falling knife immediately after oversold is first hit.
    range_long_entry  <- !trend_regime && rsi[i - 1] < p$rsi_buy  && rsi[i] >= p$rsi_buy
    range_short_entry <- allow_short_positions &&
      !trend_regime && rsi[i - 1] > p$rsi_sell && rsi[i] <= p$rsi_sell

    desired_signal <- 0L
    desired_style  <- NA_character_

    if (trend_long_entry)  { desired_signal <-  1L; desired_style <- "trend_long"  }
    if (trend_short_entry) { desired_signal <- -1L; desired_style <- "trend_short" }
    if (range_long_entry)  { desired_signal <-  1L; desired_style <- "range_long"  }
    if (range_short_entry) { desired_signal <- -1L; desired_style <- "range_short" }


    # Exits

    exit_flag   <- FALSE
    exit_reason <- NA_character_

    if (position == 1L) {
      if (entry_style == "trend_long" && hist[i] < 0) {
        exit_flag <- TRUE
        exit_reason <- "MACD trend reversal"
      }
      if (entry_style == "range_long" && rsi[i] >= p$rsi_exit) {
        exit_flag <- TRUE
        exit_reason <- "RSI mean-reversion exit"
      }
      if (!is.na(current_stop) && current_close <= current_stop) {
        exit_flag <- TRUE
        exit_reason <- "ATR trailing stop"
      }
      if (bars_held >= p$max_hold) {
        exit_flag <- TRUE
        exit_reason <- "Maximum holding period"
      }
    }

    if (position == -1L) {
      if (entry_style == "trend_short" && hist[i] > 0) {
        exit_flag <- TRUE
        exit_reason <- "MACD trend reversal"
      }
      if (entry_style == "range_short" && rsi[i] <= (100 - p$rsi_exit)) {
        exit_flag <- TRUE
        exit_reason <- "RSI mean-reversion exit"
      }
      if (!is.na(current_stop) && current_close >= current_stop) {
        exit_flag <- TRUE
        exit_reason <- "ATR trailing stop"
      }
      if (bars_held >= p$max_hold) {
        exit_flag <- TRUE
        exit_reason <- "Maximum holding period"
      }
    }


    # First execute any required EXIT at tomorrow's open.

    if (position == 1L && exit_flag) {
      exit_exec_price <- next_open * (1 - slip)
      cash <- cash + shares * exit_exec_price - commission
      realised_pnl <- shares * (exit_exec_price - entry_price) - 2 * commission

      append_trade(date = dts[i + 1],
                   event = "LONG_EXIT",
                   direction = "LONG",
                   shares = shares,
                   price = exit_exec_price,
                   reason = exit_reason,
                   trade_pnl = realised_pnl,
                   cash_after = cash)

      position      <- 0L
      shares        <- 0L
      entry_price   <- NA_real_
      entry_atr     <- NA_real_
      entry_date    <- as.Date(NA)
      entry_style   <- NA_character_
      bars_held     <- 0L
      highest_close <- NA_real_
      lowest_close  <- NA_real_
    }

    if (position == -1L && exit_flag) {
      exit_exec_price <- next_open * (1 + slip)
      cash <- cash - shares * exit_exec_price - commission
      realised_pnl <- shares * (entry_price - exit_exec_price) - 2 * commission

      append_trade(date = dts[i + 1],
                   event = "SHORT_EXIT",
                   direction = "SHORT",
                   shares = shares,
                   price = exit_exec_price,
                   reason = exit_reason,
                   trade_pnl = realised_pnl,
                   cash_after = cash)

      position      <- 0L
      shares        <- 0L
      entry_price   <- NA_real_
      entry_atr     <- NA_real_
      entry_date    <- as.Date(NA)
      entry_style   <- NA_character_
      bars_held     <- 0L
      highest_close <- NA_real_
      lowest_close  <- NA_real_
    }


    # Then, if the portfolio is flat, execute a new ENTRY at the
    # same open using today's close-generated signal.

    if (position == 0L && desired_signal != 0L) {

      # Risk-based position sizing: the cash risk per trade is a fraction of
      # current equity; stop distance is based on ATR.
      current_equity_after_exit <- cash
      stop_distance <- max(atr[i] * p$stop_atr, next_open * 0.005)
      risk_budget   <- current_equity_after_exit * p$risk_frac

      raw_shares <- floor(risk_budget / stop_distance)
      max_shares <- floor((current_equity_after_exit * max_capital_frac) / next_open)
      shares_to_trade <- max(0L, min(raw_shares, max_shares))

      if (shares_to_trade >= 1L) {
        if (desired_signal == 1L) {
          entry_exec_price <- next_open * (1 + slip)
          cash <- cash - shares_to_trade * entry_exec_price - commission
          position      <- 1L
          shares        <- shares_to_trade
          entry_price   <- entry_exec_price
          entry_atr     <- atr[i]
          entry_date    <- as.Date(dts[i + 1])
          entry_style   <- desired_style
          bars_held     <- 0L
          highest_close <- current_close
          lowest_close  <- NA_real_

          append_trade(date = dts[i + 1],
                       event = "LONG_ENTRY",
                       direction = "LONG",
                       shares = shares,
                       price = entry_exec_price,
                       reason = desired_style,
                       trade_pnl = NA_real_,
                       cash_after = cash)
        }

        if (desired_signal == -1L) {
          entry_exec_price <- next_open * (1 - slip)
          cash <- cash + shares_to_trade * entry_exec_price - commission
          position      <- -1L
          shares        <- shares_to_trade
          entry_price   <- entry_exec_price
          entry_atr     <- atr[i]
          entry_date    <- as.Date(dts[i + 1])
          entry_style   <- desired_style
          bars_held     <- 0L
          highest_close <- NA_real_
          lowest_close  <- current_close

          append_trade(date = dts[i + 1],
                       event = "SHORT_ENTRY",
                       direction = "SHORT",
                       shares = shares,
                       price = entry_exec_price,
                       reason = desired_style,
                       trade_pnl = NA_real_,
                       cash_after = cash)
        }
      }
    }
  }

  # Mark last close BEFORE any forced liquidation.
  equity[n] <- cash + position * shares * cls[n]


  # Force liquidation on the final bar so net profit is always
  # measured in realised cash terms.

  if (position == 1L) {
    final_exit_price <- cls[n] * (1 - slip)
    cash <- cash + shares * final_exit_price - commission
    realised_pnl <- shares * (final_exit_price - entry_price) - 2 * commission

    append_trade(date = dts[n],
                 event = "FINAL_LONG_EXIT",
                 direction = "LONG",
                 shares = shares,
                 price = final_exit_price,
                 reason = "Forced end-of-period liquidation",
                 trade_pnl = realised_pnl,
                 cash_after = cash)

    position <- 0L
    shares   <- 0L
    equity[n] <- cash
  }

  if (position == -1L) {
    final_exit_price <- cls[n] * (1 + slip)
    cash <- cash - shares * final_exit_price - commission
    realised_pnl <- shares * (entry_price - final_exit_price) - 2 * commission

    append_trade(date = dts[n],
                 event = "FINAL_SHORT_EXIT",
                 direction = "SHORT",
                 shares = shares,
                 price = final_exit_price,
                 reason = "Forced end-of-period liquidation",
                 trade_pnl = realised_pnl,
                 cash_after = cash)

    position <- 0L
    shares   <- 0L
    equity[n] <- cash
  }

  # Convert the trade log into a proper data.frame.
  if (length(trade_log_list) == 0) {
    trade_log <- data.frame(
      date = character(0),
      event = character(0),
      direction = character(0),
      shares = integer(0),
      price = numeric(0),
      reason = character(0),
      trade_pnl = numeric(0),
      cash_after = numeric(0),
      stringsAsFactors = FALSE
    )
  } else {
    trade_log <- do.call(rbind, trade_log_list)
  }

  equity_xts <- xts(equity, order.by = dts)
  colnames(equity_xts) <- "Equity"

  metrics <- compute_equity_metrics(equity_curve   = equity_xts,
                                    trade_log      = trade_log,
                                    initial_capital = initial_capital,
                                    final_equity   = cash)

  list(
    equity    = equity_xts,
    trade_log = trade_log,
    metrics   = metrics
  )
}

# 8. Buy-and-hold baseline

# Invest at the first available open in the period and liquidate at the last
# close. The same commission and slippage assumptions are applied so the
# comparison is fair.
buy_and_hold_backtest <- function(data,
                                  initial_capital = 10000,
                                  commission = 5,
                                  slippage_bps = 5) {
  slip <- slippage_bps / 10000
  opn  <- as.numeric(Op(data))
  cls  <- as.numeric(Cl(data))
  dts  <- index(data)

  entry_price <- opn[1] * (1 + slip)
  shares      <- floor((initial_capital - commission) / entry_price)
  cash        <- initial_capital - shares * entry_price - commission

  equity <- cash + shares * cls
  equity_xts <- xts(equity, order.by = dts)
  colnames(equity_xts) <- "Equity"

  final_exit_price <- cls[length(cls)] * (1 - slip)
  final_cash <- cash + shares * final_exit_price - commission
  equity_xts[length(equity_xts)] <- final_cash

  trade_log <- data.frame(
    date = c(as.character(dts[1]), as.character(dts[length(dts)])),
    event = c("BUY_AND_HOLD_ENTRY", "BUY_AND_HOLD_EXIT"),
    direction = c("LONG", "LONG"),
    shares = c(shares, shares),
    price = c(entry_price, final_exit_price),
    reason = c("Benchmark entry", "Forced end-of-period liquidation"),
    trade_pnl = c(NA_real_, shares * (final_exit_price - entry_price) - 2 * commission),
    cash_after = c(cash, final_cash),
    stringsAsFactors = FALSE
  )

  metrics <- compute_equity_metrics(equity_curve = equity_xts,
                                    trade_log = trade_log,
                                    initial_capital = initial_capital,
                                    final_equity = final_cash)

  list(
    equity = equity_xts,
    trade_log = trade_log,
    metrics = metrics
  )
}


# 9. Evaluate a parameter set

evaluate_strategy <- function(p) {
  full_data <- build_indicator_data(price_xts, p)
  train_data <- full_data[paste0("/", train_end_date)]
  test_data  <- full_data[paste0(test_start_date, "/")]

  train_bt <- backtest_strategy(train_data,
                                p,
                                initial_capital = initial_capital,
                                commission = commission_gbp,
                                slippage_bps = slippage_bps,
                                max_capital_frac = max_capital_frac)

  test_bt <- backtest_strategy(test_data,
                               p,
                               initial_capital = initial_capital,
                               commission = commission_gbp,
                               slippage_bps = slippage_bps,
                               max_capital_frac = max_capital_frac)

  list(
    params = p,
    full_data = full_data,
    train = train_bt,
    test = test_bt
  )
}

# 10. Fitness cache for the GA

# Evaluating a strategy is the expensive part. A simple in-memory cache avoids
# repeating identical evaluations if the GA revisits the same chromosome.
fitness_cache <- new.env(parent = emptyenv())

fitness_function <- function(x) {
  p <- repair_params(x)
  key <- paste(unlist(p), collapse = "_")

  if (exists(key, envir = fitness_cache, inherits = FALSE)) {
    return(get(key, envir = fitness_cache, inherits = FALSE))
  }

  result <- tryCatch({
    eval_list <- evaluate_strategy(p)
    fit <- eval_list$train$metrics$fitness[1]
    if (!is.finite(fit)) fit <- -1e9
    fit
  }, error = function(e) {
    -1e9
  })

  assign(key, result, envir = fitness_cache)
  result
}

# 11. Run the Genetic Algorithm

# The chosen GA settings are intentionally a little conservative to reduce
# overfitting pressure while still searching a meaningful mixed parameter space.
ga_result <- ga(type = "real-valued",
                fitness = fitness_function,
                lower = ga_lower,
                upper = ga_upper,
                popSize = 40,
                maxiter = 20,
                run = 8,
                elitism = 4,
                pcrossover = 0.8,
                pmutation = 0.15,
                keepBest = TRUE,
                seed = 123,
                monitor = gaMonitor)

best_solution <- ga_result@solution[1, ]
best_params   <- repair_params(best_solution)

# Evaluate the best strategy thoroughly on train and test data.
best_eval <- evaluate_strategy(best_params)

# 12. Evaluate baselines

fixed_eval <- evaluate_strategy(fixed_baseline_params)

full_for_buy_hold <- build_indicator_data(price_xts, best_params)
train_for_buy_hold <- full_for_buy_hold[paste0("/", train_end_date)]
test_for_buy_hold  <- full_for_buy_hold[paste0(test_start_date, "/")]

buyhold_train <- buy_and_hold_backtest(train_for_buy_hold,
                                       initial_capital = initial_capital,
                                       commission = commission_gbp,
                                       slippage_bps = slippage_bps)

buyhold_test <- buy_and_hold_backtest(test_for_buy_hold,
                                      initial_capital = initial_capital,
                                      commission = commission_gbp,
                                      slippage_bps = slippage_bps)


# 13. Random-search comparison

# The random baseline samples the same parameter space but without any guided
# evolutionary search. This gives a fair benchmark for the value added by the GA.
random_solution_generator <- function() {
  raw <- c(
    runif(1, ga_lower[1],  ga_upper[1]),
    runif(1, ga_lower[2],  ga_upper[2]),
    runif(1, ga_lower[3],  ga_upper[3]),
    runif(1, ga_lower[4],  ga_upper[4]),
    runif(1, ga_lower[5],  ga_upper[5]),
    runif(1, ga_lower[6],  ga_upper[6]),
    runif(1, ga_lower[7],  ga_upper[7]),
    runif(1, ga_lower[8],  ga_upper[8]),
    runif(1, ga_lower[9],  ga_upper[9]),
    runif(1, ga_lower[10], ga_upper[10]),
    runif(1, ga_lower[11], ga_upper[11]),
    runif(1, ga_lower[12], ga_upper[12]),
    runif(1, ga_lower[13], ga_upper[13]),
    runif(1, ga_lower[14], ga_upper[14]),
    runif(1, ga_lower[15], ga_upper[15])
  )
  repair_params(raw)
}

random_records <- vector("list", random_baseline_n)
random_param_archive <- vector("list", random_baseline_n)
for (j in seq_len(random_baseline_n)) {
  p_j <- random_solution_generator()
  random_param_archive[[j]] <- p_j
  e_j <- tryCatch(evaluate_strategy(p_j), error = function(e) NULL)

  if (is.null(e_j)) {
    random_records[[j]] <- data.frame(
      id = j,
      train_fitness = -1e9,
      train_net_profit = NA_real_,
      test_net_profit = NA_real_,
      test_sharpe = NA_real_,
      stringsAsFactors = FALSE
    )
  } else {
    random_records[[j]] <- data.frame(
      id = j,
      train_fitness = e_j$train$metrics$fitness[1],
      train_net_profit = e_j$train$metrics$net_profit[1],
      test_net_profit = e_j$test$metrics$net_profit[1],
      test_sharpe = e_j$test$metrics$sharpe[1],
      stringsAsFactors = FALSE
    )
  }
}

random_results <- do.call(rbind, random_records)
write.csv(random_results, "results/random_search_results.csv", row.names = FALSE)

best_random_idx <- which.max(random_results$train_fitness)
best_random_params <- random_param_archive[[best_random_idx]]
best_random_eval   <- evaluate_strategy(best_random_params)

random_summary <- data.frame(
  mean_train_fitness   = mean(random_results$train_fitness, na.rm = TRUE),
  best_train_fitness   = max(random_results$train_fitness, na.rm = TRUE),
  mean_train_profit    = mean(random_results$train_net_profit, na.rm = TRUE),
  mean_test_profit     = mean(random_results$test_net_profit, na.rm = TRUE),
  mean_test_sharpe     = mean(random_results$test_sharpe, na.rm = TRUE),
  best_random_row_id   = best_random_idx
)
write.csv(random_summary, "results/random_summary.csv", row.names = FALSE)


# 14. Build comparison tables

# Helper to extract a single-row metric table and add a strategy name.
with_name <- function(name, metrics_df) {
  out <- metrics_df
  out$strategy <- name
  out[, c("strategy", setdiff(names(out), "strategy"))]
}

train_comparison <- rbind(
  with_name("GA_Optimised",         best_eval$train$metrics),
  with_name("Fixed_Baseline",       fixed_eval$train$metrics),
  with_name("Best_Random_Solution", best_random_eval$train$metrics),
  with_name("Buy_and_Hold",         buyhold_train$metrics),
  data.frame(strategy = "Mean_Random_Solution",
             final_equity = NA_real_,
             net_profit = random_summary$mean_train_profit,
             total_return = NA_real_,
             annual_return = NA_real_,
             sharpe = NA_real_,
             max_dd_gbp = NA_real_,
             max_dd_pct = NA_real_,
             trades = NA_real_,
             win_rate = NA_real_,
             fitness = random_summary$mean_train_fitness)
)


test_comparison <- rbind(
  with_name("GA_Optimised",         best_eval$test$metrics),
  with_name("Fixed_Baseline",       fixed_eval$test$metrics),
  with_name("Best_Random_Solution", best_random_eval$test$metrics),
  with_name("Buy_and_Hold",         buyhold_test$metrics),
  data.frame(strategy = "Mean_Random_Solution",
             final_equity = NA_real_,
             net_profit = random_summary$mean_test_profit,
             total_return = NA_real_,
             annual_return = NA_real_,
             sharpe = random_summary$mean_test_sharpe,
             max_dd_gbp = NA_real_,
             max_dd_pct = NA_real_,
             trades = NA_real_,
             win_rate = NA_real_,
             fitness = NA_real_)
)

write.csv(train_comparison, "results/train_comparison.csv", row.names = FALSE)
write.csv(test_comparison,  "results/test_comparison.csv",  row.names = FALSE)

write.csv(
  data.frame(
    parameter = names(best_params),
    value = unlist(best_params),
    stringsAsFactors = FALSE
  ),
  "results/best_parameters.csv",
  row.names = FALSE
)

# Save trade logs for inspection.
write.csv(best_eval$train$trade_log, "results/train_trade_log_ga.csv", row.names = FALSE)
write.csv(best_eval$test$trade_log,  "results/test_trade_log_ga.csv",  row.names = FALSE)


# 15. Figures

# Figure 1: Adjusted close with train/test split
png("figures/01_price_split.png", width = 1200, height = 700)
plot(index(Ad(price_xts)), as.numeric(Ad(price_xts)),
     type = "l", lwd = 2,
     main = paste(symbol, "adjusted close with chronological train/test split"),
     xlab = "Date", ylab = "Adjusted close")
abline(v = train_end_date, lty = 2, lwd = 2)
legend("topleft",
       legend = c("Adjusted close", "Train/Test split"),
       lty = c(1, 2), lwd = c(2, 2), bty = "n")
dev.off()

# Figure 2: Training equity curves
png("figures/02_train_equity_curves.png", width = 1200, height = 700)
plot(index(best_eval$train$equity), as.numeric(best_eval$train$equity$Equity),
     type = "l", lwd = 2,
     main = "Training-period equity curves",
     xlab = "Date", ylab = "Equity (GBP)")
lines(index(fixed_eval$train$equity),   as.numeric(fixed_eval$train$equity$Equity), lwd = 2, lty = 2)
lines(index(buyhold_train$equity),      as.numeric(buyhold_train$equity$Equity), lwd = 2, lty = 3)
lines(index(best_random_eval$train$equity), as.numeric(best_random_eval$train$equity$Equity), lwd = 2, lty = 4)
legend("topleft",
       legend = c("GA optimised", "Fixed baseline", "Buy and hold", "Best random"),
       lty = c(1, 2, 3, 4), lwd = 2, bty = "n")
dev.off()

# Figure 3: Test equity curves
png("figures/03_test_equity_curves.png", width = 1200, height = 700)
plot(index(best_eval$test$equity), as.numeric(best_eval$test$equity$Equity),
     type = "l", lwd = 2,
     main = "Out-of-sample test equity curves",
     xlab = "Date", ylab = "Equity (GBP)")
lines(index(fixed_eval$test$equity),   as.numeric(fixed_eval$test$equity$Equity), lwd = 2, lty = 2)
lines(index(buyhold_test$equity),      as.numeric(buyhold_test$equity$Equity), lwd = 2, lty = 3)
lines(index(best_random_eval$test$equity), as.numeric(best_random_eval$test$equity$Equity), lwd = 2, lty = 4)
legend("topleft",
       legend = c("GA optimised", "Fixed baseline", "Buy and hold", "Best random"),
       lty = c(1, 2, 3, 4), lwd = 2, bty = "n")
dev.off()

# Figure 4: Random-search training fitness distribution versus the GA optimum.
png("figures/04_random_search_train_fitness.png", width = 1200, height = 700)
hist(random_results$train_fitness,
     breaks = 30,
     main = "Random-search training fitness distribution",
     xlab = "Training fitness",
     border = "white")
abline(v = best_eval$train$metrics$fitness[1], lwd = 3, lty = 2)
legend("topright",
       legend = c("GA best fitness"),
       lty = 2, lwd = 3, bty = "n")
dev.off()


# 16. Collect everything into a single results object

results <- list(
  config = list(
    symbol = symbol,
    start_date = start_date,
    end_date = end_date,
    train_end_date = train_end_date,
    test_start_date = test_start_date,
    initial_capital = initial_capital,
    commission_gbp = commission_gbp,
    slippage_bps = slippage_bps,
    max_capital_frac = max_capital_frac,
    random_baseline_n = random_baseline_n,
    allow_short_positions = allow_short_positions
  ),
  data_summary = data_summary,
  ga_object = ga_result,
  best_params = best_params,
  fixed_baseline_params = fixed_baseline_params,
  best_random_params = best_random_params,
  best_eval = best_eval,
  fixed_eval = fixed_eval,
  best_random_eval = best_random_eval,
  buyhold_train = buyhold_train,
  buyhold_test = buyhold_test,
  train_comparison = train_comparison,
  test_comparison = test_comparison,
  random_results = random_results,
  random_summary = random_summary
)

saveRDS(results, "results/ga_regime_strategy_results.rds")


# 17. Console summary

cat("\n===============================================================\n")
cat("GA-optimised regime-switching strategy completed.\n")
cat("Symbol: ", symbol, "\n", sep = "")
cat("Best parameters found:\n")
print(best_params)
cat("\nTraining metrics (GA best):\n")
print(best_eval$train$metrics)
cat("\nTest metrics (GA best):\n")
print(best_eval$test$metrics)
cat("\nComparison tables written to the 'results' folder.\n")
cat("Figures written to the 'figures' folder.\n")
cat("===============================================================\n\n")
