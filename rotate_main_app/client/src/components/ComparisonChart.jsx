import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

export default function ComparisonChart({ title, data, xKey, seriesA, seriesB, unit = "" }) {
  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <h4 className="mb-3 text-[13px] font-semibold text-ink">{title}</h4>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data} margin={{ top: 4, right: 8, left: -18, bottom: 0 }}>
          <CartesianGrid stroke="#DDD9CF" strokeDasharray="3 5" vertical={false} />
          <XAxis
            dataKey={xKey}
            tick={{ fontSize: 11, fill: "#5F6B62" }}
            axisLine={{ stroke: "#DDD9CF" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "#5F6B62" }}
            axisLine={false}
            tickLine={false}
            width={36}
            unit={unit}
          />
          <Tooltip
            contentStyle={{ borderRadius: 8, borderColor: "#DDD9CF", fontSize: 12 }}
            labelStyle={{ color: "#1B2420", fontWeight: 600 }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Line
            type="monotone"
            dataKey={seriesA.key}
            name={seriesA.name}
            stroke="#0F4120"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
          <Line
            type="monotone"
            dataKey={seriesB.key}
            name={seriesB.name}
            stroke="#E5A612"
            strokeWidth={2}
            strokeDasharray="4 3"
            dot={false}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
