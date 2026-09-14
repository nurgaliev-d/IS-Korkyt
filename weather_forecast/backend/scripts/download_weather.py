"""Download real daily historical weather data from Open-Meteo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd

from weather_forecast.data import validate_weather_frame


def build_archive_url(latitude: float, longitude: float, start_date: str, end_date: str) -> str:
    query = urlencode(
        {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": "temperature_2m_mean,precipitation_sum,wind_speed_10m_max",
            "timezone": "auto",
        }
    )
    return f"https://archive-api.open-meteo.com/v1/archive?{query}"


def download_weather(
    output: str | Path,
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
) -> Path:
    with urlopen(build_archive_url(latitude, longitude, start_date, end_date), timeout=30) as response:
        payload = json.load(response)

    daily = payload.get("daily", {})
    frame = pd.DataFrame(
        {
            "date": daily.get("time", []),
            "temperature": daily.get("temperature_2m_mean", []),
            "precipitation": daily.get("precipitation_sum", []),
            "wind_speed": daily.get("wind_speed_10m_max", []),
        }
    )
    cleaned = validate_weather_frame(frame)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(output_path, index=False)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="data/weather_history.csv")
    parser.add_argument("--latitude", type=float, default=44.85)
    parser.add_argument("--longitude", type=float, default=65.50)
    parser.add_argument("--start-date", default="2016-01-01")
    parser.add_argument("--end-date", default="2025-12-31")
    args = parser.parse_args()
    path = download_weather(args.output, args.latitude, args.longitude, args.start_date, args.end_date)
    print(f"Saved {path}")


if __name__ == "__main__":
    main()
