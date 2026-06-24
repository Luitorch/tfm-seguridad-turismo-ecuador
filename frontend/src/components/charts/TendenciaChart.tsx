'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { SerieLlegada } from '@/lib/api';

export function TendenciaChart({ data }: { data: SerieLlegada[] }) {
  return (
    <div style={{ width: '100%', height: 400 }}>
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="anio" stroke="#64748b" />
          <YAxis
            stroke="#64748b"
            tickFormatter={(v) => `${(v / 1_000_000).toFixed(1)}M`}
          />
          <Tooltip
            formatter={(v: number) => v.toLocaleString('es-EC')}
            labelFormatter={(l) => `Año ${l}`}
          />
          <ReferenceLine x={2022} stroke="#ef4444" strokeDasharray="3 3" label="Crisis 2022" />
          <Line
            type="monotone"
            dataKey="llegadas"
            stroke="#2563eb"
            strokeWidth={2.5}
            dot={{ r: 4, fill: '#2563eb' }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
