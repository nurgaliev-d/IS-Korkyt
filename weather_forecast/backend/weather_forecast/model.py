"""Train and serve a direct seven-day temperature forecasting model."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Mapping, Sequence

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .features import FEATURE_NAMES, build_features


class TemperatureForecaster:
    """Train one Random Forest model for each forecast day."""

    def __init__(self) -> None:
        self.model_name = "direct_random_forest"
        self.metrics: dict[str, float] = {}
        self.feature_names = FEATURE_NAMES.copy()
        self._models: dict[int, RandomForestRegressor] = {}
        self._model: RandomForestRegressor | None = None

    def fit(self, observations: Sequence[Mapping[str, object]]) -> "TemperatureForecaster":
        if len(observations) < 8:
            raise ValueError("At least eight observations are required to train")

        ordered = sorted(observations, key=lambda item: str(item["date"]))
        self._models = {}
        validation_mae: list[float] = []
        validation_rmse: list[float] = []
        validation_r2: list[float] = []

        for horizon in range(1, 8):
            feature_rows: list[list[float]] = []
            targets: list[float] = []
            for anchor_index in range(7, len(ordered) - horizon + 1):
                history = ordered[anchor_index - 7 : anchor_index]
                target = ordered[anchor_index + horizon - 1]
                target_day = date.fromisoformat(str(target["date"]))
                _, row = build_features(history, target_date=target_day)
                feature_rows.append(row)
                targets.append(float(target["temperature"]))

            if not feature_rows:
                continue

            x = np.asarray(feature_rows, dtype=float)
            y = np.asarray(targets, dtype=float)
            split_index = max(1, len(x) - max(1, len(x) // 5))
            train_x, validation_x = x[:split_index], x[split_index:]
            train_y, validation_y = y[:split_index], y[split_index:]

            candidate = RandomForestRegressor(
                n_estimators=120,
                random_state=42 + horizon,
                min_samples_leaf=1,
            )
            candidate.fit(train_x, train_y)
            self._models[horizon] = candidate

            if len(validation_x) > 0:
                validation_predictions = candidate.predict(validation_x)
                validation_mae.append(float(mean_absolute_error(validation_y, validation_predictions)))
                validation_rmse.append(float(mean_squared_error(validation_y, validation_predictions) ** 0.5))
                if len(validation_y) > 1:
                    validation_r2.append(float(r2_score(validation_y, validation_predictions)))

        if not self._models:
            raise ValueError("At least eight observations are required to train")

        self.model_name = "direct_random_forest"
        self._model = self._models.get(1)
        self.metrics = {
            "mae": float(np.mean(validation_mae)) if validation_mae else 0.0,
            "rmse": float(np.mean(validation_rmse)) if validation_rmse else 0.0,
            "r2": float(np.mean(validation_r2)) if validation_r2 else 0.0,
        }
        return self

    def _predict_direct(
        self,
        history: Sequence[Mapping[str, object]],
        horizon: int,
        target_date: date,
    ) -> float:
        model = self._models.get(horizon)
        if model is None and horizon == 1:
            model = self._model
        if model is None:
            return float(sorted(history, key=lambda item: str(item["date"]))[-1]["temperature"])

        _, values = build_features(history, target_date=target_date)
        return float(model.predict(np.asarray([values], dtype=float))[0])

    def predict(self, history: Sequence[Mapping[str, object]]) -> float:
        if len(history) < 7:
            raise ValueError("At least seven observations are required")
        ordered = sorted(history, key=lambda item: str(item["date"]))
        next_date = date.fromisoformat(str(ordered[-1]["date"])) + timedelta(days=1)
        return self._predict_direct(ordered[-7:], horizon=1, target_date=next_date)

    def predict_horizon(
        self,
        history: Sequence[Mapping[str, object]],
        horizon: int = 7,
        start_date: date | None = None,
    ) -> list[dict[str, float | str]]:
        """Predict each forecast day directly from the observed history."""

        if horizon < 1:
            raise ValueError("Forecast horizon must be positive")
        if len(history) < 7:
            raise ValueError("At least seven observations are required")

        ordered = sorted(history, key=lambda item: str(item["date"]))
        base_history = ordered[-7:]
        next_date = start_date or (date.fromisoformat(str(ordered[-1]["date"])) + timedelta(days=1))
        forecast: list[dict[str, float | str]] = []

        for offset in range(horizon):
            target_date = next_date + timedelta(days=offset)
            temperature = self._predict_direct(
                base_history,
                horizon=offset + 1,
                target_date=target_date,
            )
            forecast.append({"date": target_date.isoformat(), "temperature": temperature})

        return forecast

    def save(self, path: str | Path) -> None:
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: str | Path) -> "TemperatureForecaster":
        model = joblib.load(path)
        if not isinstance(model, cls):
            raise TypeError("The artifact is not a TemperatureForecaster")
        return model
