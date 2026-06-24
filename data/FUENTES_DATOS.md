# Fuentes de Datos - TFM Turismo Ecuador

## Datasets Seleccionados

### 1. Entradas y Salidas Internacionales (INEC / Datos Abiertos)
- **URL**: https://datosabiertos.gob.ec/dataset/https-servicios-turismo-gob-ec-turismo-en-cifras-entradas-y-salidas-internacionales
- **Formato**: CSV / ODS
- **Período**: 2018-2025 (registros individuales por viajero). El piloto utiliza principalmente 2023-2025; para el análisis espacial provincial (A3) se emplean además 2018-2019 (pre-crisis) y 2022-2024 (crisis).
- **Contenido**: Llegadas internacionales por nacionalidad, residencia, punto de entrada
- **Descarga**: Directa, sin registro
- **Carpeta destino**: `data/raw/entradas_salidas/`

### 2. Catastro Turístico Nacional (MINTUR)
- **URL**: https://datosabiertos.gob.ec/dataset/catastro-turistico-total
- **Formato**: XLSX
- **Período**: Actualizado 2025
- **Contenido**: Establecimientos turísticos por provincia, categoría y capacidad
- **Descarga**: Directa, sin registro
- **Carpeta destino**: `data/raw/catastro/`

### 3. Turismo Interno (MINTUR) — fuente explorada, NO incorporada
- **URL**: https://www.datosabiertos.gob.ec/dataset/https-servicios-turismo-gob-ec-turismo-en-cifras-turismo-interno
- **Formato**: CSV
- **Período**: 2020-2025 (actualización mensual)
- **Contenido**: Turismo doméstico, pernoctadas por destino y origen
- **Estado**: explorada durante el diseño pero NO utilizada en los cuatro análisis del piloto (centrados en turismo receptor). No se versiona en el repositorio.

### 4. Banco Mundial - Llegadas Internacionales Ecuador (API)
- **URL**: https://databank.worldbank.org/
- **Indicador**: ST.INT.ARVL (International tourism, number of arrivals)
- **Período**: 1995-2023 (anual)
- **Contenido**: Llegadas internacionales anuales con contexto regional comparativo
- **Descarga**: Via API o CSV directo
- **Carpeta destino**: `data/raw/banco_mundial/`

### 5. UNWTO - Estadísticas Turismo Ecuador — fuente explorada, NO incorporada
- **URL**: https://www.untourism.int/tourism-statistics/tourism-statistics-database
- **Período**: 1995-2025
- **Contenido**: Llegadas, gasto, tipo de alojamiento, origen de turistas
- **Estado**: explorada como referencia comparativa pero NO incorporada a los análisis del piloto (requería acceso restringido). No se versiona en el repositorio.

### 6. Índice de Homicidios Ecuador (INEC / UNODC)
- **URL INEC**: https://www.ecuadorencifras.gob.ec/defunciones-generales-y-fetales/
- **URL UNODC**: https://dataunodc.un.org/dp-intentional-homicide-victims
- **Formato**: XLSX / CSV
- **Período**: 2015-2024 (anual, idealmente mensual)
- **Contenido**: Tasa de homicidios por provincia y año — para correlacionar con caída de llegadas turísticas
- **Descarga**: Directa, sin registro
- **Carpeta destino**: `data/raw/seguridad/`

---

## Notas de Uso Académico
- Todos los datos son de acceso público o gratuito para uso académico
- Cumple RGPD y LOPD: datos estadísticos agregados o anonimizados
- Citar fuentes en el documento TFM según normativa APA
