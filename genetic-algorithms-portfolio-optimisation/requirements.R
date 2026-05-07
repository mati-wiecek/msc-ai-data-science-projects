packages <- c(
  "knitr",
  "rmarkdown",
  "quantmod",
  "TTR",
  "GA",
  "xts",
  "zoo"
)

missing_packages <- packages[!vapply(packages, requireNamespace, logical(1), quietly = TRUE)]

if (length(missing_packages) > 0) {
  install.packages(missing_packages)
}
