import pandas as pd
import pytest

from weather_forecast.data import REQUIRED_COLUMNS, validate_weather_frame


def test_validate_weather_frame_accepts_required_columns():
    frame = pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "temperature": [10.0],
            "precipitation": [0.0],
            "wind_speed": [4.0],
        }
    )

    result = validate_weather_frame(frame)

    assert list(result.columns) == REQUIRED_COLUMNS


def test_validate_weather_frame_rejects_missing_columns():
    with pytest.raises(ValueError, match="wind_speed"):
        validate_weather_frame(
            pd.DataFrame(
                {
                    "date": ["2024-01-01"],
                    "temperature": [10.0],
                    "precipitation": [0.0],
                }
            )
        )
