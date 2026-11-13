import { runScenario } from "../services/scenario.service.js";
import { asyncHandler } from "../utils/asyncHandler.js";

export const postScenario = asyncHandler(async (req, res) => {
  const { locationId, rainfallPct, salinityPct, priorities } = req.body ?? {};
  if (!locationId) {
    return res.status(400).json({ error: "locationId is required" });
  }

  const result = runScenario({ locationId, rainfallPct, salinityPct, priorities });
  res.json({ data: result });
});
