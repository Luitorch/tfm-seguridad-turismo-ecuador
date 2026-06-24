"""
Modelos Pydantic para las respuestas de la API.

Cada modelo refleja la estructura de los CSV de outputs/ o de las series
calculadas en los notebooks de analisis del TFM.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Serie temporal de llegadas (BM 2010-2022 + ESI 2023-2024)
# ---------------------------------------------------------------------------
class SerieLlegada(BaseModel):
    """Punto de la serie temporal anual de llegadas internacionales."""
    anio: int = Field(..., description="Anio del registro")
    llegadas: int = Field(..., description="Numero de llegadas internacionales")
    fuente: Optional[str] = Field(
        None, description="Origen del dato (BM = Banco Mundial, ESI = Entradas/Salidas Internacionales)"
    )


# ---------------------------------------------------------------------------
# Tabla correlacion con lag (Analisis 2)
# ---------------------------------------------------------------------------
class CorrelacionLag(BaseModel):
    """Coeficientes de correlacion homicidios->llegadas para cada lag (0-3 anos)."""
    lag: int
    n: int
    pearson_r: Optional[float] = None
    pearson_p: Optional[float] = None
    spearman_r: Optional[float] = None
    spearman_p: Optional[float] = None


# ---------------------------------------------------------------------------
# Tabla sensibilidad por mercado emisor (Analisis 2)
# ---------------------------------------------------------------------------
class MercadoSensibilidad(BaseModel):
    """Sensibilidad de cada mercado emisor a la crisis de seguridad."""
    mercado: str
    n: int
    pearson_r: Optional[float] = None
    pearson_p: Optional[float] = None
    spearman_r: Optional[float] = None
    spearman_p: Optional[float] = None
    lag_usado: Optional[int] = None


# ---------------------------------------------------------------------------
# Tabla provincias impacto (Analisis 3)
# ---------------------------------------------------------------------------
class ProvinciaImpacto(BaseModel):
    """Variacion del flujo turistico por provincia entre periodo pre y crisis."""
    provincia: str
    flujo_pre: Optional[float] = None
    flujo_crisis: Optional[float] = None
    variacion_pct: Optional[float] = None
    homicidios_crisis_total: Optional[float] = None


# ---------------------------------------------------------------------------
# Perfil de cluster (Analisis 4)
# ---------------------------------------------------------------------------
class ClusterPerfil(BaseModel):
    """Caracterizacion de un cluster K-Means."""
    cluster: int
    nombre: str
    n: int
    pct: float
    edad_media: float
    edad_mediana: float
    motivo_top1: str
    motivo_top1_pct: float
    continente_top1: str
    continente_top1_pct: Optional[float] = None
    top5_nacionalidades: str
    via_top1: str
    via_top1_pct: float
    sexo_predominante: str
    sexo_pct: float


# ---------------------------------------------------------------------------
# Evolucion 2023 -> 2024 por cluster (Analisis 4)
# ---------------------------------------------------------------------------
class ClusterEvolucion(BaseModel):
    """Cambio en la cuota de muestra de cada cluster entre 2023 y 2024."""
    cluster: int
    nombre: str
    pct_2023: float = Field(..., description="% del total de la muestra 2023")
    pct_2024: float = Field(..., description="% del total de la muestra 2024")
    cambio_pct: float = Field(..., description="Variacion % de conteos absolutos 2023->2024")


# ---------------------------------------------------------------------------
# KPIs globales
# ---------------------------------------------------------------------------
class KPIs(BaseModel):
    """Indicadores principales del TFM para el dashboard."""
    pico_pre_crisis_anio: int = Field(..., description="Ano del pico pre-crisis")
    pico_pre_crisis_valor: int = Field(..., description="Llegadas pico pre-crisis (BM)")
    crisis_anio: int = Field(..., description="Ano critico (ESI)")
    crisis_valor: int = Field(..., description="Llegadas en el ano critico (ESI)")
    variacion_pct: float = Field(..., description="% de variacion pico->crisis")
    lag_optimo: int = Field(..., description="Lag (anos) con mayor |r| entre homicidios y llegadas")
    pearson_r_lag_optimo: float = Field(..., description="Pearson r en el lag optimo")
    mercado_mas_sensible: str = Field(..., description="Mercado emisor con r mas negativo")
    mercado_pearson_r: float
    cluster_mas_colapsado: int = Field(..., description="Cluster con peor variacion 2023->2024")
    cluster_mas_colapsado_nombre: str
    cluster_mas_colapsado_cambio_pct: float
    cluster_mas_resiliente: int
    cluster_mas_resiliente_nombre: str
    cluster_mas_resiliente_cambio_pct: float
    provincia_mas_afectada: str
    provincia_mas_afectada_variacion_pct: float
