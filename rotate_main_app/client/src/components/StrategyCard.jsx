import { motion } from "framer-motion";
import { ArrowRight, Droplets, Sprout, Beaker, TrendingUp } from "lucide-react";

const indicatorMeta = [
  { key: "waterDemand", label: "Water demand", icon: Droplets, invert: false },
  { key: "soilRecovery", label: "Soil recovery", icon: Sprout, invert: false },
  { key: "salinityResilience", label: "Salinity resilience", icon: Beaker, invert: false },
  { key: "yieldStability", label: "Yield stability", icon: TrendingUp, invert: false },
];

export default function StrategyCard({ strategy, rank, isSelected, onSelect }) {
  return (
    <motion.div
      layout
      layoutId={strategy.id}
      transition={{ type: "spring", stiffness: 260, damping: 28 }}
      className={`rounded-[24px] border bg-surface p-5 ${
        isSelected ? "border-paddy ring-1 ring-paddy/30" : "border-border"
      }`}
    >
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-canvas text-[11px] font-semibold text-ink-soft">
              {rank}
            </span>
            <h3 className="font-display text-[16px] font-semibold text-ink">{strategy.name}</h3>
          </div>
          <p className="mt-0.5 text-[12px] text-ink-soft">{strategy.label}</p>
        </div>
        {typeof strategy.matchScore === "number" && (
          <span className="rounded-full bg-crop-soft px-2.5 py-1 font-mono text-[12px] font-semibold text-paddy">
            {strategy.matchScore.toFixed(0)}
          </span>
        )}
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-1.5 text-[12px] text-ink">
        {strategy.sequence.map((crop, i) => (
          <span key={crop} className="flex items-center gap-1.5">
            <span className="rounded-md border border-border bg-canvas px-2 py-1">{crop}</span>
            {i < strategy.sequence.length - 1 && <ArrowRight size={12} className="text-ink-soft" />}
          </span>
        ))}
      </div>

      <div className="mt-4 space-y-2.5">
        {indicatorMeta.map(({ key, label, icon: Icon }) => (
          <div key={key} className="flex items-center gap-2.5">
            <Icon size={13} className="shrink-0 text-ink-soft" />
            <span className="w-[124px] shrink-0 text-[11px] text-ink-soft">{label}</span>
            <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-canvas">
              <motion.div
                className="h-full rounded-full bg-paddy"
                initial={false}
                animate={{ width: `${strategy.indicators[key]}%` }}
                transition={{ duration: 0.4 }}
              />
            </div>
            <span className="w-7 shrink-0 text-right font-mono text-[11px] text-ink-soft">
              {strategy.indicators[key]}
            </span>
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={() => onSelect(strategy.id)}
        className={`mt-4 w-full rounded-md py-2 text-[13px] font-medium transition-colors ${
          isSelected
            ? "bg-paddy text-white"
            : "border border-border text-ink hover:border-paddy hover:text-paddy"
        }`}
      >
        {isSelected ? "Selected for exploration" : "View details"}
      </button>
    </motion.div>
  );
}
