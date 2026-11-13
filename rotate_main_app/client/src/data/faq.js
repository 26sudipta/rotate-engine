export const faqItems = [
  {
    q: "Is ROTATE using real NASA data?",
    a: "Not yet. This prototype runs on a clearly labelled demonstration dataset. The data layer is structured so NASA Earth Observation sources can replace it later, and the UI will only show “NASA Earth Observation API” once real data is connected.",
  },
  {
    q: "How are crop-rotation strategies scored?",
    a: "Each example rotation carries four indicator scores (water demand, soil recovery, salinity resilience, yield stability). A simple deterministic formula combines them with your priority weights and the rainfall and salinity scenario. It is a prototype formula, not a validated agronomic model.",
  },
  {
    q: "What does “closest climate analog” mean?",
    a: "It is the year in the historical series whose precipitation, temperature and soil moisture are closest, in relative terms, to current conditions. In this prototype the series is synthetic, so the result is labelled a demonstration result.",
  },
  {
    q: "Can I trust the recommendation for my farm?",
    a: "No — treat it as a way to explore trade-offs, not as agronomic advice. A validated recommendation needs real observations, locally calibrated crop models and input from agricultural extension specialists.",
  },
  {
    q: "How would real data be connected?",
    a: "Each data file under server/data has a matching service in server/services. Replacing a service with an API client leaves the routes, controllers and the whole frontend unchanged. The Methodology page lists candidate sources for each input.",
  },
];
