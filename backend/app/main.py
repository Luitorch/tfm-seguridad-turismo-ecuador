"""
Backend FastAPI del TFM "Seguridad publica y flujos turisticos internacionales en Ecuador".

Sirve los resultados de los analisis estadisticos (Banco Mundial + ESI 2023-2025)
para el dashboard frontend.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from app.routers import analisis
    from app.services import data_loader
except ImportError:
    from backend.app.routers import analisis
    from backend.app.services import data_loader

# Logging basico
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Metadatos OpenAPI / Swagger
# ---------------------------------------------------------------------------
TAGS_METADATA = [
    {
        "name": "Serie temporal",
        "description": "Series anuales de llegadas internacionales (Banco Mundial + ESI).",
    },
    {
        "name": "Correlacion",
        "description": "Analisis 2: correlacion con rezagos y sensibilidad por mercado.",
    },
    {
        "name": "Provincias",
        "description": "Analisis 3: impacto del flujo turistico provincial pre vs crisis.",
    },
    {
        "name": "Clusters",
        "description": "Analisis 4: segmentacion K-Means y evolucion 2023->2024.",
    },
    {
        "name": "KPIs",
        "description": "Indicadores agregados para tarjetas del dashboard.",
    },
    {
        "name": "Sistema",
        "description": "Endpoints de health-check y metadatos de la API.",
    },
]


app = FastAPI(
    title="TFM Seguridad y Turismo Ecuador API",
    description=(
        "API REST que expone los resultados de los analisis del TFM "
        "(Luis Torres - UNIR, Master Visual Analytics & Big Data). "
        "Datos: Banco Mundial ST.INT.ARVL, UNODC, MDI, INEC ESI 2023-2025."
    ),
    version="1.0.0",
    openapi_tags=TAGS_METADATA,
)


# ---------------------------------------------------------------------------
# CORS - frontend local (Next.js o Vite) y comodin para desarrollo
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(analisis.router, prefix="/api")


# ---------------------------------------------------------------------------
# Eventos de ciclo de vida: precarga de CSVs al iniciar
# ---------------------------------------------------------------------------
@app.on_event("startup")
def startup_precargar_datos() -> None:
    """Precarga los CSV en memoria para que el primer request sea rapido."""
    try:
        data_loader.precargar_todo()
        logger.info("Precarga de datos completada")
    except Exception as exc:  # pragma: no cover
        logger.error("Error en precarga: %s", exc)


# ---------------------------------------------------------------------------
# Endpoints de sistema
# ---------------------------------------------------------------------------
@app.get("/", tags=["Sistema"], summary="Informacion general de la API")
def root() -> dict:
    """Pagina raiz con metadatos y listado de endpoints disponibles."""
    return {
        "api": "TFM Seguridad y Turismo Ecuador",
        "version": "1.0.0",
        "autor": "Luis Torres - UNIR",
        "descripcion": (
            "Backend que sirve los resultados de los 4 analisis del TFM "
            "(tendencias, correlacion con lag, impacto provincial, clusters)."
        ),
        "documentacion": "/docs",
        "endpoints": [
            "/api/series/llegadas",
            "/api/correlacion/lag",
            "/api/correlacion/mercados",
            "/api/provincias/impacto",
            "/api/clusters/perfiles",
            "/api/clusters/evolucion",
            "/api/kpis",
        ],
    }


@app.get("/health", tags=["Sistema"], summary="Health-check del servicio")
def health() -> dict:
    """Health-check trivial para monitoreo / docker."""
    return {"status": "ok"}
