from fastapi.testclient import TestClient

import app as app_module
from weather_forecast.live import parse_observations_payload


client = TestClient(app_module.app)


def test_recent_observations_returns_seven_current_days(monkeypatch):
    observations = [
        {
            "date": f"2026-09-{8 + index:02d}",
            "temperature": 20.0 + index,
            "temperature_min": 14.0 + index,
            "temperature_max": 26.0 + index,
            "precipitation": 0.0,
            "wind_speed": 12.0,
        }
        for index in range(7)
    ]
    monkeypatch.setattr(app_module, "fetch_recent_observations", lambda horizon=7: observations)

    response = client.get("/observations/latest")

    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "Open-Meteo"
    assert len(body["history"]) == 7
    assert body["history"][0]["date"] == "2026-09-08"
    assert body["history"][0]["temperature"] == 20.0
    assert body["history"][0]["temperature_min"] == 14.0
    assert body["history"][0]["temperature_max"] == 26.0


def test_recent_observation_payload_preserves_temperature_range():
    payload = {
        "daily": {
            "time": ["2026-09-08", "2026-09-09"],
            "temperature_2m_mean": [20.0, 21.0],
            "temperature_2m_min": [14.0, 15.0],
            "temperature_2m_max": [26.0, 27.0],
            "precipitation_sum": [0.0, 1.0],
            "wind_speed_10m_max": [12.0, 13.0],
        }
    }

    observations = parse_observations_payload(payload, horizon=2)

    assert observations[0]["temperature_min"] == 14.0
    assert observations[0]["temperature_max"] == 26.0


def test_live_forecast_returns_seven_days_from_provider(monkeypatch):
    live_forecast = [
        {
            "date": f"2026-09-{15 + index:02d}",
            "temperature": 18.5 + index,
            "temperature_min": 10.0 + index,
            "temperature_max": 25.0 + index,
            "precipitation": 0.2,
            "wind_speed": 14.0,
        }
        for index in range(7)
    ]
    monkeypatch.setattr(app_module, "fetch_live_forecast", lambda horizon=7: live_forecast)

    response = client.get("/forecast/live")

    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "Open-Meteo"
    assert body["location"] == "Кызылорда"
    assert len(body["forecast"]) == 7
    assert body["forecast"][0]["date"] == "2026-09-15"
    assert body["forecast"][0]["predicted_temperature"] == 18.5
    assert body["forecast"][0]["temperature_mean"] == 18.5
    assert body["forecast"][0]["temperature_min"] == 10.0
    assert body["forecast"][0]["temperature_max"] == 25.0


def test_live_forecast_reports_provider_failure(monkeypatch):
    def fail_fetch(horizon=7):
        raise app_module.LiveWeatherError("provider unavailable")

    monkeypatch.setattr(app_module, "fetch_live_forecast", fail_fetch)

    response = client.get("/forecast/live")

    assert response.status_code == 502
    assert "provider unavailable" in response.json()["detail"]
