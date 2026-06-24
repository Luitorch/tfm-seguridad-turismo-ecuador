import { api } from '@/lib/api';
import { ProvinciasScatter } from '@/components/charts/ProvinciasScatter';

export default async function ProvinciasPage() {
  const data = await api.provinciasImpacto();
  const sorted = [...data].sort((a, b) => a.variacion_pct - b.variacion_pct);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Impacto provincial</h1>
        <p className="text-slate-600 mt-2 max-w-3xl">
          Análisis 3 — Variación porcentual de flujos turísticos por provincia de control
          migratorio (pre-crisis 2018-2019 vs crisis 2022-2024).
        </p>
        <div className="mt-4 bg-amber-50 border border-amber-200 rounded p-4 text-sm">
          <p className="font-medium text-amber-900">⚠ Limitación clave</p>
          <p className="text-amber-800 mt-1">
            La variable <code className="bg-amber-100 px-1 rounded">pro_jefm</code> registra el
            punto de control migratorio, no el destino turístico final. Ver Cap 8.1.1 del TFM.
          </p>
        </div>
      </header>

      <div className="card">
        <h2 className="card-title">Variación por provincia</h2>
        <p className="card-subtitle mb-4">
          Esmeraldas, Santa Elena y Carchi registran las caídas más severas; Pichincha y
          Galápagos mantienen o crecen.
        </p>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left">
                <th className="py-3 px-4 font-medium text-slate-600">Provincia</th>
                <th className="py-3 px-4 font-medium text-slate-600 text-right">Pre (2018-19)</th>
                <th className="py-3 px-4 font-medium text-slate-600 text-right">Crisis (2022-24)</th>
                <th className="py-3 px-4 font-medium text-slate-600 text-right">Variación %</th>
                <th className="py-3 px-4 font-medium text-slate-600 text-right">Homicidios</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((row) => (
                <tr
                  key={row.provincia}
                  className="border-b border-slate-100 hover:bg-slate-50 transition"
                >
                  <td className="py-3 px-4 font-medium">{row.provincia}</td>
                  <td className="py-3 px-4 text-right font-mono">
                    {row.flujo_pre.toLocaleString('es-EC')}
                  </td>
                  <td className="py-3 px-4 text-right font-mono">
                    {row.flujo_crisis.toLocaleString('es-EC')}
                  </td>
                  <td
                    className={`py-3 px-4 text-right font-mono font-semibold ${
                      row.variacion_pct < 0 ? 'text-danger-600' : 'text-success-600'
                    }`}
                  >
                    {row.variacion_pct.toFixed(1)}%
                  </td>
                  <td className="py-3 px-4 text-right font-mono text-slate-600">
                    {row.homicidios_crisis_total !== null
                      ? row.homicidios_crisis_total.toLocaleString('es-EC')
                      : 'n/d'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">Homicidios provinciales vs variación de flujos</h2>
        <p className="card-subtitle mb-4">
          La correlación Spearman ρ = 0,35 (p = 0,36) no es significativa: Guayas concentra el
          mayor volumen de homicidios pero apenas cae −12 % por el efecto aeropuerto de Guayaquil.
        </p>
        <ProvinciasScatter data={data} />
      </div>
    </div>
  );
}
