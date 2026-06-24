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
} from 'recharts';
import type { MercadoSensibilidad } from '@/lib/api';

export function MercadosBarChart({ data }: { data: MercadoSensibilidad[] }) {
  const sorted = [...data].sort((a, b) => a.pearson_r - b.pearson_r);
  return (
    <div style={{ width: '100%', height: 320 }}>
      <ResponsiveContainer>
        <BarChart
          data={sorted}
          layout="vertical"
          margin={{ top: 10, right: 30, left: 60, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis type="number" domain={[-1, 0]} stroke="#64748b" />
          <YAxis dataKey="mercado" type="category" stroke="#64748b" width={120} />
          <Tooltip
            formatter={(v: number) => v.toFixed(3)}
            labelFormatter={(l) => `Mercado: ${l}`}
          />
          <Bar dataKey="pearson_r">
            {sorted.map((d) => (
              <Cell
                key={d.mercado}
                fill={d.pearson_r < -0.85 ? '#dc2626' : '#ef4444'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
