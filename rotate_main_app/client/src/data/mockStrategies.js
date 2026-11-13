// Client-side mirror of server/data/strategies.data.js, used as a fast local
// fallback for slider interactions so the UI can respond instantly while the
// authoritative values still come from the API on page load. Demonstration
// data — indicator scores are illustrative, not validated agronomic outputs.

export const strategies = [
  {
    id: "strategy-a",
    name: "Strategy A",
    label: "High-water, established rotation",
    sequence: ["Boro Rice", "Jute", "Lentil (Masoor)"],
    indicators: { waterDemand: 82, soilRecovery: 58, salinityResilience: 28, yieldStability: 80 },
    notes:
      "A conventional rotation with strong yield history in freshwater floodplain districts, but reliant on consistent irrigation and low soil salinity.",
  },
  {
    id: "strategy-b",
    name: "Strategy B",
    label: "Salinity-focused rotation",
    sequence: ["Saline-tolerant Rice (BRRI dhan47)", "Sunflower", "Mustard"],
    indicators: { waterDemand: 54, soilRecovery: 66, salinityResilience: 84, yieldStability: 61 },
    notes:
      "Pairs a salt-tolerant rice variety with oilseed crops that hold up in coastal, tidally-influenced soils, at some cost to yield predictability.",
  },
  {
    id: "strategy-c",
    name: "Strategy C",
    label: "Low-water, soil-building rotation",
    sequence: ["Aus Rice", "Sesame", "Mungbean (Green Gram)"],
    indicators: { waterDemand: 38, soilRecovery: 85, salinityResilience: 55, yieldStability: 67 },
    notes:
      "A legume-heavy sequence that rebuilds soil nitrogen and tolerates shorter, less reliable rainy seasons.",
  },
];

export const priorityKeys = ["waterConservation", "soilRecovery", "salinityResilience", "yieldStability"];

export function toPriorityScores(indicators) {
  return {
    waterConservation: 100 - indicators.waterDemand,
    soilRecovery: indicators.soilRecovery,
    salinityResilience: indicators.salinityResilience,
    yieldStability: indicators.yieldStability,
  };
}
