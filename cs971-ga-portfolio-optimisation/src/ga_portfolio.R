# Genetic algorithm helpers for portfolio optimisation and asset selection.

make_manual_asset_table <- function() {
  data.frame(
    Ticker = c("GOOGL", "NVDA", "META", "XOM", "NEE", "JPM", "MA", "WMT", "PG", "EL"),
    Sector = c(
      "Communication Services", "Information Technology", "Communication Services",
      "Energy", "Utilities", "Financials", "Financials",
      "Consumer Staples", "Consumer Staples", "Consumer Staples"
    ),
    PortfolioRole = c(
      "Growth / technology exposure", "Growth / technology exposure", "Growth / technology exposure",
      "Energy exposure", "Defensive utility exposure", "Cyclical financial exposure",
      "Quality financial exposure", "Defensive consumer exposure", "Defensive consumer exposure",
      "Consumer discretionary tilt"
    ),
    stringsAsFactors = FALSE
  )
}

make_large_cap_universe <- function() {
  c(
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "BRK-B", "LLY", "V",
    "UNH", "XOM", "JNJ", "JPM", "PG", "MA", "AVGO", "HD", "CVX", "MRK",
    "ABBV", "COST", "PEP", "ADBE", "WMT", "KO", "CSCO", "BAC", "ACN", "MCD",
    "TMO", "LIN", "ABT", "DIS", "AMD", "NFLX", "DHR", "INTC", "WFC", "VZ",
    "COP", "PM", "NEE", "CAT", "NKE", "UPS", "LOW", "BA", "IBM", "GE"
  )
}

create_equal_weights <- function(n_assets) {
  rep(1 / n_assets, n_assets)
}

generate_random_weights <- function(n_portfolios, n_assets) {
  weights <- matrix(stats::rexp(n_portfolios * n_assets, rate = 1),
                    nrow = n_portfolios, ncol = n_assets)
  weights / rowSums(weights)
}

optimise_weights_sharpe <- function(mu_train,
                                    cov_train,
                                    pop_size = 60,
                                    max_iter = 80,
                                    run = 30,
                                    elitism = 2,
                                    mutation_probability = 0.20,
                                    crossover_probability = 0.80) {
  n_assets <- length(mu_train)

  fitness <- function(weights) {
    if (sum(weights) == 0) return(-1e6)
    metrics <- annualised_metrics_mucov(weights, mu_train, cov_train)
    if (!is.finite(metrics["Sharpe"])) return(-1e6)
    as.numeric(metrics["Sharpe"])
  }

  model <- GA::ga(
    type = "real-valued",
    fitness = fitness,
    lower = rep(0, n_assets),
    upper = rep(1, n_assets),
    popSize = pop_size,
    maxiter = max_iter,
    run = run,
    elitism = elitism,
    pmutation = mutation_probability,
    pcrossover = crossover_probability,
    monitor = FALSE
  )

  weights <- model@solution[1, ]
  weights <- normalise_weights(weights)
  names(weights) <- names(mu_train)

  list(model = model, weights = weights)
}

optimise_weights_return_risk <- function(mu_train,
                                         cov_train,
                                         lambda,
                                         pop_size = 55,
                                         max_iter = 60,
                                         run = 20,
                                         elitism = 2,
                                         mutation_probability = 0.20,
                                         crossover_probability = 0.80) {
  n_assets <- length(mu_train)

  fitness <- function(weights) {
    if (sum(weights) == 0) return(-1e6)
    metrics <- annualised_metrics_mucov(weights, mu_train, cov_train)
    if (!is.finite(metrics["Return"]) || !is.finite(metrics["Risk"])) return(-1e6)
    as.numeric(lambda * metrics["Return"] - (1 - lambda) * metrics["Risk"])
  }

  model <- GA::ga(
    type = "real-valued",
    fitness = fitness,
    lower = rep(0, n_assets),
    upper = rep(1, n_assets),
    popSize = pop_size,
    maxiter = max_iter,
    run = run,
    elitism = elitism,
    pmutation = mutation_probability,
    pcrossover = crossover_probability,
    monitor = FALSE
  )

  weights <- model@solution[1, ]
  weights <- normalise_weights(weights)
  names(weights) <- names(mu_train)

  list(model = model, weights = weights)
}

make_binary_suggestions <- function(n_suggestions, n_bits, target_k) {
  suggestions <- matrix(0, nrow = n_suggestions, ncol = n_bits)
  for (i in seq_len(n_suggestions)) {
    selected <- sample.int(n_bits, target_k, replace = FALSE)
    suggestions[i, selected] <- 1
  }
  suggestions
}

optimise_asset_selection_proxy <- function(mu_train,
                                           cov_train,
                                           target_k = 10,
                                           min_k = 8,
                                           max_k = 12,
                                           size_regularisation = 0.15,
                                           pop_size = 35,
                                           max_iter = 55,
                                           run = 20,
                                           mutation_probability = 0.15,
                                           crossover_probability = 0.80) {
  n_bits <- length(mu_train)

  fitness <- function(genes) {
    k <- sum(genes)
    if (k < min_k || k > max_k) return(-1e6)

    weights <- genes / sum(genes)
    metrics <- annualised_metrics_mucov(weights, mu_train, cov_train)
    if (!is.finite(metrics["Sharpe"])) return(-1e6)

    as.numeric(metrics["Sharpe"] - size_regularisation * abs(k - target_k))
  }

  model <- GA::ga(
    type = "binary",
    fitness = fitness,
    nBits = n_bits,
    popSize = pop_size,
    maxiter = max_iter,
    run = run,
    elitism = 2,
    pmutation = mutation_probability,
    pcrossover = crossover_probability,
    suggestions = make_binary_suggestions(pop_size, n_bits, target_k),
    monitor = FALSE
  )

  genes <- model@solution[1, ]
  selected_idx <- which(genes == 1)

  list(model = model, genes = genes, selected_idx = selected_idx)
}

optimise_asset_selection_integrated <- function(mu_train,
                                                cov_train,
                                                target_k = 10,
                                                min_k = 8,
                                                max_k = 12,
                                                size_regularisation = 0.15,
                                                pop_size = 25,
                                                max_iter = 30,
                                                run = 12,
                                                inner_pop = 25,
                                                inner_iter = 35,
                                                inner_run = 12,
                                                mutation_probability = 0.12,
                                                crossover_probability = 0.80) {
  n_bits <- length(mu_train)
  cache_env <- new.env(parent = emptyenv())

  fitness <- function(genes) {
    k <- sum(genes)
    if (k < min_k || k > max_k) return(-1e6)

    selected_idx <- which(genes == 1)
    cache_key <- paste(selected_idx, collapse = "-")

    if (exists(cache_key, envir = cache_env, inherits = FALSE)) {
      return(get(cache_key, envir = cache_env, inherits = FALSE))
    }

    mu_sub <- mu_train[selected_idx]
    cov_sub <- cov_train[selected_idx, selected_idx, drop = FALSE]

    inner <- optimise_weights_sharpe(
      mu_train = mu_sub,
      cov_train = cov_sub,
      pop_size = inner_pop,
      max_iter = inner_iter,
      run = inner_run,
      elitism = 1,
      mutation_probability = 0.25,
      crossover_probability = 0.80
    )

    score <- annualised_metrics_mucov(inner$weights, mu_sub, cov_sub)["Sharpe"] -
      size_regularisation * abs(k - target_k)

    score <- as.numeric(score)
    assign(cache_key, score, envir = cache_env)
    score
  }

  model <- GA::ga(
    type = "binary",
    fitness = fitness,
    nBits = n_bits,
    popSize = pop_size,
    maxiter = max_iter,
    run = run,
    elitism = 1,
    pmutation = mutation_probability,
    pcrossover = crossover_probability,
    suggestions = make_binary_suggestions(pop_size, n_bits, target_k),
    monitor = FALSE
  )

  genes <- model@solution[1, ]
  selected_idx <- which(genes == 1)

  list(model = model, genes = genes, selected_idx = selected_idx)
}

summarise_top_weights <- function(weight_list) {
  do.call(rbind, lapply(names(weight_list), function(label) {
    weights <- weight_list[[label]]
    order_idx <- order(weights, decreasing = TRUE)[seq_len(min(3, length(weights)))]
    top_values <- paste0(names(weights)[order_idx], " (", round(weights[order_idx], 3), ")")
    data.frame(
      Lambda = as.numeric(label),
      Top1 = top_values[1],
      Top2 = top_values[2],
      Top3 = top_values[3],
      stringsAsFactors = FALSE
    )
  }))
}
