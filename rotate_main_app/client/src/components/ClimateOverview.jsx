import { CloudRain, Thermometer, Droplets, Beaker } from "lucide-react";
import ClimateCard from "./ClimateCard.jsx";
import DataSourceBadge from "./DataSourceBadge.jsx";

export default function ClimateOverview({ climate, loading }) {
  return (
    <div className="rounded-[24px] border border-border bg-surface-raised p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-display text-[17px] font-semibold text-ink">Current Conditions</h3>
        <DataSourceBadge source="context" />
      </div>

      {loading || !climate ? (
        <div className="grid grid-cols-2 gap-3">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="h-[92px] animate-pulse rounded-lg border border-border bg-canvas" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          <ClimateCard icon={CloudRain} label="Precipitation" value={climate.precipitationMm} unit="mm/day" tint="water" />
          <ClimateCard icon={Thermometer} label="Temperature" value={climate.temperatureC} unit="°C" tint="clay" />
          <ClimateCard icon={Droplets} label="Soil Moisture" value={climate.soilMoisturePct} unit="%" tint="paddy" />
          <ClimateCard icon={Beaker} label="Soil Salinity" value={climate.soilSalinityDsm} unit="dS/m" tint="clay" />
        </div>
      )}

      <p className="mt-4 text-[12px] leading-relaxed text-ink-soft">
        POWER values are cached reanalysis/model output, not field measurements. The engine's
        decision window and analog evidence are shown on the Historical Analog page.
      </p>
    </div>
  );
}
