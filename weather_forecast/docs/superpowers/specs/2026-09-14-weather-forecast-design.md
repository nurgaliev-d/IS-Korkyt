# Weather Forecasting System Design

## Goal

Build a small intelligent system that presents the current seven-day forecast for Kyzylorda and, separately, predicts average temperature for each of the next seven days with an educational ML model.

## User experience

The first release is a local web application. The page shows a read-only table of the latest seven observations, the actual Open-Meteo seven-day forecast as daily average temperatures, a separate seven-day forecast from our ML model, and a per-day comparison with error and approximate percentage accuracy. The browser frontend is static and can be published to Netlify. The Python model service runs separately through FastAPI, locally at first and on a backend host when the frontend is deployed publicly. All user-facing text is localized in Russian and Kazakh, with Russian as the initial language and a visible language switcher.

## Visual direction

The interface uses a weather-station console character rather than a generic SaaS dashboard:

- Deep midnight navy background and pale cloud surfaces.
- Electric cyan for data and interaction states.
- Warm amber reserved for the predicted temperature.
- A compact editorial layout with one prominent forecast value, one input table, and a small model-status area.
- Sentence-case copy, strong keyboard focus, responsive layout, and reduced-motion support.

## Data and model scope

The production training workflow downloads daily historical weather data from Open-Meteo's archive API for a configurable location. The default example location is Kyzylorda, Kazakhstan. The target is daily average `temperature_2m_mean`. Features are built from lagged observations and calendar seasonality so the prediction does not use future weather values.

The first model comparison contains:

1. A direct scikit-learn `RandomForestRegressor` for each forecast horizon from 1 to 7 days, using lag and calendar features.
2. The previous persistence approach remains useful as a simple benchmark, but it is not the model shown in the ML result card.

The architecture leaves room for CatBoost and LSTM in a later model-comparison milestone, but the initial working prototype stays small enough to run locally and deploy reliably.

## Components

- `backend/weather_forecast/data.py`: download, validate, and load daily weather CSV data.
- `backend/weather_forecast/features.py`: create lagged and calendar features.
- `backend/weather_forecast/model.py`: train, save, load, and serve the seven direct horizon models.
- `backend/weather_forecast/live.py`: retrieve current forecast and recent observations from Open-Meteo.
- `backend/app.py`: FastAPI health, live forecast, observations, and ML prediction endpoints.
- `frontend/index.html`, `styles.css`, `app.js`: static Netlify-ready browser UI.
- `frontend/translations.js`: Russian and Kazakh interface copy.
- `Dockerfile`: package the backend service.
- `netlify.toml`: publish the static frontend directory.

## API contract

`GET /health` returns service and model status.

`GET /forecast/live` returns the current seven-day Open-Meteo forecast with minimum and maximum temperatures.

`GET /observations/latest` returns the latest seven completed daily observations used as ML input.

`POST /predict` accepts a date plus seven consecutive daily observations containing `date`, `temperature`, `temperature_min`, `temperature_max`, `precipitation`, and `wind_speed`. It returns seven dated `predicted_temperature` values, the model name, and the number of observations used.

## Non-goals for the first release

- A professional meteorological service.
- Live radar, maps, alerts, authentication, or user accounts.
- A native desktop package.
- Running the Python model directly on Netlify's static hosting.
- Missing Russian or Kazakh translations for visible interface text, validation messages, or forecast status messages.

## Verification

Unit tests will cover feature construction and model prediction. API tests will cover health, valid prediction, and invalid history. The frontend will be checked with a static file smoke test and browser-level manual verification when the local API is running.
