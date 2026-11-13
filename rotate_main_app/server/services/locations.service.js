import { locations, findLocationById } from "../data/locations.data.js";

export function listLocations() {
  return locations;
}

export function getLocation(id) {
  return findLocationById(id) || null;
}
