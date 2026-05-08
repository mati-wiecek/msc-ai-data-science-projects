# Plotting helpers for the portfolio optimisation analysis.

plot_correlation_matrix <- function(corr_matrix, title = "Correlation matrix") {
  old_par <- graphics::par(no.readonly = TRUE)
  on.exit(graphics::par(old_par), add = TRUE)

  graphics::par(mar = c(7, 7, 2.5, 1))
  graphics::image(
    seq_len(ncol(corr_matrix)), seq_len(ncol(corr_matrix)),
    corr_matrix[ncol(corr_matrix):1, ],
    axes = FALSE,
    xlab = "", ylab = "",
    main = title,
    col = grDevices::heat.colors(50)
  )
  graphics::axis(1, at = seq_len(ncol(corr_matrix)), labels = colnames(corr_matrix), las = 2, cex.axis = 0.8)
  graphics::axis(2, at = seq_len(ncol(corr_matrix)), labels = rev(colnames(corr_matrix)), las = 2, cex.axis = 0.8)
}

plot_cumulative_growth <- function(growth_ga, growth_equal, title = "Cumulative growth") {
  dates <- xts::index(growth_ga)
  y_values <- range(c(as.numeric(growth_ga), as.numeric(growth_equal)), finite = TRUE)

  graphics::plot(
    dates, as.numeric(growth_ga),
    type = "l",
    lwd = 2,
    col = "steelblue",
    ylim = y_values,
    main = title,
    xlab = "Date",
    ylab = "Growth of 1"
  )
  graphics::lines(dates, as.numeric(growth_equal), lwd = 2, lty = 2, col = "firebrick")
  graphics::legend(
    "topleft",
    legend = c("Genetic algorithm weights", "Equal weights"),
    lty = c(1, 2), lwd = c(2, 2),
    col = c("steelblue", "firebrick"),
    bty = "n"
  )
}

plot_risk_return_cloud <- function(random_metrics,
                                   ga_metrics,
                                   equal_metrics,
                                   title = "Risk-return comparison") {
  graphics::plot(
    random_metrics[, "Risk"], random_metrics[, "Return"],
    pch = 16,
    cex = 0.35,
    col = grDevices::adjustcolor("grey45", alpha.f = 0.35),
    main = title,
    xlab = "Annualised risk (volatility)",
    ylab = "Annualised return"
  )
  graphics::points(ga_metrics["Risk"], ga_metrics["Return"], pch = 19, cex = 1.35, col = "steelblue")
  graphics::points(equal_metrics["Risk"], equal_metrics["Return"], pch = 17, cex = 1.35, col = "firebrick")
  graphics::text(ga_metrics["Risk"], ga_metrics["Return"], labels = "GA", pos = 3, col = "steelblue", cex = 0.85)
  graphics::text(equal_metrics["Risk"], equal_metrics["Return"], labels = "Equal", pos = 3, col = "firebrick", cex = 0.85)
  graphics::legend(
    "bottomright",
    legend = c("Random portfolios", "Genetic algorithm", "Equal weights"),
    pch = c(16, 19, 17),
    pt.cex = c(0.7, 1.1, 1.1),
    col = c("grey45", "steelblue", "firebrick"),
    bty = "n"
  )
}

plot_lambda_tradeoff <- function(preference_table, title = "Risk-return trade-off") {
  graphics::plot(
    preference_table$Train_Risk, preference_table$Train_Return,
    type = "b",
    pch = 19,
    lwd = 2,
    col = "steelblue",
    xlab = "Annualised risk (train)",
    ylab = "Annualised return (train)",
    main = title
  )
  graphics::text(
    preference_table$Train_Risk,
    preference_table$Train_Return,
    labels = preference_table$Lambda,
    pos = 3,
    cex = 0.75
  )
}

save_base_plot <- function(path, plot_expression, width = 7, height = 4.5, units = "in", res = 180) {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  grDevices::png(filename = path, width = width, height = height, units = units, res = res)
  on.exit(grDevices::dev.off(), add = TRUE)
  force(plot_expression)
}
