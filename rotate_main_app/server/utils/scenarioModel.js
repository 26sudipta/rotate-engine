// PROTOTYPE MODEL — not a validated scientific model.
// This function is intentionally isolated so it can be swapped for a real
// crop-suitability / climate-impact model without touching calling code.
//
// scenario suitability = base suitability * rainfall factor * salinity factor * priority factor

import { toPriorityScores, priorityKeys } from "../data/strategies.data.js";

/**
 * @param {object} strategy - a strategy record from strategies.data.js
 * @param {object} scenario - { rainfallPct: number, salinityPct: number }
 * @param {object} priorities - map of priorityKey -> weight (0-100)
 */
export function calculateSuitability(strategy, scenario, priorities) {
  const { waterDemand, soilRecovery, salinityResilience, yieldStability } = strategy.indicators;

  const baseSuitability =
    (100 - waterDemand) * 0.25 +
    soilRecovery * 0.25 +
    salinityResilience * 0.25 +
    yieldStability * 0.25;

  // Rainfall factor: a rainfall drop hurts high-water-demand strategies more.
  const rainfallPct = scenario.rainfallPct ?? 0;
  const waterSensitivity = waterDemand / 100;
  const rainfallFactor = 1 + (rainfallPct / 100) * waterSensitivity * -1 * (rainfallPct < 0 ? 1 : 0.4);

  // Salinity factor: rising salinity hurts low-salinity-resilience strategies more.
  const salinityPct = scenario.salinityPct ?? 0;
  const salinitySensitivity = 1 - salinityResilience / 100;
  const salinityFactor = 1 - Math.max(0, salinityPct / 100) * salinitySensitivity;

  // Priority factor: weights the strategy's own indicator profile against user priorities.
  const priorityScores = toPriorityScores(strategy.indicators);
  const totalWeight = priorityKeys.reduce((sum, key) => sum + (priorities?.[key] ?? 25), 0) || 100;
  const priorityFactor =
    priorityKeys.reduce(
      (sum, key) => sum + (priorityScores[key] / 100) * (priorities?.[key] ?? 25),
      0
    ) / totalWeight;

  const rawScore = baseSuitability * rainfallFactor * salinityFactor * (0.5 + priorityFactor);
  const suitability = Math.max(0, Math.min(100, rawScore));

  return {
    strategyId: strategy.id,
    baseSuitability: Number(baseSuitability.toFixed(1)),
    rainfallFactor: Number(rainfallFactor.toFixed(3)),
    salinityFactor: Number(salinityFactor.toFixed(3)),
    priorityFactor: Number(priorityFactor.toFixed(3)),
    suitability: Number(suitability.toFixed(1)),
  };
}

export function calculateProjection(strategy, scenario, priorities) {
  // Simple 3-year deterministic projection: assumes the scenario's rainfall/salinity
  // shift phases in gradually rather than hitting all at once in year 1.
  const years = [1, 2, 3].map((year) => {
    const phase = year / 3;
    const phasedScenario = {
      rainfallPct: (scenario.rainfallPct ?? 0) * phase,
      salinityPct: (scenario.salinityPct ?? 0) * phase,
    };
    const result = calculateSuitability(strategy, phasedScenario, priorities);
    return { year, suitability: result.suitability };
  });

  return years;
}
