"""Analisis 3 - Impacto espacial provincial de la crisis de seguridad sobre el turismo.

Cruza tasa de homicidios provincial (MDI) con la variacion porcentual de flujos
de entrada por provincia de control migratorio (ESI pro_jefm) entre el periodo
pre-crisis (2018-2019) y el periodo de crisis (2022-2024).

LIMITACION CRITICA: pro_jefm registra el punto de control migratorio (aeropuerto/
puerto/paso fronterizo), NO el destino turistico final. Documentado en Cap 8.

Generates:
  - outputs/09_ranking_provincias_variacion.png
  - outputs/10_scatter_homicidios_vs_variacion.png
  - outputs/11_mapa_provincial_variacion.png  (fallback: barras horizontales si no hay geojson)
  - outputs/tabla_provincias_impacto.csv
"""
from pathlib import Path
import unicodedata

import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"
DATA = ROOT / "data/raw"

ESI_FILES = {
    2018: DATA / "entradas_salidas/Datos_abiertos_ ESI_2018/Datos_abiertos_ESI_2018/Datos_abiertos_ESI_2018/esi_2018/esi_2018.csv",
    2019: DATA / "entradas_salidas/Datos_abiertos_ ESI_2019/Datos_abiertos_ ESI_2019/Datos_abiertos_ ESI_2019/Metadatos_ESI_2019/ESI_2019.csv",
    2022: DATA / "entradas_salidas/Datos_abiertos_ ESI_2022/esi_2022.csv",
    2023: DATA / "entradas_salidas/Datos_abiertos_ ESI_2015/esi2023.csv",
    2024: DATA / "entradas_salidas/Datos_abiertos_ ESI_2024/esi_2024.csv",
}

HOMI_FILE = DATA / "seguridad/mdi_homicidiosintencionales_pm_2014_2025.xlsx"


def normalize_prov(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")
    return s.strip().upper()


def load_esi_flows_by_province() -> pd.DataFrame:
    """Carga conteos de entradas extranjeras con motivo Turismo por provincia y anio."""
    con = duckdb.connect()
    frames = []
    for year, path in ESI_FILES.items():
        if not path.exists():
            print(f"  [skip] no existe: {path}")
            continue
        print(f"  procesando {year}: {path.name}")
        # detectar delimitador / columnas con sniffer de duckdb
        q = f"""
        SELECT CAST(pro_jefm AS VARCHAR) AS provincia, COUNT(*) AS entradas
        FROM read_csv_auto('{path.as_posix()}', sample_size=-1, ignore_errors=true,
                           all_varchar=true)
        WHERE CAST(tip_movi AS VARCHAR) = 'Entrada'
          AND CAST(tip_naci AS VARCHAR) = 'Extranjero'
          AND CAST(mot_viam AS VARCHAR) = 'Turismo'
        GROUP BY pro_jefm
        """
        try:
            df = con.execute(q).df()
        except Exception as e:
            print(f"    fallo {e}")
            continue
        df["year"] = year
        df["provincia"] = df["provincia"].astype(str).map(normalize_prov)
        frames.append(df)
    if not frames:
        raise RuntimeError("No se pudo cargar ningun anio del ESI")
    flows = pd.concat(frames, ignore_index=True)
    flows = flows[flows["provincia"] != ""]
    flows = flows[flows["provincia"] != "NAN"]
    return flows


def load_homicide_rates_by_province() -> pd.DataFrame:
    """Carga homicidios desde la hoja '1. Homicidios Intencionales'.
    Cada fila es un evento. Agregamos por provincia y anio (a partir de fecha_infraccion)."""
    raw = pd.read_excel(
        HOMI_FILE, sheet_name="1. Homicidios Intencionales", header=0,
    )
    raw.columns = [str(c).strip().lower() for c in raw.columns]
    raw["provincia"] = raw["provincia"].astype(str).map(normalize_prov)
    raw["fecha_infraccion"] = pd.to_datetime(raw["fecha_infraccion"], errors="coerce")
    raw["anio"] = raw["fecha_infraccion"].dt.year
    return raw


def main():
    OUT.mkdir(exist_ok=True)
    print("[1/5] Cargando flujos ESI por provincia...")
    flows = load_esi_flows_by_province()
    print(flows.groupby("year")["entradas"].sum())

    print("\n[2/5] Calculando variacion pre-crisis (2018-2019) vs crisis (2022-2024)...")
    pre_mask = flows["year"].isin([2018, 2019])
    cri_mask = flows["year"].isin([2022, 2023, 2024])
    pre = flows[pre_mask].groupby("provincia")["entradas"].mean().rename("flujo_pre")
    cri = flows[cri_mask].groupby("provincia")["entradas"].mean().rename("flujo_crisis")
    var = pd.concat([pre, cri], axis=1).dropna()
    var["variacion_pct"] = 100 * (var["flujo_crisis"] - var["flujo_pre"]) / var["flujo_pre"]
    var = var[var["flujo_pre"] >= 100]  # excluir provincias con muy bajo volumen
    print(var.sort_values("variacion_pct"))

    print("\n[3/5] Cargando homicidios provinciales MDI...")
    homi = load_homicide_rates_by_province()
    print(f"  filas totales: {len(homi)}; rango anios: {homi['anio'].min()}-{homi['anio'].max()}")
    homi_cri = homi[homi["anio"].isin([2022, 2023, 2024])]
    tasa = homi_cri.groupby("provincia").size().rename("homicidios_crisis_total")
    print(f"  homicidios 2022-2024 por provincia (top 5):\n{tasa.sort_values(ascending=False).head()}")
    var = var.join(tasa, how="left")

    print("\n[4/5] Correlacion Spearman tasa homicidios x variacion flujo...")
    valid = var.dropna(subset=["homicidios_crisis_total", "variacion_pct"])
    rho, pval = spearmanr(valid["homicidios_crisis_total"], valid["variacion_pct"])
    print(f"  Spearman rho={rho:.4f}, p={pval:.4g}, n={len(valid)}")

    var.to_csv(OUT / "tabla_provincias_impacto.csv", encoding="utf-8")
    print(f"  Tabla guardada en {OUT / 'tabla_provincias_impacto.csv'}")

    print("\n[5/5] Generando figuras...")
    # Fig 09: ranking provincias
    fig, ax = plt.subplots(figsize=(10, 9))
    ranked = var.sort_values("variacion_pct")
    colors = ["#d62728" if v < 0 else "#2ca02c" for v in ranked["variacion_pct"]]
    ax.barh(ranked.index, ranked["variacion_pct"], color=colors)
    ax.axvline(0, color="black", linewidth=0.6)
    ax.set_xlabel("Variación % de flujos turísticos (crisis vs pre-crisis)")
    ax.set_title("Variación de flujos turísticos por provincia de control migratorio\n"
                 "Pre-crisis (2018-2019) vs crisis (2022-2024)")
    plt.tight_layout()
    plt.savefig(OUT / "09_ranking_provincias_variacion.png", dpi=140)
    plt.close()

    # Fig 10: scatter homicidios vs variacion
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.scatter(valid["homicidios_crisis_total"], valid["variacion_pct"], s=60, alpha=0.7)
    for prov, row in valid.iterrows():
        ax.annotate(prov, (row["homicidios_crisis_total"], row["variacion_pct"]),
                    fontsize=8, alpha=0.8, xytext=(4, 2), textcoords="offset points")
    if rho is not None:
        m, b = np.polyfit(valid["homicidios_crisis_total"], valid["variacion_pct"], 1)
        xs = np.linspace(valid["homicidios_crisis_total"].min(), valid["homicidios_crisis_total"].max(), 50)
        ax.plot(xs, m * xs + b, "--", color="grey", alpha=0.7,
                label=f"Spearman ρ={rho:.3f}  p={pval:.3g}")
        ax.legend()
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xlabel("Homicidios intencionales totales 2022-2024 (provincial)")
    ax.set_ylabel("Variación % de flujos turísticos (crisis vs pre-crisis)")
    ax.set_title("Homicidios provinciales vs variación turística")
    plt.tight_layout()
    plt.savefig(OUT / "10_scatter_homicidios_vs_variacion.png", dpi=140)
    plt.close()

    # Fig 11: "mapa" fallback con barras agrupadas por signo
    fig, ax = plt.subplots(figsize=(11, 8))
    sorted_var = var.dropna(subset=["variacion_pct"]).sort_values("variacion_pct")
    cmap = plt.cm.RdYlGn
    vmin, vmax = sorted_var["variacion_pct"].min(), sorted_var["variacion_pct"].max()
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    bars = ax.barh(sorted_var.index, sorted_var["variacion_pct"],
                   color=[cmap(norm(v)) for v in sorted_var["variacion_pct"]])
    ax.axvline(0, color="black", linewidth=0.6)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label("Variación % flujos")
    ax.set_xlabel("Variación % de flujos turísticos")
    ax.set_title("Heatmap de variación turística por provincia de control migratorio\n"
                 "Fallback (mapa coroplético no generado; ver Cap 8 limitaciones)")
    plt.tight_layout()
    plt.savefig(OUT / "11_mapa_provincial_variacion.png", dpi=140)
    plt.close()
    print("Figuras guardadas (09, 10, 11).")

    print("\n=== RESUMEN ===")
    print(f"Provincias analizadas: {len(var)}")
    print(f"Provincias con datos completos: {len(valid)}")
    print(f"Top 3 mayor caida:")
    print(var.nsmallest(3, 'variacion_pct')[['flujo_pre', 'flujo_crisis', 'variacion_pct']])
    print(f"\nTop 3 mayor crecimiento o menor caida:")
    print(var.nlargest(3, 'variacion_pct')[['flujo_pre', 'flujo_crisis', 'variacion_pct']])
    print(f"\nSpearman rho={rho:.4f}, p={pval:.4g}")
    if pval < 0.05:
        print("CRITERIO EXITO CUMPLIDO (p < 0.05)")
    else:
        print("Criterio p<0.05 NO alcanzado; reportar como hallazgo: la correlacion provincial es debil/no significativa")


if __name__ == "__main__":
    main()
