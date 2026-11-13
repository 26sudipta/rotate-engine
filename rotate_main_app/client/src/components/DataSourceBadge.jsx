import { FlaskConical, Satellite } from "lucide-react";

export default function DataSourceBadge({ source = "engine", className = "" }) {
  const isLive = source === "live";
  const isEngine = source === "engine";
  const isContext = source === "context";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-medium ${
        isLive
          ? "border-water/30 bg-water-soft text-water"
          : isEngine
            ? "border-paddy/30 bg-crop-soft text-paddy"
            : "border-clay/30 bg-clay-soft text-clay"
      } ${className}`}
    >
      {isLive ? <Satellite size={12} /> : <FlaskConical size={12} />}
      {isLive
        ? "Data source: NASA Earth Observation API"
        : isEngine
          ? "Source: ROTATE engine output"
          : isContext
            ? "Source: contextual display"
          : "Data source: Demonstration dataset"}
    </span>
  );
}
