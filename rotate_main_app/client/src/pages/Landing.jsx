import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ReferenceDot,
} from "recharts";
import {
  Satellite, History, Scale, CloudRain, Waypoints, FlaskConical, Map, Beaker, Sprout,
  BookOpenText, ArrowRight, MapPin, Mail, Layers3,
} from "lucide-react";
import PillButton from "../components/ui/PillButton.jsx";
import { Eyebrow, SectionHeading, Reveal, IconTile, CheckItem } from "../components/ui/Section.jsx";
import { TornEdge, HandUnderline, WindmillArt } from "../components/ui/Ornaments.jsx";
import { RotationEmblem, FieldStrip, CropRows } from "../components/home/HeroArt.jsx";
import FaqAccordion from "../components/FaqAccordion.jsx";
import { faqItems } from "../data/faq.js";
import { getHistoricalSeries } from "../data/mockHistorical.js";
import { strategies } from "../data/mockStrategies.js";
import { calculateSuitability } from "../utils/scenarioModel.js";

const stats = [
  ["2", "Cached ROTATE sites"],
  ["60", "Days matched before the decision"],
  ["5", "Historical analog seasons"],
  ["3", "Rotation cards to compare"],
];

const features = [
  { icon: Satellite, title: "NASA observations", body: "Cached NASA POWER weather and MODIS NDVI are shown as observed inputs, with their limits made explicit." },
  { icon: History, title: "Historical analogs", body: "The engine matches the 60 days before the decision date with comparable past Boro seasons." },
  { icon: Scale, title: "Transparent reasoning", body: "Ledoit-Wolf analog distance, weighted agreement and chance rates are part of the output." },
  { icon: CloudRain, title: "What-if scenarios", body: "Change the input window as a labelled Scenario; ROTATE never presents it as observed weather." },
  { icon: Waypoints, title: "Evidence trail", body: "Observed, Derived and Scenario tags keep NASA data, local information and ROTATE reasoning separate." },
  { icon: FlaskConical, title: "Local review first", body: "Cards compare options; they do not choose what to plant and every card needs local review." },
];

const steps = [
  { n: 1, title: "Select a farm", body: "Search or click a location on the Bangladesh map." },
  { n: 2, title: "Compare with history", body: "Find the closest historical climate analog year." },
  { n: 3, title: "Weigh your priorities", body: "Water, soil, salinity or yield — rank what matters." },
  { n: 4, title: "Stress-test with What If?", body: "Change rainfall and salinity and compare outcomes." },
];

const views = [
  { to: "/dashboard", icon: Map, title: "Dashboard", body: "Interactive map, location search and current conditions." },
  { to: "/historical", icon: History, title: "Historical Analog", body: "Current versus historical climate charts." },
  { to: "/strategies", icon: Sprout, title: "Strategies", body: "Compare rotations and re-rank by priority." },
  { to: "/scenario", icon: CloudRain, title: "What If?", body: "Scenario sliders and a three-year projection." },
  { to: "/crops", icon: BookOpenText, title: "Crop Library", body: "Example crop profiles and rotation roles." },
  { to: "/methodology", icon: Beaker, title: "Methodology", body: "How observations, local information and ROTATE reasoning stay separate." },
];

function HistoryPreview() {
  const { series, closestAnalogYear, closestAnalog } = useMemo(() => getHistoricalSeries("coastal-chattogram"), []);
  return (
    <div className="card-dashed rounded-[28px] bg-cream p-7">
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-1.5 text-[13px] font-semibold text-ink"><MapPin size={14} className="text-leaf-dark" />Coastal Chattogram</span>
        <span className="rounded-full bg-crop-soft px-2.5 py-1 text-[11px] font-semibold text-forest">Contextual climate view</span>
      </div>
      <p className="mt-3 font-display text-[15px] font-bold text-ink">Precipitation, 40-year timeline</p>
      <div className="mt-2 h-[220px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={series} margin={{ top: 8, right: 10, left: -18, bottom: 0 }}>
            <CartesianGrid stroke="#DDD9CF" strokeDasharray="3 5" vertical={false} />
            <XAxis dataKey="year" tick={{ fontSize: 11, fill: "#5F6B62" }} tickLine={false} axisLine={{ stroke: "#DDD9CF" }} interval={7} />
            <YAxis tick={{ fontSize: 11, fill: "#5F6B62" }} tickLine={false} axisLine={false} unit="mm" />
            <Tooltip contentStyle={{ borderRadius: 10, fontSize: 12, borderColor: "#DDD9CF" }} />
            <Line type="monotone" dataKey="precipitationMm" name="Precipitation" stroke="#0F4120" strokeWidth={2.2} dot={false} />
            <ReferenceDot x={closestAnalogYear} y={closestAnalog.precipitationMm} r={6} fill="#FBC02D" stroke="#0F4120" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-1 text-[12.5px] text-ink-soft">Yellow marker: closest analog in the contextual timeline ({closestAnalogYear}).</p>
    </div>
  );
}

function ScenarioPreview() {
  const [salinity, setSalinity] = useState(25);
  const [rainfall, setRainfall] = useState(-15);

  const scored = useMemo(
    () =>
      strategies
        .map((s) => ({ ...s, score: calculateSuitability(s, { rainfallPct: rainfall, salinityPct: salinity }).suitability }))
        .sort((a, b) => b.score - a.score),
    [rainfall, salinity]
  );

  return (
    <div className="card-dashed card-dashed-light rounded-[28px] bg-forest p-7 text-white">
      <p className="font-script text-[26px] leading-none text-sun">Try it — live scenario</p>
      {[
        ["Rainfall", rainfall, setRainfall, -30, 30],
        ["Soil salinity", salinity, setSalinity, -25, 50],
      ].map(([label, value, set, min, max]) => (
        <div key={label} className="mt-5">
          <div className="flex justify-between text-[13.5px]">
            <span>{label}</span>
            <span className="font-mono font-semibold text-sun">{value > 0 ? "+" : ""}{value}%</span>
          </div>
          <input type="range" min={min} max={max} value={value} onChange={(e) => set(Number(e.target.value))} aria-label={label} className="mt-1.5 w-full accent-[#FBC02D]" />
        </div>
      ))}
      <div className="mt-6 space-y-3">
        {scored.map((s, i) => (
          <div key={s.id}>
            <div className="flex justify-between text-[13px]">
              <span className={i === 0 ? "font-bold text-sun" : "text-white/85"}>{s.name}{i === 0 ? " · leads" : ""}</span>
              <span className="font-mono">{s.score.toFixed(0)}</span>
            </div>
            <div className="mt-1 h-2 overflow-hidden rounded-full bg-white/15">
              <motion.div className={`h-full rounded-full ${i === 0 ? "bg-sun" : "bg-white/60"}`} animate={{ width: `${s.score}%` }} transition={{ duration: 0.35 }} />
            </div>
          </div>
        ))}
      </div>
      <p className="mt-4 text-[12px] text-white/65">Scenario values are labelled and are not a forecast.</p>
    </div>
  );
}

export default function Landing() {
  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-b from-white to-[#FCF5E2]">
        <div className="pointer-events-none absolute -right-32 -top-20 h-[640px] w-[640px] rounded-full bg-[radial-gradient(circle,#FFE08A_0%,rgba(255,224,138,0)_68%)]" />
        <div className="relative mx-auto grid max-w-[1240px] gap-10 px-6 pb-44 pt-16 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div>
            <Eyebrow>Climate-smart rotation planning for Bangladesh</Eyebrow>
            <h1 className="mt-4 font-display text-[40px] font-extrabold leading-[1.08] tracking-tight text-forest-deep md:text-[56px]">
              Plan crop rotations with climate evidence.
            </h1>
            <HandUnderline className="mt-3 text-sun" />
            <p className="mt-6 max-w-[540px] text-[16.5px] leading-relaxed text-ink-soft">
              ROTATE connects historical climate analogs, current conditions, soil salinity and crop-rotation characteristics so researchers and extension teams can explore decisions before the season starts.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <PillButton to="/dashboard">Open the Dashboard</PillButton>
              <PillButton to="/scenario" variant="outline" icon={ArrowRight}>Try a What If? scenario</PillButton>
            </div>
            <div className="mt-8 flex flex-wrap gap-2 text-[12.5px] font-semibold">
              <span className="rounded-full bg-crop-soft px-3 py-1.5 text-forest">Cached engine outputs for offline demo</span>
              <span className="rounded-full bg-crop-soft px-3 py-1.5 text-forest">NASA Space Apps Challenge 2026</span>
            </div>
          </div>
          <RotationEmblem />
        </div>
        <FieldStrip className="absolute bottom-0 left-0 h-[130px] w-full" />
      </section>

      {/* Notice strip */}
      <section className="bg-cream">
        <div className="mx-auto flex max-w-[1240px] items-center gap-6 px-6 pb-14 pt-6">
          <span className="hidden h-[84px] w-[84px] shrink-0 items-center justify-center rounded-full bg-sun text-forest sm:flex"><FlaskConical size={34} /></span>
          <p className="font-script text-[27px] leading-[1.15] text-ink">
            ROTATE helps you compare historical examples with NASA observations and cited crop
            rules. It does not forecast the season or replace local agricultural expertise.
          </p>
        </div>
      </section>

      {/* Stats */}
      <section className="mx-auto max-w-[1240px] px-6 py-16">
        <div className="grid grid-cols-2 gap-y-10 md:grid-cols-4">
          {stats.map(([n, label], i) => (
            <Reveal key={label} delay={i * 0.06} className={`px-4 text-center ${i > 0 ? "md:border-l md:border-dashed md:border-border" : ""}`}>
              <div className="font-display text-[54px] font-extrabold leading-none text-forest">{n}</div>
              <div className="mx-auto mt-3 h-[3px] w-10 rounded-full bg-sun" />
              <p className="mx-auto mt-3 max-w-[190px] text-[14px] text-ink-soft">{label}</p>
            </Reveal>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-[1240px] px-6 pb-20">
        <SectionHeading center eyebrow="Why ROTATE" title="Built for transparent, explainable decisions">
          Everything on the platform traces back to inputs you can inspect and assumptions you can change.
        </SectionHeading>
        <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {features.map((f, i) => (
            <Reveal key={f.title} delay={(i % 3) * 0.06}>
              <div className="card-dashed h-full rounded-[28px] bg-cream p-9 text-center transition-colors hover:bg-[#E9E6DE]">
                <div className="flex justify-center"><IconTile icon={f.icon} /></div>
                <h3 className="mt-5 font-display text-[20px] font-bold text-ink">{f.title}</h3>
                <div className="mx-auto mt-3 h-[2px] w-9 bg-sun" />
                <p className="mt-4 text-[14.5px] leading-relaxed text-ink-soft">{f.body}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="relative bg-forest text-white">
        <TornEdge position="top" className="text-forest" />
        <TornEdge position="bottom" className="text-forest" />
        <WindmillArt className="pointer-events-none absolute right-8 top-6 hidden h-[340px] text-white/[0.07] lg:block" />
        <div className="relative mx-auto max-w-[1240px] px-6 py-20">
          <SectionHeading light eyebrow="How it works" title="From a map click to a stress-tested recommendation" />
          <div className="mt-12 grid gap-8 md:grid-cols-2 lg:grid-cols-4">
            {steps.map((s, i) => (
              <Reveal key={s.n} delay={i * 0.07}>
                <span className="flex h-14 w-14 items-center justify-center rounded-full bg-sun font-display text-[24px] font-extrabold text-forest">{s.n}</span>
                <h3 className="mt-4 font-display text-[19px] font-bold">{s.title}</h3>
                <p className="mt-2 text-[14.5px] leading-relaxed text-white/80">{s.body}</p>
              </Reveal>
            ))}
          </div>
          <div className="mt-12"><PillButton to="/dashboard" variant="light">Start with the map</PillButton></div>
        </div>
      </section>

      {/* Split: historical */}
      <section className="mx-auto grid max-w-[1240px] items-center gap-14 px-6 py-24 lg:grid-cols-2">
        <Reveal><HistoryPreview /></Reveal>
        <Reveal delay={0.08}>
          <SectionHeading eyebrow="Historical Analog" title="Find the year that looks like today.">
            Overlay current conditions on a 40-year timeline to see which historical season is the closest match for precipitation, temperature and soil moisture.
          </SectionHeading>
          <ul className="mt-6 grid gap-3 sm:grid-cols-2">
            <CheckItem>Three comparison charts</CheckItem>
            <CheckItem>Closest-analog highlight</CheckItem>
            <CheckItem>Hover tooltips on every chart</CheckItem>
            <CheckItem>Observed, Derived and Scenario labels</CheckItem>
          </ul>
          <div className="mt-8"><PillButton to="/historical">Open Historical Analog</PillButton></div>
        </Reveal>
      </section>

      {/* Split: scenario */}
      <section className="mx-auto grid max-w-[1240px] items-center gap-14 px-6 pb-24 lg:grid-cols-2">
        <Reveal className="lg:order-2"><ScenarioPreview /></Reveal>
        <Reveal delay={0.08} className="lg:order-1">
          <SectionHeading eyebrow="What If?" title="Stress-test every rotation.">
            Move rainfall and soil salinity and watch the ranking change. The full scenario page adds baseline-versus-scenario comparisons and a three-year projection.
          </SectionHeading>
          <ul className="mt-6 grid gap-3 sm:grid-cols-2">
            <CheckItem>Rainfall −30% to +30%</CheckItem>
            <CheckItem>Salinity −25% to +50%</CheckItem>
            <CheckItem>Deterministic, inspectable formula</CheckItem>
            <CheckItem>Replaceable with a real model</CheckItem>
          </ul>
          <div className="mt-8"><PillButton to="/scenario">Open What If?</PillButton></div>
        </Reveal>
      </section>

      {/* Explore views */}
      <section className="relative bg-bark text-white">
        <div className="mx-auto max-w-[1240px] px-6 py-20">
          <div className="flex flex-wrap items-start justify-between gap-8">
            <SectionHeading light eyebrow="Explore the platform" title="Everything you need, in one place.">
              Each view is purpose-built, consistent in design and connected through shared state — your location and priorities follow you.
            </SectionHeading>
            <div className="flex h-[150px] w-[150px] shrink-0 flex-col items-center justify-center rounded-full border-2 border-dashed border-white/50 bg-forest-mid text-center shadow-[0_0_40px_rgba(251,192,45,0.25)]">
              <span className="font-display text-[40px] font-extrabold leading-none">{views.length}<span className="text-sun">+</span></span>
              <span className="mt-1 text-[13px] font-semibold leading-tight">Core views</span>
            </div>
          </div>
          <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {views.map((v) => (
              <Link key={v.to} to={v.to} className="group flex items-start gap-4 rounded-2xl bg-white p-6 text-ink transition-transform hover:-translate-y-1">
                <IconTile icon={v.icon} size={56} />
                <span className="flex-1">
                  <span className="flex items-center justify-between font-display text-[17px] font-bold">{v.title}<ArrowRight size={17} className="text-leaf-dark transition-transform group-hover:translate-x-1" /></span>
                  <span className="mt-1 block text-[14px] leading-relaxed text-ink-soft">{v.body}</span>
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Example rotations */}
      <section className="mx-auto max-w-[1240px] px-6 py-24">
        <SectionHeading center eyebrow="Example rotations" title="Three sequences relevant to Bangladesh agriculture">
          Crop data is structured so scientifically validated rotation information can replace these examples later.
        </SectionHeading>
        <div className="mt-12 grid gap-6 lg:grid-cols-3">
          {strategies.map((s) => (
            <Reveal key={s.id}>
              <div className="h-full rounded-[28px] border border-border bg-white p-7 transition-shadow hover:shadow-lg">
                <p className="font-script text-[24px] leading-none text-leaf-dark">{s.name}</p>
                <h3 className="mt-1 font-display text-[19px] font-bold text-ink">{s.label}</h3>
                <div className="mt-4 flex flex-wrap items-center gap-1.5">
                  {s.sequence.map((c, i) => (
                    <span key={c} className="flex items-center gap-1.5">
                      <span className="rounded-full bg-crop-soft px-3 py-1 text-[12.5px] font-semibold text-forest">{c}</span>
                      {i < s.sequence.length - 1 && <ArrowRight size={13} className="text-ink-soft" />}
                    </span>
                  ))}
                </div>
                <p className="mt-4 text-[14px] leading-relaxed text-ink-soft">{s.notes}</p>
              </div>
            </Reveal>
          ))}
        </div>
        <div className="mt-10 text-center"><PillButton to="/strategies">Compare strategies</PillButton></div>
      </section>

      {/* FAQ */}
      <section className="bg-cream py-24">
        <div className="mx-auto grid max-w-[1240px] gap-14 px-6 lg:grid-cols-[0.8fr_1.2fr]">
          <div>
            <SectionHeading eyebrow="FAQ" title="Questions, answered honestly.">
              Short answers about what ROTATE compares — and where local review is needed.
            </SectionHeading>
            <div className="mt-6"><PillButton to="/contact" variant="outline" icon={Mail}>Ask us something</PillButton></div>
          </div>
          <FaqAccordion items={faqItems} />
        </div>
      </section>

      {/* CTA */}
      <section className="relative mt-24 bg-forest-deep text-white">
        <TornEdge position="top" className="text-forest-deep" />
        <div className="grid lg:grid-cols-2">
          <div className="relative px-6 py-20 lg:py-24 lg:pl-[max(1.5rem,calc((100vw-1240px)/2+1.5rem))] lg:pr-12">
            <WindmillArt className="pointer-events-none absolute right-6 top-6 h-[260px] text-white/[0.07]" />
            <h2 className="relative font-script text-[48px] uppercase leading-[0.95] md:text-[64px]">
              Ready to explore your<br />farm’s climate future?
            </h2>
            <p className="relative mt-4 font-script text-[26px] text-sun">Free to try — no sign-up needed.</p>
            <div className="relative mt-8 flex flex-wrap gap-4">
              <PillButton to="/dashboard" variant="light">Open the Dashboard</PillButton>
              <PillButton to="/methodology" variant="outline" icon={Layers3} className="!border-white/40 !text-white hover:!bg-white/10">Read the methodology</PillButton>
            </div>
          </div>
          <div className="relative min-h-[300px] overflow-hidden">
            <CropRows className="absolute inset-0 h-full w-full" />
          </div>
        </div>
      </section>
    </div>
  );
}
