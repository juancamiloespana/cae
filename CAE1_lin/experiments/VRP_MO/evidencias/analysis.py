"""
Convergence analysis for VRP multi-objective experiments.

Produces a single DataFrame `df` with all TSV rows joined with their config
parameters. Columns: config, run, iteration, evaluations, runtime_s,
max_distance, num_vehicles, generations, alpha, mu, lambda_, crossoverRate,
tournament, totalVehicles.
"""

import os
import glob
import xml.etree.ElementTree as ET
from collections import defaultdict

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONV_DIR = os.path.join(BASE_DIR, "data", "logs", "convergencia")

# ---------------------------------------------------------------------------
# 1. Parse XML configs
# ---------------------------------------------------------------------------

def parse_config(xml_path: str) -> dict:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    props = {}
    for module in root.findall("module"):
        cls = module.get("class", "")
        for prop in module.findall("property"):
            props[(cls, prop.get("name"))] = prop.get("value") or prop.text

    def get(cls_fragment, name):
        for (cls, n), v in props.items():
            if cls_fragment in cls and n == name:
                return v
        return None

    return {
        "generations":   int(get("EvolutionaryAlgorithm", "generations") or 0),
        "alpha":         int(get("EvolutionaryAlgorithm", "alpha")       or 0),
        "mu":            int(get("EvolutionaryAlgorithm", "mu")          or 0),
        "lambda":        int(get("EvolutionaryAlgorithm", "lambda")      or 0),
        "crossoverRate": float(get("EvolutionaryAlgorithm", "crossoverRate") or 0),
        "tournament":    int(get("Nsga2", "tournament") or 0),
        "totalVehicles": int(get("DronesModule", "totalVehicles") or 0),
    }


configs: dict[int, dict] = {}
for xml_path in sorted(glob.glob(os.path.join(CONV_DIR, "config-exp*.xml"))):
    exp_id = int(os.path.basename(xml_path).replace("config-exp", "").replace(".xml", ""))
    configs[exp_id] = parse_config(xml_path)

# ---------------------------------------------------------------------------
# 2. Load all TSVs
# ---------------------------------------------------------------------------
# filename pattern: {exp_id}_{run_id}.tsv

TSV_COLS = ["iteration", "evaluations", "runtime_s", "max_distance", "num_vehicles"]

runs: dict[int, list[pd.DataFrame]] = defaultdict(list)

for tsv_path in sorted(glob.glob(os.path.join(CONV_DIR, "*.tsv"))):
    fname = os.path.basename(tsv_path)
    parts = fname.replace(".tsv", "").split("_")
    if len(parts) != 2:
        continue
    exp_id, run_id = int(parts[0]), int(parts[1])

    df = pd.read_csv(tsv_path, sep="\t", header=0, names=TSV_COLS)
    df["exp"] = exp_id
    df["run"] = run_id
    runs[exp_id].append(df)


# ---------------------------------------------------------------------------
# 3. Experiment summary table (one row per experiment, config params only)
# ---------------------------------------------------------------------------

CONFIG_COLS = ["generations", "alpha", "mu", "lambda", "crossoverRate", "tournament", "totalVehicles"]

exp_summary = pd.DataFrame(
    [{"exp": exp_id, "n_runs": len(runs[exp_id]), **cfg}
     for exp_id, cfg in sorted(configs.items())]
)
exp_summary = exp_summary[["exp", "n_runs"] + CONFIG_COLS]



# ---------------------------------------------------------------------------
# 4. Filer df to just ake every 100 iteration to reduce the size of DF
filtered_runs: list[pd.DataFrame] = []
for exp_id, dfs in runs.items():
	for df in dfs:
		filtered_df = df[df["iteration"] % 100 == 0].copy()
		filtered_runs.append(filtered_df)	
df_f= pd.concat(filtered_runs, ignore_index=True)	


# ---------------------------------------------------------------------------
# 5. avg max_distance and num_vehicles per exp, run and iteraions		


agg_metrics = df_f.groupby(["exp", "iteration"], as_index=False)[["max_distance", "num_vehicles"]].agg(["mean", "max", "min", "std"])
agg_metrics.columns = ["config", "iteration",
                        "distance_mean", "distance_max", "distance_min", "distance_std",
                        "vehicles_mean", "vehicles_max", "vehicles_min", "vehicles_std"]


agg_metrics.to_csv(os.path.join(BASE_DIR, "convergence_summary.csv"), index=False)
# ---------------------------------------------------------------------------
# 6. Plot: avg max_distance evolution by iteration, one curve per exp
# ---------------------------------------------------------------------------
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

configs_ids = sorted(agg_metrics["config"].unique())
colors = cm.tab10(np.linspace(0, 1, len(configs_ids)))

METRICS = [
    # (ax_index, mean_col,         min_col,          max_col,          std_col,          ylabel,             title)
    (0, "distance_mean", "distance_min", "distance_max", "distance_std", "Max Distance",  "Convergence of Max Distance"),
    (1, "vehicles_mean", "vehicles_min", "vehicles_max", "vehicles_std", "Num Vehicles",  "Convergence of Num Vehicles"),
]

def plot_pair(col_left, col_right, title_left, title_right, ylabel_left, ylabel_right,
              suptitle, fname, std_left=None, std_right=None):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 6))
    fig.suptitle(suptitle, fontsize=13)
    for cfg_id, color in zip(configs_ids, colors):
        g = agg_metrics[agg_metrics["config"] == cfg_id].sort_values("iteration")
        iters = g["iteration"]
        for ax, col, std_col, ylabel, title in [
            (ax1, col_left,  std_left,  ylabel_left,  title_left),
            (ax2, col_right, std_right, ylabel_right, title_right),
        ]:
            ax.plot(iters, g[col], color=color, label=f"C{cfg_id - 1}")
            if std_col is not None:
                std = g[std_col].fillna(0)
                ax.fill_between(iters, g[col] - std, g[col] + std, color=color, alpha=0.15)
    for ax, ylabel, title in [
        (ax1, ylabel_left,  title_left),
        (ax2, ylabel_right, title_right),
    ]:
        ax.set_xlabel("Iteración")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(title="Configuración")
        ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(os.path.join(BASE_DIR, fname), dpi=150)

# Figure 1 — Media ± SD
plot_pair(
    "distance_mean", "vehicles_mean",
    "Distancia Máxima Media\n(banda = ±1 DE)", "Nº Vehículos Medio\n(banda = ±1 DE)",
    "Distancia Máxima", "Nº Vehículos",
    "Convergencia — Media ± 1 Desviación Estándar", "convergence_mean.pdf",
    std_left="distance_std", std_right="vehicles_std",
)

# Figure 2 — Mínimo
plot_pair(
    "distance_min", "vehicles_min",
    "Distancia Máxima Mínima", "Nº Vehículos Mínimo",
    "Distancia Máxima", "Nº Vehículos",
    "Convergencia — Mínimo", "convergence_min.pdf",
)

plt.show()

# ---------------------------------------------------------------------------
# 7. LaTeX table of configurations
# ---------------------------------------------------------------------------

latex_rows = ""
for exp_id, cfg in sorted(configs.items()):
    label = f"C{exp_id - 1}"
    n_runs = len(runs[exp_id])
    latex_rows += (
        f"        {label} & {cfg['alpha']} & {cfg['generations']:,} "
        f"& {cfg['crossoverRate']} & {cfg['tournament']} & {cfg['totalVehicles']} & {n_runs} \\\\\n"
    ).replace(",", ".")

latex_table = r"""
\begin{table}[H]
    \centering
    \caption{Configuraciones experimentales de la Fase~1 ($\alpha = \mu = \lambda$).}
    \label{tab:configs_fase1}
    \begin{tabular}{lrrrrrc}
        \toprule
        \textbf{Config} & $\boldsymbol{\alpha=\mu=\lambda}$ & \textbf{Generaciones}
            & \textbf{Tasa cruce} & \textbf{Torneo} & \textbf{Vehículos} & \textbf{Ejecuciones} \\
        \midrule
""" + latex_rows + r"""        \bottomrule
    \end{tabular}
\end{table}
"""

print(latex_table)

latex_path = os.path.join(BASE_DIR, "tabla_configuraciones.tex")
with open(latex_path, "w", encoding="utf-8") as f:
    f.write(latex_table)
print(f"Tabla guardada en: {latex_path}")

# ---------------------------------------------------------------------------
# 8. Comparison table: C4 (40.000 gen) vs C5 (80.000 gen) — distance_min
# ---------------------------------------------------------------------------
# config column uses exp_id (1-based); C4 -> exp 5, C5 -> exp 6
last_iter_c4 = agg_metrics[agg_metrics["config"] == 5]["iteration"].max()
last_iter_c5 = agg_metrics[agg_metrics["config"] == 6]["iteration"].max()

c4 = agg_metrics[(agg_metrics["config"] == 5) & (agg_metrics["iteration"] == last_iter_c4)].iloc[0]
c5 = agg_metrics[(agg_metrics["config"] == 6) & (agg_metrics["iteration"] == last_iter_c5)].iloc[0]

comparison = pd.DataFrame([
    {
        "Configuración": "C4",
        "α=μ=λ": 100,
        "Generaciones": 40_000,
        "Iter. final": int(last_iter_c4),
        "dist_min_mean": round(c4["distance_mean"], 2),
        "dist_min_min":  round(c4["distance_min"],  2),
        "dist_min_max":  round(c4["distance_max"],  2),
        "dist_min_std":  round(c4["distance_std"],  2),
    },
    {
        "Configuración": "C5",
        "α=μ=λ": 100,
        "Generaciones": 80_000,
        "Iter. final": int(last_iter_c5),
        "dist_min_mean": round(c5["distance_mean"], 2),
        "dist_min_min":  round(c5["distance_min"],  2),
        "dist_min_max":  round(c5["distance_max"],  2),
        "dist_min_std":  round(c5["distance_std"],  2),
    },
])

metrics = ["dist_min_mean", "dist_min_min", "dist_min_max", "dist_min_std"]
pct_diff = {col: round((comparison.loc[1, col] - comparison.loc[0, col]) / comparison.loc[0, col] * 100, 2)
            for col in metrics}
pct_row = pd.DataFrame([{"Configuración": "Δ C5 vs C4 (%)", "α=μ=λ": "-", "Generaciones": "-",
                          "Iter. final": "-", **pct_diff}])
comparison_full = pd.concat([comparison, pct_row], ignore_index=True)

print("\nComparación C4 vs C5 — Distancia mínima (última iteración):")
print(comparison_full.to_string(index=False))
