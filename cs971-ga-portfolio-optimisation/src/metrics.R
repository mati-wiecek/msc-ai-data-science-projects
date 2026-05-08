# Portfolio metrics and weight utilities.

normalise_weights <- function(weights) {
  if (sum(weights) <= 0 || any(!is.finite(weights))) {
    stop("Weights must be finite and have a positive sum.", call. = FALSE)
  }
  weights / sum(weights)
}

annualised_metrics_mucov <- function(weights, mu_daily, cov_daily, scale = 252) {
  if (sum(weights) == 0 || any(!is.finite(weights))) {
    return(c(Return = NA_real_, Risk = NA_real_, Sharpe = NA_real_))
  }

  weights <- weights / sum(weights)
  ann_return <- sum(weights * mu_daily) * scale
  ann_risk <- sqrt(drop(t(weights) %*% cov_daily %*% weights)) * sqrt(scale)
  sharpe <- ann_return / ann_risk

  c(Return = ann_return, Risk = ann_risk, Sharpe = sharpe)
}

portfolio_log_returns <- function(weights, returns_xts) {
  weights <- normalise_weights(weights)
  xts::xts(as.vector(as.matrix(returns_xts) %*% weights), order.by = xts::index(returns_xts))
}

max_drawdown_from_log_returns <- function(log_returns) {
  growth <- exp(cumsum(as.numeric(log_returns)))
  drawdown <- growth / cummax(growth) - 1
  min(drawdown, na.rm = TRUE)
}

portfolio_series_metrics <- function(weights, returns_xts, scale = 252) {
  if (sum(weights) == 0 || any(!is.finite(weights))) {
    return(c(Return = NA_real_, Risk = NA_real_, Sharpe = NA_real_, MaxDrawdown = NA_real_))
  }

  port_log <- portfolio_log_returns(weights, returns_xts)
  ann_return <- mean(port_log, na.rm = TRUE) * scale
  ann_risk <- stats::sd(port_log, na.rm = TRUE) * sqrt(scale)
  sharpe <- ann_return / ann_risk
  max_drawdown <- max_drawdown_from_log_returns(port_log)

  c(Return = ann_return, Risk = ann_risk, Sharpe = sharpe, MaxDrawdown = max_drawdown)
}

rank_percentile <- function(value, sample_values) {
  mean(sample_values <= value, na.rm = TRUE) * 100
}

round_numeric_columns <- function(data, digits = 4) {
  out <- data
  numeric_cols <- vapply(out, is.numeric, logical(1))
  out[numeric_cols] <- lapply(out[numeric_cols], round, digits = digits)
  out
}

rownames_to_column <- function(data, column_name = "Portfolio") {
  out <- data
  out[[column_name]] <- rownames(out)
  rownames(out) <- NULL
  out[, c(column_name, setdiff(names(out), column_name)), drop = FALSE]
}
