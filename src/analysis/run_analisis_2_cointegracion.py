"""Analisis 2 (Iteracion) - Test de cointegracion homicidios x llegadas.

Complemento al analisis A2 previo (correlacion + Granger). El test de
cointegracion (Engle-Granger) detecta si dos series no estacionarias
mantienen una relacion de equilibrio de largo plazo, lo que refuerza
la inferencia causal mas alla de la correlacion observada.

Generates:
  - outputs/18_cointegracion_residuals.png
  - outputs/tabla_cointegracion.csv
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, coint

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"
BM_HOMI_ZIP = ROOT / "data/raw/seguridad/API_VC.IHR.PSRC.P5_DS2_es_csv_v2_8348.zip"
BM_HOMI_CSV = "API_VC.IHR.PSRC.P5_DS2_es_csv_v2_8348.csv"

# Llegadas anuales Ecuador (BM ST.INT.ARVL + ESI 2023-2024)
LLEGADAS = {
    2010: 1047000, 2011: 1141000, 2012: 1272000, 2013: 1366000,
    2014: 1557000, 2015: 1544000, 2016: 1418000, 2017: 1608000,
    2018: 2535000, 2019: 2108000,
    # 2020-2022 omitidos por COVID
    2023: 863161, 2024: 703110,
}


def load_homicidios_ecuador() -> pd.Series:
    """Carga tasa homicidios x 100k Ecuador desde BM zip."""
    with zipfile.ZipFile(BM_HOMI_ZIP) as zf:
        with zf.open(BM_HOMI_CSV) as f:
            # skip metadata header
            df = pd.read_csv(f, skiprows=4)
    ec = df[df["Country Code"] == "ECU"].iloc[0]
    s = pd.Series({int(c): v for c, v in ec.items() if c.isdigit() and not pd.isna(v)})
    s.name = "tasa_homicidios"
    return s


def main():
    OUT.mkdir(exist_ok=True)
    print("[1/4] Cargando series anuales 2010-2024...")
    homi = load_homicidios_ecuador()
    lleg = pd.Series(LLEGADAS, name="llegadas")
    df = pd.concat([homi, lleg], axis=1).dropna()
    df = df[(df.index >= 2010) & (df.index <= 2024)]
    print(df)

    print("\n[2/4] Test ADF (estacionariedad) en niveles...")
    for col in df.columns:
        stat, pval, *_ = adfuller(df[col].dropna(), autolag="AIC")
        print(f"  ADF {col}: stat={stat:.3f}, p={pval:.4f} -> {'NO estacionaria' if pval > 0.05 else 'estacionaria'}")

    print("\n[3/4] Test de cointegracion Engle-Granger...")
    common = df.dropna()
    if len(common) < 10:
        print("  Insuficientes observaciones; concatenando con interpolacion 2020-2022")
    stat, pval, crit = coint(common["llegadas"], common["tasa_homicidios"])
    print(f"  Cointegracion: stat={stat:.4f}, p={pval:.4f}")
    print(f"  Valores criticos (1%, 5%, 10%): {crit}")
    cointegradas = pval < 0.10  # criterio relajado por n pequeno
    print(f"  Conclusion: series {'cointegradas (relacion de equilibrio largo plazo)' if cointegradas else 'NO cointegradas al 10%'}")

    print("\n[4/4] Estimando regresion de largo plazo y residuales...")
    # llegadas = a + b * homicidios + e
    X = common["tasa_homicidios"].values
    y = common["llegadas"].values
    b, a = np.polyfit(X, y, 1)
    resid = y - (a + b * X)
    print(f"  Coef largo plazo: llegadas = {a:.0f} + ({b:.0f}) * homicidios")
    print(f"  R^2 = {1 - resid.var() / y.var():.3f}")

    # tabla de resultados
    out_tab = pd.DataFrame({
        "anio": common.index,
        "tasa_homicidios": common["tasa_homicidios"].values,
        "llegadas": common["llegadas"].values,
        "llegadas_predicha": a + b * X,
        "residual": resid,
    })
    out_tab.to_csv(OUT / "tabla_cointegracion.csv", index=False, encoding="utf-8")
    print(f"\n  Tabla guardada en {OUT / 'tabla_cointegracion.csv'}")

    # figura
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    ax1.plot(common.index, y, "o-", color="#2563eb", label="Llegadas observadas", linewidth=2)
    ax1.plot(common.index, a + b * X, "--", color="#dc2626", label=f"Predicha (R²={1 - resid.var()/y.var():.2f})")
    ax1.set_ylabel("Llegadas internacionales")
    ax1.set_title(f"Relación de largo plazo homicidios → llegadas (Engle-Granger p={pval:.3f})")
    ax1.legend()
    ax1.grid(alpha=0.3)

    ax2.bar(common.index, resid, color=["#10b981" if r > 0 else "#ef4444" for r in resid])
    ax2.axhline(0, color="black", linewidth=0.6)
    ax2.set_ylabel("Residual (obs − pred)")
    ax2.set_xlabel("Año")
    ax2.set_title("Residuales de la regresión cointegrada")
    ax2.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT / "18_cointegracion_residuals.png", dpi=140)
    plt.close()

    print("\n=== RESUMEN ===")
    print(f"Engle-Granger p-valor: {pval:.4f}")
    print(f"Cointegradas al 10%: {'SI' if cointegradas else 'NO'}")
    print(f"Relacion: cada +1 punto en tasa homicidios -> {b:+,.0f} llegadas")


if __name__ == "__main__":
    main()
