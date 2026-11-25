import requests
import pandas as pd

url = "https://api.meteo.lt/v1/stations/vilniaus-ams/observations/latest"
data = requests.get(url, timeout=30).json()

df = pd.DataFrame(data["observations"])
df["station_code"] = data["station"]["code"]

print(df.head())
print(df.dtypes)
print("Rows:", len(df))

df["observationTimeUtc"] = pd.to_datetime(df["observationTimeUtc"])
print(df.dtypes["observationTimeUtc"])

print("Min temp:", df["airTemperature"].min())
print("Max temp:", df["airTemperature"].max())
print("Missing values:")
print(df.isna().sum())
