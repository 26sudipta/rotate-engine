import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowRight, MapPin } from "lucide-react";
import ClimateOverview from "../components/ClimateOverview.jsx";
import DataSourceBadge from "../components/DataSourceBadge.jsx";
import { useApp } from "../context/AppContext.jsx";
import { locations, findLocationById } from "../data/mockLocations.js";
import { getCurrentConditions } from "../data/mockClimate.js";
import { api } from "../services/api.js";

export default function FarmAnalysis() {
  const { id } = useParams();
  const { setSelectedLocationId } = useApp();
  const [climate, setClimate] = useState(null);
  const location = findLocationById(id) || locations[0];

  useEffect(() => {
    setSelectedLocationId(location.id);
    api.getClimate(location.id).catch(() => getCurrentConditions(location.id)).then(setClimate);
  }, [location.id, setSelectedLocationId]);

  return (
    <div className="mx-auto max-w-[1000px] px-6 py-8">
      <div className="flex items-center gap-1.5 text-[12px] text-ink-soft">
        <MapPin size={13} />
        <span>{location.region}</span>
      </div>
      <h1 className="mt-1 font-display text-[26px] font-semibold text-ink">{location.farmName}</h1>
      <p className="mt-1 text-[14px] text-ink-soft">
        {location.name}, Bangladesh · {location.soilType}
      </p>

      <div className="mt-6 grid grid-cols-1 gap-5 lg:grid-cols-[1fr_1fr]">
        <ClimateOverview climate={climate} loading={!climate} />

        <div className="rounded-[24px] border border-border bg-surface-raised p-5">
          <div className="flex items-center justify-between">
            <h3 className="font-display text-[16px] font-semibold text-ink">Plot summary</h3>
            <DataSourceBadge source="context" />
          </div>
          <dl className="mt-4 space-y-3 text-[13px]">
            <div className="flex justify-between border-b border-border/70 pb-3">
              <dt className="text-ink-soft">Farm ID</dt>
              <dd className="font-mono text-ink">farm-{location.id.slice(0, 6)}</dd>
            </div>
            <div className="flex justify-between border-b border-border/70 pb-3">
              <dt className="text-ink-soft">Soil type</dt>
              <dd className="text-ink">{location.soilType}</dd>
            </div>
            <div className="flex justify-between border-b border-border/70 pb-3">
              <dt className="text-ink-soft">Coordinates</dt>
              <dd className="font-mono text-ink">{location.lat.toFixed(2)}, {location.lng.toFixed(2)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-ink-soft">Analysis status</dt>
              <dd className="text-paddy">Ready</dd>
            </div>
          </dl>

          <Link
            to="/historical"
            className="mt-5 flex w-full items-center justify-center gap-2 rounded-md bg-paddy py-2.5 text-[13px] font-medium text-white hover:bg-paddy-light"
          >
            Compare against historical analog
            <ArrowRight size={14} />
          </Link>
        </div>
      </div>
    </div>
  );
}
