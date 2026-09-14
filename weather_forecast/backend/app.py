"""FastAPI application for live and ML weather forecasts."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from weather_forecast.data import load_observations
from weather_forecast.live import LiveWeatherError, fetch_live_forecast, fetch_recent_observations
from weather_forecast.model import TemperatureForecaster


MODEL_PATH = Path(os.getenv("WEATHER_MODEL_PATH", "artifacts/temperature_model.joblib"))
DATA_PATH = Path(os.getenv("WEATHER_DATA_PATH", "data/weather_history.csv"))


def load_forecaster() -> TemperatureForecaster | None:
    if not MODEL_PATH.exists():
        return None
    return TemperatureForecaster.load(MODEL_PATH)


FORECASTER = load_forecaster()

app = FastAPI(
    title="Weather Forecast API",
    description="Predicts next-day average temperature from recent daily observations.",
    version="0.1.0",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class WeatherObservation(BaseModel):
    date: date
    temperature: float
    temperature_min: float | None = None
    temperature_max: float | None = None
    precipitation: float = Field(ge=0)
    wind_speed: float = Field(ge=0)


class PredictRequest(BaseModel):
    forecast_date: date
    history: list[WeatherObservation] = Field(min_length=7)


class PredictResponse(BaseModel):
    forecast_date: date
    forecast: list["ForecastDay"]
    unit: str
    model: str
    observations_used: int


class ForecastDay(BaseModel):
    date: date
    predicted_temperature: float
    temperature_mean: float | None = None
    temperature_min: float | None = None
    temperature_max: float | None = None
    precipitation: float | None = None
    wind_speed: float | None = None


class DatasetResponse(BaseModel):
    history: list[WeatherObservation]


class RecentObservationsResponse(BaseModel):
    source: str
    history: list[WeatherObservation]


class LiveForecastResponse(BaseModel):
    location: str
    source: str
    forecast: list[ForecastDay]
    unit: str
    model: str
    observations_used: int


@app.get("/health")
def health() -> dict[str, bool | str]:
    return {"status": "ok", "model_loaded": FORECASTER is not None}


@app.get("/dataset/latest", response_model=DatasetResponse)
def latest_dataset() -> DatasetResponse:
    if not DATA_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail="Weather dataset is not available. Download it before starting the API.",
        )
    history = load_observations(DATA_PATH)
    if len(history) < 7:
        raise HTTPException(status_code=503, detail="Weather dataset contains fewer than seven observations.")
    return DatasetResponse(history=[WeatherObservation(**item) for item in history[-7:]])


@app.get("/observations/latest", response_model=RecentObservationsResponse)
def latest_observations() -> RecentObservationsResponse:
    try:
        observations = fetch_recent_observations(horizon=7)
    except LiveWeatherError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return RecentObservationsResponse(
        source="Open-Meteo",
        history=[WeatherObservation(**item) for item in observations],
    )


@app.get("/forecast/live", response_model=LiveForecastResponse)
def live_forecast() -> LiveForecastResponse:
    try:
        forecast = fetch_live_forecast(horizon=7)
    except LiveWeatherError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return LiveForecastResponse(
        location="Кызылорда",
        source="Open-Meteo",
        forecast=[
            ForecastDay(
                date=item["date"],
                predicted_temperature=item["temperature"],
                temperature_mean=item["temperature"],
                temperature_min=item["temperature_min"],
                temperature_max=item["temperature_max"],
                precipitation=item["precipitation"],
                wind_speed=item["wind_speed"],
            )
            for item in forecast
        ],
        unit="°C",
        model="Open-Meteo",
        observations_used=0,
    )


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    if FORECASTER is None:
        raise HTTPException(
            status_code=503,
            detail="Forecast model is not trained. Run the training command first.",
        )

    history = [observation.model_dump(mode="json") for observation in request.history]
    forecast = FORECASTER.predict_horizon(
        history,
        horizon=7,
        start_date=request.forecast_date,
    )
    return PredictResponse(
        forecast_date=request.forecast_date,
        forecast=[
            ForecastDay(date=item["date"], predicted_temperature=item["temperature"])
            for item in forecast
        ],
        unit="°C",
        model=FORECASTER.model_name,
        observations_used=len(history),
    )
