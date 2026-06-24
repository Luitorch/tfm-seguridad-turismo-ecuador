import { api } from '@/lib/api';
import { KpiCard } from '@/components/KpiCard';

export default async function Home() {
  let kpis;
  try {
    kpis = await api.kpis();
  } catch (e) {
    return (
      <div className="card">
        <h2 className="card-title text-danger-600">Backend no disponible</h2>
        <p className="card-subtitle">
          Asegúrate de levantar el API FastAPI con <code className="bg-slate-100 px-2 py-0.5 rounded">uvicorn app.main:app --reload</code> desde la carpeta <code>backend/</code>.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Resumen ejecutivo</h1>
        <p className="text-slate-600 mt-2 max-w-3xl">
          Impacto cuantificado de la crisis de seguridad pública del período 2022-2024 sobre los
          flujos turísticos internacionales del Ecuador, mediante cuatro análisis complementarios
          aplicados a ~18,6 millones de registros oficiales.
        </p>
      </header>

      <section>
        <h2 className="text-sm uppercase tracking-wider text-slate-500 mb-4">Indicadores clave</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard
            label={`Pico pre-crisis (${kpis.pico_pre_crisis_anio})`}
            value={kpis.pico_pre_crisis_valor.toLocaleString('es-EC')}
            sublabel="Llegadas internacionales"
          />
          <KpiCard
            label={`Crisis (${kpis.crisis_anio})`}
            value={kpis.crisis_valor.toLocaleString('es-EC')}
            sublabel="Llegadas internacionales"
            tone="negative"
          />
          <KpiCard
            label="Variación nacional"
            value={`${kpis.variacion_pct.toFixed(1)}%`}
            sublabel={`${kpis.pico_pre_crisis_anio} → ${kpis.crisis_anio}`}
            tone="negative"
          />
          <KpiCard
            label="Rezago óptimo"
            value={`${kpis.lag_optimo} año${kpis.lag_optimo === 1 ? '' : 's'}`}
            sublabel={`Pearson r = ${kpis.pearson_r_lag_optimo.toFixed(3)}`}
          />
          <KpiCard
            label="Mercado más sensible"
            value={kpis.mercado_mas_sensible}
            sublabel={`r = ${kpis.mercado_pearson_r.toFixed(3)}`}
            tone="negative"
          />
          <KpiCard
            label="Provincia más afectada"
            value={kpis.provincia_mas_afectada}
            sublabel={`Variación ${kpis.provincia_mas_afectada_variacion_pct.toFixed(1)}%`}
            tone="negative"
          />
          <KpiCard
            label="Cluster colapsado"
            value={`C${kpis.cluster_mas_colapsado}`}
            sublabel={`${kpis.cluster_mas_colapsado_cambio_pct.toFixed(1)}%`}
            tone="negative"
          />
          <KpiCard
            label="Cluster resiliente"
            value={`C${kpis.cluster_mas_resiliente}`}
            sublabel={`+${kpis.cluster_mas_resiliente_cambio_pct.toFixed(1)}%`}
            tone="positive"
          />
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="card-title">Diagnóstico</h3>
          <p className="text-sm text-slate-600 leading-relaxed">
            La crisis de seguridad pública del período 2022-2024 ha tenido un impacto
            estadísticamente detectable y económicamente relevante sobre el turismo internacional
            ecuatoriano. La trayectoria de recuperación post-COVID se interrumpe en 2022 y
            converge con una caída del{' '}
            <strong className="text-danger-600">
              {Math.abs(kpis.variacion_pct).toFixed(1)}%
            </strong>{' '}
            respecto al pico pre-pandemia.
          </p>
        </div>
        <div className="card">
          <h3 className="card-title">Naturaleza del efecto</h3>
          <p className="text-sm text-slate-600 leading-relaxed">
            La correlación negativa con rezago de {kpis.lag_optimo} año
            {kpis.lag_optimo === 1 ? '' : 's'} (Spearman ρ = −0,955; p &lt; 10⁻⁵ a lag 1) sugiere
            que las decisiones de viaje incorporan información sobre seguridad con un horizonte de
            anticipación significativo. Los mercados de larga distancia y el turismo terrestre
            regional son los más sensibles.
          </p>
        </div>
      </section>
    </div>
  );
}
