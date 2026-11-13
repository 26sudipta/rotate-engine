import { useMemo } from "react";

export default function HistoricalTimeline({ series, analogYear }) {
  const { minYear, maxYear } = useMemo(() => {
    if (!series?.length) return { minYear: 1986, maxYear: 2025 };
    return { minYear: series[0].year, maxYear: series[series.length - 1].year };
  }, [series]);

  const analogPct = ((analogYear - minYear) / (maxYear - minYear)) * 100;

  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <div className="mb-1 flex items-center justify-between text-[12px] text-ink-soft">
        <span>{minYear}</span>
        <span>{maxYear - minYear + 1}-year contextual timeline</span>
        <span>{maxYear}</span>
      </div>
      <div className="relative h-2 rounded-full bg-canvas">
        <div className="absolute inset-0 rounded-full bg-gradient-to-r from-water/25 via-paddy/25 to-clay/25" />
        <div
          className="absolute top-1/2 h-4 w-4 -translate-y-1/2 -translate-x-1/2 rounded-full border-2 border-surface bg-clay shadow"
          style={{ left: `${analogPct}%` }}
          title={`Closest analog: ${analogYear}`}
        />
      </div>
      <p className="mt-2 text-[12px] text-ink-soft">
        This contextual chart is separate from the engine's five-year analog output shown above.
      </p>
    </div>
  );
}
