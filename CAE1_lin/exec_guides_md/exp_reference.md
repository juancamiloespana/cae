# Experiment Reference — VRP Multi-Objective (Opt4J)

For the step-by-step workflow to run experiments see [exp_workflow.md](exp_workflow.md).

---

## Overview

The **problem** is the Vehicle Routing Problem (VRP) with two objectives:
- `max_distance [MIN]` — minimize the maximum route distance among all vehicles
- `num_vehicles [MIN]` — minimize the number of vehicles used

The **algorithm** is NSGA-II (Non-dominated Sorting Genetic Algorithm II), an evolutionary multi-objective optimizer.

---

## Folder Structure

```
CAE1  (project root)/
├── opt4j/                             ← Opt4J installation
│   ├── bin/
│   │   ├── opt4j.bat                  ← Windows launcher
│   │   └── opt4j-JVM1.8.bat          ← Windows launcher with bundled JRE
│   ├── lib/                           ← All Opt4J JARs (compile classpath)
│   ├── src/
│   │   ├── Drones/                    ← Working copy (modify this)
│   │   └── VRP_XL/                    ← Original baseline (read-only)
│   ├── plugins/                       ← Compiled plugin JARs
│   │   ├── CAE_TSP_CSV.jar
│   │   ├── VRP_XL.jar
│   │   └── Drones.jar                 ← Output of compile.sh
│   ├── compile.sh                     ← Build script for Drones.jar
│   └── jre1.8.0_301/                 ← Bundled Windows JRE
│
├── experiments/
│   ├── VRP_MO/                        ← Active working experiment folder
│   │   ├── config/
│   │   │   ├── experiments/           ← configN.xml files go here
│   │   │   └── reference-points/
│   │   │       └── points.txt         ← Ideal and nadir reference points
│   │   ├── src/
│   │   │   ├── run_experiments.py     ← Orchestrates Opt4J runs
│   │   │   └── run_metrics.py         ← Computes HV and Epsilon metrics
│   │   ├── scripts/
│   │   │   ├── run_experiments.bat    ← Launcher for run_experiments.py
│   │   │   ├── run_metrics.bat        ← Launcher for run_metrics.py
│   │   │   └── IndexPlots.plot        ← gnuplot index to view all plots
│   │   └── data/
│   │       ├── logs/                  ← Raw TSV output: <exp>_<run>.tsv
│   │       └── results/              ← Metrics, fronts, gnuplot scripts
│   │           ├── HV-ExpN.txt
│   │           ├── HVBest-ExpN.txt
│   │           ├── RefFront-ExpN.txt
│   │           ├── metrics-summary.csv
│   │           └── plots/
│   │               ├── HVBoxplot.plot
│   │               ├── EpsilonBoxplot.plot
│   │               ├── RefFronts.plot
│   │               └── ParetoRunsExpA_vs_ExpB.plot
│   └── _ejemplo/                      ← Completed reference example (read-only)
│       └── (same structure as VRP_MO, with 5 experiments × 30 runs)
│
├── tsp_experiments/                   ← TSP mono-objective convergence study
│   ├── instances/                     ← TSP benchmark instances
│   ├── mono_exp1/ mono_exp2/ mono_exp3/
│   └── mono_exp_PLANTILLA/            ← Blank template for new TSP experiments
│
│
├── docs/                              ← Course PDFs and reference docs
│   ├── prototipo_VRP_Drones.pdf
│   └── Experimentacion_AGs_Multiobjetivo.pdf
│
└── other_software/                    ← Auxiliary tools (gnuplot, NetLogo)
```

---

## Example Experiments (Reference — `experiments\_ejemplo\`)

A completed 5-experiment study on VRP (100 clients, 10 vehicles). `data\logs\` already contains all 150 TSV files (5 experiments × 30 runs), so running `run_experiments.bat` on it will skip every run with `Ya existe X_Y.tsv. Se omite` — this is expected. Skip straight to Step 4 (`run_metrics.bat`) to explore the results.

| Exp | Algorithm | Generations | mu | lambda | HV mean | Notes |
|-----|-----------|-------------|-----|--------|---------|-------|
| 1 | NSGA-II | 1000 | 100 | 100 | 0.705 | Baseline |
| 2 | NSGA-II | 4000 | 25 | 25 | 0.701 | More generations, small offspring |
| 3 | NSGA-II | 10000 | 25 | 25 | 0.772 | Long run, small offspring |
| 4 | NSGA-II | 10000 | 100 | 100 | **0.880** | Long run, large offspring — best |
| 5 | Random Search | 10000 | — | — | 0.500 | Baseline comparison — worst |

Reference `points.txt`: `1 1` / `4000 11`

---

## Generated Files Reference

All generated files live inside `data\`. The `config\` and `scripts\` folders are never modified by the scripts.

| File | Created by |
|---|---|
| `data\logs\<N>_<run>.tsv` | `run_experiments.bat` — one per run |
| `data\logs\config-exp<N>.xml` | `run_experiments.bat` — config snapshot for traceability |
| `data\results\HV-Exp<N>.txt` | `run_metrics.bat` |
| `data\results\HVBest-Exp<N>.txt` | `run_metrics.bat` |
| `data\results\RefFront-Exp<N>.txt` | `run_metrics.bat` |
| `data\results\RefFront-Global.txt` | `run_metrics.bat` (global epsilon mode only) |
| `data\results\metrics-summary.csv` | `run_metrics.bat` |
| `data\results\plots\ParetoRunsExpA_vs_ExpB.plot` | `run_experiments.bat` |
| `data\results\plots\HVBoxplot.plot` | `run_metrics.bat` |
| `data\results\plots\EpsilonBoxplot.plot` | `run_metrics.bat` |
| `data\results\plots\RefFronts.plot` | `run_metrics.bat` |

---

## Files to Review When the Folder Structure Changes

Any time an experiment folder is renamed/moved, or `opt4j\` is relocated, the following files contain hardcoded paths that must be updated manually.

### Per experiment folder (applies to both `VRP_MO\` and `_ejemplo\`)

| File | Hardcoded path | What to update |
|------|---------------|----------------|
| `scripts\run_experiments.bat` | `OPT4J_CMD=..\..\opt4j\bin\opt4j-JVM1.8.bat` | Relative path from experiment root to the Opt4J launcher |
| `scripts\run_metrics.bat` | `LOG_DIR`, `POINTS_FILE`, `OUT_DIR` (relative to experiment root) | Only change if internal experiment structure changes |
| `scripts\IndexPlots.plot` | `plots_dir = "data/results/plots"` | Only change if internal experiment structure changes |
| `data\results\plots\ParetoRunsExpA_vs_ExpB.plot` | `data_dir="../../logs"` | Auto-generated — delete and re-run `run_experiments.bat` to regenerate |

### If `opt4j\` is renamed or moved

Update `OPT4J_CMD` in all `run_experiments.bat` files across every experiment folder. The metrics scripts and gnuplot files are not affected — they do not reference `opt4j\`.

### If an experiment folder is moved deeper or shallower

The `..\..` in `run_experiments.bat` climbs from `<expFolder>\` (one level) up to `experiments\` (second level) and then into `opt4j\`. Adjust the number of `..` to match the new depth:

```
experiments\VRP_MO\   →  ..\..\opt4j\bin\opt4j-JVM1.8.bat   (2 levels up to CAE1\)
experiments\sub\EXP\  →  ..\..\..\opt4j\bin\opt4j-JVM1.8.bat (3 levels up to CAE1\)
```

### Checklist

When reorganizing, go through this list in order:

- [ ] `experiments\<folder>\scripts\run_experiments.bat` — update `OPT4J_CMD`
- [ ] Re-run `run_experiments.bat` (regenerates `ParetoRunsExpA_vs_ExpB.plot`)
- [ ] Re-run `run_metrics.bat` (regenerates all boxplot and RefFronts scripts)
- [ ] Update the **File Paths Quick Reference** section below

---

## File Paths Quick Reference

| What | Path (relative to `CAE1\`) |
|------|---------------------------|
| Opt4J Windows launcher (bundled JRE) | `opt4j\bin\opt4j-JVM1.8.bat` |
| All Opt4J JARs (classpath) | `opt4j\lib\*.jar` |
| Plugin folder | `opt4j\plugins\` |
| Drones plugin source | `opt4j\src\Drones\` |
| VRP_XL baseline source | `opt4j\src\VRP_XL\` |
| Build script | `opt4j\compile.sh` |
| Active experiment folder | `experiments\VRP_MO\` |
| Reference example folder | `experiments\_ejemplo\` |
| Experiment configs | `experiments\<folder>\config\experiments\config<N>.xml` |
| Reference points | `experiments\<folder>\config\reference-points\points.txt` |
| Experiment runner | `experiments\<folder>\src\run_experiments.py` |
| Metrics script | `experiments\<folder>\src\run_metrics.py` |
| Raw logs | `experiments\<folder>\data\logs\<exp>_<run>.tsv` |
| Metrics summary | `experiments\<folder>\data\results\metrics-summary.csv` |
| gnuplot plots | `experiments\<folder>\data\results\plots\*.plot` |
| Plot index | `experiments\<folder>\scripts\IndexPlots.plot` |
