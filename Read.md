# Lithuania Weather Pipeline

A small data pipeline that collects hourly weather observations from Lithuanian
weather stations and stores them in a SQL database.

## What it does
1. **Extract** the latest observations for 5 stations from the Lithuanian Hydrometeorological Service API (api.meteo.lt).
2. **Clean** the data with pandas: convert times and remove duplicates.
3. **Validate** with data quality checks: temperature and humidity ranges, no negative wind speed, no duplicate rows, no empty data.
4. **Load** into SQLite with an upsert, so running it twice never creates duplicates.

## Run it
    pip install -r requirements.txt
    python pipeline.py

## Test it
    python -m pytest

## Stack
Python, pandas, requests, SQLite, pytest.

Data source: Lithuanian Hydrometeorological Service (LHMT), api.meteo.lt.
Check the service's terms of use for data licensing and attribution.
