import { Link } from "react-router-dom";
import { Satellite, Database, Calculator } from "lucide-react";
import { SectionHeading, CheckItem, IconTile } from "../components/ui/Section.jsx";
import PillButton from "../components/ui/PillButton.jsx";
import FaqAccordion from "../components/FaqAccordion.jsx";
import { faqItems } from "../data/faq.js";

const dataLayers = [
  ["Weather window", "Observed NASA POWER values", "60 days before the decision date"],
  ["Vegetation response", "Observed MODIS Terra NDVI", "250 m area around the field"],
  ["Salinity class", "Local information, not NASA", "User-selected SRDI class"],
  ["Crop benefits and risks", "Derived from cited rule table", "Needs expert review"],
  ["Analog distance and confidence", "Derived by ROTATE", "Ledoit-Wolf Mahalanobis matching"],
  ["What-if changes", "Scenario values", "Never presented as observations or forecasts"],
];

export default function Methodology() {
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
          ROTATE uses transparent analog-year matching rather than a forecast. It fits the
          training data only, selects five comparable Boro seasons, and reports agreement with
          the exact chance rate.
        </SectionHeading>
        <div className="mt-6 rounded-[24px] bg-forest p-7 font-mono text-[14px] leading-relaxed text-white">
          <p className="text-sun">ROTATE comparison =</p>
          <p className="pl-4">60-day NASA POWER weather window</p>
          <p className="pl-4">→ five historical analog seasons</p>
          <p className="pl-4">→ MODIS NDVI response and confidence</p>
          <p className="pl-4">→ cited rotation benefits, risks and local review</p>
        </div>
        <ul className="mt-6 grid gap-3 md:grid-cols-2">
          <CheckItem>Ledoit-Wolf distance is fitted on training seasons only</CheckItem>
          <CheckItem>Five analog years are fixed before results are viewed</CheckItem>
          <CheckItem>Confidence includes the chance rate for the observed agreement</CheckItem>
          <CheckItem>Backtest verdict: no demonstrable skill, so analogs are historical examples</CheckItem>
        </ul>
        <div className="mt-6 rounded-2xl border border-border bg-cream p-5 text-[14px]">
          <p className="font-display font-bold">The UI keeps scenario exploration separate</p>
          <p className="mt-2 font-mono text-[13px] text-ink-soft">
            User priorities can change card ordering; they do not turn historical examples into a forecast.
          </p>
        </div>
      </section>

      <section className="mt-16">
        <SectionHeading eyebrow="Data and provenance" title="What each layer means">
          The engine keeps NASA observations, local information, ROTATE-derived reasoning and
          scenario values visibly separate.
        </SectionHeading>
        <div className="mt-6 overflow-x-auto rounded-[22px] border border-border">
          <table className="w-full min-w-[640px] text-left text-[14px]">
            <thead className="bg-forest text-white">
              <tr><th className="px-5 py-3.5 font-display">Layer</th><th className="px-5 py-3.5 font-display">Label in ROTATE</th><th className="px-5 py-3.5 font-display">Use</th></tr>
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
        <SectionHeading eyebrow="Limits" title="What ROTATE cannot tell you" />
        <ul className="mt-6 grid gap-3 md:grid-cols-2">
          <CheckItem>It does not forecast the coming season</CheckItem>
          <CheckItem>POWER is reanalysis/model output, not a field measurement</CheckItem>
          <CheckItem>One 250 m NDVI pixel can cover more land than a smallholder plot</CheckItem>
          <CheckItem>It does not measure field salinity or prove rotation performance</CheckItem>
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
