import requests
url = "https://api.meteo.lt/v1/stations"
response = requests.get(url,timeout = 30)
print ("Status:",response.status_code)
stations = response.json()
print("Number of stations:", len(stations))
print(stations[0])

