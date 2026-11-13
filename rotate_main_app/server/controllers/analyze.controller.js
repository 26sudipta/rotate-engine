import { getClimateForLocation } from "../services/climate.service.js";
import { getHistoricalForLocation } from "../services/historical.service.js";
import { rankStrategiesByPriority } from "../services/strategies.service.js";
import { asyncHandler } from "../utils/asyncHandler.js";

export const analyzeLocation = asyncHandler(async (req, res) => {
  const { locationId, priorities } = req.body ?? {};
  if (!locationId) {
    return res.status(400).json({ error: "locationId is required" });
  }

  const climate = getClimateForLocation(locationId);
  const historical = getHistoricalForLocation(locationId);
  if (!climate || !historical) {
    return res.status(404).json({ error: `No data available for "${locationId}"` });
  }

  const strategies = rankStrategiesByPriority(priorities);

  res.json({
    data: {
      locationId,
      climate,
      historical,
      recommendedStrategy: strategies[0],
      strategies,
      status: "Analysis ready",
      dataSource: "demo",
    },
  });
});
