import { listLocations, getLocation } from "../services/locations.service.js";
import { asyncHandler } from "../utils/asyncHandler.js";

export const getAllLocations = asyncHandler(async (req, res) => {
  res.json({ data: listLocations() });
});

export const getLocationById = asyncHandler(async (req, res) => {
  const location = getLocation(req.params.id);
  if (!location) {
    return res.status(404).json({ error: `Location "${req.params.id}" not found` });
  }
  res.json({ data: location });
});
