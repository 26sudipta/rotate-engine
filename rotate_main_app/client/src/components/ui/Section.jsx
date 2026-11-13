import { motion } from "framer-motion";
import { WheatEar } from "./Ornaments.jsx";

export function Eyebrow({ children, light = false, center = false }) {
  return (
    <div className={`flex items-center gap-3 ${center ? "justify-center" : ""}`}>
      <WheatEar className="text-sun" />
      <span className={`font-script text-[24px] leading-none ${light ? "text-sun" : "text-leaf-dark"}`}>{children}</span>
    </div>
  );
}

export function SectionHeading({ eyebrow, title, children, center = false, light = false, className = "" }) {
  return (
    <div className={`${center ? "mx-auto text-center" : ""} max-w-[760px] ${className}`}>
      {eyebrow && <Eyebrow light={light} center={center}>{eyebrow}</Eyebrow>}
      <h2 className={`mt-3 font-display text-[34px] font-bold leading-[1.12] tracking-tight md:text-[42px] ${light ? "text-white" : "text-ink"}`}>
        {title}
      </h2>
      {children && (
        <p className={`mt-4 text-[16px] leading-relaxed ${light ? "text-white/85" : "text-ink-soft"}`}>{children}</p>
      )}
    </div>
  );
}

/** Subtle fade-up on first scroll into view. */
export function Reveal({ children, delay = 0, className = "" }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.45, delay }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

export function IconTile({ icon: Icon, size = 72 }) {
  return (
    <span
      className="flex items-center justify-center rounded-[22px] bg-sun text-forest"
      style={{ width: size, height: size }}
    >
      <Icon size={size * 0.42} strokeWidth={2.1} />
    </span>
  );
}

export function CheckItem({ children, light = false }) {
  return (
    <li className={`flex items-center gap-2.5 text-[15px] ${light ? "text-white" : "text-ink"}`}>
      <span className="flex h-[20px] w-[20px] shrink-0 items-center justify-center rounded-full bg-leaf text-white">
        <svg viewBox="0 0 12 12" className="h-3 w-3" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M2.5 6.4 4.9 8.7 9.5 3.6" />
        </svg>
      </span>
      {children}
    </li>
  );
}
