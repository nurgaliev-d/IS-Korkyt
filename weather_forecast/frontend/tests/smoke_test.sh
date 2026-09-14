#!/usr/bin/env bash
set -euo pipefail

frontend_dir="$(cd "$(dirname "$0")/.." && pwd)"
project_dir="$(cd "$frontend_dir/.." && pwd)"

test -f "$frontend_dir/index.html"
test -f "$frontend_dir/styles.css"
test -f "$frontend_dir/config.js"
test -f "$frontend_dir/translations.js"
test -f "$frontend_dir/app.js"
test -f "$frontend_dir/comparison.js"
grep -q 'styles.css' "$frontend_dir/index.html"
grep -q 'config.js' "$frontend_dir/index.html"
grep -q 'translations.js' "$frontend_dir/index.html"
grep -q 'app.js' "$frontend_dir/index.html"
grep -q 'forecast-table' "$frontend_dir/index.html"
grep -q 'forecast-chart' "$frontend_dir/index.html"
grep -q 'live-forecast-button' "$frontend_dir/index.html"
grep -q 'ml-forecast-body' "$frontend_dir/index.html"
grep -q 'comparison-body' "$frontend_dir/index.html"
grep -q 'mlForecastTitle' "$frontend_dir/translations.js"
grep -q 'comparisonTitle' "$frontend_dir/translations.js"
grep -q '/predict' "$frontend_dir/app.js"
if grep -q 'mlButton' "$frontend_dir/index.html"; then
  echo "ML button must not be present"
  exit 1
fi
if grep -q 'submitForecast' "$frontend_dir/app.js"; then
  echo "ML submit handler must not be present"
  exit 1
fi
grep -q 'sevenDays' "$frontend_dir/translations.js"
grep -q 'backendOutdated' "$frontend_dir/translations.js"
grep -q 'Array.isArray(result.forecast)' "$frontend_dir/app.js"
grep -q '/observations/latest' "$frontend_dir/app.js"
grep -q 'readonly' "$frontend_dir/app.js"
grep -q 'temperature_min' "$frontend_dir/app.js"
grep -q 'temperature_max' "$frontend_dir/app.js"
grep -q 'calculateForecastComparison' "$frontend_dir/app.js"
grep -q '/forecast/live' "$frontend_dir/app.js"
grep -q 'liveLoading' "$frontend_dir/translations.js"
grep -q 'ru:' "$frontend_dir/translations.js"
grep -q 'kk:' "$frontend_dir/translations.js"
grep -q 'publish.*frontend' "$project_dir/netlify.toml"

echo "frontend smoke test passed"
