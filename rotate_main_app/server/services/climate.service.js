import { getCurrentConditions } from "../data/climate.data.js";
import { findLocationById } from "../data/locations.data.js";

export function getClimateForLocation(locationId) {
  const location = findLocationById(locationId);
  const conditions = getCurrentConditions(locationId);
  if (!location || !conditions) return null;

  return {
    locationId,
    locationName: location.name,
    ...conditions,
  };
}
