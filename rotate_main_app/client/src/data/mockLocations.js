// Demonstration dataset only — mirrors server/data/locations.data.js.
// Used as an immediate fallback so the map renders before the API responds.

export const locations = [
  { id: "coastal-chattogram", name: "Coastal Chattogram", region: "Chattogram Division", lat: 22.15, lng: 91.75, zoom: 10, farmName: "Anwara Delta Plot", soilType: "Saline clay loam" },
  { id: "dhaka", name: "Dhaka", region: "Dhaka Division", lat: 23.81, lng: 90.41, zoom: 10, farmName: "Savar Floodplain Plot", soilType: "Silty clay" },
  { id: "khulna", name: "Khulna", region: "Khulna Division", lat: 22.82, lng: 89.55, zoom: 10, farmName: "Dumuria Tidal Plot", soilType: "Saline clay" },
  { id: "barisal", name: "Barisal", region: "Barisal Division", lat: 22.7, lng: 90.37, zoom: 10, farmName: "Kirtankhola Char Plot", soilType: "Alluvial silt" },
  { id: "rajshahi", name: "Rajshahi", region: "Rajshahi Division", lat: 24.37, lng: 88.6, zoom: 10, farmName: "Padma Terrace Plot", soilType: "Sandy loam" },
  { id: "sylhet", name: "Sylhet", region: "Sylhet Division", lat: 24.9, lng: 91.87, zoom: 10, farmName: "Haor Basin Plot", soilType: "Peaty clay" },
];

export const findLocationById = (id) => locations.find((l) => l.id === id);
