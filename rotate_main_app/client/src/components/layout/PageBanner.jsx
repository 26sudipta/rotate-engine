import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import { GrassEdge, WindmillArt } from "../ui/Ornaments.jsx";

export default function PageBanner({ title, subtitle, crumbs = [] }) {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-forest-deep via-forest to-forest-mid text-white">
      <svg aria-hidden viewBox="0 0 1440 220" preserveAspectRatio="none" className="absolute inset-x-0 bottom-0 h-[70%] w-full">
        <path d="M0 160 C 220 110, 420 190, 700 140 C 960 95, 1180 170, 1440 120 V220 H0 Z" fill="#fff" opacity="0.05" />
        <path d="M0 190 C 260 150, 520 210, 800 170 C 1060 135, 1260 200, 1440 160 V220 H0 Z" fill="#fff" opacity="0.06" />
      </svg>
      <WindmillArt className="pointer-events-none absolute -right-4 top-2 hidden h-[250px] text-white/10 md:block" />
      <div className="relative mx-auto max-w-[1280px] px-6 pb-16 pt-12">
        <h1 className="font-script text-[52px] uppercase leading-[0.95] tracking-wide md:text-[68px]">{title}</h1>
        {subtitle && <p className="mt-3 max-w-2xl text-[15.5px] text-white/85">{subtitle}</p>}
        <nav aria-label="Breadcrumb" className="mt-5 flex items-center gap-1.5 text-[13px] text-white/70">
          <Link to="/" className="hover:text-sun">Home</Link>
          {crumbs.map((c) => (
            <span key={c} className="flex items-center gap-1.5"><ChevronRight size={13} />{c}</span>
          ))}
        </nav>
      </div>
      <div className="absolute inset-x-0 bottom-0 text-white"><GrassEdge /></div>
    </section>
  );
}
