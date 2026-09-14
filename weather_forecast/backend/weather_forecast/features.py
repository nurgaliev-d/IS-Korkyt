"""Feature construction for next-day temperature forecasting."""

from __future__ import annotations

from datetime import date, timedelta
from math import cos, pi, sin
from typing import Mapping, Sequence


FEATURE_NAMES = [
    "temperature_lag_1",
    "temperature_lag_7",
    "temperature_mean_7",
    "precipitation_lag_1",
    "wind_speed_lag_1",
    "day_of_year_sin",
    "day_of_year_cos",
]


def build_features(
    history: Sequence[Mapping[str, object]],
    target_date: date | None = None,
) -> tuple[list[str], list[float]]:
    """Build one feature row from seven observations for a target date."""

    if len(history) < 7:
        raise ValueError("At least seven observations are required")

    observations = sorted(history, key=lambda item: str(item["date"]))
    latest = observations[-1]
    temperatures = [float(item["temperature"]) for item in observations[-7:]]
    next_date = target_date or (date.fromisoformat(str(latest["date"])) + timedelta(days=1))
    day_of_year_angle = 2 * pi * next_date.timetuple().tm_yday / 365.25

    values = [
        temperatures[-1],
        temperatures[0],
        sum(temperatures) / len(temperatures),
        float(observations[-2]["precipitation"]),
        float(observations[-2]["wind_speed"]),
        sin(day_of_year_angle),
        cos(day_of_year_angle),
    ]
    return FEATURE_NAMES.copy(), values
