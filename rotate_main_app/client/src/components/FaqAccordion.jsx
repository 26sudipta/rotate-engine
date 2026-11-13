import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus } from "lucide-react";

export default function FaqAccordion({ items }) {
  const [openIndex, setOpenIndex] = useState(0);

  return (
    <div className="space-y-3">
      {items.map((item, i) => {
        const open = openIndex === i;
        return (
          <div key={item.q} className={`overflow-hidden rounded-2xl border transition-colors ${open ? "border-forest bg-forest text-white" : "border-border bg-white text-ink"}`}>
            <button
              type="button"
              aria-expanded={open}
              onClick={() => setOpenIndex(open ? -1 : i)}
              className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left font-display text-[15.5px] font-semibold"
            >
              {item.q}
              <motion.span animate={{ rotate: open ? 45 : 0 }} className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full ${open ? "bg-sun text-forest" : "bg-cream text-forest"}`}>
                <Plus size={15} strokeWidth={2.6} />
              </motion.span>
            </button>
            <AnimatePresence initial={false}>
              {open && (
                <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.2 }} className="overflow-hidden">
                  <p className="px-5 pb-5 text-[14.5px] leading-relaxed text-white/85">{item.a}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        );
      })}
    </div>
  );
}
