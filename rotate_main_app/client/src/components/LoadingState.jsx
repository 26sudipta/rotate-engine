import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";

export default function LoadingState({ label = "Loading..." }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex items-center gap-2.5 text-[13px] text-ink-soft"
    >
      <Loader2 size={15} className="animate-spin text-paddy" />
      <span>{label}</span>
    </motion.div>
  );
}
