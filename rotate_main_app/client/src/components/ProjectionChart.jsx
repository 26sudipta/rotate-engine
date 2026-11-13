import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

export default function ProjectionChart({ projection }) {
  const data = projection.map((p) => ({ label: `Year ${p.year}`, suitability: p.suitability }));

  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <h4 className="mb-3 text-[13px] font-semibold text-ink">3-Year Projection</h4>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="#DDD9CF" strokeDasharray="3 5" vertical={false} />
          <XAxis dataKey="label" tick={{ fontSize: 11, fill: "#5F6B62" }} axisLine={{ stroke: "#DDD9CF" }} tickLine={false} />
          <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: "#5F6B62" }} axisLine={false} tickLine={false} width={34} />
          <Tooltip
            contentStyle={{ borderRadius: 8, borderColor: "#DDD9CF", fontSize: 12 }}
            formatter={(v) => [`${v}`, "Suitability"]}
          />
          <Bar dataKey="suitability" radius={[4, 4, 0, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill={i === 0 ? "#BFE0B8" : i === 1 ? "#4FAE5E" : "#0F4120"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
