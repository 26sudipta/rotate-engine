import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { MapPin, Radio, CircleUserRound, Menu, X, LayoutDashboard } from "lucide-react";
import { useApp } from "../../context/AppContext.jsx";
import { LogoMark } from "../ui/Ornaments.jsx";
import PillButton from "../ui/PillButton.jsx";

const navItems = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/historical", label: "Historical Analog" },
  { to: "/strategies", label: "Strategies" },
  { to: "/scenario", label: "What If?" },
  { to: "/crops", label: "Crop Library" },
  { to: "/methodology", label: "Methodology" },
  { to: "/contact", label: "Contact" },
];

export default function Header() {
  const { selectedLocation } = useApp();
  const [open, setOpen] = useState(false);

  const linkClass = ({ isActive }) =>
    `relative whitespace-nowrap px-2.5 py-2 text-[14px] font-semibold transition-colors ${
      isActive ? "text-forest" : "text-ink/80 hover:text-forest"
    } ${isActive ? "after:absolute after:inset-x-2.5 after:-bottom-0.5 after:h-[3px] after:rounded-full after:bg-sun" : ""}`;

  return (
    <header className="sticky top-0 z-50">
      <div className="bg-forest-deep text-white">
        <div className="mx-auto flex h-9 max-w-[1280px] items-center justify-between px-6 text-[12.5px]">
          <span className="hidden text-white/80 sm:block">Explore historical climate analogs for Bangladesh farms</span>
          <div className="ml-auto flex items-center gap-4 sm:gap-5">
            <span className="flex items-center gap-1.5"><MapPin size={13} className="text-sun" />{selectedLocation.name}</span>
            <span className="flex items-center gap-1.5"><Radio size={13} className="text-sun" />Engine output</span>
          </div>
        </div>
      </div>

      <div className="border-b border-border/70 bg-white/95 backdrop-blur">
        <div className="mx-auto flex h-[76px] max-w-[1280px] items-center justify-between px-6">
          <Link to="/" className="flex items-center gap-2.5" onClick={() => setOpen(false)}>
            <LogoMark />
            <span>
              <span className="block font-display text-[24px] font-bold leading-none tracking-tight text-forest">ROTATE</span>
              <span className="mt-1 hidden text-[10.5px] leading-none text-ink-soft sm:block">Climate-resilient crop rotation intelligence</span>
            </span>
          </Link>

          <nav className="hidden items-center gap-0.5 xl:flex">
            {navItems.map((item) => (
              <NavLink key={item.to} to={item.to} className={linkClass}>{item.label}</NavLink>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            <div className="hidden md:block"><PillButton to="/dashboard" icon={LayoutDashboard}>Open Dashboard</PillButton></div>
            <button type="button" aria-label="Profile and settings" className="flex h-10 w-10 items-center justify-center rounded-full border border-border text-ink-soft transition-colors hover:border-forest hover:text-forest">
              <CircleUserRound size={20} />
            </button>
            <button type="button" aria-label="Toggle menu" onClick={() => setOpen((v) => !v)} className="flex h-10 w-10 items-center justify-center rounded-full bg-cream text-forest xl:hidden">
              {open ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {open && (
          <nav className="border-t border-border/70 bg-white px-6 py-3 xl:hidden">
            <div className="mx-auto flex max-w-[1280px] flex-col">
              {navItems.map((item) => (
                <NavLink key={item.to} to={item.to} onClick={() => setOpen(false)} className={({ isActive }) => `rounded-lg px-3 py-2.5 text-[15px] font-semibold ${isActive ? "bg-crop-soft text-forest" : "text-ink"}`}>
                  {item.label}
                </NavLink>
              ))}
            </div>
          </nav>
        )}
      </div>
    </header>
  );
}
