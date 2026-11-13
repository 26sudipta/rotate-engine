import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { CloudRain, Beaker, ArrowRight } from "lucide-react";
import ScenarioSlider from "../components/ScenarioSlider.jsx";
import ProjectionChart from "../components/ProjectionChart.jsx";
import BaselineScenarioChart from "../components/BaselineScenarioChart.jsx";
import { useApp } from "../context/AppContext.jsx";
import { strategies as fallbackStrategies } from "../data/mockStrategies.js";
import { calculateSuitability, calculateProjection } from "../utils/scenarioModel.js";
import { getCurrentConditions } from "../data/mockClimate.js";
import { api } from "../services/api.js";

export default function Scenario() {
  const { selectedLocationId, selectedLocation, priorities, scenario, setScenario, setSelectedStrategyId } = useApp();
  const [strategies, setStrategies] = useState(fallbackStrategies);
  const [baseline, setBaseline] = useState(getCurrentConditions(selectedLocationId));
  const [pulse, setPulse] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    api.getStrategies().then(setStrategies).catch(() => {});
  }, []);

  useEffect(() => {
    api.getClimate(selectedLocationId).catch(() => getCurrentConditions(selectedLocationId)).then(setBaseline);
  }, [selectedLocationId]);

  const results = useMemo(() => {
    return strategies
      .map((strategy) => ({
        ...strategy,
        suitability: calculateSuitability(strategy, scenario, priorities),
        noChangeScore: calculateSuitability(strategy, { rainfallPct: 0, salinityPct: 0 }, priorities).suitability,
        projection: calculateProjection(strategy, scenario, priorities),
      }))
      .sort((a, b) => b.suitability.suitability - a.suitability.suitability);
  }, [strategies, scenario, priorities]);

  const recommended = results[0];

  const handleScenarioChange = (key, value) => {
    setScenario({ ...scenario, [key]: value });
    setPulse(true);
    setTimeout(() => setPulse(false), 1200);
  };

  if (!baseline) return null;

  const projectedPrecipitation = Number((baseline.precipitationMm * (1 + scenario.rainfallPct / 100)).toFixed(1));
  const projectedMoisture = Number(Math.min(100, Math.max(0, baseline.soilMoisturePct * (1 + (scenario.rainfallPct * 0.5) / 100))).toFixed(1));
  const projectedSalinity = Number((baseline.soilSalinityDsm * (1 + scenario.salinityPct / 100)).toFixed(1));


  return (
    <div className="mx-auto max-w-[1200px] px-6 py-8">

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <ScenarioSlider
          icon={CloudRain}
          label="Rainfall"
          value={scenario.rainfallPct}
          min={-30}
          max={30}
          onChange={(v) => handleScenarioChange("rainfallPct", v)}
          tint="water"
        />
        <ScenarioSlider
          icon={Beaker}
          label="Soil salinity"
          value={scenario.salinityPct}
          min={-25}
          max={50}
          onChange={(v) => handleScenarioChange("salinityPct", v)}
          tint="clay"
        />
      </div>

      <div className="mt-2 h-4 text-[12px] font-medium text-paddy">
        <AnimatePresence>
          {pulse && (
            <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              Scenario conditions updated. Strategy comparison updated.
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      <div className="mt-4 grid grid-cols-1 gap-5 lg:grid-cols-3">
        <BaselineScenarioChart
          title="Precipitation"
          unit="mm"
          data={[{ label: selectedLocation.name, current: baseline.precipitationMm, scenario: projectedPrecipitation }]}
          note="Baseline demonstration value adjusted by the rainfall slider."
        />
        <BaselineScenarioChart
          title="Soil moisture"
          unit="%"
          data={[{ label: selectedLocation.name, current: baseline.soilMoisturePct, scenario: projectedMoisture }]}
          note="Prototype assumption: moisture moves at half the rainfall change."
        />
        <BaselineScenarioChart
          title="Strategy suitability"
          domain={[0, 100]}
          data={results.map((r) => ({ label: r.name.replace("Strategy ", "") , current: r.noChangeScore, scenario: r.suitability.suitability }))}
          note="Scenario score uses the prototype formula (see Methodology)."
        />
      </div>

      {recommended && (
        <div className="mt-6 grid grid-cols-1 gap-5 lg:grid-cols-[1fr_1fr]">
          <div className="rounded-[24px] border border-paddy/30 bg-crop-soft/40 p-5">
            <p className="text-[12px] font-medium text-paddy">Recommended Strategy to Explore</p>
            <h2 className="mt-1 font-display text-[18px] font-semibold text-ink">
              {recommended.name} — {recommended.label}
            </h2>
            <p className="mt-1 text-[13px] text-ink-soft">
              Scenario suitability score: <span className="font-mono text-ink">{recommended.suitability.suitability}</span> / 100
              <span className="ml-1 text-[11px] text-clay">(prototype analysis)</span>
            </p>
            <button
              type="button"
              onClick={() => {
                setSelectedStrategyId(recommended.id);
                navigate("/results");
              }}
              className="mt-4 inline-flex items-center gap-2 rounded-md bg-paddy px-5 py-2.5 text-[13px] font-medium text-white hover:bg-paddy-light"
            >
              View recommendation summary
              <ArrowRight size={14} />
            </button>
          </div>
          <ProjectionChart projection={recommended.projection} />
        </div>
      )}
    </div>
  );
}
