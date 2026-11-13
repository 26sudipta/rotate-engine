import { FlaskConical, Satellite } from "lucide-react";

export default function DataSourceBadge({ source = "demo", className = "" }) {
  const isLive = source === "live";
  const isEngine = source === "engine";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-medium ${
        isLive
          ? "border-water/30 bg-water-soft text-water"
          : "border-clay/30 bg-clay-soft text-clay"
      } ${className}`}
    >
      {isLive ? <Satellite size={12} /> : <FlaskConical size={12} />}
      {isLive
        ? "Data source: NASA Earth Observation API"
        : isEngine
          ? "Data source: ROTATE Python engine snapshot"
          : "Data source: Demonstration dataset"}
    </span>
  );
}
