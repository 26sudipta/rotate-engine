import { createContext, useContext, useState, useMemo } from "react";
import { locations as fallbackLocations } from "../data/mockLocations.js";

const AppContext = createContext(null);

const DEFAULT_PRIORITIES = {
  waterConservation: 25,
  soilRecovery: 25,
  salinityResilience: 25,
  yieldStability: 25,
};

const DEFAULT_SCENARIO = {
  rainfallPct: -15,
  salinityPct: 25,
};

export function AppProvider({ children }) {
  const [selectedLocationId, setSelectedLocationId] = useState("coastal-chattogram");
  const [analysisStatus, setAnalysisStatus] = useState("idle"); // idle | analyzing | ready
  const [priorities, setPriorities] = useState(DEFAULT_PRIORITIES);
  const [scenario, setScenario] = useState(DEFAULT_SCENARIO);
  const [selectedStrategyId, setSelectedStrategyId] = useState("existing");

  const selectedLocation = useMemo(
    () => fallbackLocations.find((l) => l.id === selectedLocationId) || fallbackLocations[0],
    [selectedLocationId]
  );

  const value = {
    selectedLocationId,
    setSelectedLocationId,
    selectedLocation,
    analysisStatus,
    setAnalysisStatus,
    priorities,
    setPriorities,
    scenario,
    setScenario,
    selectedStrategyId,
    setSelectedStrategyId,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within an AppProvider");
  return ctx;
}
