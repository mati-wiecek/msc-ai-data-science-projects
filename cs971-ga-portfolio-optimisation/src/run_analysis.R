# End-to-end analysis script. Run from the repository root with:
# Rscript src/run_analysis.R

set.seed(123)

source("src/data_utils.R")
source("src/metrics.R")
source("src/ga_portfolio.R")
source("src/plotting.R")

load_required_packages(c("quantmod", "GA", "xts"))

dir.create("data/raw", recursive = TRUE, showWarnings = FALSE)
dir.create("outputs", recursive = TRUE, showWarnings = FALSE)
dir.create("figures", recursive = TRUE, showWarnings = FALSE)

START_DATE <- "2021-01-01"
END_DATE <- "2025-12-31"
TRAIN_WINDOW <- "2021/2024"
HOLDOUT_WINDOW <- "2025"

assets_manual <- make_manual_asset_table()
tickers_10 <- assets_manual$Ticker

prices_10 <- download_adjusted_prices(
  tickers = tickers_10,
  start_date = START_DATE,
  end_date = END_DATE,
  cache_path = "data/raw/prices_manual_10.rds"
)

returns_10 <- calculate_log_returns(prices_10)
split_10 <- split_returns(returns_10, TRAIN_WINDOW, HOLDOUT_WINDOW)
train_10 <- split_10$train
holdout_10 <- split_10$holdout

mu_train_10 <- colMeans(train_10)
cov_train_10 <- stats::cov(train_10)
mu_holdout_10 <- colMeans(holdout_10)
cov_holdout_10 <- stats::cov(holdout_10)

corr_matrix <- stats::cor(train_10)
save_base_plot(
  "figures/correlation_matrix_train.png",
  plot_correlation_matrix(corr_matrix, "Correlation matrix (train: 2021-2024)")
)

weight_ga <- optimise_weights_sharpe(mu_train_10, cov_train_10)
w_ga <- weight_ga$weights
w_equal <- create_equal_weights(length(w_ga))
names(w_equal) <- names(w_ga)

weights_table <- data.frame(
  Ticker = names(w_ga),
  Weight_GA = as.numeric(w_ga),
  Weight_Equal = as.numeric(w_equal),
  stringsAsFactors = FALSE
)
weights_table <- weights_table[order(-weights_table$Weight_GA), ]
write.csv(weights_table, "outputs/manual_portfolio_weights.csv", row.names = FALSE)

train_performance <- rbind(
  GA_Train = portfolio_series_metrics(w_ga, train_10),
  Equal_Train = portfolio_series_metrics(w_equal, train_10)
)
holdout_performance <- rbind(
  GA_Holdout = portfolio_series_metrics(w_ga, holdout_10),
  Equal_Holdout = portfolio_series_metrics(w_equal, holdout_10)
)
write.csv(rownames_to_column(as.data.frame(train_performance)), "outputs/train_performance.csv", row.names = FALSE)
write.csv(rownames_to_column(as.data.frame(holdout_performance)), "outputs/holdout_performance.csv", row.names = FALSE)

port_ga_holdout <- portfolio_log_returns(w_ga, holdout_10)
port_equal_holdout <- portfolio_log_returns(w_equal, holdout_10)
growth_ga <- exp(cumsum(port_ga_holdout))
growth_equal <- exp(cumsum(port_equal_holdout))
save_base_plot(
  "figures/cumulative_growth_holdout.png",
  plot_cumulative_growth(growth_ga, growth_equal, "Cumulative growth in holdout period")
)

n_random <- 2000
random_weights <- generate_random_weights(n_random, length(w_ga))
random_train_metrics <- t(apply(random_weights, 1, annualised_metrics_mucov,
                                mu_daily = mu_train_10, cov_daily = cov_train_10))
random_holdout_metrics <- t(apply(random_weights, 1, annualised_metrics_mucov,
                                  mu_daily = mu_holdout_10, cov_daily = cov_holdout_10))

ga_train_metrics <- annualised_metrics_mucov(w_ga, mu_train_10, cov_train_10)
eq_train_metrics <- annualised_metrics_mucov(w_equal, mu_train_10, cov_train_10)
ga_holdout_metrics <- annualised_metrics_mucov(w_ga, mu_holdout_10, cov_holdout_10)
eq_holdout_metrics <- annualised_metrics_mucov(w_equal, mu_holdout_10, cov_holdout_10)

rank_table <- data.frame(
  Portfolio = c("Genetic algorithm weights", "Equal weights"),
  Train_Sharpe = c(ga_train_metrics["Sharpe"], eq_train_metrics["Sharpe"]),
  Train_Percentile = c(
    rank_percentile(ga_train_metrics["Sharpe"], random_train_metrics[, "Sharpe"]),
    rank_percentile(eq_train_metrics["Sharpe"], random_train_metrics[, "Sharpe"])
  ),
  Holdout_Sharpe = c(ga_holdout_metrics["Sharpe"], eq_holdout_metrics["Sharpe"]),
  Holdout_Percentile = c(
    rank_percentile(ga_holdout_metrics["Sharpe"], random_holdout_metrics[, "Sharpe"]),
    rank_percentile(eq_holdout_metrics["Sharpe"], random_holdout_metrics[, "Sharpe"])
  ),
  stringsAsFactors = FALSE
)
write.csv(rank_table, "outputs/random_portfolio_rankings.csv", row.names = FALSE)

save_base_plot(
  "figures/risk_return_train.png",
  plot_risk_return_cloud(
    random_metrics = random_train_metrics,
    ga_metrics = ga_train_metrics,
    equal_metrics = eq_train_metrics,
    title = "Risk-return comparison (train)"
  )
)

lambda_grid <- seq(0, 1, by = 0.2)
preference_results <- list()
preference_weights <- list()

for (lambda in lambda_grid) {
  solution <- optimise_weights_return_risk(mu_train_10, cov_train_10, lambda = lambda)
  weights <- solution$weights
  preference_weights[[as.character(lambda)]] <- weights

  train_metrics <- annualised_metrics_mucov(weights, mu_train_10, cov_train_10)
  holdout_metrics <- annualised_metrics_mucov(weights, mu_holdout_10, cov_holdout_10)

  preference_results[[as.character(lambda)]] <- data.frame(
    Lambda = lambda,
    Train_Return = as.numeric(train_metrics["Return"]),
    Train_Risk = as.numeric(train_metrics["Risk"]),
    Train_Sharpe = as.numeric(train_metrics["Sharpe"]),
    Holdout_Return = as.numeric(holdout_metrics["Return"]),
    Holdout_Risk = as.numeric(holdout_metrics["Risk"]),
    Holdout_Sharpe = as.numeric(holdout_metrics["Sharpe"]),
    stringsAsFactors = FALSE
  )
}

preference_table <- do.call(rbind, preference_results)
preference_table <- preference_table[order(preference_table$Lambda), ]
write.csv(preference_table, "outputs/preference_sweep_metrics.csv", row.names = FALSE)

top_weights_table <- summarise_top_weights(preference_weights)
top_weights_table <- top_weights_table[order(top_weights_table$Lambda), ]
write.csv(top_weights_table, "outputs/preference_sweep_top_weights.csv", row.names = FALSE)

save_base_plot(
  "figures/lambda_risk_return_tradeoff.png",
  plot_lambda_tradeoff(preference_table, "Risk-return trade-off across lambda")
)

pool_tickers <- make_large_cap_universe()
prices_pool <- download_adjusted_prices(
  tickers = pool_tickers,
  start_date = START_DATE,
  end_date = END_DATE,
  cache_path = "data/raw/prices_pool_50.rds"
)
returns_pool <- calculate_log_returns(prices_pool)
split_pool <- split_returns(returns_pool, TRAIN_WINDOW, HOLDOUT_WINDOW)
train_pool <- split_pool$train
holdout_pool <- split_pool$holdout

mu_pool_train <- colMeans(train_pool)
cov_pool_train <- stats::cov(train_pool)
mu_pool_holdout <- colMeans(holdout_pool)
cov_pool_holdout <- stats::cov(holdout_pool)

proxy_selection <- optimise_asset_selection_proxy(mu_pool_train, cov_pool_train)
proxy_tickers <- colnames(train_pool)[proxy_selection$selected_idx]

train_proxy <- train_pool[, proxy_tickers]
holdout_proxy <- holdout_pool[, proxy_tickers]
mu_proxy_train <- colMeans(train_proxy)
cov_proxy_train <- stats::cov(train_proxy)
mu_proxy_holdout <- colMeans(holdout_proxy)
cov_proxy_holdout <- stats::cov(holdout_proxy)

proxy_weight_solution <- optimise_weights_sharpe(mu_proxy_train, cov_proxy_train)
w_proxy_ga <- proxy_weight_solution$weights
w_proxy_equal <- create_equal_weights(length(proxy_tickers))

proxy_table <- rbind(
  Proxy_Equal_Train = annualised_metrics_mucov(w_proxy_equal, mu_proxy_train, cov_proxy_train),
  Proxy_GA_Train = annualised_metrics_mucov(w_proxy_ga, mu_proxy_train, cov_proxy_train),
  Proxy_Equal_Holdout = annualised_metrics_mucov(w_proxy_equal, mu_proxy_holdout, cov_proxy_holdout),
  Proxy_GA_Holdout = annualised_metrics_mucov(w_proxy_ga, mu_proxy_holdout, cov_proxy_holdout)
)
write.csv(rownames_to_column(as.data.frame(proxy_table)), "outputs/proxy_selection_performance.csv", row.names = FALSE)
write.csv(data.frame(Ticker = proxy_tickers), "outputs/proxy_selected_assets.csv", row.names = FALSE)

integrated_selection <- optimise_asset_selection_integrated(mu_pool_train, cov_pool_train)
integrated_tickers <- colnames(train_pool)[integrated_selection$selected_idx]

train_integrated <- train_pool[, integrated_tickers]
holdout_integrated <- holdout_pool[, integrated_tickers]
mu_integrated_train <- colMeans(train_integrated)
cov_integrated_train <- stats::cov(train_integrated)
mu_integrated_holdout <- colMeans(holdout_integrated)
cov_integrated_holdout <- stats::cov(holdout_integrated)

integrated_weight_solution <- optimise_weights_sharpe(
  mu_integrated_train, cov_integrated_train,
  pop_size = 65, max_iter = 70, run = 22
)
w_integrated <- integrated_weight_solution$weights

integrated_table <- rbind(
  Integrated_GA_Train = annualised_metrics_mucov(w_integrated, mu_integrated_train, cov_integrated_train),
  Integrated_GA_Holdout = annualised_metrics_mucov(w_integrated, mu_integrated_holdout, cov_integrated_holdout)
)
write.csv(rownames_to_column(as.data.frame(integrated_table)), "outputs/integrated_selection_performance.csv", row.names = FALSE)
write.csv(data.frame(Ticker = integrated_tickers), "outputs/integrated_selected_assets.csv", row.names = FALSE)

n_subsets <- 300
subset_size <- 10
random_subset_sharpes <- numeric(n_subsets)
for (i in seq_len(n_subsets)) {
  subset_i <- sample(colnames(train_pool), subset_size, replace = FALSE)
  mu_i <- mu_pool_holdout[subset_i]
  cov_i <- cov_pool_holdout[subset_i, subset_i, drop = FALSE]
  w_i <- create_equal_weights(subset_size)
  random_subset_sharpes[i] <- annualised_metrics_mucov(w_i, mu_i, cov_i)["Sharpe"]
}

subset_comparison <- data.frame(
  Portfolio = c("Manual 10 assets with GA weights", "Integrated selection with GA weights", "Random subset equal-weight mean"),
  Holdout_Sharpe = c(
    as.numeric(ga_holdout_metrics["Sharpe"]),
    as.numeric(annualised_metrics_mucov(w_integrated, mu_integrated_holdout, cov_integrated_holdout)["Sharpe"]),
    mean(random_subset_sharpes, na.rm = TRUE)
  ),
  Percentile_vs_Random_Subsets = c(
    rank_percentile(ga_holdout_metrics["Sharpe"], random_subset_sharpes),
    rank_percentile(annualised_metrics_mucov(w_integrated, mu_integrated_holdout, cov_integrated_holdout)["Sharpe"], random_subset_sharpes),
    NA_real_
  ),
  stringsAsFactors = FALSE
)
write.csv(subset_comparison, "outputs/random_subset_comparison.csv", row.names = FALSE)

message("Analysis complete. Tables saved to outputs/ and figures saved to figures/.")
