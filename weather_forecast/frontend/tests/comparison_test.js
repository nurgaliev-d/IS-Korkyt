const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(path.join(__dirname, "..", "comparison.js"), "utf8");
vm.runInThisContext(source);

const actual = [
  { date: "2026-09-14", temperature_mean: 20 },
  { date: "2026-09-15", temperature_mean: 0 },
];
const predicted = [
  { date: "2026-09-14", predicted_temperature: 19 },
  { date: "2026-09-15", predicted_temperature: 2 },
];

assert.deepEqual(calculateForecastComparison(actual, predicted), [
  {
    date: "2026-09-14",
    actualTemperature: 20,
    predictedTemperature: 19,
    error: 1,
    accuracy: 95,
  },
  {
    date: "2026-09-15",
    actualTemperature: 0,
    predictedTemperature: 2,
    error: 2,
    accuracy: 0,
  },
]);

console.log("comparison test passed");
