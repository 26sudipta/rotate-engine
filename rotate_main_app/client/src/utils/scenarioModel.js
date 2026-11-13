// PROTOTYPE MODEL — mirrors server/utils/scenarioModel.js so scenario sliders
// can update the UI instantly without waiting on a network round trip. Not a
// validated scientific model. Keep in sync with the server copy, or replace
// both with a shared package once a real model is connected.

import { toPriorityScores, priorityKeys } from "../data/mockStrategies.js";

export function calculateSuitability(strategy, scenario, priorities) {
  const { waterDemand, soilRecovery, salinityResilience, yieldStability } = strategy.indicators;

  const baseSuitability =
    (100 - waterDemand) * 0.25 +
    soilRecovery * 0.25 +
    salinityResilience * 0.25 +
    yieldStability * 0.25;

  const rainfallPct = scenario.rainfallPct ?? 0;
  const waterSensitivity = waterDemand / 100;
  const rainfallFactor = 1 + (rainfallPct / 100) * waterSensitivity * -1 * (rainfallPct < 0 ? 1 : 0.4);

  const salinityPct = scenario.salinityPct ?? 0;
  const salinitySensitivity = 1 - salinityResilience / 100;
  const salinityFactor = 1 - Math.max(0, salinityPct / 100) * salinitySensitivity;

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
    suitability: Number(suitability.toFixed(1)),
  };
}

export function calculateProjection(strategy, scenario, priorities) {
  return [1, 2, 3].map((year) => {
    const phase = year / 3;
    const phasedScenario = {
      rainfallPct: (scenario.rainfallPct ?? 0) * phase,
      salinityPct: (scenario.salinityPct ?? 0) * phase,
    };
    const result = calculateSuitability(strategy, phasedScenario, priorities);
    return { year, suitability: result.suitability };
  });
}

export function rankStrategiesByPriority(strategies, priorities) {
  const totalWeight = priorityKeys.reduce((sum, key) => sum + (priorities?.[key] ?? 25), 0) || 100;

  return strategies
    .map((strategy) => {
      const scores = toPriorityScores(strategy.indicators);
      const weightedScore =
        priorityKeys.reduce((sum, key) => sum + scores[key] * (priorities?.[key] ?? 25), 0) /
        totalWeight;
      return { ...strategy, matchScore: Number(weightedScore.toFixed(1)) };
    })
    .sort((a, b) => b.matchScore - a.matchScore);
}
