import { Link } from "react-router-dom";
import { Satellite, Database, Calculator } from "lucide-react";
import { SectionHeading, CheckItem, IconTile } from "../components/ui/Section.jsx";
import PillButton from "../components/ui/PillButton.jsx";
import FaqAccordion from "../components/FaqAccordion.jsx";
import { faqItems } from "../data/faq.js";
import { strategies } from "../data/mockStrategies.js";
import { calculateSuitability } from "../utils/scenarioModel.js";

// Candidate sources only — none of these are connected in the prototype.
const dataLayers = [
  ["Precipitation", "Demonstration dataset", "NASA GPM IMERG (satellite precipitation)"],
  ["Temperature", "Demonstration dataset", "NASA POWER meteorology"],
  ["Soil moisture", "Demonstration dataset", "NASA SMAP soil moisture"],
  ["Soil salinity", "Demonstration dataset", "No direct NASA product — needs in-situ or national soil survey data"],
  ["Historical series", "Synthetic 40-year series", "NASA POWER / reanalysis archives"],
  ["Crop profiles", "Illustrative indicators", "Validated agronomic models and extension guidance"],
];

export default function Methodology() {
  const example = strategies.find((s) => s.id === "strategy-b");
  const result = calculateSuitability(example, { rainfallPct: -15, salinityPct: 25 }, {});

  return (
    <div className="mx-auto max-w-[1100px] px-6 py-14">
      <div className="grid gap-6 md:grid-cols-3">
        {[
          [Satellite, "Observations", "Environmental inputs enter through the server's data layer."],
          [Database, "Analysis", "Services compare current conditions with history and crop profiles."],
          [Calculator, "Scoring", "An isolated, deterministic formula produces suitability scores."],
        ].map(([Icon, t, b]) => (
          <div key={t} className="card-dashed rounded-[26px] bg-cream p-8 text-center">
            <div className="flex justify-center"><IconTile icon={Icon} size={64} /></div>
            <h3 className="mt-4 font-display text-[18px] font-bold">{t}</h3>
            <p className="mt-2 text-[14px] text-ink-soft">{b}</p>
          </div>
        ))}
      </div>

      <section className="mt-16">
        <SectionHeading eyebrow="Scoring" title="How suitability is calculated">
          This is a prototype formula, intentionally simple and separated in code (<code className="font-mono text-[14px]">utils/scenarioModel.js</code>) so a real scientific model can replace it.
        </SectionHeading>
        <div className="mt-6 rounded-[24px] bg-forest p-7 font-mono text-[14px] leading-relaxed text-white">
          <p className="text-sun">scenario suitability =</p>
          <p className="pl-4">base suitability</p>
          <p className="pl-4">× rainfall factor</p>
          <p className="pl-4">× salinity factor</p>
          <p className="pl-4">× (0.5 + priority factor)</p>
        </div>
        <ul className="mt-6 grid gap-3 md:grid-cols-2">
          <CheckItem>Base: average of water conservation, soil recovery, salinity resilience and yield stability</CheckItem>
          <CheckItem>Rainfall: drops hurt high-water-demand rotations more</CheckItem>
          <CheckItem>Salinity: increases hurt low-resilience rotations more</CheckItem>
          <CheckItem>Priority: weights each indicator by your slider values</CheckItem>
        </ul>
        <div className="mt-6 rounded-2xl border border-border bg-cream p-5 text-[14px]">
          <p className="font-display font-bold">Worked example — {example.name} at −15% rainfall, +25% salinity (equal priorities)</p>
          <p className="mt-2 font-mono text-[13px] text-ink-soft">
            base {result.baseSuitability} → scenario suitability <span className="font-bold text-forest">{result.suitability}</span> / 100
          </p>
        </div>
      </section>

      <section className="mt-16">
        <SectionHeading eyebrow="Data" title="Where real data would plug in">
          Nothing below is connected yet. The right-hand column lists candidate sources to evaluate, not integrations.
        </SectionHeading>
        <div className="mt-6 overflow-x-auto rounded-[22px] border border-border">
          <table className="w-full min-w-[640px] text-left text-[14px]">
            <thead className="bg-forest text-white">
              <tr><th className="px-5 py-3.5 font-display">Input</th><th className="px-5 py-3.5 font-display">Prototype uses</th><th className="px-5 py-3.5 font-display">Candidate real source</th></tr>
            </thead>
            <tbody>
              {dataLayers.map(([a, b, c], i) => (
                <tr key={a} className={i % 2 ? "bg-cream/60" : "bg-white"}>
                  <td className="px-5 py-3.5 font-semibold">{a}</td>
                  <td className="px-5 py-3.5 text-clay">{b}</td>
                  <td className="px-5 py-3.5 text-ink-soft">{c}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="mt-16">
        <SectionHeading eyebrow="Limitations" title="What this prototype cannot tell you" />
        <ul className="mt-6 grid gap-3 md:grid-cols-2">
          <CheckItem>Indicator scores are illustrative, not field-validated</CheckItem>
          <CheckItem>Climate values and history are demonstration data</CheckItem>
          <CheckItem>No local soil, water-access or market constraints</CheckItem>
          <CheckItem>Not a substitute for agricultural extension advice</CheckItem>
        </ul>
      </section>

      <section id="faq" className="mt-16 scroll-mt-32">
        <SectionHeading eyebrow="FAQ" title="Frequently asked questions" />
        <div className="mt-6"><FaqAccordion items={faqItems} /></div>
        <div className="mt-8 flex flex-wrap gap-4">
          <PillButton to="/contact">Still have a question?</PillButton>
          <Link to="/scenario" className="inline-flex items-center px-3 text-[14px] font-semibold text-forest underline-offset-4 hover:underline">Try a scenario</Link>
        </div>
      </section>
    </div>
  );
}
