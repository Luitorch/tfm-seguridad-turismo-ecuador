"""Genera los datos procesados (agregados) del piloto a partir del ESI bruto.

Lee los CSV originales del ESI (varios GB) con DuckDB y escribe en
data/processed/ agregaciones de tamano reducido que alimentan los analisis
del Capitulo 5. Esto permite reproducir los analisis sin volver a descargar
ni reprocesar el dataset completo.

Salidas (data/processed/):
  - esi_turismo_mensual_nacionalidad.csv : entradas de extranjeros con motivo
        Turismo, agregadas por anio, mes y nacionalidad.
  - esi_entradas_provincia_anio.csv      : entradas de extranjeros por anio y
        provincia del punto de control migratorio (pro_jefm).
  - esi_turismo_perfil_anio.csv          : perfil sociodemografico agregado
        (anio, sexo, via, continente, rango de edad) de turistas extranjeros.

Uso: python src/data/generar_datos_procesados.py
"""
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/entradas_salidas"
PROC = ROOT / "data/processed"
PROC.mkdir(parents=True, exist_ok=True)

NEEDED = ["anio_movi", "mes_movi", "tip_movi", "tip_naci", "mot_viam",
          "nac_migr", "pro_jefm", "sex_migr", "edad", "via_tran", "cont_nac"]


def archivos_esi_validos(con: duckdb.DuckDBPyConnection) -> list[str]:
    """Devuelve los CSV del ESI que contienen las columnas necesarias."""
    validos = []
    for f in sorted(RAW.rglob("*.csv")):
        if "muestra" in f.name.lower():
            continue
        try:
            cols = con.execute(
                f"SELECT * FROM read_csv_auto('{f.as_posix()}') LIMIT 0"
            ).df().columns.tolist()
            if all(c in cols for c in NEEDED):
                validos.append(f.as_posix())
        except Exception:
            continue
    return validos


def union_sql(files: list[str]) -> str:
    cols = ", ".join(NEEDED)
    partes = [
        f"SELECT {cols} FROM read_csv_auto('{f}', ignore_errors=true)"
        for f in files
    ]
    return " UNION ALL ".join(partes)


def main() -> int:
    con = duckdb.connect()
    files = archivos_esi_validos(con)
    if not files:
        print("No se encontraron CSV del ESI con el esquema esperado en", RAW)
        return 1
    print(f"Archivos ESI validos: {len(files)}")
    for f in files:
        print("  -", Path(f).name)

    base = union_sql(files)
    con.execute(f"CREATE VIEW esi AS {base}")

    # 1. Entradas turismo por anio, mes, nacionalidad
    con.execute(f"""
        COPY (
            SELECT anio_movi AS anio, mes_movi AS mes, nac_migr AS nacionalidad,
                   COUNT(*) AS total
            FROM esi
            WHERE tip_movi='Entrada' AND tip_naci='Extranjero' AND mot_viam='Turismo'
            GROUP BY anio_movi, mes_movi, nac_migr
            ORDER BY anio, mes, total DESC
        ) TO '{(PROC / "esi_turismo_mensual_nacionalidad.csv").as_posix()}'
        (HEADER, DELIMITER ',');
    """)
    print("Generado: esi_turismo_mensual_nacionalidad.csv")

    # 2. Entradas de extranjeros por anio y provincia de control migratorio
    con.execute(f"""
        COPY (
            SELECT anio_movi AS anio, pro_jefm AS provincia, COUNT(*) AS total
            FROM esi
            WHERE tip_movi='Entrada' AND tip_naci='Extranjero'
            GROUP BY anio_movi, pro_jefm
            ORDER BY anio, total DESC
        ) TO '{(PROC / "esi_entradas_provincia_anio.csv").as_posix()}'
        (HEADER, DELIMITER ',');
    """)
    print("Generado: esi_entradas_provincia_anio.csv")

    # 3. Perfil sociodemografico agregado de turistas extranjeros
    con.execute(f"""
        COPY (
            SELECT anio_movi AS anio, sex_migr AS sexo, via_tran AS via,
                   cont_nac AS continente,
                   CASE
                     WHEN TRY_CAST(edad AS INTEGER) < 25 THEN '<25'
                     WHEN TRY_CAST(edad AS INTEGER) < 40 THEN '25-39'
                     WHEN TRY_CAST(edad AS INTEGER) < 60 THEN '40-59'
                     WHEN TRY_CAST(edad AS INTEGER) >= 60 THEN '60+'
                     ELSE 'n/d'
                   END AS rango_edad,
                   COUNT(*) AS total
            FROM esi
            WHERE tip_movi='Entrada' AND tip_naci='Extranjero' AND mot_viam='Turismo'
            GROUP BY anio, sexo, via, continente, rango_edad
            ORDER BY anio, total DESC
        ) TO '{(PROC / "esi_turismo_perfil_anio.csv").as_posix()}'
        (HEADER, DELIMITER ',');
    """)
    print("Generado: esi_turismo_perfil_anio.csv")

    print(f"\nDatos procesados escritos en: {PROC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
