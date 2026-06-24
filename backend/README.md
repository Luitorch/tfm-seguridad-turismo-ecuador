# Backend TFM - API de Seguridad y Turismo Ecuador

API REST en FastAPI que expone los resultados de los analisis del TFM
"Seguridad publica y flujos turisticos internacionales en Ecuador"
(Luis Torres - UNIR, Master Visual Analytics & Big Data).

## Requisitos

- Python 3.10+
- Los CSV de resultados deben existir en `../outputs/`:
  - `tabla_correlacion_lag.csv`
  - `tabla_sensibilidad_mercados.csv`
  - `tabla_provincias_impacto.csv`
  - `tabla_clusters_caracterizacion.csv`
- Opcional: `../data/raw/banco_mundial/API_ST.INT.ARVL_DS2_es_csv_v2_4967.zip`
  (si no esta, se usa el fallback documentado del notebook 03).

## Instalacion y arranque

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La API queda disponible en `http://localhost:8000`.
La documentacion interactiva Swagger en `http://localhost:8000/docs`
y ReDoc en `http://localhost:8000/redoc`.

## Endpoints

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| GET | `/` | Metadatos de la API y listado de endpoints |
| GET | `/health` | Health-check |
| GET | `/api/series/llegadas` | Serie anual de llegadas (BM 2010-2019 + ESI 2023-2024) |
| GET | `/api/correlacion/lag` | Correlacion homicidios -> llegadas para lag 0-3 anos |
| GET | `/api/correlacion/mercados` | Sensibilidad de los top-5 mercados emisores |
| GET | `/api/provincias/impacto` | Variacion del flujo provincial pre vs crisis |
| GET | `/api/clusters/perfiles` | Caracterizacion de los 8 perfiles K-Means |
| GET | `/api/clusters/evolucion` | Evolucion 2023 -> 2024 por cluster |
| GET | `/api/kpis` | Indicadores agregados para tarjetas del dashboard |

## Estructura

```
backend/
  app/
    main.py                 # App FastAPI + CORS + routers + lifecycle
    routers/
      analisis.py           # Endpoints de los 4 analisis
    services/
      data_loader.py        # Carga de CSV con cache en memoria
    models/
      schemas.py            # Modelos Pydantic de las respuestas
  requirements.txt
  README.md
```

## Notas de implementacion

- Los CSV se cargan **una sola vez** al iniciar la app (evento `startup`)
  y quedan cacheados en memoria.
- Si un CSV requerido no existe, los endpoints afectados devuelven
  HTTP 503 con un mensaje claro.
- Endpoints sincronicos (sin `async`): son lecturas O(1) en memoria.
- CORS abierto a `http://localhost:3000` y `*` para desarrollo.
