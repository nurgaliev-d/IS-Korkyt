from fastapi.testclient import TestClient

import app as app_module
from test_model import make_observations
from weather_forecast.model import TemperatureForecaster


client = TestClient(app_module.app)


def test_latest_dataset_returns_seven_real_observations(monkeypatch, tmp_path):
    source = tmp_path / "weather_history.csv"
    source.write_text(
        "date,temperature,precipitation,wind_speed\n"
        + "\n".join(
            f"{row['date']},{row['temperature']},{row['precipitation']},{row['wind_speed']}"
            for row in make_observations(8)
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(app_module, "DATA_PATH", source)

    response = client.get("/dataset/latest")

    assert response.status_code == 200
    assert len(response.json()["history"]) == 7
    assert response.json()["history"][0]["date"] == "2024-01-02"


def test_health_reports_service_status():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "model_loaded" in response.json()


def test_predict_returns_seven_day_temperature_forecast(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "FORECASTER",
        TemperatureForecaster().fit(make_observations(30)),
    )
    response = client.post(
        "/predict",
        json={
            "forecast_date": "2024-01-15",
            "history": make_observations(30),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["forecast_date"] == "2024-01-15"
    assert len(body["forecast"]) == 7
    assert body["forecast"][0]["date"] == "2024-01-15"
    assert isinstance(body["forecast"][0]["predicted_temperature"], float)
    assert body["unit"] == "°C"
    assert body["model"] == "direct_random_forest"


def test_predict_rejects_history_shorter_than_seven_observations(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "FORECASTER",
        TemperatureForecaster().fit(make_observations(30)),
    )
    response = client.post(
        "/predict",
        json={
            "forecast_date": "2024-01-15",
            "history": make_observations(6),
        },
    )

    assert response.status_code == 422
