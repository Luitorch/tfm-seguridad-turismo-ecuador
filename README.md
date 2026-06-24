# Seguridad pública y flujos turísticos internacionales en Ecuador

**Análisis de impacto mediante técnicas de Big Data y Visual Analytics (2010-2025)**

Trabajo Fin de Máster · Máster Universitario en Análisis y Visualización de Datos Masivos (Visual Analytics & Big Data) · Universidad Internacional de La Rioja (UNIR)

**Autor:** Luis Torres · 2026

---

## Resumen

Este repositorio contiene el código, los datos procesados y las visualizaciones generadas para un piloto experimental que cuantifica el impacto de la crisis de seguridad pública ecuatoriana del período 2022-2024 sobre los flujos turísticos internacionales. El estudio integra cuatro fuentes oficiales —los registros individuales de Entradas y Salidas Internacionales del INEC (aproximadamente 18,6 millones de registros y 6,4 GB), las series anuales del Banco Mundial, las estadísticas mensuales de homicidios intencionales del Ministerio del Interior y el catastro turístico del MINTUR— y aplica cuatro análisis complementarios: descomposición STL, correlación con rezago y prueba de causalidad de Granger, análisis espacial provincial y agrupamiento K-Means de perfiles de turista. El procesamiento se realiza con DuckDB como motor analítico in-process, lo que demuestra la viabilidad del análisis de Big Data turístico en infraestructura single-node.

## Hallazgos principales

- **Correlación negativa robusta:** la tasa de homicidios y las llegadas turísticas muestran correlación de Spearman ρ = −0,955 a un año de rezago (p < 10⁻⁵).
- **Sensibilidad por mercado:** China lidera la elasticidad (r = −0,90), seguida de Perú, Colombia, España y Estados Unidos con coeficientes prácticamente equivalentes.
- **Impacto territorial:** Esmeraldas, Santa Elena y Carchi registran caídas de entre el 80 y el 93 % en flujos; Pichincha y Galápagos mantienen o crecen.
- **Recomposición del visitante:** ocho clústeres identifican mercados de larga distancia (Asia, África, Francia) como los más colapsados y al turismo latino regional aéreo como segmento resiliente.

## Estructura del repositorio

```
tfm-seguridad-turismo-ecuador/
├── data/
│   ├── raw/              # Fuentes originales (no versionadas por tamaño)
│   ├── processed/        # Datos agregados con DuckDB
│   └── FUENTES_DATOS.md
├── notebooks/            # 5 notebooks Jupyter numerados
│   ├── 01_exploracion_datos.ipynb
│   ├── 02_estacionalidad_tendencia.ipynb
│   ├── 03_correlacion_lag_granger.ipynb
│   ├── 04_espacial_provincial.ipynb (vía script)
│   └── 05_kmeans_perfiles.ipynb
├── src/
│   ├── data/             # Ingesta y generación de agregados
│   ├── analysis/         # Scripts de análisis
│   └── visualization/    # Helpers de visualización
├── backend/              # FastAPI sirviendo los resultados
├── frontend/             # Dashboard Next.js + Tailwind
├── outputs/              # Carpeta destino de figuras y tablas (se generan al ejecutar)
└── README.md
```

## Reproducción

### Requisitos

- Python 3.10 o superior
- 16 GB de RAM (para procesamiento del ESI completo)
- Node.js 18+ (sólo para el frontend)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/Luitorch/tfm-seguridad-turismo-ecuador.git
cd tfm-seguridad-turismo-ecuador

# 2. Entorno virtual e instalación de dependencias
python -m venv venv
venv\Scripts\activate              # Windows
# source venv/bin/activate          # Linux/macOS
pip install -r backend/requirements.txt

# 3. Descargar los conjuntos de datos brutos siguiendo data/FUENTES_DATOS.md
# (el repositorio no incluye los CSV del ESI por su tamaño, 6.4 GB)

# 4. Ejecutar los notebooks en orden
jupyter notebook notebooks/

# 5. (Opcional) Levantar el dashboard
cd backend && uvicorn app.main:app --reload    # API en :8000
cd ../frontend && npm install && npm run dev    # UI en :3000
```

## Verificación y reproducibilidad

Cada figura y tabla del Capítulo 5 del trabajo tiene un origen reproducible. La siguiente tabla indica qué notebook o script genera cada resultado, de modo que la comisión evaluadora pueda verificar la trazabilidad completa de las cifras:

| Notebook / script | Análisis | Figuras | Tablas |
|-------------------|----------|---------|--------|
| `notebooks/02_estacionalidad_tendencia.ipynb` | A1 · Tendencia y estacionalidad (STL) | 5.1 – 5.4 | — |
| `notebooks/03_correlacion_lag_granger.ipynb` | A2 · Correlación con rezago y Granger | 5.5 – 5.7 | 5.3, 5.4 |
| `src/analysis/run_analisis_2_cointegracion.py` | A2 · Cointegración (Engle-Granger) | 5.17 | — |
| `src/analysis/run_analisis_3_espacial.py` | A3 · Impacto espacial provincial | 5.8 – 5.10 | 5.5 |
| `src/analysis/run_analisis_3_mapa_real.py` | A3 · Mapa de burbujas geo-referenciado | 5.18 | — |
| `notebooks/05_kmeans_perfiles.ipynb` | A4 · Perfiles de turista (K-Means) | 5.11 – 5.13 | 5.6 |
| `src/analysis/run_analisis_4_kprototypes.py` | A4 · Clustering mixto (K-Prototypes) | 5.14 – 5.16 | — |

Las figuras se depositan en `outputs/` al ejecutar cada notebook o script; la carpeta se publica vacía y se rellena durante la reproducción. Las figuras y tablas definitivas están incorporadas en la memoria del TFM.

## Stack tecnológico

| Capa | Tecnología |
|------|------------|
| Ingesta y procesamiento | DuckDB |
| Análisis estadístico | Python (pandas, statsmodels, scikit-learn, scipy) |
| Visualización | Matplotlib, Seaborn, Plotly |
| Backend del dashboard | FastAPI |
| Frontend del dashboard | Next.js + React + Tailwind |

## Fuentes de datos

| Fuente | Cobertura | Volumen |
|--------|-----------|---------|
| ESI — INEC (datosabiertos.gob.ec) | 2015–2025 | ~18,6 M registros · 6,4 GB |
| Banco Mundial ST.INT.ARVL | 2010–2022 | Serie anual |
| MDI homicidios intencionales | 2014–2025 | Serie provincial/mensual |
| Catastro turístico MINTUR | 2026 | Oferta provincial |

## Limitación principal

La variable `pro_jefm` del conjunto ESI registra el punto de control migratorio, no el destino turístico final. Esta limitación condiciona la interpretación del análisis espacial y se documenta de forma explícita en el Capítulo 8 del trabajo.

## Citación

> Torres, L. (2026). *Seguridad pública y flujos turísticos internacionales en Ecuador: análisis de impacto mediante técnicas de Big Data y Visual Analytics (2010-2025)* [Trabajo Fin de Máster]. Universidad Internacional de La Rioja.

## Licencia

Código distribuido bajo licencia MIT (ver `LICENSE`). Los datos brutos se rigen por las licencias de datos abiertos del Estado ecuatoriano (INEC, MDI, MINTUR) y del Banco Mundial.
