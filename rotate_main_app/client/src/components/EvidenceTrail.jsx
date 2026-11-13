import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Satellite, LineChart, Sprout, FlaskConical } from "lucide-react";

const steps = [
  {
    icon: Satellite,
    title: "NASA Earth Observations",
    body:
      "Structured to accept precipitation, temperature, soil moisture, and salinity signals from NASA Earth Observation sources. This prototype uses demonstration values in their place.",
  },
  {
    icon: LineChart,
    title: "Climate Pattern Analysis",
    body:
      "Current conditions are compared against a historical timeline to identify the closest climate analog year, giving context for how conditions have shifted.",
  },
  {
    icon: Sprout,
    title: "Crop & Rotation Characteristics",
    body:
      "Each candidate rotation carries indicator scores for water demand, soil recovery, salinity resilience, and yield stability, based on example agronomic profiles.",
  },
  {
    icon: FlaskConical,
    title: "Scenario Result",
    body:
      "A deterministic prototype formula combines climate signals, crop characteristics, and stated priorities into a single suitability score for the current scenario.",
  },
];

export default function EvidenceTrail() {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded-[24px] border border-border bg-surface">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-5 py-4 text-left"
      >
        <span className="font-display text-[15px] font-semibold text-ink">Why this strategy?</span>
        <motion.span animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }}>
          <ChevronDown size={17} className="text-ink-soft" />
        </motion.span>
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="space-y-0 px-5 pb-5">
              {steps.map((step, i) => (
                <div key={step.title} className="flex gap-3.5">
                  <div className="flex flex-col items-center">
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-border bg-canvas text-paddy">
                      <step.icon size={14} />
                    </span>
                    {i < steps.length - 1 && <span className="my-1 w-px flex-1 bg-border" />}
                  </div>
                  <div className="pb-6">
                    <h4 className="text-[13px] font-semibold text-ink">{step.title}</h4>
                    <p className="mt-1 text-[12px] leading-relaxed text-ink-soft">{step.body}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
