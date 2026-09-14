"""Train and persist the weather forecasting model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from weather_forecast.data import load_observations
from weather_forecast.model import TemperatureForecaster


def train_from_csv(
    source: str | Path,
    artifact: str | Path,
    metrics_path: str | Path,
) -> TemperatureForecaster:
    observations = load_observations(source)
    forecaster = TemperatureForecaster().fit(observations)
    artifact_path = Path(artifact)
    metrics_file = Path(metrics_path)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_file.parent.mkdir(parents=True, exist_ok=True)
    forecaster.save(artifact_path)
    metrics_file.write_text(
        json.dumps(
            {
                "model": forecaster.model_name,
                "metrics": forecaster.metrics,
                "observations": len(observations),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return forecaster


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="data/weather_history.csv")
    parser.add_argument("--artifact", default="artifacts/temperature_model.joblib")
    parser.add_argument("--metrics", default="artifacts/model_metrics.json")
    args = parser.parse_args()
    forecaster = train_from_csv(args.source, args.artifact, args.metrics)
    print(f"Selected model: {forecaster.model_name}")
    print(json.dumps(forecaster.metrics, indent=2))


if __name__ == "__main__":
    main()
