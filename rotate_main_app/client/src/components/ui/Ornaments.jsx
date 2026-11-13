// Original decorative SVG pieces that echo the reference design's visual language:
// wheat-ear ornament, torn-paper edges, grass blades and hand-drawn line art.

function seeded(seed) {
  let s = seed;
  return () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

const tornPath = (() => {
  const rnd = seeded(7);
  const w = 1440;
  const h = 18;
  let d = `M0 ${h} L0 ${h * 0.5}`;
  let x = 0;
  while (x < w) {
    x += 6 + rnd() * 14;
    d += ` L${Math.min(x, w).toFixed(1)} ${(h * (0.12 + rnd() * 0.6)).toFixed(1)}`;
  }
  return `${d} L${w} ${h} Z`;
})();

const grassPath = (() => {
  const rnd = seeded(21);
  const w = 1440;
  const h = 26;
  let d = `M0 ${h}`;
  let x = 0;
  while (x < w) {
    const bw = 4 + rnd() * 5;
    const bh = 7 + rnd() * (h - 8);
    d += ` L${x.toFixed(1)} ${h} L${(x + bw / 2).toFixed(1)} ${(h - bh).toFixed(1)} L${(x + bw).toFixed(1)} ${h}`;
    x += bw;
  }
  return `${d} L${w} ${h} Z`;
})();

/** Torn-paper edge. Place inside a `relative` section; colour follows `text-*`. */
export function TornEdge({ position = "top", className = "" }) {
  const placement = position === "top" ? "bottom-full" : "top-full rotate-180";
  return (
    <svg
      aria-hidden
      viewBox="0 0 1440 18"
      preserveAspectRatio="none"
      className={`pointer-events-none absolute left-0 h-[14px] w-full ${placement} ${className}`}
      fill="currentColor"
    >
      <path d={tornPath} />
    </svg>
  );
}

/** Row of grass blades. Fill follows `text-*` (use the colour of the section below). */
export function GrassEdge({ className = "" }) {
  return (
    <svg
      aria-hidden
      viewBox="0 0 1440 26"
      preserveAspectRatio="none"
      className={`pointer-events-none block h-[18px] w-full md:h-[24px] ${className}`}
      fill="currentColor"
    >
      <path d={grassPath} />
    </svg>
  );
}

/** Horizontal wheat-ear ornament used beside section eyebrows. */
export function WheatEar({ className = "" }) {
  const pairs = [0, 1, 2, 3, 4];
  return (
    <svg aria-hidden viewBox="0 0 84 18" className={`h-[16px] w-[76px] ${className}`} fill="currentColor">
      <rect x="2" y="8.2" width="78" height="1.6" rx="0.8" />
      {pairs.map((i) => (
        <g key={i} transform={`translate(${22 + i * 11} 9)`}>
          <ellipse cx="0" cy="-3.6" rx="2" ry="5" transform="rotate(-38)" />
          <ellipse cx="0" cy="3.6" rx="2" ry="5" transform="rotate(38)" />
        </g>
      ))}
    </svg>
  );
}

/** Hand-drawn double underline for hero headings. */
export function HandUnderline({ className = "" }) {
  return (
    <svg aria-hidden viewBox="0 0 480 14" className={`h-[14px] w-full max-w-[480px] ${className}`} fill="none" strokeLinecap="round">
      <path d="M3 8 C 110 3, 290 11, 476 5" stroke="currentColor" strokeWidth="4.5" />
      <path d="M40 11 C 150 8, 300 12, 420 9" stroke="currentColor" strokeWidth="1.6" opacity="0.6" />
    </svg>
  );
}

/** Faint line-art windmill for section backgrounds. */
export function WindmillArt({ className = "" }) {
  return (
    <svg aria-hidden viewBox="0 0 300 360" fill="none" stroke="currentColor" strokeWidth="1.3" className={className}>
      <path d="M120 360 L135 150 H165 L180 360 Z" />
      <path d="M128 250 H172 M124 300 H176 M132 200 H168" />
      <path d="M135 150 L150 128 L165 150" />
      <g transform="translate(150 140)">
        {[35, 125, 215, 305].map((a) => (
          <g key={a} transform={`rotate(${a})`}>
            <path d="M-5 -10 L-15 -135 L15 -135 L5 -10 Z" />
            <path d="M-9 -42 H9 M-11 -72 H11 M-13 -102 H13 M0 -10 V-135" />
          </g>
        ))}
        <circle r="6" fill="currentColor" />
      </g>
    </svg>
  );
}

/** Original logo mark: shield with leaf and a rotation arc. */
export function LogoMark({ className = "h-10 w-9" }) {
  return (
    <svg aria-hidden viewBox="0 0 40 44" className={className}>
      <path d="M4 7 Q4 2 9 2 H31 Q36 2 36 7 V26 Q36 38 20 42 Q4 38 4 26 Z" fill="#0F4120" />
      <path d="M11 29 C10 17 19 9 31 9 C31 22 24 31 11 29 Z" fill="#FBC02D" />
      <path d="M12 28 C17 22 22 17 28 12" stroke="#0F4120" strokeWidth="1.6" strokeLinecap="round" fill="none" />
      <path d="M9 18 A12 12 0 0 1 20 8" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" fill="none" opacity="0.9" />
    </svg>
  );
}
