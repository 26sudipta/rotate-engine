import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import HistoricalTimeline from "../components/HistoricalTimeline.jsx";
import ComparisonChart from "../components/ComparisonChart.jsx";
import DataSourceBadge from "../components/DataSourceBadge.jsx";
import { useApp } from "../context/AppContext.jsx";
import { getHistoricalSeries } from "../data/mockHistorical.js";
import { getCurrentConditions } from "../data/mockClimate.js";
import { api } from "../services/api.js";

export default function HistoricalAnalog() {
  const { selectedLocationId, selectedLocation } = useApp();
  const [historical, setHistorical] = useState(null);
  const [current, setCurrent] = useState(null);

  useEffect(() => {
    api.getHistorical(selectedLocationId).catch(() => getHistoricalSeries(selectedLocationId)).then(setHistorical);
    api.getClimate(selectedLocationId).catch(() => getCurrentConditions(selectedLocationId)).then(setCurrent);
  }, [selectedLocationId]);

  if (!historical || !current) {
    return <div className="mx-auto max-w-[1200px] px-6 py-16 text-[13px] text-ink-soft">Loading historical record...</div>;
  }

  const chartData = historical.series.map((row) => ({
    year: row.year,
    historicalPrecipitation: row.precipitationMm,
    historicalTemperature: row.temperatureC,
    historicalSoilMoisture: row.soilMoisturePct,
    currentPrecipitation: current.precipitationMm,
    currentTemperature: current.temperatureC,
    currentSoilMoisture: current.soilMoisturePct,
  }));

  return (
    <div className="mx-auto max-w-[1200px] px-6 py-8">
      <div className="flex justify-end">
        <DataSourceBadge source="demo" />
      </div>

      <div className="mt-6">
        <HistoricalTimeline series={historical.series} analogYear={historical.closestAnalogYear} />
      </div>

      <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="rounded-lg border border-border bg-surface-raised p-4 text-center">
          <p className="text-[12px] font-medium text-ink-soft">Current Conditions</p>
          <p className="mt-1 font-mono text-[13px] text-ink">
            {current.precipitationMm} mm · {current.temperatureC}°C · {current.soilMoisturePct}% moisture
          </p>
        </div>
        <div className="rounded-lg border border-clay/30 bg-clay-soft p-4 text-center">
          <p className="text-[12px] font-medium text-clay">Closest Climate Analog — {historical.closestAnalogYear}</p>
          <p className="mt-1 font-mono text-[13px] text-ink">
            {historical.closestAnalog.precipitationMm} mm · {historical.closestAnalog.temperatureC}°C ·{" "}
            {historical.closestAnalog.soilMoisturePct}% moisture
          </p>
          <p className="mt-1 text-[11px] text-clay">Demonstration result</p>
        </div>
      </div>

      <div className="mt-5 grid grid-cols-1 gap-5 lg:grid-cols-3">
        <ComparisonChart
          title="Precipitation"
          data={chartData}
          xKey="year"
          unit="mm"
          seriesA={{ key: "currentPrecipitation", name: "Current" }}
          seriesB={{ key: "historicalPrecipitation", name: "Historical" }}
        />
        <ComparisonChart
          title="Temperature"
          data={chartData}
          xKey="year"
          unit="°C"
          seriesA={{ key: "currentTemperature", name: "Current" }}
          seriesB={{ key: "historicalTemperature", name: "Historical" }}
        />
        <ComparisonChart
          title="Soil Moisture"
          data={chartData}
          xKey="year"
          unit="%"
          seriesA={{ key: "currentSoilMoisture", name: "Current" }}
          seriesB={{ key: "historicalSoilMoisture", name: "Historical" }}
        />
      </div>

      <Link
        to="/strategies"
        className="mt-6 inline-flex items-center gap-2 rounded-md bg-paddy px-5 py-2.5 text-[13px] font-medium text-white hover:bg-paddy-light"
      >
        Explore crop rotation strategies
        <ArrowRight size={14} />
      </Link>
    </div>
  );
}
