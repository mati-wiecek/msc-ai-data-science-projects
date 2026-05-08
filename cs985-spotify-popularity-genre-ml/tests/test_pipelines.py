import pandas as pd

from spotify_ml.pipelines import classification_baseline_table, regression_baseline_table


def test_regression_baseline_table_returns_expected_columns():
    df = pd.DataFrame(
        {
            "Id": range(1, 9),
            "title": [f"song{i}" for i in range(8)],
            "artist": ["a", "b", "a", "c", "b", "c", "a", "d"],
            "top genre": ["pop", "rock", "pop", "soul", "rock", "soul", "pop", "folk"],
            "year": [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007],
            "bpm": [100, 120, 110, 130, 90, 140, 95, 115],
            "nrgy": [50, 60, 55, 70, 45, 75, 47, 57],
            "pop": [40, 50, 45, 60, 42, 65, 41, 48],
        }
    )
    result = regression_baseline_table(df)
    assert {"task", "model", "metric", "train_metric", "validation_metric"}.issubset(result.columns)
    assert len(result) >= 3


def test_classification_baseline_table_returns_scores():
    rows = []
    genres = ["pop", "rock", "soul"]
    for idx in range(30):
        genre = genres[idx % len(genres)]
        rows.append(
            {
                "Id": idx + 1,
                "title": f"song{idx}",
                "artist": f"artist_{idx % 5}",
                "year": 2000 + (idx % 12),
                "bpm": 90 + idx,
                "nrgy": 40 + (idx % 50),
                "pop": 35 + (idx % 30),
                "top genre": genre,
            }
        )
    df = pd.DataFrame(rows)
    result = classification_baseline_table(df)
    assert len(result) >= 2
    assert result["validation_metric"].notna().all()
