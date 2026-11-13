import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

/** Grouped bars comparing a baseline ("Current") against the scenario value for each category. */
export default function BaselineScenarioChart({ title, data, unit = "", note, domain }) {
  return (
    <div className="rounded-[24px] border border-border bg-white p-5">
      <h4 className="font-display text-[14.5px] font-bold text-ink">{title}</h4>
      <div className="mt-3">
        <ResponsiveContainer width="100%" height={210}>
          <BarChart data={data} margin={{ top: 4, right: 6, left: 0, bottom: 0 }} barGap={4}>
            <CartesianGrid stroke="#DDD9CF" strokeDasharray="3 5" vertical={false} />
            <XAxis dataKey="label" tick={{ fontSize: 11, fill: "#5F6B62" }} tickLine={false} axisLine={{ stroke: "#DDD9CF" }} />
            <YAxis tick={{ fontSize: 11, fill: "#5F6B62" }} tickLine={false} axisLine={false} width={46} unit={unit} domain={domain} />
            <Tooltip cursor={{ fill: "rgba(15,65,32,0.05)" }} contentStyle={{ borderRadius: 10, borderColor: "#DDD9CF", fontSize: 12 }} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Bar dataKey="current" name="Current" fill="#BFE0B8" radius={[5, 5, 0, 0]} animationDuration={400} />
            <Bar dataKey="scenario" name="Scenario" fill="#0F4120" radius={[5, 5, 0, 0]} animationDuration={400} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      {note && <p className="mt-2 text-[11.5px] text-ink-soft">{note}</p>}
    </div>
  );
}
