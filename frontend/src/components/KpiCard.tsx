interface KpiCardProps {
  label: string;
  value: string | number;
  sublabel?: string;
  tone?: 'neutral' | 'positive' | 'negative';
}

export function KpiCard({ label, value, sublabel, tone = 'neutral' }: KpiCardProps) {
  const toneClass =
    tone === 'positive' ? 'text-success-600' : tone === 'negative' ? 'text-danger-600' : 'text-brand-700';
  return (
    <div className="card">
      <div className={`text-3xl font-bold ${toneClass}`}>{value}</div>
      <div className="kpi-label">{label}</div>
      {sublabel && <div className="text-xs text-slate-400 mt-2">{sublabel}</div>}
    </div>
  );
}
