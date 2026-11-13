import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence, LayoutGroup } from "framer-motion";
import { ArrowRight } from "lucide-react";
import StrategyCard from "../components/StrategyCard.jsx";
import PrioritySlider from "../components/PrioritySlider.jsx";
import EvidenceTrail from "../components/EvidenceTrail.jsx";
import { useApp } from "../context/AppContext.jsx";
import { strategies as fallbackStrategies } from "../data/mockStrategies.js";
import { rankStrategiesByPriority } from "../utils/scenarioModel.js";
import { api, loadEngineStrategies } from "../services/api.js";
import DataSourceBadge from "../components/DataSourceBadge.jsx";

export default function Strategies() {
  const { priorities, setPriorities, selectedLocationId, selectedStrategyId, setSelectedStrategyId } = useApp();
  const [baseStrategies, setBaseStrategies] = useState(fallbackStrategies);
  const [engineLoaded, setEngineLoaded] = useState(false);
  const [justUpdated, setJustUpdated] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;
    loadEngineStrategies(selectedLocationId).then((result) => {
      if (cancelled || !result) return;
      setBaseStrategies(result.strategies);
      setEngineLoaded(true);
    }).catch(() => {
      api.getStrategies().then((data) => {
        if (!cancelled) setBaseStrategies(data);
      }).catch(() => {});
    });
    return () => { cancelled = true; };
  }, [selectedLocationId]);

  const ranked = useMemo(
    () => engineLoaded ? baseStrategies : rankStrategiesByPriority(baseStrategies, priorities),
    [baseStrategies, priorities, engineLoaded]
  );

  const handlePriorityChange = (next) => {
    setPriorities(next);
    setJustUpdated(true);
    const timer = setTimeout(() => setJustUpdated(false), 1400);
    return () => clearTimeout(timer);
  };

  const selectedStrategy = ranked.find((s) => s.id === selectedStrategyId) ?? ranked[0];

  return (
    <div className="mx-auto max-w-[1200px] px-6 py-8">
      {engineLoaded && <DataSourceBadge source="engine" />}

      <div className="mt-6">
        <PrioritySlider priorities={priorities} onChange={handlePriorityChange} />
        <div className="mt-2 h-4 text-[12px] font-medium text-paddy">
          <AnimatePresence>
            {justUpdated && (
              <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                {engineLoaded
                  ? "Python engine snapshot loaded; live priority reranking needs a backend."
                  : "Strategy comparison updated."}
              </motion.span>
            )}
          </AnimatePresence>
        </div>
      </div>

      <LayoutGroup>
        <div className="mt-2 grid grid-cols-1 gap-5 lg:grid-cols-3">
          {ranked.map((strategy, i) => (
            <StrategyCard
              key={strategy.id}
              strategy={strategy}
              rank={i + 1}
              isSelected={strategy.id === selectedStrategyId}
              onSelect={setSelectedStrategyId}
            />
          ))}
        </div>
      </LayoutGroup>

      {selectedStrategy && (
        <div className="mt-8 rounded-[24px] border border-paddy/30 bg-crop-soft/40 p-5">
          <p className="text-[12px] font-medium text-paddy">Recommended Strategy to Explore</p>
          <h2 className="mt-1 font-display text-[19px] font-semibold text-ink">
            {selectedStrategy.name} — {selectedStrategy.label}
          </h2>
          <p className="mt-1 text-[13px] text-ink-soft">{selectedStrategy.notes}</p>

          <div className="mt-4">
            <EvidenceTrail />
          </div>

          <button
            type="button"
            onClick={() => navigate("/results")}
            className="mt-4 inline-flex items-center gap-2 rounded-md bg-paddy px-5 py-2.5 text-[13px] font-medium text-white hover:bg-paddy-light"
          >
            View recommendation summary
            <ArrowRight size={14} />
          </button>
        </div>
      )}
    </div>
  );
}
