// Demonstration dataset only. Years and values are synthetically generated
// to illustrate the shape of a historical-analog comparison. They are NOT
// derived from real NASA climate records. Replace generateSeries() with a
// call into a real historical climate archive (e.g. NASA POWER, ERA5) later.

import { getCurrentConditions } from "./climate.data.js";

const START_YEAR = 1986;
const END_YEAR = 2025;

// Small deterministic pseudo-random generator so results are stable across requests.
function seededNoise(seed) {
  const x = Math.sin(seed * 12.9898) * 43758.5453;
  return x - Math.floor(x);
}

function generateSeries(locationId, baseline) {
  const seedBase = [...locationId].reduce((a, c) => a + c.charCodeAt(0), 0);
  const years = [];

  for (let year = START_YEAR; year <= END_YEAR; year++) {
    const t = (year - START_YEAR) / (END_YEAR - START_YEAR);
    const noise = seededNoise(seedBase + year);
    // Gentle long-term drift plus year-to-year noise, purely for demonstration shape.
    const precipitationMm = Math.max(
      2,
      baseline.precipitationMm * (0.85 + 0.3 * noise) * (1 - 0.1 * t)
    );
    const temperatureC = baseline.temperatureC * (0.97 + 0.06 * noise) + t * 0.9;
    const soilMoisturePct = Math.min(
      60,
      Math.max(8, baseline.soilMoisturePct * (0.8 + 0.4 * noise) * (1 - 0.08 * t))
    );

    years.push({
      year,
      precipitationMm: Number(precipitationMm.toFixed(1)),
      temperatureC: Number(temperatureC.toFixed(1)),
      soilMoisturePct: Number(soilMoisturePct.toFixed(1)),
    });
  }

  return years;
}

export function getHistoricalSeries(locationId) {
  const baseline = getCurrentConditions(locationId);
  if (!baseline) return null;

  const series = generateSeries(locationId, baseline);

  // "Closest analog" = historical year with smallest combined distance to current conditions.
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

  return {
    locationId,
    series,
    closestAnalogYear: closest.year,
    closestAnalog: closest,
    dataSource: "demo",
  };
}
