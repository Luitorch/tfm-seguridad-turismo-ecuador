"""
Script de descarga de datos turísticos de Ecuador.
Fuentes: Banco Mundial (API directa), datos manuales de MINTUR/INEC.
"""

import requests
import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"


def descargar_banco_mundial() -> pd.DataFrame:
    """
    Descarga indicadores de turismo de Ecuador desde la API del Banco Mundial.
    No requiere registro ni API key.
    """
    indicadores = {
        "ST.INT.ARVL": "llegadas_internacionales",
        "ST.INT.DPRT": "salidas_internacionales",
        "ST.INT.RCPT.CD": "ingresos_turismo_usd",
        "ST.INT.XPND.CD": "gasto_turismo_usd",
    }

    pais = "EC"  # Ecuador
    inicio = 1995
    fin = 2023

    registros = []

    for codigo, nombre in indicadores.items():
        url = (
            f"https://api.worldbank.org/v2/country/{pais}/indicator/{codigo}"
            f"?format=json&per_page=100&mrv={fin - inicio + 1}&date={inicio}:{fin}"
        )
        print(f"Descargando {nombre}...")
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        datos = resp.json()

        if len(datos) < 2 or not datos[1]:
            print(f"  Sin datos para {nombre}")
            continue

        for entrada in datos[1]:
            registros.append({
                "año": int(entrada["date"]),
                "indicador": nombre,
                "valor": entrada["value"],
                "pais": entrada["country"]["value"],
            })

    df = pd.DataFrame(registros)
    df = df.pivot_table(index="año", columns="indicador", values="valor").reset_index()
    df = df.sort_values("año")

    salida = RAW_DIR / "banco_mundial" / "ecuador_turismo_worldbank.csv"
    df.to_csv(salida, index=False)
    print(f"\nGuardado en: {salida}")
    print(df.tail())
    return df


def descargar_llegadas_regionales() -> pd.DataFrame:
    """
    Descarga llegadas internacionales de países vecinos para comparativa regional.
    """
    paises = {
        "EC": "Ecuador",
        "CO": "Colombia",
        "PE": "Peru",
        "BO": "Bolivia",
        "CL": "Chile",
    }

    registros = []
    for codigo, nombre in paises.items():
        url = (
            f"https://api.worldbank.org/v2/country/{codigo}/indicator/ST.INT.ARVL"
            f"?format=json&per_page=50&date=2000:2023"
        )
        print(f"Descargando llegadas {nombre}...")
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        datos = resp.json()

        if len(datos) < 2 or not datos[1]:
            continue

        for entrada in datos[1]:
            if entrada["value"] is not None:
                registros.append({
                    "año": int(entrada["date"]),
                    "pais": nombre,
                    "llegadas_internacionales": entrada["value"],
                })

    df = pd.DataFrame(registros).sort_values(["pais", "año"])

    salida = RAW_DIR / "banco_mundial" / "llegadas_regionales_comparativa.csv"
    df.to_csv(salida, index=False)
    print(f"\nGuardado en: {salida}")
    return df


if __name__ == "__main__":
    print("=" * 60)
    print("DESCARGA DE DATOS TURÍSTICOS - TFM ECUADOR")
    print("=" * 60)

    print("\n[1/2] Banco Mundial - Indicadores Ecuador")
    df_ecuador = descargar_banco_mundial()

    print("\n[2/2] Banco Mundial - Comparativa Regional")
    df_regional = descargar_llegadas_regionales()

    print("\nDescarga completada.")
    print(f"Filas Ecuador: {len(df_ecuador)}")
    print(f"Filas Regional: {len(df_regional)}")
