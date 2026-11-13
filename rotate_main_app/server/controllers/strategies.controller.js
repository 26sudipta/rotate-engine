import { listStrategies, rankStrategiesByPriority } from "../services/strategies.service.js";
import { asyncHandler } from "../utils/asyncHandler.js";

export const getStrategies = asyncHandler(async (req, res) => {
  res.json({ data: listStrategies() });
});

export const getRankedStrategies = asyncHandler(async (req, res) => {
  const priorities = req.query;
  const ranked = rankStrategiesByPriority({
    waterConservation: Number(priorities.waterConservation ?? 25),
    soilRecovery: Number(priorities.soilRecovery ?? 25),
    salinityResilience: Number(priorities.salinityResilience ?? 25),
    yieldStability: Number(priorities.yieldStability ?? 25),
  });
  res.json({ data: ranked });
});
