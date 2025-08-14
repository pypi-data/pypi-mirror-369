# show_pore_distribution.py
# -*- coding: utf-8 -*-
"""
Lee outputs/csv/results.csv y muestra la distribución de poros:
- Vista de la tabla (primeras filas)
- Histogramas de surface_area y filled_volume
- Conteo de predicted_vacancy (número de vacancias asignadas por poro)
- Scatter surface_area vs filled_volume con tamaño ~ predicted_vacancy

Uso:
    python show_pore_distribution.py
    python show_pore_distribution.py --csv otra/ruta.csv
"""

import argparse
from pathlib import Path
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

REQUIRED_COLS = ["archivo", "surface_area", "filled_volume", "predicted_vacancy"]

def load_results(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"No existe el archivo: {csv_path.as_posix()}")
    df = pd.read_csv(csv_path)

    # Normaliza nombres por si vienen con variantes
    cols_norm = {c.lower().strip(): c for c in df.columns}
    def pick(*cands):
        for c in cands:
            if c in cols_norm:
                return cols_norm[c]
        return None

    col_archivo   = pick("archivo", "file", "path")
    col_area      = pick("surface_area", "area", "surfacearea")
    col_vol       = pick("filled_volume", "volume", "filledvolume")
    col_vac       = pick("predicted_vacancy", "vacancy", "vacancys", "vacancys_est", "predicted")

    missing = []
    if col_archivo is None: missing.append("archivo")
    if col_area    is None: missing.append("surface_area")
    if col_vol     is None: missing.append("filled_volume")
    if col_vac     is None: missing.append("predicted_vacancy")

    if missing:
        raise ValueError(
            "Faltan columnas requeridas: "
            + ", ".join(missing)
            + f"\nColumnas disponibles: {list(df.columns)}"
        )

    # Renombra a nombres canónicos para trabajar más fácil
    df = df.rename(columns={
        col_archivo: "archivo",
        col_area: "surface_area",
        col_vol: "filled_volume",
        col_vac: "predicted_vacancy"
    })

    # Cast numérico seguro
    for c in ("surface_area", "filled_volume", "predicted_vacancy"):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Quita filas totalmente vacías en esas 3 métricas
    df = df.dropna(subset=["surface_area", "filled_volume", "predicted_vacancy"])
    return df

def show_table_head(df: pd.DataFrame, n=10):
    print("\n=== Vista de resultados (primeras filas) ===")
    cols = ["archivo", "surface_area", "filled_volume", "predicted_vacancy"]
    print(df[cols].head(n).to_string(index=False))

def plot_histogram(series: pd.Series, title: str, xlabel: str):
    plt.figure()
    # bins automáticos (freedman-diaconis-ish) si hay suficientes datos
    bins = "auto"
    plt.hist(series.dropna().values, bins=bins)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Frecuencia")
    plt.tight_layout()

def plot_counts(series: pd.Series, title: str, xlabel: str):
    plt.figure()
    counts = series.round(0).astype(int).value_counts().sort_index()
    plt.bar(counts.index.astype(str), counts.values)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Cantidad de poros")
    plt.tight_layout()

def plot_scatter(df: pd.DataFrame):
    plt.figure()
    x = df["surface_area"].values
    y = df["filled_volume"].values
    s = np.clip(df["predicted_vacancy"].values, 0, None)

    # Escalado de tamaño de marcador (para que se vea bien)
    # base + factor * vacancias
    size = 10 + 15 * (s / (np.nanpercentile(s, 90) + 1e-9))
    plt.scatter(x, y, s=size)
    plt.title("Surface Area vs Filled Volume (tamaño ~ vacancias)")
    plt.xlabel("surface_area")
    plt.ylabel("filled_volume")
    plt.tight_layout()

def print_summary(df: pd.DataFrame):
    total_vac = int(np.ceil(df["predicted_vacancy"].fillna(0).sum()))
    n_poros   = len(df)
    print(f"\n=== Resumen ===")
    print(f"Poros (filas): {n_poros}")
    print(f"Vacancias totales (ceil): {total_vac}")

    # Estadísticas simples
    for col in ("surface_area", "filled_volume", "predicted_vacancy"):
        s = df[col]
        print(f"\n[{col}]")
        print(f"  min:   {s.min():.4f}")
        print(f"  p25:   {s.quantile(0.25):.4f}")
        print(f"  p50:   {s.quantile(0.50):.4f}")
        print(f"  p75:   {s.quantile(0.75):.4f}")
        print(f"  max:   {s.max():.4f}")
        print(f"  media: {s.mean():.4f}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, default="outputs/csv/results.csv",
                        help="Ruta al CSV de resultados (por defecto: outputs/csv/results.csv)")
    args = parser.parse_args()

    df = load_results(Path(args.csv))
    show_table_head(df, n=10)
    print_summary(df)

    # Plots
    plot_histogram(df["surface_area"], title="Distribución de Surface Area", xlabel="surface_area")
    plot_histogram(df["filled_volume"], title="Distribución de Filled Volume", xlabel="filled_volume")
    plot_counts(df["predicted_vacancy"], title="Distribución de Vacancias Asignadas", xlabel="predicted_vacancy")
    plot_scatter(df)

    plt.show()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
