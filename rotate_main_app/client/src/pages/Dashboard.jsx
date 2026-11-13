import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, ArrowRight } from "lucide-react";
import MapPanel from "../components/MapPanel.jsx";
import ClimateOverview from "../components/ClimateOverview.jsx";
import LoadingState from "../components/LoadingState.jsx";
import { useApp } from "../context/AppContext.jsx";
import { getCurrentConditions } from "../data/mockClimate.js";
import { api } from "../services/api.js";

// Page background: a light-but-deep sage → green gradient, clearly darker than the
// cream map and white cards so the map stays the focal point. Tweak the stops here.
const PAGE_BACKGROUND = `
  radial-gradient(900px 480px at 8% 0%, rgba(255, 255, 255, 0.45), transparent 60%),
  radial-gradient(700px 420px at 100% 100%, rgba(15, 65, 32, 0.22), transparent 65%),
  linear-gradient(135deg, #D3E7D3 0%, #A9CFB0 48%, #78AE8B 100%)
`;

export default function Dashboard() {
  const { selectedLocationId, setSelectedLocationId, selectedLocation, analysisStatus, setAnalysisStatus } = useApp();
  const [climate, setClimate] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;
    let timer;
    setAnalysisStatus("analyzing");
    setClimate(null);

    api
      .getClimate(selectedLocationId)
      .catch(() => getCurrentConditions(selectedLocationId))
      .then((data) => {
        if (cancelled) return;
        // Short delay so the "Analyzing current conditions..." state is visible.
        timer = setTimeout(() => {
          setClimate(data);
          setAnalysisStatus("ready");
        }, 1100);
      });

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [selectedLocationId, setAnalysisStatus]);

  return (
    // -mb-24 lets the gradient run underneath the footer's torn edge (no white gap).
    <div className="-mb-24 pb-28" style={{ background: PAGE_BACKGROUND }}>
      <div className="mx-auto max-w-[1400px] px-6 py-10">
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-[1.6fr_1fr]">
          {/* Map: white frame + shadow lifts it off the green background */}
          <div className="h-[560px] rounded-[28px] bg-white p-1.5 shadow-[0_18px_40px_-18px_rgba(11,51,24,0.55)]">
            <MapPanel selectedLocationId={selectedLocationId} onSelectLocation={setSelectedLocationId} />
          </div>

          <div className="flex flex-col gap-5">
            <div className="rounded-[24px] border border-white/60 bg-white p-5 shadow-[0_14px_32px_-18px_rgba(11,51,24,0.5)]">
              <p className="text-[12px] font-medium text-ink-soft">Selected Location</p>
              <h2 className="mt-1 font-display text-[19px] font-semibold text-ink">
                {selectedLocation.name}, Bangladesh
              </h2>
              <p className="text-[13px] text-ink-soft">
                {selectedLocation.farmName} · {selectedLocation.soilType}
              </p>

              <div className="mt-4 h-px bg-border" />

              <div className="mt-4 min-h-[24px]">
                <AnimatePresence mode="wait">
                  {analysisStatus === "analyzing" ? (
                    <LoadingState key="loading" label="Analyzing current conditions..." />
                  ) : (
                    <motion.div
                      key="ready"
                      initial={{ opacity: 0, y: 4 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex items-center gap-2 text-[13px] font-medium text-paddy"
                    >
                      <CheckCircle2 size={15} />
                      Analysis ready
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              <button
                type="button"
                onClick={() => navigate(`/farm/${selectedLocation.id}`)}
                disabled={analysisStatus !== "ready"}
                className="mt-4 flex w-full items-center justify-center gap-2 rounded-full bg-paddy py-2.5 text-[13px] font-semibold text-white transition-colors hover:bg-paddy-light disabled:cursor-not-allowed disabled:opacity-50"
              >
                View farm analysis
                <ArrowRight size={14} />
              </button>
            </div>

            <ClimateOverview climate={climate} loading={analysisStatus === "analyzing"} />
          </div>
        </div>
      </div>
    </div>
  );
}
