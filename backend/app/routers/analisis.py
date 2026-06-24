"""
Endpoints del dashboard del TFM.

Cada endpoint expone un resultado de los analisis estadisticos del TFM:
- Serie temporal de llegadas
- Correlacion con lag
- Sensibilidad de mercados emisores
- Impacto provincial
- Perfiles de clusters K-Means
- Evolucion 2023->2024 por cluster
- KPIs agregados para el dashboard
"""

from __future__ import annotations

import logging
import math
from typing import List

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    ClusterEvolucion,
    ClusterPerfil,
    CorrelacionLag,
    KPIs,
    MercadoSensibilidad,
    ProvinciaImpacto,
    SerieLlegada,
)
from app.services import data_loader

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _df_to_records(df) -> list[dict]:
    """Convierte un DataFrame a lista de dicts saneando NaN -> None."""
    records = df.to_dict(orient="records")
    saneados = []
    for r in records:
        nuevo = {}
        for k, v in r.items():
            if isinstance(v, float) and math.isnan(v):
                nuevo[k] = None
            else:
                nuevo[k] = v
        saneados.append(nuevo)
    return saneados


def _safe_load(nombre: str):
    """Wrapper que convierte FileNotFoundError -> HTTP 503."""
    try:
        return data_loader.load_csv(nombre)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error cargando {nombre}: {exc}")


# ---------------------------------------------------------------------------
# 1) Serie temporal de llegadas
# ---------------------------------------------------------------------------
@router.get(
    "/series/llegadas",
    response_model=List[SerieLlegada],
    tags=["Serie temporal"],
    summary="Serie anual de llegadas internacionales (BM 2010-2019 + ESI 2023-2024)",
)
def get_serie_llegadas():
    """Devuelve la serie unificada usada en los analisis 1, 2 y 4."""
    try:
        df = data_loader.load_llegadas()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"No se pudo construir la serie: {exc}")
    return _df_to_records(df)


# ---------------------------------------------------------------------------
# 2) Correlacion con lag
# ---------------------------------------------------------------------------
@router.get(
    "/correlacion/lag",
    response_model=List[CorrelacionLag],
    tags=["Correlacion"],
    summary="Correlacion homicidios -> llegadas para lag 0-3 anos",
)
def get_correlacion_lag():
    df = _safe_load("correlacion_lag")
    return _df_to_records(df)


# ---------------------------------------------------------------------------
# 3) Sensibilidad por mercado emisor
# ---------------------------------------------------------------------------
@router.get(
    "/correlacion/mercados",
    response_model=List[MercadoSensibilidad],
    tags=["Correlacion"],
    summary="Sensibilidad de los principales mercados emisores a la crisis",
)
def get_correlacion_mercados():
    df = _safe_load("mercados")
    return _df_to_records(df)


# ---------------------------------------------------------------------------
# 4) Impacto provincial
# ---------------------------------------------------------------------------
@router.get(
    "/provincias/impacto",
    response_model=List[ProvinciaImpacto],
    tags=["Provincias"],
    summary="Variacion del flujo turistico por provincia (pre vs crisis)",
)
def get_provincias_impacto():
    df = _safe_load("provincias")
    return _df_to_records(df)


# ---------------------------------------------------------------------------
# 5) Perfiles de clusters
# ---------------------------------------------------------------------------
@router.get(
    "/clusters/perfiles",
    response_model=List[ClusterPerfil],
    tags=["Clusters"],
    summary="Caracterizacion de los 8 perfiles K-Means",
)
def get_clusters_perfiles():
    df = _safe_load("clusters")
    return _df_to_records(df)


# ---------------------------------------------------------------------------
# 6) Evolucion 2023 -> 2024 por cluster
# ---------------------------------------------------------------------------
@router.get(
    "/clusters/evolucion",
    response_model=List[ClusterEvolucion],
    tags=["Clusters"],
    summary="Evolucion de la cuota de cada cluster entre 2023 y 2024",
)
def get_clusters_evolucion():
    try:
        return data_loader.load_cluster_evolucion()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error: {exc}")


# ---------------------------------------------------------------------------
# 7) KPIs para tarjetas del dashboard
# ---------------------------------------------------------------------------
@router.get(
    "/kpis",
    response_model=KPIs,
    tags=["KPIs"],
    summary="Indicadores agregados para tarjetas del dashboard",
)
def get_kpis():
    try:
        return data_loader.get_kpis()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error calculando KPIs: {exc}")
