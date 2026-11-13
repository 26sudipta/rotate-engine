// Demonstration dataset only — mirrors server/data/historical.data.js.
// Synthetic 40-year series for illustrating the historical-analog UI shape.

import { getCurrentConditions } from "./mockClimate.js";

const START_YEAR = 1986;
const END_YEAR = 2025;

function seededNoise(seed) {
  const x = Math.sin(seed * 12.9898) * 43758.5453;
  return x - Math.floor(x);
}

export function getHistoricalSeries(locationId) {
  const baseline = getCurrentConditions(locationId);
  if (!baseline) return null;

  const seedBase = [...locationId].reduce((a, c) => a + c.charCodeAt(0), 0);
  const series = [];

  for (let year = START_YEAR; year <= END_YEAR; year++) {
    const t = (year - START_YEAR) / (END_YEAR - START_YEAR);
    const noise = seededNoise(seedBase + year);
    series.push({
      year,
      precipitationMm: Number(Math.max(2, baseline.precipitationMm * (0.85 + 0.3 * noise) * (1 - 0.1 * t)).toFixed(1)),
      temperatureC: Number((baseline.temperatureC * (0.97 + 0.06 * noise) + t * 0.9).toFixed(1)),
      soilMoisturePct: Number(Math.min(60, Math.max(8, baseline.soilMoisturePct * (0.8 + 0.4 * noise) * (1 - 0.08 * t))).toFixed(1)),
    });
  }

  let closest = series[0];
  let bestScore = Infinity;
  for (const row of series) {
    const score =
      Math.abs(row.precipitationMm - baseline.precipitationMm) / baseline.precipitationMm +
      Math.abs(row.temperatureC - baseline.temperatureC) / baseline.temperatureC +
      Math.abs(row.soilMoisturePct - baseline.soilMoisturePct) / baseline.soilMoisturePct;
    if (score < bestScore) {
      bestScore = score;
      closest = row;
    }
  }

  return { locationId, series, closestAnalogYear: closest.year, closestAnalog: closest };
}
