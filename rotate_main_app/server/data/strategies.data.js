// Example crop-rotation sequences relevant to Bangladeshi agriculture.
// Indicator scores (0-100) are illustrative placeholders for the prototype,
// not outputs of a validated agronomic model. Structure is kept stable so a
// real crop-suitability model can populate the same fields later.

export const strategies = [
  {
    id: "strategy-a",
    name: "Strategy A",
    label: "High-water, established rotation",
    sequence: ["Boro Rice", "Jute", "Lentil (Masoor)"],
    indicators: {
      waterDemand: 82,
      soilRecovery: 58,
      salinityResilience: 28,
      yieldStability: 80,
    },
    notes:
      "A conventional rotation with strong yield history in freshwater floodplain districts, but reliant on consistent irrigation and low soil salinity.",
  },
  {
    id: "strategy-b",
    name: "Strategy B",
    label: "Salinity-focused rotation",
    sequence: ["Saline-tolerant Rice (BRRI dhan47)", "Sunflower", "Mustard"],
    indicators: {
      waterDemand: 54,
      soilRecovery: 66,
      salinityResilience: 84,
      yieldStability: 61,
    },
    notes:
      "Pairs a salt-tolerant rice variety with oilseed crops that hold up in coastal, tidally-influenced soils, at some cost to yield predictability.",
  },
  {
    id: "strategy-c",
    name: "Strategy C",
    label: "Low-water, soil-building rotation",
    sequence: ["Aus Rice", "Sesame", "Mungbean (Green Gram)"],
    indicators: {
      waterDemand: 38,
      soilRecovery: 85,
      salinityResilience: 55,
      yieldStability: 67,
    },
    notes:
      "A legume-heavy sequence that rebuilds soil nitrogen and tolerates shorter, less reliable rainy seasons.",
  },
];

export const priorityKeys = [
  "waterConservation",
  "soilRecovery",
  "salinityResilience",
  "yieldStability",
];

// Maps a strategy's raw indicators to the same axes used by the priority slider.
// waterConservation is the inverse of waterDemand (lower demand = better conservation).
export function toPriorityScores(indicators) {
  return {
    waterConservation: 100 - indicators.waterDemand,
    soilRecovery: indicators.soilRecovery,
    salinityResilience: indicators.salinityResilience,
    yieldStability: indicators.yieldStability,
  };
}
