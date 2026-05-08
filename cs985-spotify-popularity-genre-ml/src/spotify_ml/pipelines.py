"""Model pipelines used by the project."""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVC

from .config import CLASSIFICATION_TARGET, ID_COLUMN, RANDOM_STATE, REGRESSION_TARGET
from .evaluation import rmse
from .features import add_artist_title_text, clean_year_and_add_decade


def make_one_hot_encoder(*, sparse: bool):
    """Create a version-compatible OneHotEncoder."""

    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=sparse)
    except TypeError:  # scikit-learn < 1.2
        return OneHotEncoder(handle_unknown="ignore", sparse=sparse)


def make_tabular_preprocessor(
    numeric_columns: Iterable[str],
    categorical_columns: Iterable[str],
    *,
    sparse_output: bool,
) -> ColumnTransformer:
    """Build a standard numeric/categorical preprocessing pipeline."""

    return ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                list(numeric_columns),
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("one_hot", make_one_hot_encoder(sparse=sparse_output)),
                    ]
                ),
                list(categorical_columns),
            ),
        ],
        remainder="drop",
    )


def regression_baseline_table(train_df: pd.DataFrame) -> pd.DataFrame:
    """Compare lightweight regression baselines on a reproducible validation split."""

    from sklearn.linear_model import LinearRegression, Ridge

    prepared = clean_year_and_add_decade(train_df)
    y = prepared[REGRESSION_TARGET].copy()
    X = prepared.drop(columns=[REGRESSION_TARGET])
    X = X.drop(columns=[c for c in [ID_COLUMN, "title", "artist", "year"] if c in X.columns])

    categorical = [c for c in ["top genre", "decade"] if c in X.columns]
    numeric = [c for c in X.columns if c not in categorical]
    preprocessor = make_tabular_preprocessor(numeric, categorical, sparse_output=False)

    X_train, X_valid, y_train, y_valid = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    models = {
        "Dummy mean": DummyRegressor(strategy="mean"),
        "Linear regression": LinearRegression(),
        "Ridge regression": Ridge(alpha=2.0, random_state=RANDOM_STATE),
        "Random forest": RandomForestRegressor(
            n_estimators=50,
            random_state=RANDOM_STATE,
            min_samples_leaf=2,
            max_features=0.7,
            n_jobs=1,
        ),
    }

    rows: list[dict] = []
    for name, model in models.items():
        pipe = Pipeline(steps=[("preprocess", preprocessor), ("model", model)])
        pipe.fit(X_train, y_train)
        rows.append(
            {
                "task": "regression",
                "model": name,
                "metric": "RMSE",
                "train_metric": rmse(y_train, pipe.predict(X_train)),
                "validation_metric": rmse(y_valid, pipe.predict(X_valid)),
            }
        )
    return pd.DataFrame(rows)


def fit_regression_final(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    *,
    mode: str = "quick",
    use_title_text: bool = False,
) -> tuple[pd.DataFrame, dict]:
    """Fit the final regression model and return a prediction dataframe.

    CatBoost is used when available because it handles high-cardinality categorical features well.
    The quick mode keeps runtime suitable for portfolio reproducibility. The full mode uses more
    iterations and can optionally include title text.
    """

    try:
        from catboost import CatBoostRegressor, Pool
    except Exception as exc:  # pragma: no cover - fallback only used when CatBoost is unavailable
        raise ImportError("CatBoost is required for the final regression model.") from exc

    train = clean_year_and_add_decade(train_df)
    test = clean_year_and_add_decade(test_df)
    y = train[REGRESSION_TARGET].copy()
    X = train.drop(columns=[REGRESSION_TARGET, ID_COLUMN])
    X_test = test.drop(columns=[ID_COLUMN])

    if not use_title_text:
        X = X.drop(columns=[c for c in ["title"] if c in X.columns])
        X_test = X_test.drop(columns=[c for c in ["title"] if c in X_test.columns])

    categorical = [c for c in ["artist", "top genre", "decade"] if c in X.columns]
    text = ["title"] if use_title_text and "title" in X.columns else []

    for col in categorical:
        X[col] = X[col].fillna("missing").astype(str)
        X_test[col] = X_test[col].fillna("missing").astype(str)
    for col in text:
        X[col] = X[col].fillna("").astype(str)
        X_test[col] = X_test[col].fillna("").astype(str)

    X_train, X_valid, y_train, y_valid = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    iterations = 350 if mode == "quick" else 1400
    validation_model = CatBoostRegressor(
        loss_function="RMSE",
        eval_metric="RMSE",
        iterations=iterations,
        learning_rate=0.05,
        depth=6,
        l2_leaf_reg=8,
        random_seed=RANDOM_STATE,
        verbose=False,
        allow_writing_files=False,
        od_type="Iter",
        od_wait=50,
        subsample=0.8,
        bootstrap_type="Bernoulli",
        thread_count=2,
    )
    train_pool = Pool(X_train, y_train, cat_features=categorical, text_features=text or None)
    valid_pool = Pool(X_valid, y_valid, cat_features=categorical, text_features=text or None)
    validation_model.fit(train_pool, eval_set=valid_pool, use_best_model=True)

    best_iteration = validation_model.get_best_iteration()
    if best_iteration is None or best_iteration <= 0:
        best_iteration = iterations
    final_iterations = max(100, int(best_iteration * 1.1)) if mode == "quick" else max(500, int(best_iteration * 1.2))

    full_pool = Pool(X, y, cat_features=categorical, text_features=text or None)
    final_model = CatBoostRegressor(
        loss_function="RMSE",
        eval_metric="RMSE",
        iterations=final_iterations,
        learning_rate=0.05,
        depth=6,
        l2_leaf_reg=8,
        random_seed=RANDOM_STATE,
        verbose=False,
        allow_writing_files=False,
        subsample=0.8,
        bootstrap_type="Bernoulli",
        thread_count=2,
    )
    final_model.fit(full_pool)
    predictions = np.clip(final_model.predict(X_test), 0, 100)

    submission = pd.DataFrame({ID_COLUMN: test[ID_COLUMN], REGRESSION_TARGET: predictions})
    diagnostics = {
        "model": "CatBoostRegressor",
        "mode": mode,
        "use_title_text": use_title_text,
        "validation_train_rmse": rmse(y_train, validation_model.predict(X_train)),
        "validation_rmse": rmse(y_valid, validation_model.predict(X_valid)),
        "best_iteration": int(best_iteration),
        "final_iterations": int(final_iterations),
    }
    return submission, diagnostics


def classification_baseline_table(train_df: pd.DataFrame) -> pd.DataFrame:
    """Compare classification baselines on a stable stratified validation split."""

    prepared = clean_year_and_add_decade(train_df).dropna(subset=[CLASSIFICATION_TARGET]).copy()
    counts = prepared[CLASSIFICATION_TARGET].value_counts()
    stable = prepared[prepared[CLASSIFICATION_TARGET].map(counts) >= 2].copy()

    drop_cols = [ID_COLUMN, CLASSIFICATION_TARGET, "title", "year"]
    X = stable.drop(columns=[c for c in drop_cols if c in stable.columns]).copy()
    y = stable[CLASSIFICATION_TARGET].copy()

    categorical = [c for c in ["artist", "decade"] if c in X.columns]
    numeric = [c for c in X.columns if c not in categorical]
    for col in categorical:
        X[col] = X[col].fillna("missing").astype(str)

    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)
    X_train, X_valid, y_train, y_valid = train_test_split(
        X,
        y_encoded,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y_encoded,
    )

    preprocessor = make_tabular_preprocessor(numeric, categorical, sparse_output=True)
    models = {
        "Dummy most frequent": DummyClassifier(strategy="most_frequent"),
        "Linear SVC balanced": LinearSVC(
            C=1.0, class_weight="balanced", random_state=RANDOM_STATE, max_iter=5000
        ),
        "Random forest": RandomForestClassifier(
            n_estimators=50,
            random_state=RANDOM_STATE,
            min_samples_leaf=2,
            max_features="sqrt",
            n_jobs=1,
        ),
    }

    rows: list[dict] = []
    for name, model in models.items():
        pipe = Pipeline(steps=[("preprocess", preprocessor), ("model", model)])
        pipe.fit(X_train, y_train)
        rows.append(
            {
                "task": "classification",
                "model": name,
                "metric": "Accuracy",
                "train_metric": float(accuracy_score(y_train, pipe.predict(X_train))),
                "validation_metric": float(accuracy_score(y_valid, pipe.predict(X_valid))),
            }
        )
    return pd.DataFrame(rows)


def classification_text_variant_score(train_df: pd.DataFrame) -> dict:
    """Evaluate the optional TF-IDF text model without using it as the default."""

    prepared = clean_year_and_add_decade(train_df).dropna(subset=[CLASSIFICATION_TARGET]).copy()
    prepared = add_artist_title_text(prepared)
    counts = prepared[CLASSIFICATION_TARGET].value_counts()
    stable = prepared[prepared[CLASSIFICATION_TARGET].map(counts) >= 2].copy()

    X = stable.drop(columns=[ID_COLUMN, CLASSIFICATION_TARGET]).copy()
    y = stable[CLASSIFICATION_TARGET].copy()
    categorical = [c for c in ["decade"] if c in X.columns]
    numeric = [c for c in X.columns if c not in categorical and c not in ["artist_title_text", "title", "artist", "year"]]

    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)
    X_train, X_valid, y_train, y_valid = train_test_split(
        X,
        y_encoded,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y_encoded,
    )

    text_pipeline = Pipeline(
        steps=[
            ("to_array", FunctionTransformer(lambda x: x.squeeze().to_numpy(), validate=False)),
            (
                "tfidf",
                TfidfVectorizer(
                    analyzer="char_wb", ngram_range=(3, 5), min_df=2, max_features=25000
                ),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("one_hot", make_one_hot_encoder(sparse=True)),
                    ]
                ),
                categorical,
            ),
            ("text", text_pipeline, ["artist_title_text"]),
        ],
        remainder="drop",
        sparse_threshold=1.0,
    )

    best_score = -1.0
    best_c = None
    for c_value in [0.5, 1.0, 2.0]:
        pipe = Pipeline(
            steps=[
                ("preprocess", preprocessor),
                (
                    "model",
                    LinearSVC(
                        C=c_value,
                        class_weight="balanced",
                        random_state=RANDOM_STATE,
                        max_iter=5000,
                    ),
                ),
            ]
        )
        pipe.fit(X_train, y_train)
        score = float(accuracy_score(y_valid, pipe.predict(X_valid)))
        if score > best_score:
            best_score = score
            best_c = c_value
    return {
        "task": "classification",
        "model": f"TF-IDF text SVC (best C={best_c})",
        "metric": "Accuracy",
        "train_metric": np.nan,
        "validation_metric": best_score,
    }


def fit_classification_final(train_df: pd.DataFrame, test_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Fit the final classification model and return a prediction dataframe.

    This tabular LinearSVC pipeline is the default because it matched the validated
    prediction file and outperformed the TF-IDF text variant on the reproducible validation split.
    """

    train = clean_year_and_add_decade(train_df).dropna(subset=[CLASSIFICATION_TARGET]).copy()
    test = clean_year_and_add_decade(test_df).copy()

    drop_cols = [ID_COLUMN, CLASSIFICATION_TARGET, "title", "year"]
    X = train.drop(columns=[c for c in drop_cols if c in train.columns]).copy()
    y = train[CLASSIFICATION_TARGET].copy()
    X_test = test.drop(columns=[c for c in [ID_COLUMN, "title", "year"] if c in test.columns]).copy()

    categorical = [c for c in ["artist", "decade"] if c in X.columns]
    numeric = [c for c in X.columns if c not in categorical]
    for col in categorical:
        X[col] = X[col].fillna("missing").astype(str)
        X_test[col] = X_test[col].fillna("missing").astype(str)

    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)
    preprocessor = make_tabular_preprocessor(numeric, categorical, sparse_output=True)
    pipe = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            (
                "model",
                LinearSVC(C=1.0, class_weight="balanced", random_state=RANDOM_STATE, max_iter=5000),
            ),
        ]
    )
    pipe.fit(X, y_encoded)
    predictions = encoder.inverse_transform(pipe.predict(X_test))
    submission = pd.DataFrame({ID_COLUMN: test[ID_COLUMN], CLASSIFICATION_TARGET: predictions})
    diagnostics = {
        "model": "LinearSVC",
        "C": 1.0,
        "class_weight": "balanced",
        "n_classes": int(len(encoder.classes_)),
    }
    return submission, diagnostics
