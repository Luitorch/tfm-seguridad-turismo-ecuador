'use client';

import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LabelList,
} from 'recharts';
import type { ProvinciaImpacto } from '@/lib/api';

export function ProvinciasScatter({ data }: { data: ProvinciaImpacto[] }) {
  const points = data
    .filter((d) => d.homicidios_crisis_total !== null)
    .map((d) => ({
      provincia: d.provincia,
      x: d.homicidios_crisis_total ?? 0,
      y: d.variacion_pct,
    }));

  return (
    <div style={{ width: '100%', height: 380 }}>
      <ResponsiveContainer>
        <ScatterChart margin={{ top: 20, right: 30, left: 40, bottom: 50 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            type="number"
            dataKey="x"
            name="Homicidios"
            stroke="#64748b"
            label={{
              value: 'Homicidios provinciales 2022-2024',
              position: 'insideBottom',
              offset: -10,
              fill: '#64748b',
              fontSize: 12,
            }}
          />
          <YAxis
            type="number"
            dataKey="y"
            name="Variación %"
            stroke="#64748b"
            label={{
              value: 'Variación %',
              angle: -90,
              position: 'insideLeft',
              fill: '#64748b',
              fontSize: 12,
            }}
          />
          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            content={({ payload }) => {
              if (!payload || payload.length === 0) return null;
              const p = payload[0].payload as { provincia: string; x: number; y: number };
              return (
                <div className="bg-white border border-slate-300 rounded p-3 text-xs shadow-sm">
                  <p className="font-semibold">{p.provincia}</p>
                  <p>Homicidios: {p.x.toLocaleString('es-EC')}</p>
                  <p>Variación: {p.y.toFixed(1)}%</p>
                </div>
              );
            }}
          />
          <Scatter data={points} fill="#2563eb">
            <LabelList
              dataKey="provincia"
              position="top"
              style={{ fontSize: 10, fill: '#475569' }}
            />
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
