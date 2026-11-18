# Work Guide — Drone Route Optimization (CAE1 Final Project)

Full context reference for the entire project. Each section below maps directly to a
section of `docs/informe_latex/main.tex`.

**Deadline:** 18 May 2026 · **Instance:** Valdebueyes3 · **Max drones:** 10

---

## Grading weights (quick reference)

| Block | Report section | Weight |
|---|---|---|
| 1. Problem modelling | §1 Introducción + §2 Modelamiento Formal | 15% |
| 2. GA modelling + code | §3 Modelamiento AG + §4 Descripción Código | 15% |
| 3. Phase 1 convergence | §5 Fase 1 | 15% |
| 4. Phase 2 parametric | §6 Fase 2 | 20% |
| 5. Multi-objective analysis | §7 Indicadores | 20% |
| 6. Solution interpretation | §9 Interpretación Pareto | 10% |
| 7. Clarity, reproducibility | §11–12 Aportaciones + Referencias | 5% |

---

## §1 — Introducción y Contexto del Problema (Block 1 · 15%)

### What to cover
- Control station: coordinates, role as common origin/destination.
- Available drones: fleet size, homogeneous, identified by integer id.
- Sweeps: pairs of 2D points, atomic units (both endpoints always traveled together).
- Flight routes: ordered sequences of points from CS through sweeps back to CS.
- Candidate solutions: what a valid solution looks like.
- Objectives to minimize.
- Simplifying assumptions:
  - Single altitude (2D problem).
  - No flight time modelling.
  - No autonomy (range) constraint.
  - Homogeneous fleet.
  - Single CS shared by all drones.

### Key point for "Excelente"
The rubric checks explicitly that the **implicit last drone** is described correctly:
a drone with no sweeps assigned has route CS→CS with distance 0 and is not counted
as active. This must be stated, not assumed.

---

## §2 — Modelamiento Formal del Problema (Block 1 · 15%)

### Professor's guidance
A formal mathematical formulation (indices, parameters, decision variables, auxiliary
variables, objective functions, constraints) is preferred — it leads to a clearer and
more compact description than a prose equivalent.

See [math_formulation_guide.md](math_formulation_guide.md) for the complete reference
draft, notation conventions, and feedback protocol. **Status: complete and verified.**

### VRP → Drones concept mapping

| VRP concept | Drone concept |
|---|---|
| Depot | Control Station (CS) — coordinates `(x_cs, y_cs)` |
| Vehicle `i` | Drone `i` — identified by integer id |
| Client `j` — point `(x, y)` | Swept `j` — segment `(x1, y1, x2, y2)` |
| Route | Flight path starting and ending at CS |

---

## §3 — Modelamiento del Algoritmo Genético (Block 2 · 15%)

This is the most detailed section to write. The goal is that **any engineer who knows
GAs** could read this section alone and understand what algorithm is running, what it
operates on, and what it produces — without seeing the code.

### Rubric checklist — all items must be explicitly covered

| Item | Where in the section |
|---|---|
| Genotype representation | Genotype subsection |
| Phenotype representation | Decoding / Phenotype subsection |
| Role of `Creator` | Creator subsection |
| Role of `Decoder` | Decoding subsection |
| Role of `Evaluator` | Evaluator subsection |
| Chromosome → drone routes → objective values chain | Explicit end-to-end paragraph |
| Why permutation operators can be reused | Dedicated subsection |
| Relation to VRP and to the drone problem | Explicit paragraph at the start of §3 |

### End-to-end chain — must be stated as a single coherent paragraph

The section must include one paragraph that traces the full pipeline explicitly:

> The chromosome (permutation of sweep ids and drone separators) is decoded by
> `VRPDecoder` into a set of drone routes (`VRPRoutes`). `VRPEvaluator` then computes
> `(f1, f2) = (max_distance, num_vehicles)` from those routes. NSGA-II uses these
> values to rank and select individuals for the next generation.

This chain — chromosome → routes → objectives → selection — must be visible as a
unit, not only inferable from reading three separate subsections.

### Relation to VRP — must be stated in §3, not only in §2

The section must briefly restate or reference the VRP → Drones mapping and explain
why this means standard VRP permutation operators apply without modification.
A one-paragraph reminder is sufficient: the drone problem is a direct adaptation of
VRP where clients become sweeps (two endpoints instead of one), the depot becomes the
CS, and vehicles become drones. The encoding and operators are inherited directly.

### Algorithm: NSGA-II + permutation operators

The base algorithm is **NSGA-II** (Deb et al. 2002). NSGA-II fixes selection
(non-dominated sorting + crowding distance) and replacement strategy. The remaining
operators — crossover and mutation — are chosen separately and described below.

You do **not** need to reproduce the NSGA-II pseudocode in full. Cite the original
paper and state which components it provides. Then describe only the operators you
chose and why they are compatible with the encoding.

### Inputs (what the algorithm receives)

- **Swept file** (`fileName`): list of sweeps, each as `X1 Y1 X2 Y2` (four columns).
  Instance Valdebueyes3 has 121 sweeps → 242 endpoint coordinates.
- **CS file** (`fileNameCS`): single line with `X Y` coordinates of the control station.
- **Parameters**: population size `alpha = mu = lambda`, number of generations,
  crossover operator + rate, mutation operator + rate, tournament size.

### Outputs (what the algorithm produces)

The output is an **approximation of the Pareto front** — a set of non-dominated
solutions. Each solution in the front is:
- A **phenotype** (`VRPRoutes`): a set of drone routes, each a list of `Point` objects
  starting and ending at CS.
- A pair of **objective values**: `(max_distance, num_vehicles)`.

The front approximation is what gets stored, visualized, and compared using HV and
epsilon. Individual route plans (phenotypes) are used for the interpretation in §9.

### Genotype representation

A **permutation without repetition** of `n + (m-1)` integers, where:
- `n` = number of sweeps (121 for Valdebueyes3)
- `m` = maximum number of drones (10)
- `m-1` = 9 drone separator genes

So the chromosome has **130 genes** total: 121 sweep ids + 9 drone ids.

The **last drone is implicit** — it does not appear in the chromosome. Its sweeps are
those remaining after all separator genes have been processed.

### Decoding: genotype → phenotype

The `VRPDecoder` reads the chromosome left to right:

1. Appends the implicit last drone gene at the end.
2. Sweeps between two consecutive drone genes are assigned to the drone immediately
   following them.
3. Two consecutive drone genes → that drone's route is empty → drone not used.
4. For each assigned sweep, the decoder computes the drone's current position (last
   point added to its route) and adds the sweep's two endpoints in **nearest-first
   order** (the endpoint closer to the current position is added first).
5. Every drone route begins and ends at CS.

The result is a `VRPRoutes` phenotype — the set of all drone routes.

### Evaluator

The `VRPEvaluator` computes both objective values from the phenotype:
- `f1 = max_distance`: maximum total route distance among all active drones.
- `f2 = num_vehicles`: count of drones whose route distance > 0.

Both are minimized simultaneously by NSGA-II.

### Creator

`VRPCreator` generates an initial random permutation of the 130 genes. No modification
was needed — `Swept` extends `Client`, so the existing permutation logic handles it.

### Why standard permutation operators work

Sweep genes (`Swept`) are subclasses of `Client`, so any permutation crossover or
mutation operator that preserves the permutation property (no duplicates, all genes
present) is valid. Drone separator genes are treated as ordinary permutation elements —
their relative order determines the drone assignment boundaries.

### Operators used (describe in report)

For each operator selected in Phase 2, state:
1. Its name in Opt4J.
2. What it does structurally to the chromosome.
3. Why it is compatible with the permutation encoding.
4. What parameter it exposes (rate, etc.) and what value was selected.

---

## §4 — Descripción del Código Implementado (Block 2 · 15%)

### Professor's guidance
Describe only the **changes made from VRP to Drones**. You do not need to explain
every file. The explanation of experiment scripts (batch runner, HV/epsilon calculator,
gnuplot scripts) is **not required** — only your code changes.

### What changed

**`VRPProblem.java`** — three changes:
1. Add `Swept` as a subclass of `Client` with a second coordinate pair `(x2, y2)` and
   a `getPoint2()` method.
2. Replace `readInstance()` with `readSwepts()` that reads four columns per row.
3. Add `fileNameCS` parameter and `readCS()` method to load the CS coordinates from a
   separate file.

**`VRPDecoder.java`** — one change in `decode()`:
- For each gene that is a `Swept` (not a plain `Client`), compare distances from the
  drone's current position to both endpoints and add them in nearest-first order.
- Replaces the old single-point add with a two-point conditional add.

**`VRPModule.java` / `DronesModule.java`**:
- Add `fileNameCS` and `fileName` GUI fields with `@Constant` and `@File` annotations.
- Field order in source determines GUI display order.

**No changes needed in:** `VRPCreator`, `VRPEvaluator`, `VRPRoutes`, `VRPRoute`,
`VRPWidgetService`, `VRPWidgetXLService` — these are reused without modification.

### Compile and deploy
```bash
cd opt4j
./compile.sh        # produces plugins/VRP_XL.jar
```
Then sync to Windows: see CLAUDE.md for rsync commands.

---

## §5 — Fase 1: Evaluación de la Convergencia Práctica (Block 3 · 15%)

### Goal
Establish a **base configuration** with sufficient convergence before any parametric
comparison. An unconverged base invalidates all Phase 2 comparisons.

### Protocol
1. Fix `alpha = mu = lambda` (fully generational model).
2. Choose initial population size and generation count.
3. Run in Opt4J GUI — observe both objective curves visually.
4. If either curve has not plateaued, double the generations (or population).
5. Does doubling yield ≥ 1% improvement? If yes, keep increasing. If no, stop.
6. Also verify the Pareto front spans the full solution space (from minimum drones
   to minimum distance) — full coverage confirms the approximation is trustworthy.
7. The final configuration is the **base for Phase 2**.

### Number of runs
Phase 1 uses **single manual runs** via the GUI — not 10 independent runs.
The 10-run protocol applies only in Phase 2 (Block 5).

### Professor note — run count
The course statement asks for 10 independent runs per configuration. The example
report shows 30. **10 runs is sufficient** — the professor confirmed this explicitly
to avoid blocking machines.

### Configurations evaluated: C0–C5
See `main.tex` §5 table for the full sequence. Selected base: **C4**
(`alpha = mu = lambda = 100`, 40.000 generations). C5 (80.000 gen) yields < 1%
improvement in all distance metrics and is discarded.

---

## §6 — Fase 2: Análisis Paramétrico (Block 4 · 20%)

### Important: alpha = mu = lambda applies ONLY to Phase 1

The enunciado (section 6.1) explicitly states that `alpha = mu = lambda` is a
constraint maintained **during Phase 1 only**. In Phase 2 there is no such
requirement — you may vary `alpha`, `mu`, and `lambda` independently if you choose
to study population parameters. The base configuration C4 happens to have them
equal (all 100), but this is the starting point, not a constraint that must be
maintained throughout Phase 2.

### Principle: one factor at a time
1. Start from base configuration (C4).
2. Change **one** operator or parameter.
3. Keep everything else fixed.
4. Run **10 independent executions**.
5. Compare using HV, epsilon, and stability (boxplots).
6. Best alternative becomes the new base. Move to next factor.

Justify the **order** in which factors are studied — it is a methodological decision.

### Mandatory factors (minimum)

**1. Crossover operator** — test all operators compatible with permutation encoding.
Report: which are compatible and why, which wins, whether differences are meaningful.

**2. Crossover rate (`crossoverRate`)** — must include default `0.95` and ≥ 2
alternatives. If best is at boundary, reason whether to explore further.

**3. Mutation rate (`mutationRate`)** — compare default adaptive rate vs. ≥ 2 fixed
constants. Reason about exploration/exploitation balance.

**4. Mutation operator** — `MIXED` is mandatory baseline. Individual operators optional
but valued if well justified.

### Final contrast: Random Search
After selecting final GA configuration, run **Random Search** with the same total
evaluations, 10 times independently, same metrics. Answer: does the GA add real value?

---

## §7 — Indicadores y Análisis de Resultados (Block 5 · 20%)

### Per configuration, collect
- HV for each of the 10 runs → `HV-Exp<n>.txt`
- Epsilon indicator for each run
- Pareto front approximations (all 10 runs overlaid)
- Stability: mean, median, IQR, boxplots

### Decision rule
Best = highest average HV. Tiebreak = lowest average epsilon. A configuration with
slightly lower mean HV but much better stability may be preferable — discuss explicitly.

### Critical requirements
- Reference point, ideal point, and nadir point **documented and consistent** across
  all configurations. Configure `hv/points.txt` before computing hypervolumes.
- Do not report only the mean — stability and dispersion are explicitly evaluated.
- In MOO there is no single "best fitness" per run — output is a Pareto front.

### Graphs
Professor confirmed: **Python-generated graphs are acceptable**. Include them in the
report body; if page limit is exceeded, move to an annex. You decide which graphs to
include.

Every plot must have: title, labeled axes, labeled series, caption, consistent ranges
across related plots.

---

## §8 — Contraste con Búsqueda Aleatoria (Block 4 · 20%)

Covered in §6 above under "Final contrast: Random Search."

---

## §9 — Interpretación de Soluciones Representativas del Frente de Pareto (Block 6 · 10%)

### Required: ≥ 3 representative solutions

| Solution type | Focus |
|---|---|
| Few drones | High workload per drone — is max distance operationally acceptable? |
| Low max distance | How many drones needed? Is fleet size realistic? |
| Compromise | Trade-off justification — which would you actually deploy and why? |

### Per solution, quantify
- Number of active drones.
- Sweep assignment per drone.
- Total distance per drone route.
- **Non-useful distance** per drone (transit between sweeps and CS).
- Widget-generated image of the route plan.

### Key point for "Excelente"
Go beyond numbers. Explain what the solution means operationally — coverage balance,
risk, deployment decisions in the context of forest surveillance.

---

## §10 — Conclusiones (Block 7 · 5%)

Synthesis of results across all phases. At minimum address:
- What the convergence analysis established and why C4 was selected.
- Which parametric configuration won Phase 2 and what the key trade-offs were.
- Whether NSGA-II adds real value over Random Search.
- Which Pareto front solution would be operationally recommended and why.

---

## §11 — Aportaciones Individuales (Block 7 · 5%)

### What the enunciado requires
The section must be titled **"Aportaciones de los miembros del grupo"** and include
a table with at minimum three columns: Estudiante / Aportaciones realizadas /
Evidencias o partes del trabajo asociadas. A fourth column "Valoración del grupo"
(Significativa / Parcial / Insuficiente) is also expected.

### What counts as sufficient (rúbrica — Excelente)
Contributions must be **concrete, verifiable, and coherent** with the delivered
memory, code, and results. The professor cross-checks the table against:
- The code and which files were modified.
- The Excel of experimental results.
- Config files, scripts, plots, screenshots.
- Intermediate versions, commits, or edit history.

### What does NOT count
- Generic labels: "redacción", "revisión", "ayuda en la memoria".
- Descriptions not tied to a specific technical, experimental, or analytical task.
- Nominal presence in the group with no traceable output.

A declaration from the rest of the group that a member did not participate
significantly is treated as a relevant evidence — that member may receive an
individual fail even if the group grade passes.

### How to write each entry — concrete examples

| Too vague (fail risk) | Concrete (acceptable) |
|---|---|
| Redacción de la memoria | Redacción de §2 (formulación matemática) y §3 (genotipo, decoder, evaluator) |
| Revisión del código | Implementación de `Swept` en `VRPProblem.java` y modificación del decoder para extremo más cercano |
| Análisis de resultados | Ejecución de 10 runs para experimentos E1–E4, cálculo de HV y épsilon, boxplots de estabilidad |
| Preparación de experimentos | Diseño de configs XML para Fase 2 (cruce y tasa de mutación), ejecución de scripts y validación de TSVs |
| Interpretación del frente | Selección y análisis operativo de 3 soluciones representativas del frente Pareto (§9) |
| Visualización | Generación de gráficas de convergencia con `analysis.py` e inclusión en LaTeX |

### Structure to use in main.tex

```latex
\begin{table}[H]
\centering
\begin{tabular}{p{3cm} p{7cm} p{3cm} p{2cm}}
\toprule
\textbf{Estudiante} & \textbf{Aportaciones realizadas} & \textbf{Evidencias} & \textbf{Valoración} \\
\midrule
Nombre 1 & ... & Clases modificadas, secciones X, Y & Significativa \\
Nombre 2 & ... & Configs XML, Excel, gráficas & Significativa \\
...
\bottomrule
\end{tabular}
\end{table}
```

The `Evidencias` column should name **specific files, sections, tables, or scripts**
— not categories. The more specific, the more defensible.

---

## §12 — Referencias y Recursos Utilizados (Block 7 · 5%)

Replace the placeholder entry in `ref.bib`. Cite at minimum:
- Opt4J paper.
- NSGA-II paper (Deb et al. 2002).
- Course materials as applicable.

---

## Deliverables checklist

- [ ] Report PDF (12–15 pages, excluding annexes).
- [ ] ZIP with final source code (only modified files required, not the full framework).
- [ ] Excel with full experimental results (configurations, seeds, HV and epsilon per run,
      summary, final configuration, representative solutions).
- [ ] Individual contributions table (concrete, verifiable, consistent with deliverables).
