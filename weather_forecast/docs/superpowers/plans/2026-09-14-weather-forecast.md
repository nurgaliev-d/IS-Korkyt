# Weather Forecasting System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Netlify-ready browser frontend and FastAPI backend that show the current Open-Meteo seven-day forecast alongside our own seven-day ML temperature forecast.

**Architecture:** A static frontend in `frontend/` sends JSON to a separate FastAPI service in `backend/`. The backend serves Open-Meteo's current forecast through `/forecast/live`, recent observations through `/observations/latest`, and a direct seven-horizon scikit-learn model through `/predict`; Netlify publishes only the frontend, while the backend can run locally or on a Python-capable host.

**Tech Stack:** Python, FastAPI, Pydantic, pandas, scikit-learn, joblib, pytest, vanilla HTML/CSS/JavaScript, Docker, Netlify.

**Spec:** `weather_forecast/docs/superpowers/specs/2026-09-14-weather-forecast-design.md`

## Global Constraints

- The production data source is real historical daily weather data from Open-Meteo's archive API.
- Tests may use small deterministic in-memory fixtures; they are not the production training dataset.
- The target is daily average temperature for each horizon from 1 to 7 days, a regression problem evaluated with MAE, RMSE, and R².
- The frontend is static and deployable by Netlify; FastAPI remains a separate backend service.
- No future weather values may be used when constructing prediction features.
- The latest observations table is read-only; the page distinguishes provider forecast values from ML-generated values.
- Production code is written only after a failing test demonstrates the required behavior.

---

### Task 1: Create the backend test-first foundation

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/pytest.ini`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_features.py`
- Create: `backend/weather_forecast/__init__.py`
- Create: `backend/weather_forecast/features.py`

**Interfaces:**
- `build_features(history: list[dict]) -> tuple[list[str], list[float]]` consumes chronological observations and produces feature names plus one feature row.
- The required input fields are `date`, `temperature`, `precipitation`, and `wind_speed`.

- [ ] **Step 1: Write the failing feature test**

```python
def test_build_features_uses_lags_and_calendar_values():
    features, values = build_features(seven_observations)
    assert features == ["temperature_lag_1", "temperature_lag_7", "temperature_mean_7", "precipitation_lag_1", "wind_speed_lag_1", "day_of_year_sin", "day_of_year_cos"]
    assert values[0] == 16.0
    assert values[1] == 10.0
    assert round(values[2], 4) == 13.0
```

- [ ] **Step 2: Run `pytest -q` from `weather_forecast/backend` and verify it fails because `build_features` is missing.**
- [ ] **Step 3: Implement the minimal chronological feature builder with lag-1, lag-7, seven-day mean, previous-day precipitation/wind, and sine/cosine day-of-year features.**
- [ ] **Step 4: Run `pytest -q tests/test_features.py` and verify the test passes.**
- [ ] **Step 5: Commit the foundation with `git add weather_forecast/backend && git commit -m "test: define weather forecast features"`.**

### Task 2: Implement training and prediction

**Files:**
- Create: `backend/weather_forecast/model.py`
- Create: `backend/tests/test_model.py`
- Create: `backend/data/.gitkeep`

**Interfaces:**
- `TemperatureForecaster.fit(observations: list[dict]) -> TemperatureForecaster` trains seven direct Random Forest horizon models.
- `TemperatureForecaster.predict(history: list[dict]) -> float` predicts the next day's average temperature.
- `TemperatureForecaster.predict_horizon(history: list[dict], forecast_date: date) -> list[dict]` returns seven dated predictions without recursive inputs.
- `TemperatureForecaster.save(path: str) -> None` and `TemperatureForecaster.load(path: str) -> TemperatureForecaster` persist the selected model.

- [ ] **Step 1: Write a failing test that fits on a deterministic increasing fixture and asserts `predict` returns a finite float.**
- [ ] **Step 2: Run `pytest -q tests/test_model.py` and verify it fails because `TemperatureForecaster` is missing.**
- [ ] **Step 3: Implement separate training rows and `RandomForestRegressor` models for horizons 1 through 7, evaluated with MAE, RMSE, and R².**
- [ ] **Step 4: Implement save/load with joblib and reject histories shorter than seven observations with `ValueError`.**
- [ ] **Step 5: Run `pytest -q tests/test_model.py` and verify it passes.**
- [ ] **Step 6: Commit with `git add weather_forecast/backend && git commit -m "feat: train temperature forecasting model"`.**

### Task 3: Add the FastAPI service

**Files:**
- Create: `backend/app.py`
- Create: `backend/tests/test_api.py`
- Modify: `backend/requirements.txt`

**Interfaces:**
- `GET /health` returns `{"status": "ok", "model_loaded": bool}`.
- `GET /forecast/live` returns the current seven-day Open-Meteo forecast.
- `GET /observations/latest` returns seven latest completed observations for ML input.
- `POST /predict` accepts `{ "forecast_date": "YYYY-MM-DD", "history": [...] }` and returns seven ML forecast values.

- [ ] **Step 1: Write failing API tests for health, valid prediction, and fewer-than-seven-observations validation.**
- [ ] **Step 2: Run `pytest -q tests/test_api.py` and verify it fails because `app` is missing.**
- [ ] **Step 3: Implement Pydantic request/response models, CORS configuration, a model-loading helper, and the two endpoints.**
- [ ] **Step 4: Return HTTP 422 for malformed input and HTTP 503 with an actionable message when no trained artifact exists.**
- [ ] **Step 5: Run `pytest -q tests/test_api.py` and verify it passes.**
- [ ] **Step 6: Commit with `git add weather_forecast/backend && git commit -m "feat: expose weather forecast API"`.**

### Task 4: Build the Netlify-ready frontend

**Files:**
- Create: `frontend/index.html`
- Create: `frontend/styles.css`
- Create: `frontend/app.js`
- Create: `frontend/config.js`
- Create: `frontend/translations.js`
- Create: `netlify.toml`

**Interfaces:**
- The page loads with seven read-only recent-observation rows, an actual Open-Meteo forecast card, and a separate ML forecast card.
- `app.js` loads `/observations/latest` and posts those rows to `${window.WEATHER_API_URL}/predict`, while `/forecast/live` supplies the actual forecast card.
- `translations.js` contains complete Russian and Kazakh strings for labels, help text, buttons, validation, loading, errors, and results.

- [ ] **Step 1: Write a static smoke test command that checks the HTML references `styles.css`, `config.js`, and `app.js`, and that `netlify.toml` publishes `frontend`.**
- [ ] **Step 2: Run the smoke test and verify it fails because the frontend files are missing.**
- [ ] **Step 3: Implement the weather-station-console layout with responsive CSS, keyboard focus, accessible labels, reduced-motion support, and a Russian/Kazakh language switcher.**
- [ ] **Step 4: Implement the form serialization, localized loading state, localized result state, and localized error state in vanilla JavaScript.**
- [ ] **Step 5: Run the smoke test and open the page against the local API for manual verification.**
- [ ] **Step 6: Commit with `git add weather_forecast/frontend weather_forecast/netlify.toml && git commit -m "feat: add Netlify weather forecast frontend"`.**

### Task 5: Add real-data setup, Docker, and project documentation

**Files:**
- Create: `backend/weather_forecast/data.py`
- Create: `backend/scripts/download_weather.py`
- Create: `backend/scripts/train_model.py`
- Create: `backend/Dockerfile`
- Create: `backend/.dockerignore`
- Create: `weather_forecast/README.md`
- Create: `weather_forecast/.gitignore`

**Interfaces:**
- `download_weather.py` writes daily Open-Meteo data to `data/weather_history.csv` using configurable latitude, longitude, start date, and end date.
- `train_model.py` reads that CSV, trains `TemperatureForecaster`, and writes `artifacts/temperature_model.joblib` plus `artifacts/model_metrics.json`.

- [ ] **Step 1: Write a failing data-validation test for the required CSV columns and a training-script test for artifact creation.**
- [ ] **Step 2: Run the tests and verify they fail because the data module and scripts are missing.**
- [ ] **Step 3: Implement the Open-Meteo downloader, CSV validation, training CLI, Docker image, and setup documentation.**
- [ ] **Step 4: Download a real historical dataset, train the model, and record MAE, RMSE, and R².**
- [ ] **Step 5: Run the full backend test suite and the frontend smoke test.**
- [ ] **Step 6: Commit with `git add weather_forecast && git commit -m "docs: add real weather data and deployment setup"`.**
