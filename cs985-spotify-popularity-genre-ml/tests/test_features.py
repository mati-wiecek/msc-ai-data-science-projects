import pandas as pd

from spotify_ml.features import add_artist_title_text, clean_year_and_add_decade


def test_clean_year_and_add_decade_extracts_four_digit_year():
    df = pd.DataFrame({"year": ["1996 remaster", "unknown", 2011]})
    result = clean_year_and_add_decade(df)
    assert result.loc[0, "year_clean"] == 1996
    assert result.loc[2, "decade"] == "2010"
    assert result["decade"].isna().sum() == 0


def test_add_artist_title_text_handles_missing_values():
    df = pd.DataFrame({"artist": ["Queen", None], "title": ["Radio Ga Ga", "Unknown"]})
    result = add_artist_title_text(df)
    assert result.loc[0, "artist_title_text"] == "queen radio ga ga"
    assert result.loc[1, "artist_title_text"] == "unknown"
