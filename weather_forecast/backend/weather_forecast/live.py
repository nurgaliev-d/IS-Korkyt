"""Fetch the current seven-day forecast for Kyzylorda from Open-Meteo."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


LATITUDE = 44.85
LONGITUDE = 65.50
TIMEZONE = "Asia/Qyzylorda"
LOCATION = "Кызылорда"
SOURCE = "Open-Meteo"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


class LiveWeatherError(RuntimeError):
    """Raised when the live weather provider returns unusable data."""


def _number(value: Any, field: str, index: int) -> float:
    if value is None:
        raise LiveWeatherError(f"Open-Meteo returned no {field} for forecast day {index + 1}")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise LiveWeatherError(f"Open-Meteo returned invalid {field} data") from exc


def parse_forecast_payload(payload: dict[str, Any], horizon: int = 7) -> list[dict[str, float | str]]:
    daily = payload.get("daily")
    if not isinstance(daily, dict):
        raise LiveWeatherError("Open-Meteo response does not contain daily forecast data")

    dates = daily.get("time")
    means = daily.get("temperature_2m_mean")
    minimums = daily.get("temperature_2m_min")
    maximums = daily.get("temperature_2m_max")
    precipitation = daily.get("precipitation_sum")
    wind_speed = daily.get("wind_speed_10m_max")
    fields = (dates, means, minimums, maximums, precipitation, wind_speed)
    if not all(isinstance(field, list) and len(field) >= horizon for field in fields):
        raise LiveWeatherError("Open-Meteo response contains fewer than seven forecast days")

    forecast: list[dict[str, float | str]] = []
    for index in range(horizon):
        forecast.append(
            {
                "date": str(dates[index]),
                "temperature": _number(means[index], "mean temperature", index),
                "temperature_min": _number(minimums[index], "minimum temperature", index),
                "temperature_max": _number(maximums[index], "maximum temperature", index),
                "precipitation": _number(precipitation[index], "precipitation", index),
                "wind_speed": _number(wind_speed[index], "wind speed", index),
            }
        )
    return forecast


def fetch_live_forecast(horizon: int = 7) -> list[dict[str, float | str]]:
    query = urlencode(
        {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "daily": ",".join(
                [
                    "temperature_2m_mean",
                    "temperature_2m_min",
                    "temperature_2m_max",
                    "precipitation_sum",
                    "wind_speed_10m_max",
                ]
            ),
            "forecast_days": horizon,
            "timezone": TIMEZONE,
        }
    )
    request = Request(
        f"{FORECAST_URL}?{query}",
        headers={"Accept": "application/json", "User-Agent": "weather-forecast-student-project/1.0"},
    )
    try:
        with urlopen(request, timeout=10) as response:
            payload = json.load(response)
    except (URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        raise LiveWeatherError(f"Could not reach Open-Meteo: {exc}") from exc
    return parse_forecast_payload(payload, horizon=horizon)


def parse_observations_payload(payload: dict[str, Any], horizon: int = 7) -> list[dict[str, float | str]]:
    daily = payload.get("daily")
    if not isinstance(daily, dict):
        raise LiveWeatherError("Open-Meteo response does not contain daily observation data")

    dates = daily.get("time")
    temperatures = daily.get("temperature_2m_mean")
    minimums = daily.get("temperature_2m_min")
    maximums = daily.get("temperature_2m_max")
    precipitation = daily.get("precipitation_sum")
    wind_speed = daily.get("wind_speed_10m_max")
    fields = (dates, temperatures, minimums, maximums, precipitation, wind_speed)
    if not all(isinstance(field, list) and len(field) >= horizon for field in fields):
        raise LiveWeatherError("Open-Meteo response contains fewer than seven observation days")

    observations: list[dict[str, float | str]] = []
    for index in range(horizon):
        observations.append(
            {
                "date": str(dates[index]),
                "temperature": _number(temperatures[index], "mean temperature", index),
                "temperature_min": _number(minimums[index], "minimum temperature", index),
                "temperature_max": _number(maximums[index], "maximum temperature", index),
                "precipitation": _number(precipitation[index], "precipitation", index),
                "wind_speed": _number(wind_speed[index], "wind speed", index),
            }
        )
    return observations


def fetch_recent_observations(
    horizon: int = 7,
) -> list[dict[str, float | str]]:
    query = urlencode(
        {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "daily": ",".join(
                [
                    "temperature_2m_mean",
                    "temperature_2m_min",
                    "temperature_2m_max",
                    "precipitation_sum",
                    "wind_speed_10m_max",
                ]
            ),
            "past_days": horizon,
            "forecast_days": 1,
            "timezone": TIMEZONE,
        }
    )
    request = Request(
        f"{FORECAST_URL}?{query}",
        headers={"Accept": "application/json", "User-Agent": "weather-forecast-student-project/1.0"},
    )
    try:
        with urlopen(request, timeout=10) as response:
            payload = json.load(response)
    except (URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        raise LiveWeatherError(f"Could not reach Open-Meteo: {exc}") from exc

    observations = parse_observations_payload(payload, horizon=horizon + 1)
    if len(observations) != horizon + 1:
        raise LiveWeatherError("Open-Meteo did not return the expected recent days")
    return observations[:-1]
