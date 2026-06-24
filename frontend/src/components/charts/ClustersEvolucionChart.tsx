'use client';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList,
} from 'recharts';
import type { ClusterEvolucion } from '@/lib/api';

export function ClustersEvolucionChart({ data }: { data: ClusterEvolucion[] }) {
  const sorted = [...data].sort((a, b) => a.cambio_pct - b.cambio_pct);
  return (
    <div style={{ width: '100%', height: 360 }}>
      <ResponsiveContainer>
        <BarChart
          data={sorted}
          layout="vertical"
          margin={{ top: 10, right: 60, left: 100, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis type="number" stroke="#64748b" />
          <YAxis
            dataKey="nombre"
            type="category"
            stroke="#64748b"
            width={180}
            tick={{ fontSize: 11 }}
          />
          <Tooltip
            formatter={(v: number) => `${v.toFixed(1)}%`}
            labelFormatter={(l) => `Cluster: ${l}`}
          />
          <Bar dataKey="cambio_pct">
            <LabelList
              dataKey="cambio_pct"
              position="right"
              formatter={(v: number) => `${v > 0 ? '+' : ''}${v.toFixed(1)}%`}
              style={{ fontSize: 11, fill: '#475569' }}
            />
            {sorted.map((d) => (
              <Cell
                key={d.cluster}
                fill={d.cambio_pct > 0 ? '#10b981' : '#ef4444'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
