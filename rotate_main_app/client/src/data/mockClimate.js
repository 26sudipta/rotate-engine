// Demonstration dataset only — mirrors server/data/climate.data.js.
// NOT live NASA Earth Observation values.

export const currentConditions = {
  "coastal-chattogram": { precipitationMm: 18.4, temperatureC: 29.6, soilMoisturePct: 34, soilSalinityDsm: 5.8 },
  dhaka: { precipitationMm: 12.1, temperatureC: 30.8, soilMoisturePct: 28, soilSalinityDsm: 0.9 },
  khulna: { precipitationMm: 15.2, temperatureC: 29.1, soilMoisturePct: 31, soilSalinityDsm: 7.2 },
  barisal: { precipitationMm: 16.8, temperatureC: 29.4, soilMoisturePct: 33, soilSalinityDsm: 4.6 },
  rajshahi: { precipitationMm: 6.3, temperatureC: 32.1, soilMoisturePct: 19, soilSalinityDsm: 1.1 },
  sylhet: { precipitationMm: 22.7, temperatureC: 28.3, soilMoisturePct: 41, soilSalinityDsm: 0.4 },
};

export const getCurrentConditions = (locationId) => currentConditions[locationId] || null;
