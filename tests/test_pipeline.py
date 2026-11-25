import pandas as pd
import pytest
from pipeline import clean, validate, DataQualityError


def test_clean_converts_time_and_removes_duplicates():
    raw = pd.DataFrame({
        "observationTimeUtc": ["2026-11-24 00:00:00", "2026-11-24 00:00:00", "2026-11-24 01:00:00"],
        "station_code": ["vilniaus-ams", "vilniaus-ams", "vilniaus-ams"],
        "airTemperature": [0.0, 0.0, 1.0],
    })

    result = clean(raw)

    assert len(result) == 2
    assert str(result["observationTimeUtc"].dtype).startswith("datetime64")

def make_good_df():
    return pd.DataFrame({
        "observationTimeUtc": pd.to_datetime(["2026-11-24 00:00:00"]),
        "station_code": ["vilniaus-ams"],
        "airTemperature": [0.0],
        "relativeHumidity": [95],
        "windSpeed": [2.0],
    })


def test_validate_accepts_good_data():
    assert len(validate(make_good_df())) == 1


def test_validate_rejects_bad_temperature():
    df = make_good_df()
    df["airTemperature"] = 99
    with pytest.raises(DataQualityError):
        validate(df)


def test_validate_rejects_bad_humidity():
    df = make_good_df()
    df["relativeHumidity"] = 150
    with pytest.raises(DataQualityError):
        validate(df)


def test_validate_rejects_empty_data():
    with pytest.raises(DataQualityError):
        validate(make_good_df().iloc[0:0])
