import { api } from '@/lib/api';
import { MercadosBarChart } from '@/components/charts/MercadosBarChart';

export default async function CorrelacionPage() {
  const [lag, mercados] = await Promise.all([
    api.correlacionLag(),
    api.correlacionMercados(),
  ]);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Correlación con seguridad</h1>
        <p className="text-slate-600 mt-2 max-w-3xl">
          Análisis 2 — Correlación con rezago entre la tasa de homicidios y las llegadas
          internacionales, complementada con prueba de causalidad de Granger y desagregación por
          mercado emisor.
        </p>
      </header>

      <div className="card">
        <h2 className="card-title">Correlación por rezago (2010-2024)</h2>
        <p className="card-subtitle mb-4">
          El rezago óptimo se sitúa en 1-2 años. Spearman ρ = −0,955 a lag 1 (p &lt; 10⁻⁵).
        </p>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left">
                <th className="py-3 px-4 font-medium text-slate-600">Lag (años)</th>
                <th className="py-3 px-4 font-medium text-slate-600">n</th>
                <th className="py-3 px-4 font-medium text-slate-600">Pearson r</th>
                <th className="py-3 px-4 font-medium text-slate-600">p Pearson</th>
                <th className="py-3 px-4 font-medium text-slate-600">Spearman ρ</th>
                <th className="py-3 px-4 font-medium text-slate-600">p Spearman</th>
              </tr>
            </thead>
            <tbody>
              {lag.map((row) => (
                <tr
                  key={row.lag}
                  className="border-b border-slate-100 hover:bg-slate-50 transition"
                >
                  <td className="py-3 px-4 font-medium">{row.lag}</td>
                  <td className="py-3 px-4">{row.n}</td>
                  <td className="py-3 px-4 text-danger-600 font-mono">
                    {row.pearson_r.toFixed(3)}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-600">
                    {row.pearson_p.toExponential(2)}
                  </td>
                  <td className="py-3 px-4 text-danger-600 font-mono">
                    {row.spearman_r.toFixed(3)}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-600">
                    {row.spearman_p.toExponential(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">Sensibilidad por mercado emisor (lag = 2)</h2>
        <p className="card-subtitle mb-4">
          China lidera la elasticidad. La diferenciación regional vs lejana es pequeña, lo que
          sugiere transmisión global efectiva de la información de seguridad.
        </p>
        <MercadosBarChart data={mercados} />
      </div>
    </div>
  );
}
