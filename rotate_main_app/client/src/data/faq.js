export const faqItems = [
  {
    q: "Is ROTATE using real NASA data?",
    a: "The engine uses cached NASA POWER weather and MODIS Terra NDVI files. POWER is reanalysis/model output rather than a field measurement, and NDVI describes vegetation around the field at 250 m. The app keeps those limits visible.",
  },
  {
    q: "How are crop-rotation strategies scored?",
    a: "The engine builds three cards: the current rotation plus two alternatives. Benefits and risks come from the cited rule table; farmer priorities and constraints affect comparison. Every card needs local review.",
  },
  {
    q: "What does “closest climate analog” mean?",
    a: "It is one of five past Boro seasons whose 60-day weather window most resembles the period before the decision date. The method is transparent analog matching, not a forecast.",
  },
  {
    q: "Can I trust the recommendation for my farm?",
    a: "Use it to compare historical examples, not as a prescription. ROTATE does not forecast, measure field-level salinity, or show how a rotation performed. Review the cards with local agricultural experts.",
  },
  {
    q: "How would real data be connected?",
    a: "The public demo uses a build-time snapshot of the Python engine outputs so it can run free and offline. The engine reads cached data; network fetches stay in the separate scripts workflow.",
  },
];
