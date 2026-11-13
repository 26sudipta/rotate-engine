import { getHistoricalForLocation } from "../services/historical.service.js";
import { asyncHandler } from "../utils/asyncHandler.js";

export const getHistorical = asyncHandler(async (req, res) => {
  const historical = getHistoricalForLocation(req.params.locationId);
  if (!historical) {
    return res.status(404).json({ error: `No historical data for "${req.params.locationId}"` });
  }
  res.json({ data: historical });
});
