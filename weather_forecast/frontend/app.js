const state = {
  language: localStorage.getItem("weather-language") || "ru",
  currentForecast: null,
  currentModel: null,
  currentMlForecast: null,
  currentMlModel: null
};

const observationsBody = document.querySelector("#observations-body");
const forecastBody = document.querySelector("#forecast-body");
const forecastChart = document.querySelector("#forecast-chart");
const forecastModel = document.querySelector("#forecast-model");
const errorBox = document.querySelector("#form-error");
const statusBox = document.querySelector("#form-status");
const forecastValue = document.querySelector("#forecast-value");
const forecastDate = document.querySelector("#forecast-date");
const forecastTemperatureHeading = document.querySelector("#forecast-table thead th:nth-child(2)");
const liveForecastButton = document.querySelector("#live-forecast-button");
const mlForecastBody = document.querySelector("#ml-forecast-body");
const mlForecastModel = document.querySelector("#ml-forecast-model");
const mlForecastDate = document.querySelector("#ml-forecast-date");
const mlErrorBox = document.querySelector("#ml-form-error");
const mlStatusBox = document.querySelector("#ml-form-status");
const comparisonBody = document.querySelector("#comparison-body");
const comparisonStatus = document.querySelector("#comparison-status");

function t(key) {
  return translations[state.language][key] || translations.ru[key] || key;
}

function locale() {
  return state.language === "kk" ? "kk-KZ" : "ru-RU";
}

function formatDate(value, options = { day: "numeric", month: "short" }) {
  return new Intl.DateTimeFormat(locale(), options).format(new Date(`${value}T00:00:00`));
}

function isoDate(date) {
  return date.toISOString().slice(0, 10);
}

function nextDay(dateString) {
  const next = new Date(`${dateString}T00:00:00`);
  next.setDate(next.getDate() + 1);
  return isoDate(next);
}

function readRawRows() {
  return [...observationsBody.querySelectorAll("tr")].map((row) =>
    Object.fromEntries(
      [...row.querySelectorAll("input")].map((input) => [input.name, input.value])
    )
  );
}

function renderRows(rows = []) {
  observationsBody.innerHTML = rows.map((row, index) => `
    <tr>
      <th scope="row">${String(index + 1).padStart(2, "0")}</th>
      <td><input required readonly name="date" type="date" value="${row.date}" aria-label="${t("date")} ${index + 1}" /></td>
      <td><input required readonly name="temperature_min" type="number" step="0.1" value="${row.temperature_min ?? row.temperature}" aria-label="${t("temperatureMin")} ${index + 1}" /></td>
      <td><input required readonly name="temperature_max" type="number" step="0.1" value="${row.temperature_max ?? row.temperature}" aria-label="${t("temperatureMax")} ${index + 1}" /></td>
      <td><input required readonly name="precipitation" type="number" min="0" step="0.1" value="${row.precipitation}" aria-label="${t("precipitation")} ${index + 1}" /></td>
      <td><input required readonly name="wind_speed" type="number" min="0" step="0.1" value="${row.wind_speed}" aria-label="${t("windSpeed")} ${index + 1}" /></td>
    </tr>
  `).join("");
}

function applyTranslations() {
  document.documentElement.lang = state.language;
  document.title = t("pageTitle");
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-aria]").forEach((element) => {
    element.setAttribute("aria-label", t(element.dataset.i18nAria));
  });
  document.querySelectorAll(".language-button").forEach((button) => {
    const active = button.dataset.language === state.language;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  const existingRows = readRawRows();
  renderRows(existingRows.length === 7 ? existingRows : []);
  if (state.currentForecast) renderForecast(state.currentForecast, state.currentModel);
  if (state.currentMlForecast) renderMlForecast(state.currentMlForecast, state.currentMlModel);
}

function showMessage(element, message) {
  element.textContent = message;
  element.hidden = false;
}

function clearMessages() {
  errorBox.hidden = true;
  statusBox.hidden = true;
}

function showMlMessage(element, message) {
  element.textContent = message;
  element.hidden = false;
}

function renderForecast(forecast, model) {
  state.currentForecast = forecast;
  state.currentModel = model;
  const temperatures = forecast.map(forecastAverageTemperature);
  const minimum = Math.min(...temperatures);
  const maximum = Math.max(...temperatures);
  const range = maximum - minimum || 1;
  const formatter = new Intl.NumberFormat(locale(), { maximumFractionDigits: 1 });

  forecastTemperatureHeading.textContent = t("forecastTemperature");
  forecastValue.textContent = `${formatter.format(temperatures[0])} °C`;
  forecastDate.textContent = `${formatDate(forecast[0].date)} — ${formatDate(forecast[forecast.length - 1].date)}`;
  forecastModel.textContent = model;
  forecastBody.innerHTML = forecast.map((item) => `
    <tr><td>${formatDate(item.date, { day: "numeric", month: "long", weekday: "short" })}</td><td>${formatter.format(forecastAverageTemperature(item))} °C</td></tr>
  `).join("");
  forecastChart.innerHTML = forecast.map((item) => {
    const height = 24 + ((temperatures[forecast.indexOf(item)] - minimum) / range) * 64;
    const chartLabel = `${new Intl.NumberFormat(locale(), { maximumFractionDigits: 0 }).format(forecastAverageTemperature(item))}°`;
    return `<div class="chart-column"><span class="chart-value">${chartLabel}</span><span class="chart-bar" style="height:${height}px"></span><span class="chart-day">${formatDate(item.date, { weekday: "short" })}</span></div>`;
  }).join("");
  renderComparison();
}

function readForecastResponse(result) {
  if (!Array.isArray(result.forecast)) {
    if (typeof result.predicted_temperature === "number") {
      throw new Error(t("backendOutdated"));
    }
    throw new Error(t("invalidResponse"));
  }
  if (result.forecast.length !== 7) {
    throw new Error(t("invalidResponse"));
  }
  return result.forecast;
}

async function loadLatestHistory() {
  try {
    const response = await fetch(`${window.WEATHER_API_URL}/observations/latest`);
    if (!response.ok) throw new Error(t("datasetUnavailable"));
    const result = await response.json();
    if (!Array.isArray(result.history) || result.history.length !== 7) {
      throw new Error(t("datasetUnavailable"));
    }
    renderRows(result.history);
    loadMlForecast(result.history);
  } catch (error) {
    showMessage(errorBox, error.message || t("datasetUnavailable"));
  }
}

function renderMlForecast(forecast, model) {
  state.currentMlForecast = forecast;
  state.currentMlModel = model;
  const formatter = new Intl.NumberFormat(locale(), { maximumFractionDigits: 1 });
  mlForecastModel.textContent = model;
  mlForecastDate.textContent = `${formatDate(forecast[0].date)} — ${formatDate(forecast[forecast.length - 1].date)}`;
  mlForecastBody.innerHTML = forecast.map((item) => `
    <tr><td>${formatDate(item.date, { day: "numeric", month: "long", weekday: "short" })}</td><td>${formatter.format(item.predicted_temperature)} °C</td></tr>
  `).join("");
  renderComparison();
}

function renderComparison() {
  if (!state.currentForecast || !state.currentMlForecast) {
    comparisonBody.innerHTML = "";
    comparisonStatus.textContent = t("comparisonWaiting");
    comparisonStatus.hidden = false;
    return;
  }

  const rows = calculateForecastComparison(state.currentForecast, state.currentMlForecast);
  const formatter = new Intl.NumberFormat(locale(), { maximumFractionDigits: 1 });
  comparisonBody.innerHTML = rows.map((item) => `
    <tr>
      <td>${formatDate(item.date, { day: "numeric", month: "long", weekday: "short" })}</td>
      <td>${formatter.format(item.actualTemperature)} °C</td>
      <td>${formatter.format(item.predictedTemperature)} °C</td>
      <td>${formatter.format(item.error)} °C</td>
      <td>${formatter.format(item.accuracy)}%</td>
    </tr>
  `).join("");
  comparisonStatus.textContent = rows.length === 7 ? t("comparisonReady") : t("comparisonWaiting");
  comparisonStatus.hidden = rows.length === 7;
}

async function loadMlForecast(history) {
  mlErrorBox.hidden = true;
  showMlMessage(mlStatusBox, t("mlLoading"));
  try {
    const response = await fetch(`${window.WEATHER_API_URL}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        forecast_date: nextDay(history[history.length - 1].date),
        history
      })
    });
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(payload.detail || t("mlUnavailable"));
    }
    const result = await response.json();
    const forecast = readForecastResponse(result);
    renderMlForecast(forecast, result.model);
    showMlMessage(mlStatusBox, `${t("mlLoaded")} · ${result.model}`);
  } catch (error) {
    mlStatusBox.hidden = true;
    showMlMessage(mlErrorBox, error.message || t("mlUnavailable"));
  }
}

async function loadLiveForecast() {
  liveForecastButton.disabled = true;
  clearMessages();
  showMessage(statusBox, t("liveLoading"));
  try {
    const response = await fetch(`${window.WEATHER_API_URL}/forecast/live`);
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(payload.detail || t("liveUnavailable"));
    }
    const result = await response.json();
    renderForecast(readForecastResponse(result), result.model);
    showMessage(statusBox, `${t("liveLoaded")} · ${result.location}`);
  } catch (error) {
    showMessage(errorBox, error.message || t("liveUnavailable"));
    statusBox.hidden = true;
  } finally {
    liveForecastButton.disabled = false;
  }
}

document.querySelectorAll(".language-button").forEach((button) => {
  button.addEventListener("click", () => {
    state.language = button.dataset.language;
    localStorage.setItem("weather-language", state.language);
    applyTranslations();
  });
});

liveForecastButton.addEventListener("click", loadLiveForecast);
applyTranslations();
loadLatestHistory();
loadLiveForecast();
