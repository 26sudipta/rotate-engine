import { Wheat, Leaf, Bean } from "lucide-react";

const R = 150;
const nodes = [
  { angle: -90, icon: Wheat, year: "Year 1", crop: "Boro Rice" },
  { angle: 30, icon: Leaf, year: "Year 2", crop: "Jute" },
  { angle: 150, icon: Bean, year: "Year 3", crop: "Lentil" },
];

const rad = (d) => (d * Math.PI) / 180;
const pt = (angle) => [210 + R * Math.cos(rad(angle)), 210 + R * Math.sin(rad(angle))];

function arc(from, to) {
  const a1 = from + 25;
  const a2 = to - 25;
  const [x1, y1] = pt(a1);
  const [x2, y2] = pt(a2);
  const tx = -Math.sin(rad(a2));
  const ty = Math.cos(rad(a2));
  const nx = Math.cos(rad(a2));
  const ny = Math.sin(rad(a2));
  const tip = [x2 + tx * 12, y2 + ty * 12];
  const b1 = [x2 - tx * 3 + nx * 8, y2 - ty * 3 + ny * 8];
  const b2 = [x2 - tx * 3 - nx * 8, y2 - ty * 3 - ny * 8];
  return {
    d: `M${x1.toFixed(1)} ${y1.toFixed(1)} A${R} ${R} 0 0 1 ${x2.toFixed(1)} ${y2.toFixed(1)}`,
    head: `${tip.join(",")} ${b1.join(",")} ${b2.join(",")}`,
  };
}

/** Illustrates a three-year crop rotation cycle (example sequence). */
export function RotationEmblem() {
  const arcs = [arc(-90, 30), arc(30, 150), arc(150, 270)];
  return (
    <div className="relative mx-auto aspect-square w-full max-w-[430px]">
      <div className="absolute inset-[6%] rounded-full bg-[radial-gradient(circle,#FFE9A8_0%,#FFF6DC_55%,rgba(255,246,220,0)_72%)]" />
      <svg aria-hidden viewBox="0 0 420 420" className="absolute inset-0">
        <circle cx="210" cy="210" r="188" fill="none" stroke="#0F4120" strokeOpacity="0.18" strokeDasharray="3 7" />
        {arcs.map((a, i) => (
          <g key={i}>
            <path d={a.d} fill="none" stroke="#0F4120" strokeWidth="5" strokeLinecap="round" />
            <polygon points={a.head} fill="#0F4120" />
          </g>
        ))}
      </svg>
      {nodes.map(({ angle, icon: Icon, year, crop }) => {
        const left = 50 + (R / 420) * 100 * Math.cos(rad(angle));
        const top = 50 + (R / 420) * 100 * Math.sin(rad(angle));
        return (
          <div key={year} className="absolute flex -translate-x-1/2 -translate-y-1/2 flex-col items-center" style={{ left: `${left}%`, top: `${top}%` }}>
            <span className="flex h-[84px] w-[84px] items-center justify-center rounded-full border-4 border-white bg-sun text-forest shadow-md">
              <Icon size={34} strokeWidth={1.9} />
            </span>
            <span className="mt-1.5 whitespace-nowrap rounded-full bg-forest px-3 py-1 text-center text-[11.5px] font-semibold leading-tight text-white">
              {year} · {crop}
            </span>
          </div>
        );
      })}
      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
        <span className="block font-script text-[30px] leading-[0.9] text-forest">Example<br />3-year<br />rotation</span>
      </div>
    </div>
  );
}

const bales = [90, 330, 640, 905, 1180, 1370];
const trees = [30, 150, 190, 760, 1290];

/** Golden field with hay bales; the grass blades along the bottom take the colour of the next section. */
export function FieldStrip({ className = "" }) {
  return (
    <svg aria-hidden viewBox="0 0 1440 150" preserveAspectRatio="xMidYMax slice" className={className}>
      <defs>
        <linearGradient id="fieldGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#F0CF7A" />
          <stop offset="1" stopColor="#CFA040" />
        </linearGradient>
      </defs>
      <rect y="64" width="1440" height="90" fill="url(#fieldGrad)" />
      <rect y="60" width="1440" height="8" fill="#E8D8A8" opacity="0.7" />
      {trees.map((x) => (
        <g key={x} stroke="#7F8F62" strokeWidth="1.4" fill="#8FA070">
          <line x1={x} y1="64" x2={x} y2="46" />
          <circle cx={x} cy="42" r="7" stroke="none" opacity="0.8" />
        </g>
      ))}
      {bales.map((x, i) => {
        const y = 96 + (i % 2) * 6;
        const r = 22 + (i % 3) * 3;
        return (
          <g key={x}>
            <ellipse cx={x} cy={y + r * 0.9} rx={r * 1.25} ry="5" fill="#8A6420" opacity="0.25" />
            <ellipse cx={x} cy={y} rx={r * 1.15} ry={r} fill="#C9962F" />
            <ellipse cx={x} cy={y} rx={r * 0.82} ry={r * 0.72} fill="none" stroke="#A97A22" strokeWidth="1.6" />
            <ellipse cx={x} cy={y} rx={r * 0.48} ry={r * 0.42} fill="none" stroke="#A97A22" strokeWidth="1.6" />
            <ellipse cx={x} cy={y} rx={r * 0.16} ry={r * 0.14} fill="#A97A22" />
          </g>
        );
      })}
      <g className="text-cream" fill="currentColor">
        <path d={blades} />
      </g>
    </svg>
  );
}

const blades = (() => {
  let s = 5;
  const rnd = () => ((s = (s * 9301 + 49297) % 233280) / 233280);
  let d = "M0 150";
  let x = 0;
  while (x < 1440) {
    const w = 4 + rnd() * 5;
    const h = 8 + rnd() * 16;
    d += ` L${x.toFixed(1)} 150 L${(x + w / 2).toFixed(1)} ${(150 - h).toFixed(1)} L${(x + w).toFixed(1)} 150`;
    x += w;
  }
  return `${d} L1440 150 Z`;
})();

/** Converging crop rows used on the closing call-to-action panel. */
export function CropRows({ className = "" }) {
  const lines = Array.from({ length: 13 }, (_, i) => -480 + i * 80);
  return (
    <svg aria-hidden viewBox="0 0 600 440" preserveAspectRatio="xMidYMid slice" className={className}>
      <defs>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#FFE9A8" />
          <stop offset="1" stopColor="#FFF8E1" />
        </linearGradient>
        <linearGradient id="soil" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#4FAE5E" />
          <stop offset="1" stopColor="#1B6B35" />
        </linearGradient>
      </defs>
      <rect width="600" height="440" fill="url(#sky)" />
      <circle cx="430" cy="120" r="54" fill="#FBC02D" />
      <circle cx="430" cy="120" r="78" fill="#FBC02D" opacity="0.25" />
      <path d="M0 200 C120 170 220 205 330 185 C430 168 520 195 600 180 V440 H0 Z" fill="#9CCB8F" />
      <path d="M0 215 H600 V440 H0 Z" fill="url(#soil)" />
      {lines.map((x) => (
        <line key={x} x1="300" y1="215" x2={300 + x * 1.9} y2="440" stroke="#0F4120" strokeOpacity="0.35" strokeWidth="3" />
      ))}
    </svg>
  );
}
