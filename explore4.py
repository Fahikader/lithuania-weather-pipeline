import requests
import pandas as pd

BASE = "https://api.meteo.lt/v1"
station_codes = ["vilniaus-ams", "kauno-ams", "klaipedos-ams", "siauliu-ams", "utenos-ams"]

frames = []
for code in station_codes:
    url = f"{BASE}/stations/{code}/observations/latest"
    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        print("Skipping", code, "status", response.status_code)
        continue
    data = response.json()
    df = pd.DataFrame(data["observations"])
    df["station_code"] = data["station"]["code"]
    frames.append(df)

all_data = pd.concat(frames, ignore_index=True)
print(all_data.groupby("station_code").size())
print("Total rows:", len(all_data))
