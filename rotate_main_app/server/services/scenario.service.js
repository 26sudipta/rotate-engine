import { strategies } from "../data/strategies.data.js";
import { getCurrentConditions } from "../data/climate.data.js";
import { calculateSuitability, calculateProjection } from "../utils/scenarioModel.js";

export function runScenario({ locationId, rainfallPct = -15, salinityPct = 25, priorities }) {
  const baseline = getCurrentConditions(locationId);

  const scenario = { rainfallPct, salinityPct };

  const results = strategies
    .map((strategy) => {
      const suitability = calculateSuitability(strategy, scenario, priorities);
      const projection = calculateProjection(strategy, scenario, priorities);
      return { ...strategy, suitability, projection };
    })
    .sort((a, b) => b.suitability.suitability - a.suitability.suitability);

  const projectedClimate = baseline
    ? {
        precipitationMm: Number((baseline.precipitationMm * (1 + rainfallPct / 100)).toFixed(1)),
        soilMoisturePct: Number(Math.min(100, Math.max(0, baseline.soilMoisturePct * (1 + (rainfallPct * 0.5) / 100))).toFixed(1)),
        soilSalinityDsm: Number((baseline.soilSalinityDsm * (1 + salinityPct / 100)).toFixed(1)),
      }
    : null;

  return {
    locationId,
    scenario,
    baseline,
    projectedClimate,
    recommendedStrategyId: results[0]?.id ?? null,
    results,
    dataSource: "demo",
    modelStatus: "prototype",
  };
}
