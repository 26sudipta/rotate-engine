import { useMemo } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, RotateCcw } from "lucide-react";
import EvidenceTrail from "../components/EvidenceTrail.jsx";
import DataSourceBadge from "../components/DataSourceBadge.jsx";
import { useApp } from "../context/AppContext.jsx";
import { strategies } from "../data/mockStrategies.js";
import { rankStrategiesByPriority } from "../utils/scenarioModel.js";

export default function Results() {
  const { selectedLocation, priorities, scenario, selectedStrategyId } = useApp();

  const ranked = useMemo(() => rankStrategiesByPriority(strategies, priorities), [priorities]);
  const strategy = ranked.find((s) => s.id === selectedStrategyId) ?? ranked[0];

  return (
    <div className="mx-auto max-w-[900px] px-6 py-10">
      <div className="flex items-center justify-between">
        <p className="text-[12px] font-medium text-ink-soft">Prototype analysis for {selectedLocation.name}</p>
        <DataSourceBadge source="demo" />
      </div>

      <h1 className="mt-2 font-display text-[28px] font-semibold text-ink">Recommended Strategy to Explore</h1>
      <h2 className="mt-1 font-display text-[20px] font-medium text-paddy">
        {strategy.name} — {strategy.label}
      </h2>

      <div className="mt-4 flex flex-wrap items-center gap-1.5 text-[13px] text-ink">
        {strategy.sequence.map((crop, i) => (
          <span key={crop} className="flex items-center gap-1.5">
            <span className="rounded-md border border-border bg-canvas px-2.5 py-1">{crop}</span>
            {i < strategy.sequence.length - 1 && <ArrowRight size={13} className="text-ink-soft" />}
          </span>
        ))}
      </div>

      <p className="mt-4 max-w-xl text-[14px] leading-relaxed text-ink-soft">{strategy.notes}</p>

      <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {Object.entries(strategy.indicators).map(([key, value]) => (
          <div key={key} className="rounded-lg border border-border bg-surface p-3 text-center">
            <p className="font-mono text-[20px] font-semibold text-ink">{value}</p>
            <p className="mt-0.5 text-[11px] capitalize text-ink-soft">
              {key.replace(/([A-Z])/g, " $1").trim()}
            </p>
          </div>
        ))}
      </div>

      <div className="mt-6 rounded-lg border border-border bg-surface-raised p-4 text-[13px] text-ink-soft">
        Evaluated under a scenario of{" "}
        <span className="font-mono text-ink">{scenario.rainfallPct > 0 ? "+" : ""}{scenario.rainfallPct}% rainfall</span> and{" "}
        <span className="font-mono text-ink">{scenario.salinityPct > 0 ? "+" : ""}{scenario.salinityPct}% soil salinity</span>{" "}
        relative to current demonstration conditions.
      </div>

      <div className="mt-6">
        <EvidenceTrail />
      </div>

      <p className="mt-6 text-[12px] text-ink-soft">
        This output is a demonstration result from a prototype scoring model. It is not a
        scientifically validated crop recommendation.
      </p>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <Link
          to="/scenario"
          className="inline-flex items-center gap-2 rounded-md bg-paddy px-5 py-2.5 text-[13px] font-medium text-white hover:bg-paddy-light"
        >
          Run a What If scenario
          <ArrowRight size={14} />
        </Link>
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 rounded-md border border-border px-5 py-2.5 text-[13px] font-medium text-ink hover:border-paddy hover:text-paddy"
        >
          <RotateCcw size={14} />
          Back to dashboard
        </Link>
      </div>
    </div>
  );
}
