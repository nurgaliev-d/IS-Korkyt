from datetime import date, timedelta
from math import isfinite, sin

import pytest

from weather_forecast.model import TemperatureForecaster


def make_observations(count=14):
    start = date(2024, 1, 1)
    return [
        {
            "date": (start + timedelta(days=index)).isoformat(),
            "temperature": float(8 + index * 0.6),
            "precipitation": float(index % 2),
            "wind_speed": float(4 + index % 3),
        }
        for index in range(count)
    ]


def make_seasonal_observations(count=120):
    start = date(2024, 1, 1)
    return [
        {
            "date": (start + timedelta(days=index)).isoformat(),
            "temperature": float(15 + 10 * sin(index * 2 * 3.14159 / 30)),
            "precipitation": float(index % 2),
            "wind_speed": float(4 + index % 3),
        }
        for index in range(count)
    ]


def test_forecaster_trains_and_predicts_a_finite_temperature():
    observations = make_observations(30)
    forecaster = TemperatureForecaster().fit(observations)

    prediction = forecaster.predict(observations[-7:])

    assert isinstance(prediction, float)
    assert isfinite(prediction)
    assert forecaster.model_name == "direct_random_forest"


def test_forecaster_rejects_short_history():
    with pytest.raises(ValueError, match="eight observations"):
        TemperatureForecaster().fit(make_observations(7))


def test_forecaster_predicts_seven_consecutive_days():
    observations = make_seasonal_observations()
    forecaster = TemperatureForecaster().fit(observations)

    forecast = forecaster.predict_horizon(observations[-7:], horizon=7)

    assert len(forecast) == 7
    assert forecast[0]["date"] == "2024-04-30"
    assert forecast[-1]["date"] == "2024-05-06"
    assert all(isinstance(item["temperature"], float) for item in forecast)
    assert len({round(item["temperature"], 3) for item in forecast}) > 1
