export default function ClimateCard({ icon: Icon, label, value, unit, tint = "paddy" }) {
  const tints = {
    paddy: "bg-crop-soft text-paddy",
    water: "bg-water-soft text-water",
    clay: "bg-clay-soft text-clay",
  };

  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2.5">
        <span className={`flex h-8 w-8 items-center justify-center rounded-md ${tints[tint]}`}>
          <Icon size={16} strokeWidth={2} />
        </span>
        <span className="text-[13px] text-ink-soft">{label}</span>
      </div>
      <div className="mt-3 flex items-baseline gap-1 font-mono">
        <span className="text-[26px] font-semibold leading-none text-ink">{value}</span>
        <span className="text-[13px] text-ink-soft">{unit}</span>
      </div>
    </div>
  );
}
