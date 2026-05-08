"""Command-line experiment runner.

Usage:
    python -m spotify_ml.run_experiments --data-dir data/raw --output-dir outputs --figure-dir figures
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .config import (
    CLASSIFICATION_TARGET,
    DEFAULT_DATA_DIR,
    DEFAULT_FIGURE_DIR,
    DEFAULT_OUTPUT_DIR,
    ID_COLUMN,
    REGRESSION_TARGET,
)
from .data import load_datasets, validate_submission
from .evaluation import metrics_frame
from .pipelines import (
    classification_baseline_table,
    classification_text_variant_score,
    fit_classification_final,
    fit_regression_final,
    regression_baseline_table,
)


def _save_barh(series: pd.Series, title: str, xlabel: str, ylabel: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    series.sort_values().plot(kind="barh", ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _save_metric_bars(df: pd.DataFrame, task: str, title: str, ylabel: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    subset = df[df["task"] == task].copy()
    if subset.empty:
        return
    fig, ax = plt.subplots(figsize=(9, 5))
    subset.set_index("model")["validation_metric"].plot(kind="bar", ax=ax)
    ax.set_title(title)
    ax.set_xlabel("model")
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def run(args: argparse.Namespace) -> None:
    data = load_datasets(args.data_dir)
    output_dir = Path(args.output_dir)
    figure_dir = Path(args.figure_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    regression_baselines = regression_baseline_table(data.regression_train)
    classification_baselines = classification_baseline_table(data.classification_train)
    text_variant = pd.DataFrame([classification_text_variant_score(data.classification_train)])
    metrics = metrics_frame(
        (regression_baselines.to_dict("records")
         + classification_baselines.to_dict("records")
         + text_variant.to_dict("records"))
    )
    metrics.to_csv(output_dir / "local_validation_metrics.csv", index=False)

    regression_submission, regression_diagnostics = fit_regression_final(
        data.regression_train,
        data.regression_test,
        mode=args.mode,
        use_title_text=args.use_title_text,
    )
    validate_submission(
        regression_submission,
        expected_rows=len(data.regression_test),
        expected_columns=[ID_COLUMN, REGRESSION_TARGET],
    )
    regression_submission.to_csv(output_dir / "regression_submission.csv", index=False)

    classification_submission, classification_diagnostics = fit_classification_final(
        data.classification_train,
        data.classification_test,
    )
    validate_submission(
        classification_submission,
        expected_rows=len(data.classification_test),
        expected_columns=[ID_COLUMN, CLASSIFICATION_TARGET],
    )
    classification_submission.to_csv(output_dir / "classification_submission.csv", index=False)

    diagnostics = {
        "regression": regression_diagnostics,
        "classification": classification_diagnostics,
    }
    (output_dir / "model_diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")

    # Figures for the README/report.
    fig, ax = plt.subplots(figsize=(8, 5))
    data.regression_train[REGRESSION_TARGET].hist(bins=20, ax=ax)
    ax.set_title("Popularity target distribution")
    ax.set_xlabel("popularity")
    ax.set_ylabel("count")
    fig.tight_layout()
    fig.savefig(figure_dir / "regression_target_distribution.png", dpi=160)
    plt.close(fig)

    class_counts = data.classification_train[CLASSIFICATION_TARGET].dropna().value_counts().head(15)
    _save_barh(
        class_counts,
        "Top 15 genre labels by frequency",
        "count",
        "genre",
        figure_dir / "classification_class_distribution.png",
    )
    _save_metric_bars(
        metrics,
        "regression",
        "Regression validation RMSE by model",
        "RMSE (lower is better)",
        figure_dir / "regression_validation_rmse.png",
    )
    _save_metric_bars(
        metrics,
        "classification",
        "Classification validation accuracy by model",
        "accuracy (higher is better)",
        figure_dir / "classification_validation_accuracy.png",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Spotify-style ML experiments.")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR), help="Directory with raw CSV files.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for generated outputs.")
    parser.add_argument("--figure-dir", default=str(DEFAULT_FIGURE_DIR), help="Directory for generated figures.")
    parser.add_argument(
        "--mode",
        choices=["quick", "full"],
        default="quick",
        help="Regression training budget. Full mode is slower and uses more CatBoost iterations.",
    )
    parser.add_argument(
        "--use-title-text",
        action="store_true",
        help="Include the song title as a CatBoost text feature for regression.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    run(parser.parse_args())


if __name__ == "__main__":
    main()
