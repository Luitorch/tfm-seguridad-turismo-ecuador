"""Analisis 4 (K-Prototypes) - Segmentacion de turistas extranjeros que ingresan
a Ecuador (ESI 2023-2025).

Objetivo: superar el coeficiente Silhouette=0.21 obtenido con K-Means + one-hot
(notebook 05_kmeans_perfiles.ipynb). El one-hot satura el espacio con dimensiones
binarias diluidas, generando fronteras difusas. K-Prototypes (Huang 1998) maneja
variables mixtas numerico/categoricas nativamente combinando distancia Euclidea
para numericas y distancia Hamming para categoricas, controlada por gamma.

Estrategia:
  1. Muestra estratificada por anio via DuckDB (2.5% como en el K-Means previo),
     filtrando mot_viam='Turismo' AND tip_movi='Entrada' AND tip_naci='Extranjero'.
  2. Variable numerica: edad. Categoricas: nac_migr (top-20 + "Otro"),
     cont_nac, sex_migr, via_tran.
  3. K-Prototypes para k=3..8 con n_init=5.
  4. Silhouette computado sobre matriz de distancias Gower (mixta nativa),
     calculada en un subsample de 8000 puntos para tractabilidad O(n^2).
  5. Eleccion de k optimo por Silhouette maxima.
  6. Caracterizacion de clusters y comparacion 2023 vs 2024.

Outputs:
  - outputs/15_kprototypes_codo.png
  - outputs/16_kprototypes_perfiles.png
  - outputs/17_kprototypes_evolucion.png
  - outputs/tabla_clusters_kprototypes.csv
"""
from __future__ import annotations

import os
import sys
import time
import warnings
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from kmodes.kprototypes import KPrototypes
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
np.random.seed(42)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"
DATA = ROOT / "data/raw"
OUT.mkdir(parents=True, exist_ok=True)

ESI_FILES = {
    2023: DATA / "entradas_salidas/Datos_abiertos_ ESI_2015/esi2023.csv",
    2024: DATA / "entradas_salidas/Datos_abiertos_ ESI_2024/esi_2024.csv",
    2025: DATA / "entradas_salidas/Datos_abiertos_ESI_2025/ESI2025.csv",
}

FRAC = 0.025  # 2.5% estratificado por anio (~117k registros sin filtro Turismo)
SIL_SAMPLE = 8000  # sub-muestra para Silhouette Gower (matriz n*n)
K_GRID = list(range(3, 9))
N_INIT_KP = 5
RANDOM_STATE = 42


# ---------------------------------------------------------------------------
# 1. Carga
# ---------------------------------------------------------------------------
def cargar_muestra() -> pd.DataFrame:
    con = duckdb.connect()
    frames = []
    for anio, path in ESI_FILES.items():
        if not path.exists():
            raise FileNotFoundError(path)
        q = f"""
            SELECT anio_movi, mes_movi, sex_migr, nac_migr, cont_nac,
                   via_tran, mot_viam, edad
            FROM read_csv_auto('{path.as_posix()}', ignore_errors=true)
            WHERE tip_movi = 'Entrada'
              AND tip_naci = 'Extranjero'
              AND mot_viam = 'Turismo'
            USING SAMPLE {FRAC*100:.2f}%
        """
        df = con.execute(q).df()
        df["anio_etiq"] = anio
        frames.append(df)
        print(f"  {anio}: {len(df):,} filas")
    con.close()
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------------
# 2. Limpieza y construccion de matriz mixta
# ---------------------------------------------------------------------------
def preparar(df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, list[int]]:
    df = df.dropna(subset=["edad", "sex_migr", "cont_nac", "via_tran", "nac_migr"]).copy()
    df["edad"] = pd.to_numeric(df["edad"], errors="coerce")
    df = df.dropna(subset=["edad"])
    df = df[(df["edad"] >= 0) & (df["edad"] <= 100)]

    top_nac = df["nac_migr"].value_counts().head(20).index.tolist()
    df["nac_grp"] = df["nac_migr"].where(df["nac_migr"].isin(top_nac), "Otro")

    top_via = df["via_tran"].value_counts().head(5).index.tolist()
    df["via_grp"] = df["via_tran"].where(df["via_tran"].isin(top_via), "Otro")

    meses = {"Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5,
             "Junio": 6, "Julio": 7, "Agosto": 8, "Septiembre": 9,
             "Octubre": 10, "Noviembre": 11, "Diciembre": 12}
    df["mes_num"] = df["mes_movi"].map(meses).fillna(0).astype(int)

    # Matriz para K-Prototypes: edad numerica, resto categoricas (object)
    feat = pd.DataFrame({
        "edad": df["edad"].astype(float).values,
        "sex": df["sex_migr"].astype(str).values,
        "cont": df["cont_nac"].astype(str).values,
        "via": df["via_grp"].astype(str).values,
        "nac": df["nac_grp"].astype(str).values,
    })
    # En kmodes hay que pasar np.array con dtypes mixtos => usar object
    X = feat.values.astype(object)
    cat_idx = [1, 2, 3, 4]  # indices categoricos
    return df.reset_index(drop=True), X, cat_idx


# ---------------------------------------------------------------------------
# 3. Distancia Gower y Silhouette
# ---------------------------------------------------------------------------
def gower_matrix(num: np.ndarray, cat: np.ndarray, ranges: np.ndarray) -> np.ndarray:
    """Calcula matriz de distancia Gower para variables mixtas.

    num: (n, p_num) floats; cat: (n, p_cat) strings; ranges: (p_num,) rango por feature.
    Distancia = promedio sobre features de: |xi-xj|/range_k (num) o 1{xi!=xj} (cat).
    """
    n = num.shape[0]
    p_num = num.shape[1]
    p_cat = cat.shape[1]
    total = p_num + p_cat
    D = np.zeros((n, n), dtype=np.float32)
    # Numericas
    for k in range(p_num):
        col = num[:, k].astype(np.float32)
        r = ranges[k] if ranges[k] > 0 else 1.0
        diff = np.abs(col[:, None] - col[None, :]) / r
        D += diff
    # Categoricas
    for k in range(p_cat):
        col = cat[:, k]
        diff = (col[:, None] != col[None, :]).astype(np.float32)
        D += diff
    D /= total
    return D


def silhouette_gower(X: np.ndarray, cat_idx: list[int], labels: np.ndarray,
                     sample: int = SIL_SAMPLE, seed: int = RANDOM_STATE) -> float:
    """Silhouette score sobre una sub-muestra usando distancia Gower."""
    rng = np.random.RandomState(seed)
    if len(labels) > sample:
        idx = rng.choice(len(labels), sample, replace=False)
    else:
        idx = np.arange(len(labels))
    Xs = X[idx]
    ls = labels[idx]
    if len(np.unique(ls)) < 2:
        return -1.0
    num_idx = [i for i in range(X.shape[1]) if i not in cat_idx]
    num = Xs[:, num_idx].astype(float)
    cat = Xs[:, cat_idx].astype(str)
    ranges = np.array([num[:, k].max() - num[:, k].min() for k in range(num.shape[1])],
                      dtype=np.float32)
    D = gower_matrix(num, cat, ranges)
    return float(silhouette_score(D, ls, metric="precomputed"))


# ---------------------------------------------------------------------------
# 4. Barrido de k
# ---------------------------------------------------------------------------
def barrer_k(X: np.ndarray, cat_idx: list[int]) -> pd.DataFrame:
    resultados = []
    labels_por_k: dict[int, np.ndarray] = {}
    modelos: dict[int, KPrototypes] = {}
    for k in K_GRID:
        t0 = time.time()
        kp = KPrototypes(n_clusters=k, init="Huang", n_init=N_INIT_KP,
                         random_state=RANDOM_STATE, verbose=0, n_jobs=1,
                         max_iter=50)
        labels = kp.fit_predict(X, categorical=cat_idx)
        dt = time.time() - t0
        sil = silhouette_gower(X, cat_idx, labels)
        resultados.append({"k": k, "cost": kp.cost_, "silhouette": sil,
                           "tiempo_s": dt})
        labels_por_k[k] = labels
        modelos[k] = kp
        print(f"  k={k}  cost={kp.cost_:.0f}  silhouette={sil:.4f}  t={dt:.1f}s")
    res_df = pd.DataFrame(resultados)
    return res_df, labels_por_k, modelos


# ---------------------------------------------------------------------------
# 5. Caracterizacion
# ---------------------------------------------------------------------------
def caracterizar(df: pd.DataFrame, labels: np.ndarray) -> pd.DataFrame:
    df = df.copy()
    df["cluster"] = labels
    perfil = []
    n_total = len(df)
    for c in sorted(df["cluster"].unique()):
        sub = df[df["cluster"] == c]
        naciones = sub["nac_grp"].value_counts(normalize=True).head(5)
        cont = sub["cont_nac"].value_counts(normalize=True).head(2)
        via = sub["via_grp"].value_counts(normalize=True).head(2)
        sex = sub["sex_migr"].value_counts(normalize=True)
        edad_media = sub["edad"].mean()
        rango_edad = ("joven" if edad_media < 28
                      else ("adulto" if edad_media < 45 else "senior"))
        cont_short = {"América": "americano", "Europa": "europeo",
                      "Asia": "asiatico", "África": "africano",
                      "Oceanía": "oceanico"}.get(cont.index[0],
                                                 str(cont.index[0]).lower())
        nombre = f"Turismo - {cont_short} {rango_edad} ({via.index[0]})"
        perfil.append({
            "cluster": c, "nombre": nombre, "n": len(sub),
            "pct": 100 * len(sub) / n_total,
            "edad_media": edad_media, "edad_mediana": sub["edad"].median(),
            "continente_top1": cont.index[0],
            "continente_top1_pct": 100 * cont.iloc[0],
            "top5_nacionalidades": ", ".join(naciones.index[:5].tolist()),
            "via_top1": via.index[0], "via_top1_pct": 100 * via.iloc[0],
            "sexo_predominante": sex.idxmax(), "sexo_pct": 100 * sex.max(),
        })
    return pd.DataFrame(perfil)


# ---------------------------------------------------------------------------
# 6. Figuras
# ---------------------------------------------------------------------------
def fig_codo(res_df: pd.DataFrame, sil_kmeans: float = 0.21) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    axes[0].plot(res_df["k"], res_df["cost"], marker="o", color="steelblue")
    axes[0].set_title("K-Prototypes: costo total (numerico + gamma * categorico)")
    axes[0].set_xlabel("k")
    axes[0].set_ylabel("Cost")
    axes[0].grid(alpha=0.3)

    axes[1].plot(res_df["k"], res_df["silhouette"], marker="o", color="crimson",
                 label="K-Prototypes (Gower)")
    axes[1].axhline(sil_kmeans, ls=":", color="gray",
                    label=f"K-Means previo ({sil_kmeans:.2f})")
    axes[1].axhline(0.4, ls="--", color="green", label="Objetivo 0.40")
    axes[1].set_title("Silhouette Gower por k")
    axes[1].set_xlabel("k")
    axes[1].set_ylabel("Silhouette")
    axes[1].legend()
    axes[1].grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT / "15_kprototypes_codo.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_perfiles(df: pd.DataFrame, labels: np.ndarray) -> None:
    df = df.copy()
    df["cluster"] = labels
    fig, axes = plt.subplots(1, 3, figsize=(19, 5.5))

    cont_pivot = pd.crosstab(df["cluster"], df["cont_nac"], normalize="index") * 100
    sns.heatmap(cont_pivot, annot=True, fmt=".1f", cmap="Blues", ax=axes[0],
                cbar_kws={"label": "%"})
    axes[0].set_title("Continente por cluster (%)")
    axes[0].set_xlabel("Continente")
    axes[0].set_ylabel("Cluster")

    via_pivot = pd.crosstab(df["cluster"], df["via_grp"], normalize="index") * 100
    sns.heatmap(via_pivot, annot=True, fmt=".1f", cmap="YlOrRd", ax=axes[1],
                cbar_kws={"label": "%"})
    axes[1].set_title("Via de transporte por cluster (%)")
    axes[1].set_xlabel("Via")
    axes[1].set_ylabel("Cluster")

    edad_data = [df[df["cluster"] == c]["edad"].values
                 for c in sorted(df["cluster"].unique())]
    axes[2].boxplot(edad_data, labels=sorted(df["cluster"].unique()))
    axes[2].set_title("Edad por cluster")
    axes[2].set_xlabel("Cluster")
    axes[2].set_ylabel("Edad")
    axes[2].grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT / "16_kprototypes_perfiles.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_evolucion(df: pd.DataFrame, labels: np.ndarray,
                  perfil_df: pd.DataFrame) -> pd.Series:
    df = df.copy()
    df["cluster"] = labels
    conteo = pd.crosstab(df["cluster"], df["anio_etiq"])
    dist_anio = pd.crosstab(df["cluster"], df["anio_etiq"], normalize="columns") * 100
    var_pct = ((conteo[2024] - conteo[2023]) / conteo[2023] * 100).round(2)

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    etiquetas = [f"C{c}: {n[:38]}"
                 for c, n in zip(perfil_df["cluster"], perfil_df["nombre"])]
    dist_anio.T.plot(kind="bar", ax=axes[0], colormap="tab10", edgecolor="white")
    axes[0].set_title("Composicion relativa por anio (%)")
    axes[0].set_xlabel("Anio")
    axes[0].set_ylabel("% de turistas")
    axes[0].legend(etiquetas, title="Cluster",
                   bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    axes[0].tick_params(axis="x", rotation=0)
    axes[0].grid(alpha=0.3, axis="y")

    var_sorted = var_pct.sort_values()
    colors = ["#c0392b" if v < 0 else "#27ae60" for v in var_sorted.values]
    bars = axes[1].barh([f"C{c}" for c in var_sorted.index],
                        var_sorted.values, color=colors, edgecolor="black")
    axes[1].axvline(0, color="black", linewidth=0.8)
    axes[1].set_title("Variacion 2023 -> 2024 por cluster (%)")
    axes[1].set_xlabel("Variacion %")
    for bar, v in zip(bars, var_sorted.values):
        axes[1].text(v + (1 if v >= 0 else -1),
                     bar.get_y() + bar.get_height() / 2,
                     f"{v:+.1f}%", va="center",
                     ha="left" if v >= 0 else "right", fontsize=9)
    axes[1].grid(alpha=0.3, axis="x")
    plt.tight_layout()
    plt.savefig(OUT / "17_kprototypes_evolucion.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    return var_pct


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    print("[1/5] Carga muestra DuckDB (Turismo + Entrada + Extranjero, 2.5% por anio)...")
    raw = cargar_muestra()
    print(f"  total muestra: {len(raw):,}")

    print("[2/5] Preparacion matriz mixta...")
    df_clean, X, cat_idx = preparar(raw)
    print(f"  filas limpias: {len(df_clean):,}")
    print(f"  features: edad (num) + {len(cat_idx)} categoricas "
          "[sex, cont, via, nac]")

    print(f"[3/5] Barrido K-Prototypes k={K_GRID[0]}..{K_GRID[-1]} "
          f"(n_init={N_INIT_KP}, sample silhouette={SIL_SAMPLE})...")
    res_df, labels_por_k, _modelos = barrer_k(X, cat_idx)

    idx_best = int(res_df["silhouette"].idxmax())
    k_opt = int(res_df.loc[idx_best, "k"])
    sil_opt = float(res_df.loc[idx_best, "silhouette"])
    labels = labels_por_k[k_opt]
    print(f"  k optimo: {k_opt}  Silhouette={sil_opt:.4f}")

    print("[4/5] Caracterizacion y figuras...")
    perfil_df = caracterizar(df_clean, labels)
    perfil_df.to_csv(OUT / "tabla_clusters_kprototypes.csv", index=False)

    fig_codo(res_df)
    fig_perfiles(df_clean, labels)
    var_pct = fig_evolucion(df_clean, labels, perfil_df)

    # tabla intermedia con metricas de cada k para anexo
    res_df.to_csv(OUT / "tabla_clusters_kprototypes_kgrid.csv", index=False)

    print("[5/5] Resumen final")
    print("=" * 72)
    print("ANALISIS 4 - K-Prototypes perfiles turistas (ESI 2023-2025)")
    print("=" * 72)
    print(f"Muestra: {len(df_clean):,} | k optimo = {k_opt} | "
          f"Silhouette Gower = {sil_opt:.4f}")
    print(f"(Comparacion: K-Means previo Silhouette = 0.2108 con one-hot)")
    print()
    for _, r in perfil_df.iterrows():
        print(f"C{int(r['cluster'])}: {r['nombre']} "
              f"({r['pct']:.1f}%, edad media {r['edad_media']:.1f})")
        print(f"     Nacionalidades top: {r['top5_nacionalidades']}")
    print()
    print("Variacion 2023 -> 2024 (% sobre muestra):")
    for c, v in var_pct.sort_values().items():
        nombre = perfil_df.set_index("cluster").loc[c, "nombre"]
        print(f"   C{int(c)} ({nombre}): {v:+.2f}%")
    colapsado = var_pct.idxmin()
    resiliente = var_pct.idxmax()
    n_col = perfil_df.set_index("cluster").loc[colapsado, "nombre"]
    n_res = perfil_df.set_index("cluster").loc[resiliente, "nombre"]
    print()
    print(f"COLAPSADO : C{int(colapsado)} ({n_col}) {var_pct[colapsado]:+.2f}%")
    print(f"RESILIENTE: C{int(resiliente)} ({n_res}) {var_pct[resiliente]:+.2f}%")
    print()
    print("Archivos generados en outputs/:")
    for f in ["15_kprototypes_codo.png", "16_kprototypes_perfiles.png",
              "17_kprototypes_evolucion.png", "tabla_clusters_kprototypes.csv",
              "tabla_clusters_kprototypes_kgrid.csv"]:
        print("  -", f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
