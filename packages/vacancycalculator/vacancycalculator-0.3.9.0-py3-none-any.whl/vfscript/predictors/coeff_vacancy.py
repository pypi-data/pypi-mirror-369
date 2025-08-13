from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# seaborn es opcional; solo para el violín
try:
    import seaborn as sns
    _HAS_SNS = True
except Exception:
    _HAS_SNS = False


@dataclass
class GroupDef:
    name: str
    min_v: int
    max_v: Optional[int]  # None para 10+


class GroupCoefficientCalculator:
    """
    Calcula, para cada grupo de vacancias, el coeficiente:
        coef(grupo) = mean(surface_area del grupo) / min_vacancias_del_grupo

    Grupos fijos:
      - 1-3  -> min_v=1,  max_v=3
      - 4-6  -> min_v=4,  max_v=6
      - 7-9  -> min_v=7,  max_v=9
      - 10+  -> min_v=10, max_v=None (sin tope)
    """

    GROUPS: Dict[str, GroupDef] = {
        "1-3": GroupDef("1-3", 2, 3),
        "4-6": GroupDef("4-6", 5, 6),
        "7-9": GroupDef("7-9", 8, 9),
        "10+": GroupDef("10+", 10, None),
    }

    def __init__(self, json_path: str = "outputs/json/training_graph.json"):
        self.json_path = json_path
        self.df: Optional[pd.DataFrame] = None

    def load(self) -> pd.DataFrame:
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)

        for c in ("surface_area", "vacancys"):
            if c not in df.columns:
                raise ValueError(f"Falta la columna requerida '{c}' en el JSON.")

        df = df.dropna(subset=["surface_area", "vacancys"]).copy()
        df = df[df["vacancys"] > 0].copy()

        df["area_por_vacancia"] = df["surface_area"] / df["vacancys"]

        df["grupo"] = df["vacancys"].apply(self._clasificar_grupo)
        self.df = df
        return df

    @staticmethod
    def _clasificar_grupo(v: float) -> str:
        v = int(v)
        if 1 <= v <= 3:
            return "1-3"
        elif 4 <= v <= 6:
            return "4-6"
        elif 7 <= v <= 9:
            return "7-9"
        else:
            return "10+"

    # -------------------- Cálculo del coeficiente --------------------
    def compute_coefficients(self, use_observed_min_instead: bool = False) -> pd.DataFrame:
        """
        Devuelve DataFrame con:
          grupo, n_rows, mean_surface_area, min_divisor, coeficiente, mean_area_por_vacancia, std_area_por_vacancia

        Parámetros
        ----------
        use_observed_min_instead : bool
            False (por defecto) -> divide por el mínimo teórico del grupo (1,4,7,10).
            True  -> divide por el mínimo de 'vacancys' OBSERVADO dentro del grupo en tus datos.
        """
        if self.df is None:
            self.load()

        rows = []
        for gname, gdef in self.GROUPS.items():
            gdf = self._slice_group(self.df, gdef)
            if gdf.empty:
                rows.append({
                    "grupo": gname,
                    "n_rows": 0,
                    "mean_surface_area": np.nan,
                    "min_divisor": gdef.min_v if not use_observed_min_instead else np.nan,
                    "coeficiente": np.nan,
                    "mean_area_por_vacancia": np.nan,
                    "std_area_por_vacancia": np.nan,
                })
                continue

            mean_sa = float(gdf["surface_area"].mean())
            if use_observed_min_instead:
                min_div = int(gdf["vacancys"].min())
            else:
                min_div = gdef.min_v

            coef = mean_sa / min_div if min_div > 0 else np.nan

            rows.append({
                "grupo": gname,
                "n_rows": int(len(gdf)),
                "mean_surface_area": mean_sa,
                "min_divisor": int(min_div),
                "coeficiente": float(coef),
                "mean_area_por_vacancia": float(gdf["area_por_vacancia"].mean()),
                "std_area_por_vacancia": float(gdf["area_por_vacancia"].std(ddof=1)) if len(gdf) > 1 else 0.0,
            })

        out = pd.DataFrame(rows)
        # Orden lógico
        order = ["1-3", "4-6", "7-9", "10+"]
        out["grupo"] = pd.Categorical(out["grupo"], categories=order, ordered=True)
        out = out.sort_values("grupo").reset_index(drop=True)
        return out

    def _slice_group(self, df: pd.DataFrame, g: GroupDef) -> pd.DataFrame:
        if g.max_v is None:
            return df[(df["vacancys"] >= g.min_v)]
        return df[(df["vacancys"] >= g.min_v) & (df["vacancys"] <= g.max_v)]

    # -------------------- Plots (opcionales) --------------------
    def plot_violin(self):
        """Reproduce tu gráfico violín original (por 'vacancys')."""
        if self.df is None:
            self.load()
        if not _HAS_SNS:
            raise RuntimeError("Seaborn no está disponible. Instálalo o usa otra rutina de plot.")
        df = self.df

        grouped = df.groupby("vacancys")["area_por_vacancia"]
        stats = grouped.agg(["mean", "std"]).reset_index()
        stats["std"] = stats["std"].fillna(0)

        plt.figure(figsize=(10, 6))
        sns.violinplot(
            x="vacancys", y="area_por_vacancia",
            data=df, inner=None, color="lightblue"
        )
        plt.errorbar(
            x=stats["vacancys"], y=stats["mean"], yerr=stats["std"],
            fmt="o", color="darkblue", ecolor="black",
            elinewidth=1.5, capsize=4, label="Media ± std"
        )
        plt.xlabel("Número de vacancias")
        plt.ylabel("Área de superficie por vacancia")
        plt.title("Distribución del área por vacancia (violín + media ± std)")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.legend()
        plt.tight_layout()
        plt.show()


# -------------------- Ejemplo de uso --------------------
# if __name__ == "__main__":
    # calc = GroupCoefficientCalculator("outputs/json/training_graph.json")
    # df = calc.load()

    # Calcular coeficientes usando el mínimo TEÓRICO por grupo (1,4,7,10)
    # coef_df = calc.compute_coefficients(use_observed_min_instead=False)
    # print("\nCoeficientes por grupo (min teórico):")
    # print(coef_df)

    # Si preferís dividir por el mínimo OBSERVADO en tus datos
    # coef_obs_df = calc.compute_coefficients(use_observed_min_instead=True)
    # print("\nCoeficientes por grupo (min observado):")
    # print(coef_obs_df)

    # (Opcional) Plot violín como el script original
    # calc.plot_violin()
