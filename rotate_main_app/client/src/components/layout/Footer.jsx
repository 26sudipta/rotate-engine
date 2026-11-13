import { Link } from "react-router-dom";
import { FlaskConical } from "lucide-react";
import { LogoMark, TornEdge, WindmillArt } from "../ui/Ornaments.jsx";

const platform = [
  ["/dashboard", "Dashboard"],
  ["/historical", "Historical Analog"],
  ["/strategies", "Strategies"],
  ["/scenario", "What If?"],
  ["/results", "Results"],
];
const resources = [
  ["/crops", "Crop Library"],
  ["/methodology", "Methodology"],
  ["/methodology#faq", "FAQ"],
  ["/contact", "Contact"],
];

export default function Footer({ flush = false }) {
  return (
    <footer className={`relative bg-forest-deep text-white ${flush ? "" : "mt-24"}`}>
      <TornEdge position="top" className="text-forest-deep" />
      <WindmillArt className="pointer-events-none absolute right-6 top-6 hidden h-[280px] text-white/[0.07] lg:block" />
      <div className="relative mx-auto grid max-w-[1280px] gap-10 px-6 pb-10 pt-16 md:grid-cols-2 lg:grid-cols-[1.4fr_0.8fr_0.8fr_1.2fr]">
        <div>
          <div className="flex items-center gap-2.5">
            <LogoMark />
            <span className="font-display text-[26px] font-bold leading-none">ROTATE</span>
          </div>
          <p className="mt-4 max-w-sm text-[14.5px] leading-relaxed text-white/75">
            A decision-support prototype connecting climate observations, historical analogs, crop-rotation characteristics and scenario analysis for Bangladesh farmland.
          </p>
        </div>
        <div>
          <h4 className="font-display text-[16px] font-bold">Platform</h4>
          <ul className="mt-4 space-y-2.5 text-[14.5px] text-white/75">
            {platform.map(([to, label]) => (
              <li key={to}><Link to={to} className="transition-colors hover:text-sun">{label}</Link></li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="font-display text-[16px] font-bold">Resources</h4>
          <ul className="mt-4 space-y-2.5 text-[14.5px] text-white/75">
            {resources.map(([to, label]) => (
              <li key={to}><Link to={to} className="transition-colors hover:text-sun">{label}</Link></li>
            ))}
          </ul>
        </div>
        <div className="card-dashed card-dashed-light rounded-[26px] bg-white/[0.06] p-6">
          <div className="flex items-center gap-2 text-sun"><FlaskConical size={17} /><span className="font-script text-[22px] leading-none">Prototype notice</span></div>
          <p className="mt-3 text-[13.5px] leading-relaxed text-white/75">
            Values labelled “Demonstration dataset” are illustrative. They are not NASA measurements or validated crop recommendations.
          </p>
        </div>
      </div>
      <div className="relative border-t border-white/10">
        <div className="mx-auto flex max-w-[1280px] flex-col items-center justify-between gap-2 px-6 py-5 text-[13px] text-white/60 sm:flex-row">
          <span>© 2026 ROTATE · Built for the NASA Space Apps Challenge</span>
          <span>Not affiliated with or endorsed by NASA</span>
        </div>
      </div>
    </footer>
  );
}
