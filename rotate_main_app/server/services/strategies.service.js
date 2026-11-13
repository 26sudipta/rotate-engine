import { strategies, toPriorityScores, priorityKeys } from "../data/strategies.data.js";

export function listStrategies() {
  return strategies;
}

export function getStrategy(id) {
  return strategies.find((s) => s.id === id) || null;
}

/**
 * Ranks strategies by a weighted sum of their indicator scores against user priorities.
 * priorities: { waterConservation, soilRecovery, salinityResilience, yieldStability } each 0-100
 */
export function rankStrategiesByPriority(priorities) {
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
