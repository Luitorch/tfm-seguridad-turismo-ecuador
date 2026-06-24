// Cliente API para el backend FastAPI del TFM
// En el navegador usa el rewrite /api/* -> http://localhost:8000/api/* (ver next.config.mjs).
// En el servidor (Server Components / SSR) Node necesita una URL absoluta, así que
// apunta directamente al backend (configurable con la variable de entorno API_BASE).

const BASE =
  typeof window === 'undefined'
    ? process.env.API_BASE ?? 'http://localhost:8000/api'
    : '/api';

export interface SerieLlegada {
  anio: number;
  llegadas: number;
  fuente: string;
}

export interface CorrelacionLag {
  lag: number;
  n: number;
  pearson_r: number;
  pearson_p: number;
  spearman_r: number;
  spearman_p: number;
}

export interface MercadoSensibilidad {
  mercado: string;
  n: number;
  pearson_r: number;
  pearson_p: number;
  spearman_r: number;
  spearman_p: number;
  lag_usado: number;
}

export interface ProvinciaImpacto {
  provincia: string;
  flujo_pre: number;
  flujo_crisis: number;
  variacion_pct: number;
  homicidios_crisis_total: number | null;
}

export interface ClusterPerfil {
  cluster: number;
  nombre: string;
  n: number;
  pct: number;
  edad_media: number;
  edad_mediana: number;
  motivo_top1: string;
  motivo_top1_pct: number;
  continente_top1: string;
  continente_top1_pct: number;
  top5_nacionalidades: string;
  via_top1: string;
  via_top1_pct: number;
  sexo_predominante: string;
  sexo_pct: number;
}

export interface ClusterEvolucion {
  cluster: number;
  nombre: string;
  pct_2023: number;
  pct_2024: number;
  cambio_pct: number;
}

export interface Kpis {
  pico_pre_crisis_anio: number;
  pico_pre_crisis_valor: number;
  crisis_anio: number;
  crisis_valor: number;
  variacion_pct: number;
  lag_optimo: number;
  pearson_r_lag_optimo: number;
  mercado_mas_sensible: string;
  mercado_pearson_r: number;
  cluster_mas_colapsado: number;
  cluster_mas_colapsado_nombre: string;
  cluster_mas_colapsado_cambio_pct: number;
  cluster_mas_resiliente: number;
  cluster_mas_resiliente_nombre: string;
  cluster_mas_resiliente_cambio_pct: number;
  provincia_mas_afectada: string;
  provincia_mas_afectada_variacion_pct: number;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`API ${path} respondió ${res.status}`);
  return res.json() as Promise<T>;
}

export const api = {
  serieLlegadas: () => get<SerieLlegada[]>('/series/llegadas'),
  correlacionLag: () => get<CorrelacionLag[]>('/correlacion/lag'),
  correlacionMercados: () => get<MercadoSensibilidad[]>('/correlacion/mercados'),
  provinciasImpacto: () => get<ProvinciaImpacto[]>('/provincias/impacto'),
  clustersPerfiles: () => get<ClusterPerfil[]>('/clusters/perfiles'),
  clustersEvolucion: () => get<ClusterEvolucion[]>('/clusters/evolucion'),
  kpis: () => get<Kpis>('/kpis'),
};
