// Thin fetch wrapper around the ROTATE Express API.
// Base URL is read from an environment variable so it can point at a real
// deployment without code changes.

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:4000/api";

export { loadEngineSnapshot, loadEngineStrategies } from "./engineAdapter.js";

async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.error || `Request to ${path} failed (${response.status})`);
  }

  const json = await response.json();
  return json.data;
}

export const api = {
  getLocations: () => request("/locations"),
  getLocation: (id) => request(`/locations/${id}`),
  getClimate: (locationId) => request(`/climate/${locationId}`),
  getHistorical: (locationId) => request(`/historical/${locationId}`),
  getStrategies: () => request("/strategies"),
  getRankedStrategies: (priorities) =>
    request(`/strategies/ranked?${new URLSearchParams(priorities).toString()}`),
  analyze: (locationId, priorities) =>
    request("/analyze", { method: "POST", body: JSON.stringify({ locationId, priorities }) }),
  runScenario: (payload) =>
    request("/scenario", { method: "POST", body: JSON.stringify(payload) }),
  getCrops: () => request("/crops"),
  sendContact: (payload) => request("/contact", { method: "POST", body: JSON.stringify(payload) }),
  health: () => request("/health"),
};
