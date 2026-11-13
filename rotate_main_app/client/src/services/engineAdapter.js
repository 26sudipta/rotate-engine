const ENGINE_FILES = {
  "coastal-chattogram": "cards_ctg.json",
  rajshahi: "cards_barind.json",
};

const CROP_LABELS = {
  boro: "Boro rice",
  fallow: "Fallow",
  t_aman: "T. Aman",
  wheat: "Wheat",
  jute: "Jute",
  mungbean: "Mungbean",
  mustard: "Mustard",
  sunflower: "Sunflower",
  sesame: "Sesame",
  aus: "Aus rice",
};

function percentage(value) {
  return value == null ? 0 : Math.max(0, Math.min(100, Math.round(value * 100)));
}

function cardToStrategy(card) {
  const breakdown = card.score_breakdown ?? {};
  const indicators = {
    waterDemand: Math.max(0, 100 - percentage(breakdown.water)),
    soilRecovery: percentage(breakdown.soil_n),
    salinityResilience: percentage(breakdown.salinity),
    yieldStability: percentage(breakdown.yield_stability),
  };
  const score = Object.values(breakdown).reduce(
    (total, value) => total + (typeof value === "number" ? value : 0),
    0
  );

  return {
    id: card.card_id,
    name: card.strategy.name,
    label: card.is_existing ? "Current rotation" : "Alternative to compare",
    sequence: card.strategy.slots.map((slot) => CROP_LABELS[slot] ?? slot),
    indicators,
    matchScore: score * 100,
    notes: card.why,
    engineCard: card,
  };
}

export async function loadEngineStrategies(locationId) {
  const file = ENGINE_FILES[locationId];
  if (!file) return null;

  const response = await fetch(`/engine/${file}`);
  if (!response.ok) {
    throw new Error(`Engine snapshot request failed (${response.status})`);
  }

  const cardSet = await response.json();
  if (cardSet.status === "not_cached") {
    throw new Error(cardSet.message);
  }

  return {
    strategies: cardSet.cards.map(cardToStrategy),
    cardSet,
  };
}

export async function loadEngineSnapshot(locationId) {
  const file = ENGINE_FILES[locationId];
  if (!file) return null;
  const response = await fetch(`/engine/${file}`);
  if (!response.ok) throw new Error(`Engine snapshot request failed (${response.status})`);
  return response.json();
}
