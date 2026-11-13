const labels = {
  waterConservation: "Water Conservation",
  soilRecovery: "Soil Recovery",
  salinityResilience: "Salinity Resilience",
  yieldStability: "Yield Stability",
};

export default function PrioritySlider({ priorities, onChange }) {
  const handleChange = (key, value) => {
    onChange({ ...priorities, [key]: Number(value) });
  };

  return (
    <div className="rounded-[24px] border border-border bg-surface-raised p-5">
      <h3 className="font-display text-[16px] font-semibold text-ink">What matters most?</h3>
      <p className="mt-1 text-[12px] text-ink-soft">
        Adjust the weight given to each priority. Strategy rankings update as you drag.
      </p>

      <div className="mt-4 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {Object.entries(labels).map(([key, label]) => (
          <div key={key}>
            <div className="mb-1.5 flex items-center justify-between text-[12px]">
              <span className="text-ink">{label}</span>
              <span className="font-mono text-ink-soft">{priorities[key]}</span>
            </div>
            <input
              type="range"
              min={0}
              max={100}
              step={1}
              value={priorities[key]}
              onChange={(e) => handleChange(key, e.target.value)}
              className="w-full accent-paddy"
              aria-label={label}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
