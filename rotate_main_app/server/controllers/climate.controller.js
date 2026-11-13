import { getClimateForLocation } from "../services/climate.service.js";
import { asyncHandler } from "../utils/asyncHandler.js";

export const getClimate = asyncHandler(async (req, res) => {
  const climate = getClimateForLocation(req.params.locationId);
  if (!climate) {
    return res.status(404).json({ error: `No climate data for "${req.params.locationId}"` });
  }
  res.json({ data: climate });
});
