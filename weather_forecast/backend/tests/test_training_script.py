from pathlib import Path

from test_model import make_observations
from weather_forecast.model import TemperatureForecaster
from scripts.train_model import train_from_csv


def test_train_from_csv_creates_model_artifact(tmp_path: Path):
    source = tmp_path / "weather.csv"
    artifact = tmp_path / "temperature_model.joblib"
    metrics = tmp_path / "model_metrics.json"
    source.write_text(
        "date,temperature,precipitation,wind_speed\n"
        + "\n".join(
            f"{row['date']},{row['temperature']},{row['precipitation']},{row['wind_speed']}"
            for row in make_observations(30)
        )
        + "\n",
        encoding="utf-8",
    )

    result = train_from_csv(source, artifact, metrics)

    assert artifact.exists()
    assert metrics.exists()
    assert result.model_name == "direct_random_forest"
    assert isinstance(TemperatureForecaster.load(artifact), TemperatureForecaster)
