import sqlite3

import pandas as pd
import requests

BASE = "https://api.meteo.lt/v1"
STATIONS = ["vilniaus-ams", "kauno-ams", "klaipedos-ams", "siauliu-ams", "utenos-ams"]
DB_PATH = "weather.db"

COLUMNS = {
    "station_code": "station_code",
    "observationTimeUtc": "observation_time_utc",
    "airTemperature": "air_temperature",
    "feelsLikeTemperature": "feels_like_temperature",
    "windSpeed": "wind_speed",
    "windGust": "wind_gust",
    "windDirection": "wind_direction",
    "cloudCover": "cloud_cover",
    "seaLevelPressure": "sea_level_pressure",
    "relativeHumidity": "relative_humidity",
    "precipitation": "precipitation",
    "snowDepth": "snow_depth",
    "conditionCode": "condition_code",
}

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS observations (
    station_code           TEXT NOT NULL,
    observation_time_utc   TEXT NOT NULL,
    air_temperature        REAL,
    feels_like_temperature REAL,
    wind_speed             REAL,
    wind_gust              REAL,
    wind_direction         INTEGER,
    cloud_cover            INTEGER,
    sea_level_pressure     REAL,
    relative_humidity      INTEGER,
    precipitation          REAL,
    snow_depth             INTEGER,
    condition_code         TEXT,
    PRIMARY KEY (station_code, observation_time_utc)
)
"""


class DataQualityError(Exception):
    """Raised when the data fails a quality check."""


# ---------- EXTRACT ----------
def extract_station(code):
    """Download the latest observations for one station."""
    url = f"{BASE}/stations/{code}/observations/latest"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data["observations"])
    df["station_code"] = data["station"]["code"]
    return df


def extract_all(codes=STATIONS):
    """Download all stations and combine them into one table."""
    frames = []
    for code in codes:
        try:
            frames.append(extract_station(code))
        except requests.RequestException as error:
            print("Skipping", code, "-", error)
    return pd.concat(frames, ignore_index=True)


# ---------- CLEAN ----------
def clean(df):
    """Fix types and remove duplicates."""
    df = df.copy()
    df["observationTimeUtc"] = pd.to_datetime(df["observationTimeUtc"])
    df = df.drop_duplicates(subset=["station_code", "observationTimeUtc"])
    return df


# ---------- VALIDATE ----------
def validate(df):
    """Check the data is sensible. Raise an error if not."""
    if df.empty:
        raise DataQualityError("No data")
    if not df["airTemperature"].between(-50, 50).all():
        raise DataQualityError("Temperature missing or outside -50 to 50")
    if not df["relativeHumidity"].between(0, 100).all():
        raise DataQualityError("Humidity missing or outside 0 to 100")
    if (df["windSpeed"] < 0).any():
        raise DataQualityError("Negative wind speed")
    if df.duplicated(subset=["station_code", "observationTimeUtc"]).any():
        raise DataQualityError("Duplicate station and time")
    return df


# ---------- LOAD ----------
def load(df, db_path=DB_PATH):
    """Save the table into the database. Safe to run many times."""
    out = df[list(COLUMNS)].rename(columns=COLUMNS).copy()
    out["observation_time_utc"] = out["observation_time_utc"].dt.strftime("%Y-%m-%d %H:%M:%S")
    names = list(out.columns)
    sql = (f"INSERT OR REPLACE INTO observations ({', '.join(names)}) "
           f"VALUES ({', '.join('?' * len(names))})")
    conn = sqlite3.connect(db_path)
    try:
        with conn:
            conn.execute(CREATE_TABLE)
            conn.executemany(sql, out.itertuples(index=False, name=None))
    finally:
        conn.close()
    return len(out)


if __name__ == "__main__":
    df = validate(clean(extract_all()))
    rows = load(df)
    print("Saved rows:", rows)
