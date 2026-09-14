function forecastAverageTemperature(item) {
  if (Number.isFinite(item.temperature_mean)) return item.temperature_mean;
  if (Number.isFinite(item.predicted_temperature)) return item.predicted_temperature;
  return null;
}

function calculateForecastComparison(actualForecast, predictedForecast) {
  const predictionsByDate = new Map(
    predictedForecast.map((item) => [item.date, item.predicted_temperature])
  );

  return actualForecast.flatMap((actual) => {
    const actualTemperature = forecastAverageTemperature(actual);
    const predictedTemperature = predictionsByDate.get(actual.date);
    if (!Number.isFinite(actualTemperature) || !Number.isFinite(predictedTemperature)) return [];

    const error = Math.abs(predictedTemperature - actualTemperature);
    const denominator = Math.max(Math.abs(actualTemperature), 1);
    const accuracy = Math.max(0, 100 - (error / denominator) * 100);
    return [{
      date: actual.date,
      actualTemperature,
      predictedTemperature,
      error,
      accuracy,
    }];
  });
}
