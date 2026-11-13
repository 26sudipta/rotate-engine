import { getHistoricalSeries } from "../data/historical.data.js";

export function getHistoricalForLocation(locationId) {
  return getHistoricalSeries(locationId);
}
