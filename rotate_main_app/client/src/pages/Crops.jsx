import { useEffect, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, FlaskConical, TriangleAlert, SearchX } from "lucide-react";
import { api } from "../services/api.js";

const roles = ["All", "Cereal", "Legume", "Oilseed", "Fiber"];

function Meter({ label, value }) {
  return (
    <div>
      <div className="flex justify-between text-[12px] text-ink-soft"><span>{label}</span><span className="font-mono">{value}</span></div>
      <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-white"><div className="h-full rounded-full bg-forest" style={{ width: `${value}%` }} /></div>
    </div>
  );
}

export default function Crops() {
  const [crops, setCrops] = useState(null);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [role, setRole] = useState("All");

  useEffect(() => {
    api.getCrops().then(setCrops).catch((e) => setError(e.message));
  }, []);

  const filtered = useMemo(() => {
    if (!crops) return [];
    return crops.filter(
      (c) =>
        (role === "All" || c.role === role) &&
        `${c.name} ${c.localName} ${c.season}`.toLowerCase().includes(query.toLowerCase())
    );
  }, [crops, query, role]);

  return (
    <div className="mx-auto max-w-[1240px] px-6 py-14">
      <div className="flex items-start gap-3 rounded-2xl border border-clay/30 bg-clay-soft p-4 text-[13.5px] text-ink">
        <FlaskConical size={18} className="mt-0.5 shrink-0 text-clay" />
        <p>Crop profiles are illustrative placeholders for the prototype, not validated agronomic data. They exist so real crop-rotation information can replace them without changing the interface.</p>
      </div>

      <div className="mt-8 flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap gap-2">
          {roles.map((r) => (
            <button key={r} type="button" onClick={() => setRole(r)} className={`rounded-full px-4 py-2 text-[13.5px] font-semibold transition-colors ${role === r ? "bg-forest text-white" : "bg-cream text-ink hover:bg-[#E6E2D8]"}`}>{r}</button>
          ))}
        </div>
        <div className="relative w-full sm:w-[300px]">
          <Search size={16} className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-ink-soft" />
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search crops or seasons..." className="w-full rounded-full border border-border bg-white py-2.5 pl-10 pr-4 text-[14px] focus:border-forest focus:outline-none focus:ring-2 focus:ring-forest/20" />
        </div>
      </div>

      {error && (
        <div className="mt-10 flex items-center gap-3 rounded-2xl border border-alert/30 bg-red-50 p-5 text-[14px] text-alert"><TriangleAlert size={18} />Couldn't load crops: {error}. Make sure the API server is running.</div>
      )}

      {!crops && !error && (
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {[0, 1, 2, 3, 4, 5].map((i) => <div key={i} className="h-[250px] animate-pulse rounded-[26px] bg-cream" />)}
        </div>
      )}

      {crops && filtered.length === 0 && (
        <div className="mt-14 flex flex-col items-center text-center text-ink-soft"><SearchX size={34} /><p className="mt-3 font-display text-[17px] font-bold text-ink">No crops match your filters</p><p className="text-[14px]">Try a different search term or role.</p></div>
      )}

      <motion.div layout className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <AnimatePresence>
          {filtered.map((c) => (
            <motion.article layout key={c.id} initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }} className="card-dashed rounded-[26px] bg-cream p-7">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-display text-[20px] font-bold text-ink">{c.name}</h3>
                  <p className="text-[14px] text-ink-soft">{c.localName}</p>
                </div>
                <span className="rounded-full bg-sun px-3 py-1 text-[12px] font-bold text-forest">{c.role}</span>
              </div>
              <p className="mt-3 text-[13.5px] leading-relaxed text-ink-soft">{c.summary}</p>
              <p className="mt-3 text-[12.5px] font-semibold text-leaf-dark">Season: {c.season}</p>
              <div className="mt-4 space-y-2.5">
                <Meter label="Water need" value={c.waterNeed} />
                <Meter label="Salinity tolerance" value={c.salinityTolerance} />
                <Meter label="Soil benefit" value={c.soilBenefit} />
              </div>
            </motion.article>
          ))}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
