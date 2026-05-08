# Utility functions for downloading price data and preparing return series.

load_required_packages <- function(packages) {
  missing_packages <- packages[!vapply(packages, requireNamespace, logical(1), quietly = TRUE)]
  if (length(missing_packages) > 0) {
    stop(
      "Missing required R packages: ", paste(missing_packages, collapse = ", "),
      ". Install them before running the analysis.",
      call. = FALSE
    )
  }

  invisible(lapply(packages, library, character.only = TRUE))
}

safe_get_adjusted <- function(symbol, start_date, end_date) {
  tryCatch({
    x <- suppressWarnings(
      quantmod::getSymbols(
        symbol,
        src = "yahoo",
        from = start_date,
        to = end_date,
        auto.assign = FALSE
      )
    )
    quantmod::Ad(x)
  }, error = function(e) {
    warning("Download failed for ", symbol, ": ", conditionMessage(e), call. = FALSE)
    NULL
  })
}

download_adjusted_prices <- function(tickers,
                                     start_date,
                                     end_date,
                                     cache_path = NULL,
                                     refresh_cache = FALSE) {
  if (!is.null(cache_path) && file.exists(cache_path) && !refresh_cache) {
    return(readRDS(cache_path))
  }

  price_list <- lapply(tickers, safe_get_adjusted, start_date = start_date, end_date = end_date)
  names(price_list) <- tickers

  valid <- !vapply(price_list, is.null, logical(1))
  price_list <- price_list[valid]

  if (length(price_list) == 0) {
    stop("No price series were downloaded successfully.", call. = FALSE)
  }

  prices <- do.call(merge, price_list)
  colnames(prices) <- names(price_list)
  prices <- stats::na.omit(prices)

  if (!is.null(cache_path)) {
    dir.create(dirname(cache_path), recursive = TRUE, showWarnings = FALSE)
    saveRDS(prices, cache_path)
  }

  prices
}

calculate_log_returns <- function(prices) {
  stats::na.omit(diff(log(prices)))
}

split_returns <- function(returns, train_window = "2021/2024", holdout_window = "2025") {
  list(
    train = returns[train_window],
    holdout = returns[holdout_window]
  )
}
