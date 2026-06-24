"""Analisis 3 (Iteracion) - Mapa geografico mejorado de impacto provincial.

Mejora del mapa fallback del A3 previo: reemplaza el heatmap de barras por un
mapa cartografico real usando coordenadas centroides de las capitales provinciales
de Ecuador, con burbujas proporcionales al volumen de flujos y color codificando
la variacion porcentual (rojo=caida, verde=crecimiento).

No se usa choropleth con shapefile porque no se localizo un geojson oficial
de provincias del Ecuador en repositorios publicos verificables. La opcion
adoptada (puntos + tamano + color) preserva la dimension geografica esencial
sin inventar polígonos no oficiales.

Generates:
  - outputs/19_mapa_provincial_burbujas.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"
TABLA = OUT / "tabla_provincias_impacto.csv"

# Centroides aproximados (lat, lon) de capitales provinciales del Ecuador continental
# Fuente: coordenadas geográficas de capitales (INEC, Wikipedia verificada)
CENTROIDES = {
    "AZUAY":           (-2.90, -78.99),
    "BOLIVAR":         (-1.59, -79.00),
    "CANAR":           (-2.55, -78.94),
    "CARCHI":          ( 0.81, -77.71),
    "COTOPAXI":        (-0.93, -78.62),
    "CHIMBORAZO":      (-1.67, -78.65),
    "EL ORO":          (-3.26, -79.96),
    "ESMERALDAS":      ( 0.97, -79.65),
    "GUAYAS":          (-2.18, -79.91),
    "IMBABURA":        ( 0.35, -78.12),
    "LOJA":            (-3.99, -79.21),
    "LOS RIOS":        (-1.81, -79.53),
    "MANABI":          (-1.05, -80.45),
    "MORONA SANTIAGO": (-2.30, -78.12),
    "NAPO":            (-1.05, -77.81),
    "PASTAZA":         (-1.45, -78.00),
    "PICHINCHA":       (-0.18, -78.47),
    "TUNGURAHUA":      (-1.25, -78.62),
    "ZAMORA CHINCHIPE":(-4.06, -78.95),
    "SUCUMBIOS":       ( 0.08, -76.88),
    "ORELLANA":        (-0.46, -76.99),
    "SANTO DOMINGO":   (-0.25, -79.17),
    "SANTA ELENA":     (-2.22, -80.85),
    "GALAPAGOS":       (-0.78, -91.13),
}


def main():
    OUT.mkdir(exist_ok=True)
    print("[1/3] Cargando tabla de impacto provincial...")
    df = pd.read_csv(TABLA)
    df["lat"] = df["provincia"].map(lambda p: CENTROIDES.get(p, (np.nan, np.nan))[0])
    df["lon"] = df["provincia"].map(lambda p: CENTROIDES.get(p, (np.nan, np.nan))[1])
    df = df.dropna(subset=["lat", "lon"])
    print(df)

    print("\n[2/3] Generando mapa de burbujas...")
    fig, ax = plt.subplots(figsize=(12, 11))

    # Galapagos esta lejos; usaremos inset
    cont = df[df["provincia"] != "GALAPAGOS"]
    gal = df[df["provincia"] == "GALAPAGOS"]

    # Normalizar tamanos de burbuja segun flujo pre-crisis (log para evitar dominancia de Carchi)
    sizes_cont = 50 + 500 * np.log10(cont["flujo_pre"].clip(lower=10) + 1) / np.log10(cont["flujo_pre"].max() + 1)
    cmap = plt.cm.RdYlGn
    norm = plt.Normalize(vmin=-100, vmax=20)

    sc = ax.scatter(
        cont["lon"], cont["lat"],
        s=sizes_cont,
        c=cont["variacion_pct"],
        cmap=cmap, norm=norm,
        edgecolor="black", linewidth=0.8, alpha=0.85,
    )

    # Etiquetas
    for _, row in cont.iterrows():
        ax.annotate(
            f"{row['provincia']}\n{row['variacion_pct']:+.1f}%",
            (row["lon"], row["lat"]),
            xytext=(8, 4), textcoords="offset points",
            fontsize=8, fontweight="bold",
            color="black",
        )

    ax.set_xlim(-81.5, -75.0)
    ax.set_ylim(-5.0, 1.5)
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.set_title(
        "Impacto de la crisis de seguridad sobre los flujos turísticos\n"
        "por provincia de control migratorio (pre-crisis 2018-2019 vs crisis 2022-2024)",
        fontsize=12,
    )
    ax.grid(alpha=0.2)
    ax.set_aspect("equal")

    # Inset con Galapagos
    if len(gal) > 0:
        from mpl_toolkits.axes_grid1.inset_locator import inset_axes
        axin = inset_axes(ax, width="22%", height="22%", loc="lower left",
                          bbox_to_anchor=(0.02, 0.02, 1, 1), bbox_transform=ax.transAxes)
        axin.scatter(gal["lon"], gal["lat"], s=200, c=gal["variacion_pct"], cmap=cmap, norm=norm,
                     edgecolor="black", linewidth=0.8)
        axin.annotate(f"GALÁPAGOS\n{gal.iloc[0]['variacion_pct']:+.1f}%",
                      (gal.iloc[0]['lon'], gal.iloc[0]['lat']),
                      xytext=(6, 4), textcoords="offset points", fontsize=7, fontweight="bold")
        axin.set_xlim(-91.6, -90.6)
        axin.set_ylim(-1.3, -0.3)
        axin.set_xticks([])
        axin.set_yticks([])
        axin.set_title("Galápagos", fontsize=8)
        axin.set_facecolor("#f0f8ff")

    # Colorbar
    cbar = plt.colorbar(sc, ax=ax, fraction=0.025, pad=0.04)
    cbar.set_label("Variación % de flujos", fontsize=10)

    # Leyenda de tamano
    txt = "Tamaño de burbuja ∝ log(flujo pre-crisis)"
    ax.text(0.99, 0.02, txt, transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8, style="italic", color="#666",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#ccc"))

    plt.tight_layout()
    plt.savefig(OUT / "19_mapa_provincial_burbujas.png", dpi=140)
    plt.close()

    print("[3/3] Mapa guardado en outputs/19_mapa_provincial_burbujas.png")
    print(f"\nResumen: {len(df)} provincias mapeadas (incluyendo Galápagos como inset)")


if __name__ == "__main__":
    main()
