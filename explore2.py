import json
import requests

url = "https://api.meteo.lt/v1/stations/vilniaus-ams/observations/latest"
response = requests.get(url, timeout=30)

print("Status:", response.status_code)

data = response.json()
print(type(data))
print(json.dumps(data, indent=2, ensure_ascii=False)[:1500])
