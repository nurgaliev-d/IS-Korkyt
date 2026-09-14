from weather_forecast.features import build_features


def test_build_features_uses_lags_and_calendar_values(seven_observations):
    features, values = build_features(seven_observations)

    assert features == [
        "temperature_lag_1",
        "temperature_lag_7",
        "temperature_mean_7",
        "precipitation_lag_1",
        "wind_speed_lag_1",
        "day_of_year_sin",
        "day_of_year_cos",
    ]
    assert values[0] == 16.0
    assert values[1] == 10.0
    assert round(values[2], 4) == 13.0
