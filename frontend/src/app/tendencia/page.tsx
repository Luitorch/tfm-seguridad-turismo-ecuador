import { api } from '@/lib/api';
import { TendenciaChart } from '@/components/charts/TendenciaChart';

export default async function TendenciaPage() {
  const data = await api.serieLlegadas();
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Tendencia y estacionalidad</h1>
        <p className="text-slate-600 mt-2 max-w-3xl">
          Análisis 1 — Descomposición STL de la serie de llegadas internacionales 2010-2025.
          Combina datos anuales del Banco Mundial (2010-2022) con la agregación del ESI INEC
          (2023-2024).
        </p>
      </header>

      <div className="card">
        <h2 className="card-title">Llegadas internacionales por año</h2>
        <p className="card-subtitle mb-4">
          El cambio de pendiente en 2022 coincide con el inicio de la escalada de homicidios y
          atenúa la recuperación post-COVID.
        </p>
        <TendenciaChart data={data} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="card">
          <h3 className="card-title text-base">Pre-pandemia</h3>
          <p className="text-sm text-slate-600">
            Crecimiento sostenido 2010-2019, alcanzando 2,1 millones de llegadas en 2019.
          </p>
        </div>
        <div className="card">
          <h3 className="card-title text-base">Caída pandémica</h3>
          <p className="text-sm text-slate-600">
            Contracción abrupta en 2020-2021 por COVID-19.
          </p>
        </div>
        <div className="card">
          <h3 className="card-title text-base">Quiebre 2022</h3>
          <p className="text-sm text-slate-600 text-danger-600">
            Interrupción de la recuperación coincidente con la crisis de seguridad.
          </p>
        </div>
      </div>
    </div>
  );
}
