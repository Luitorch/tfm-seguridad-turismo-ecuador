"""
Servicio de carga de datos.

Lee una sola vez los CSVs de `outputs/` y la serie temporal de llegadas
(BM + ESI) en memoria. Cachea los DataFrames y los KPIs derivados para
que los endpoints sean lecturas O(1).
"""

from __future__ import annotations

import io
import logging
import os
import zipfile
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Rutas base. Se calcula la raiz del proyecto subiendo desde este archivo:
# backend/app/services/data_loader.py -> .../tfm_inicial
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[3]
OUTPUTS_DIR = ROOT_DIR / "outputs"
DATA_RAW_DIR = ROOT_DIR / "data" / "raw"

# Mapa: nombre logico -> ruta del archivo
CSV_PATHS: Dict[str, Path] = {
    "correlacion_lag": OUTPUTS_DIR / "tabla_correlacion_lag.csv",
    "mercados": OUTPUTS_DIR / "tabla_sensibilidad_mercados.csv",
    "provincias": OUTPUTS_DIR / "tabla_provincias_impacto.csv",
    "clusters": OUTPUTS_DIR / "tabla_clusters_caracterizacion.csv",
}

# Cache simple en memoria
_CACHE: Dict[str, pd.DataFrame] = {}
_LLEGADAS_CACHE: Optional[pd.DataFrame] = None
_KPIS_CACHE: Optional[dict] = None


# ---------------------------------------------------------------------------
# Carga generica de CSV con cache
# ---------------------------------------------------------------------------
def load_csv(name: str) -> pd.DataFrame:
    """Carga un CSV registrado en CSV_PATHS. Cachea en memoria."""
    if name in _CACHE:
        return _CACHE[name]

    ruta = CSV_PATHS.get(name)
    if ruta is None:
        raise KeyError(f"CSV no registrado: {name}")
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontro el CSV: {ruta}")

    df = pd.read_csv(ruta)
    _CACHE[name] = df
    logger.info("CSV cargado: %s (%d filas)", name, len(df))
    return df


# ---------------------------------------------------------------------------
# Serie de llegadas (BM 2010-2019 + ESI 2023-2024)
# ---------------------------------------------------------------------------
def load_llegadas() -> pd.DataFrame:
    """
    Construye la serie temporal de llegadas internacionales.

    Origen:
      - Banco Mundial ST.INT.ARVL (2010-2019 / hasta 2022 si existiera)
      - ESI 2023 y 2024 (agregado anual de turistas extranjeros con motivo Turismo)

    Si no se puede leer alguna fuente real, se usa la serie historica
    documentada en los notebooks 03 y 05 como fallback (fuente "fallback").
    """
    global _LLEGADAS_CACHE
    if _LLEGADAS_CACHE is not None:
        return _LLEGADAS_CACHE

    serie_bm = _load_bm_arrivals()
    serie_esi = _ESI_FALLBACK.copy()  # ESI 2023-2024 (valores conocidos)

    if serie_bm is None or serie_bm.empty:
        logger.warning("No se pudo leer el ZIP del Banco Mundial; uso fallback documentado")
        serie_bm = _BM_FALLBACK.copy()

    df = pd.concat([serie_bm, serie_esi], ignore_index=True)
    df = df.drop_duplicates(subset="anio", keep="last").sort_values("anio").reset_index(drop=True)
    df["anio"] = df["anio"].astype(int)
    df["llegadas"] = df["llegadas"].astype(int)
    _LLEGADAS_CACHE = df
    return df


def _load_bm_arrivals() -> Optional[pd.DataFrame]:
    """Lee el ZIP del Banco Mundial y devuelve llegadas anuales de Ecuador."""
    zip_path = DATA_RAW_DIR / "banco_mundial" / "API_ST.INT.ARVL_DS2_es_csv_v2_4967.zip"
    if not zip_path.exists():
        return None
    try:
        with zipfile.ZipFile(zip_path) as z:
            nombres = [n for n in z.namelist() if n.endswith(".csv") and "Metadata" not in n]
            if not nombres:
                return None
            with z.open(nombres[0]) as f:
                raw = pd.read_csv(io.BytesIO(f.read()), skiprows=4, encoding="utf-8")

        ecu = raw[raw["Country Code"] == "ECU"].copy()
        anios = [str(y) for y in range(2010, 2023)]
        cols_existentes = [c for c in anios if c in ecu.columns]
        long = (
            ecu[["Country Name"] + cols_existentes]
            .melt(id_vars="Country Name", var_name="anio", value_name="llegadas")
        )
        long["anio"] = long["anio"].astype(int)
        long = long.dropna(subset=["llegadas"])
        long["llegadas"] = long["llegadas"].astype(int)
        long["fuente"] = "BM"
        return long[["anio", "llegadas", "fuente"]].reset_index(drop=True)
    except Exception as exc:  # pragma: no cover - log y fallback
        logger.error("Error leyendo BM ZIP: %s", exc)
        return None


# Fallback documentado en notebooks 03/05 - se usa solo si no hay ZIP del BM.
_BM_FALLBACK = pd.DataFrame(
    [
        {"anio": 2010, "llegadas": 1047000, "fuente": "BM"},
        {"anio": 2011, "llegadas": 1141000, "fuente": "BM"},
        {"anio": 2012, "llegadas": 1272000, "fuente": "BM"},
        {"anio": 2013, "llegadas": 1364000, "fuente": "BM"},
        {"anio": 2014, "llegadas": 1695000, "fuente": "BM"},
        {"anio": 2015, "llegadas": 1676000, "fuente": "BM"},
        {"anio": 2016, "llegadas": 1569000, "fuente": "BM"},
        {"anio": 2017, "llegadas": 1806000, "fuente": "BM"},
        {"anio": 2018, "llegadas": 2535000, "fuente": "BM"},
        {"anio": 2019, "llegadas": 2108000, "fuente": "BM"},
    ]
)

# ESI: agregados anuales de extranjeros con motivo Turismo (notebook 03)
_ESI_FALLBACK = pd.DataFrame(
    [
        {"anio": 2023, "llegadas": 863161, "fuente": "ESI"},
        {"anio": 2024, "llegadas": 703110, "fuente": "ESI"},
    ]
)


# ---------------------------------------------------------------------------
# Evolucion de clusters 2023 -> 2024.
# Tomado del notebook 05 (cuotas de muestra y variacion %)
# ---------------------------------------------------------------------------
_CLUSTER_EVOLUCION = [
    {"cluster": 0, "pct_2023": 16.33, "pct_2024": 22.64, "cambio_pct": 30.10},
    {"cluster": 1, "pct_2023": 17.08, "pct_2024": 17.25, "cambio_pct": -5.26},
    {"cluster": 2, "pct_2023": 21.36, "pct_2024": 15.38, "cambio_pct": -32.42},
    {"cluster": 3, "pct_2023": 35.92, "pct_2024": 36.50, "cambio_pct": -4.65},
    {"cluster": 4, "pct_2023": 1.57, "pct_2024": 1.37, "cambio_pct": -18.36},
    {"cluster": 5, "pct_2023": 1.90, "pct_2024": 2.23, "cambio_pct": 9.86},
    {"cluster": 6, "pct_2023": 0.22, "pct_2024": 0.14, "cambio_pct": -39.80},
    {"cluster": 7, "pct_2023": 5.62, "pct_2024": 4.49, "cambio_pct": -25.04},
]


def load_cluster_evolucion() -> list[dict]:
    """Devuelve la evolucion 2023->2024 por cluster con su nombre."""
    perfiles = load_csv("clusters")
    nombre_por_cluster = dict(zip(perfiles["cluster"].astype(int), perfiles["nombre"]))
    out = []
    for row in _CLUSTER_EVOLUCION:
        c = int(row["cluster"])
        out.append(
            {
                "cluster": c,
                "nombre": nombre_por_cluster.get(c, f"Cluster {c}"),
                "pct_2023": row["pct_2023"],
                "pct_2024": row["pct_2024"],
                "cambio_pct": row["cambio_pct"],
            }
        )
    return out


# ---------------------------------------------------------------------------
# KPIs agregados
# ---------------------------------------------------------------------------
def get_kpis() -> dict:
    """Calcula los KPIs principales a partir de los CSVs cacheados."""
    global _KPIS_CACHE
    if _KPIS_CACHE is not None:
        return _KPIS_CACHE

    serie = load_llegadas()
    correlacion = load_csv("correlacion_lag")
    mercados = load_csv("mercados")
    provincias = load_csv("provincias")
    evolucion = load_cluster_evolucion()

    # Pico pre-crisis: maximo de llegadas <= 2019 (BM)
    pre = serie[serie["anio"] <= 2019]
    fila_pre = pre.loc[pre["llegadas"].idxmax()]
    llegadas_pre = int(fila_pre["llegadas"])
    anio_pre = int(fila_pre["anio"])

    # Llegadas en crisis: ultimo ano ESI disponible (2024)
    crisis = serie[serie["anio"] >= 2023]
    if not crisis.empty:
        fila_crisis = crisis.loc[crisis["anio"].idxmax()]
        llegadas_crisis = int(fila_crisis["llegadas"])
        anio_crisis = int(fila_crisis["anio"])
    else:
        llegadas_crisis = int(serie.iloc[-1]["llegadas"])
        anio_crisis = int(serie.iloc[-1]["anio"])

    variacion_pct = round((llegadas_crisis - llegadas_pre) / llegadas_pre * 100, 2)

    # Lag optimo: |pearson_r| maximo
    corr_valid = correlacion.dropna(subset=["pearson_r"]).copy()
    corr_valid["abs_r"] = corr_valid["pearson_r"].abs()
    fila_lag = corr_valid.loc[corr_valid["abs_r"].idxmax()]
    lag_opt = int(fila_lag["lag"])
    corr_lag_opt = round(float(fila_lag["pearson_r"]), 4)

    # Mercado mas sensible (r mas negativo)
    fila_mkt = mercados.loc[mercados["pearson_r"].idxmin()]
    mercado_top = str(fila_mkt["mercado"])
    r_mkt = round(float(fila_mkt["pearson_r"]), 4)

    # Cluster mas colapsado / mas resiliente
    evol_sorted = sorted(evolucion, key=lambda x: x["cambio_pct"])
    cluster_col = evol_sorted[0]
    cluster_res = evol_sorted[-1]

    # Provincia mas afectada (variacion mas negativa)
    prov_valid = provincias.dropna(subset=["variacion_pct"])
    fila_prov = prov_valid.loc[prov_valid["variacion_pct"].idxmin()]

    _KPIS_CACHE = {
        "pico_pre_crisis_anio": anio_pre,
        "pico_pre_crisis_valor": llegadas_pre,
        "crisis_anio": anio_crisis,
        "crisis_valor": llegadas_crisis,
        "variacion_pct": variacion_pct,
        "lag_optimo": lag_opt,
        "pearson_r_lag_optimo": corr_lag_opt,
        "mercado_mas_sensible": mercado_top,
        "mercado_pearson_r": r_mkt,
        "cluster_mas_colapsado": int(cluster_col["cluster"]),
        "cluster_mas_colapsado_nombre": cluster_col["nombre"],
        "cluster_mas_colapsado_cambio_pct": round(float(cluster_col["cambio_pct"]), 2),
        "cluster_mas_resiliente": int(cluster_res["cluster"]),
        "cluster_mas_resiliente_nombre": cluster_res["nombre"],
        "cluster_mas_resiliente_cambio_pct": round(float(cluster_res["cambio_pct"]), 2),
        "provincia_mas_afectada": str(fila_prov["provincia"]),
        "provincia_mas_afectada_variacion_pct": round(float(fila_prov["variacion_pct"]), 2),
    }
    return _KPIS_CACHE


# ---------------------------------------------------------------------------
# Precarga (llamada desde main.py)
# ---------------------------------------------------------------------------
def precargar_todo() -> None:
    """Fuerza la carga inicial de todos los CSV registrados."""
    for nombre, ruta in CSV_PATHS.items():
        if not ruta.exists():
            logger.warning("Falta CSV %s en %s", nombre, ruta)
            continue
        load_csv(nombre)
    load_llegadas()
    try:
        get_kpis()
    except Exception as exc:
        logger.warning("No se pudieron precalcular KPIs: %s", exc)
