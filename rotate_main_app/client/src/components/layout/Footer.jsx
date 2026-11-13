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
            ROTATE helps farmers and local experts explore crop-rotation options using cached NASA observations, local information and cited crop rules.
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
        <div className="flex items-center gap-2 text-sun"><FlaskConical size={17} /><span className="font-script text-[22px] leading-none">Use with local expertise</span></div>
          <p className="mt-3 text-[13.5px] leading-relaxed text-white/75">
          ROTATE compares historical examples; it does not forecast the season or replace agricultural advice. Every card needs local review.
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
