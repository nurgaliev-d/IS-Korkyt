"""Load and validate daily weather observations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_COLUMNS = ["date", "temperature", "precipitation", "wind_speed"]


def validate_weather_frame(frame: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    cleaned = frame[REQUIRED_COLUMNS].copy()
    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
    for column in REQUIRED_COLUMNS[1:]:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
    if cleaned.isna().any().any():
        raise ValueError("Weather data contains invalid or missing values")
    if (cleaned["precipitation"] < 0).any() or (cleaned["wind_speed"] < 0).any():
        raise ValueError("Precipitation and wind speed cannot be negative")

    cleaned = cleaned.sort_values("date").drop_duplicates("date").reset_index(drop=True)
    cleaned["date"] = cleaned["date"].dt.strftime("%Y-%m-%d")
    return cleaned


def load_observations(path: str | Path) -> list[dict[str, Any]]:
    return validate_weather_frame(pd.read_csv(path)).to_dict(orient="records")
