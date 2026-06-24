import { api } from '@/lib/api';
import { ClustersEvolucionChart } from '@/components/charts/ClustersEvolucionChart';

export default async function PerfilesPage() {
  const [perfiles, evolucion] = await Promise.all([
    api.clustersPerfiles(),
    api.clustersEvolucion(),
  ]);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Perfiles de turista</h1>
        <p className="text-slate-600 mt-2 max-w-3xl">
          Análisis 4 — K-Means sobre 117 000 registros del ESI 2023-2025 (muestra estratificada).
          Ocho clústeres identificados con Silhouette = 0,21.
        </p>
      </header>

      <div className="card">
        <h2 className="card-title">Evolución relativa 2023 → 2024</h2>
        <p className="card-subtitle mb-4">
          Segmentos resilientes (verde) y colapsados (rojo) durante el período de crisis.
        </p>
        <ClustersEvolucionChart data={evolucion} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {perfiles.map((p) => {
          const ev = evolucion.find((e) => e.cluster === p.cluster);
          const cambio = ev?.cambio_pct ?? 0;
          const isPositive = cambio > 0;
          return (
            <div key={p.cluster} className="card">
              <div className="flex items-baseline justify-between">
                <h3 className="card-title text-base">C{p.cluster}</h3>
                <span
                  className={`text-sm font-semibold ${
                    isPositive ? 'text-success-600' : 'text-danger-600'
                  }`}
                >
                  {isPositive ? '+' : ''}
                  {cambio.toFixed(1)}%
                </span>
              </div>
              <p className="text-xs uppercase tracking-wider text-slate-500 mt-1">{p.nombre}</p>
              <dl className="text-xs space-y-1.5 mt-4 text-slate-600">
                <div className="flex justify-between">
                  <dt>Tamaño</dt>
                  <dd>
                    {p.n.toLocaleString('es-EC')} ({p.pct.toFixed(1)}%)
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt>Edad media</dt>
                  <dd>{p.edad_media.toFixed(0)} años</dd>
                </div>
                <div className="flex justify-between">
                  <dt>Continente</dt>
                  <dd>{p.continente_top1}</dd>
                </div>
                <div className="flex justify-between">
                  <dt>Vía</dt>
                  <dd>{p.via_top1}</dd>
                </div>
                <div className="flex justify-between">
                  <dt>Sexo</dt>
                  <dd>
                    {p.sexo_predominante} ({p.sexo_pct.toFixed(0)}%)
                  </dd>
                </div>
              </dl>
              <p className="text-xs text-slate-500 mt-3 italic">
                {p.top5_nacionalidades}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
