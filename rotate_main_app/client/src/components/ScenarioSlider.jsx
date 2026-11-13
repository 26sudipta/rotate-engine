export default function ScenarioSlider({ icon: Icon, label, value, min, max, onChange, tint = "water" }) {
  const tints = {
    water: "accent-water text-water",
    clay: "accent-clay text-clay",
  };

  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-[13px] font-medium text-ink">
          <Icon size={15} className={tints[tint].split(" ")[1]} />
          {label}
        </div>
        <span className={`font-mono text-[14px] font-semibold ${tints[tint].split(" ")[1]}`}>
          {value > 0 ? "+" : ""}
          {value}%
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={1}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className={`mt-3 w-full ${tints[tint].split(" ")[0]}`}
        aria-label={label}
      />
      <div className="mt-1 flex justify-between text-[11px] text-ink-soft">
        <span>{min}%</span>
        <span>Current → baseline</span>
        <span>{max > 0 ? "+" : ""}{max}%</span>
      </div>
    </div>
  );
}
