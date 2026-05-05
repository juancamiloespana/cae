# Experiment Workflow — VRP Multi-Objective (Opt4J)

All commands are run from inside the experiment folder (e.g. `experiments\VRP_MO\`).

For context on the folder structure, algorithms, and generated files see [exp_reference.md](exp_reference.md).

---

## Step 0 — Clean the folder for a new experiment

Clear all generated outputs and old configs before starting fresh:

```
rmdir /s /q data
del /q config\experiments\*.xml
```

- `data\` holds all logs, metrics, and plots — the scripts recreate it automatically.
- `config\experiments\*.xml` — delete old configs so they don't get picked up in the new run.

**Partial resets** (if you only need to redo part of the workflow):

```
REM Re-run only Opt4J, keep metrics
del /q data\logs\*.tsv

REM Re-run only metrics, keep logs
rmdir /s /q data\results
```

---

## Step 1 — Design your experiment plan

Each experiment is a different algorithm configuration. Create one `configN.xml` per experiment inside `config\experiments\`. Files must be named `config1.xml`, `config2.xml`, etc.

**Minimal XML template (NSGA-II + VRP):**

```xml
<configuration>
  <module class="org.opt4j.CAE.VRP.VRPModule">
    <property name="clients">100</property>
    <property name="totalVehicles">10</property>
  </module>
  <module class="org.opt4j.core.common.logger.LoggerModule">
    <property name="filename">output.tsv</property>
    <property name="loggingPerEvaluation">false</property>
    <property name="evaluationStep">100</property>
    <property name="loggingPerIteration">true</property>
    <property name="iterationStep">1000</property>
  </module>
  <module class="org.opt4j.optimizers.ea.EvolutionaryAlgorithmModule">
    <property name="generations">1000</property>
    <property name="alpha">100</property>
    <property name="mu">100</property>
    <property name="lambda">100</property>
    <property name="crossoverRate">0.95</property>
  </module>
  <module class="org.opt4j.optimizers.ea.Nsga2Module">
    <property name="tournament">2</property>
  </module>
</configuration>
```

**Key parameters to vary across experiments:**

| Parameter | Description | Example values |
|-----------|-------------|----------------|
| `generations` | Total number of NSGA-II generations | 1000, 4000, 10000 |
| `iterationStep` | Must match `generations` (logs only final front) | same as generations |
| `alpha` | Population size | 100 |
| `mu` | Number of parents selected per generation | 25, 100 |
| `lambda` | Number of offspring per generation | 25, 100 |
| `crossoverRate` | Probability of crossover | 0.95 |
| `tournament` | Tournament size for NSGA-II selection | 2 |
| `clients` | Number of VRP clients (problem size) | 100 |
| `totalVehicles` | Maximum vehicles available | 10 |

**Alternative algorithm (Random Search):**

```xml
<module class="org.opt4j.optimizers.rs.RandomSearchModule">
  <property name="batchsize">100</property>
  <property name="iterations">10000</property>
</module>
```

**Important:** `iterationStep` in `LoggerModule` must equal `generations` so Opt4J writes only the final Pareto front approximation per run (not intermediate snapshots).

---

## Step 2 — Define reference points

Edit `config\reference-points\points.txt`. It must contain **exactly 2 non-empty lines**: the ideal point and the nadir point.

```
<zideal_1> <zideal_2>
<znadir_1> <znadir_2>
```

**Rules:**
- `ideal < nadir` for each objective (strict inequality)
- All objectives are treated as minimization
- Values separated by spaces (not commas)
- Comments allowed (lines starting with `#`)

**Example for VRP (used in reference experiments):**

```
1  1
4000 11
```

Interpretation:
- Objective 1 (`max_distance`): ideal = 1, nadir = 4000
- Objective 2 (`num_vehicles`): ideal = 1, nadir = 11

**How to choose ideal/nadir:**
- Run a few exploratory runs first to see the range of objective values in the TSV logs
- Set ideal slightly below the best observed value
- Set nadir at or above the worst observed value
- If a point falls outside `[ideal, nadir]`, `run_metrics.py` fails by default — use `--allow-outside-box` to discard them instead

---

## Step 3 — Run experiments

From inside `experiments\VRP_MO\`:

```
scripts\run_experiments.bat
```

Or call Python directly for more control:

```
python src\run_experiments.py ^
  --opt4j-cmd ..\..\opt4j\bin\opt4j-JVM1.8.bat ^
  --exp-dir config\experiments ^
  --log-dir data\logs ^
  --results-dir data\results ^
  --runs 30 ^
  --total 5
```

**Key arguments:**

| Argument | Description | Default |
|----------|-------------|---------|
| `--opt4j-cmd` | Path to Opt4J launcher (required) | — |
| `--exp-dir` | Folder containing configN.xml files | `experimentos` |
| `--log-dir` | Where to write `<exp>_<run>.tsv` logs | `log` |
| `--results-dir` | Where to write gnuplot scripts | `data\results` |
| `--runs` | Number of runs per experiment | 30 |
| `--total` | Total number of experiments (auto-detected if omitted) | auto |
| `--experiments` | Run only specific experiments, e.g. `1,3,5` | all |
| `--force-rerun` | Re-run even if log file already exists | false |

**Output log format (`data\logs\<exp>_<run>.tsv`):**

```
iteration   evaluations   runtime[s]   max_distance[MIN]   num_vehicles[MIN]
1000        100000        2.55         453.62              10
1000        100000        2.55         843.06              5
...
```

Each row is one solution on the final Pareto front. Objectives start at **column 4** (1-indexed).

---

## Step 4 — Run metrics

From inside `experiments\VRP_MO\`:

```
scripts\run_metrics.bat
```

Or call Python directly:

```
python src\run_metrics.py ^
  --log-dir data\logs ^
  --points config\reference-points\points.txt ^
  --nobj 2 ^
  --out-dir data\results
```

**Key arguments:**

| Argument | Description | Default |
|----------|-------------|---------|
| `--log-dir` | Folder with `<exp>_<run>.tsv` files (required) | — |
| `--points` | Path to `points.txt` (required) | — |
| `--nobj` | Number of objectives (required) | — |
| `--out-dir` | Where to write results | `.` |
| `--experiments` | Compute only specific experiments | all |
| `--epsilon-ref-mode` | `experiment` or `global` combined front as epsilon reference | `experiment` |
| `--allow-outside-box` | Discard points outside ideal-nadir instead of failing | fail |

**Note:** HV computation is implemented **only for 2 objectives** (`--nobj 2`).

**Example `metrics-summary.csv` (reference experiments):**

| experiment | runs | hv_mean | hv_std | hv_median | eps_mean | hv_combined |
|------------|------|---------|--------|-----------|----------|-------------|
| 1 | 30 | 0.705 | 0.028 | 0.711 | 0.115 | 0.763 |
| 4 | 30 | 0.880 | 0.007 | 0.881 | 0.036 | 0.894 |

Higher HV = better (1.0 = perfect). Lower Epsilon = better (0 = reference-quality front).

---

## Step 5 — Visualize with gnuplot

From inside `experiments\VRP_MO\`:

```
gnuplot scripts\IndexPlots.plot
```

Loads 4 plots in sequence (press Enter between each):

1. **HVBoxplot** — quality and stability per experiment
2. **EpsilonBoxplot** — quality and robustness per experiment
3. **RefFronts** — overlay of all reference Pareto fronts
4. **ParetoRunsExpA_vs_ExpB** — all 30 runs of experiments 1 and 2

Or load individually:

```
gnuplot data\results\plots\HVBoxplot.plot
gnuplot data\results\plots\RefFronts.plot
```

**Customizing `ParetoRunsExpA_vs_ExpB.plot`** — edit the top variables:

```gnuplot
exp1=1       # first experiment to compare
exp2=3       # second experiment to compare
run_end=30   # number of runs
obj_x_col=4  # TSV column for x-axis objective
obj_y_col=5  # TSV column for y-axis objective
```

---

## Common Issues

| Problem | Likely cause | Fix |
|---------|-------------|-----|
| All runs say `Ya existe X_Y.tsv. Se omite` | `data\logs` already contains TSV files from a previous run | Delete the TSV files in `data\logs\` and re-run, or pass `--force-rerun` to overwrite them |
| `No se ha generado output.tsv` | `iterationStep` ≠ `generations` or Opt4J crashed | Set `iterationStep` = `generations` in XML |
| `puntos fuera de la caja ideal-nadir` | Nadir is too tight | Widen nadir in `points.txt` or use `--allow-outside-box` |
| `points.txt debe contener exactamente 2 lineas` | Blank line in file | Remove blank lines from `points.txt` |
| `ideal (X) debe ser < nadir (Y)` | ideal ≥ nadir | Fix `points.txt` so ideal < nadir strictly |
| `No se encontraron ficheros configN.xml` | Wrong file names | Rename to `config1.xml`, `config2.xml`, ... |
| gnuplot shows wrong range | `xrange`/`yrange` clipped | Comment out or adjust range in the `.plot` file |
