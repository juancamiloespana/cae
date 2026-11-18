# CLAUDE.md — CAE1

## What this project is

University master's course: **CAE (Conocimiento Aplicado a Empresas)** — implementing and modifying metaheuristic optimization algorithms using the **Opt4J v3.2** framework.

The workflow is: write and compile Java source on Linux (WSL2), then run the full Opt4J GUI on Windows.

---

## Sync between WSL and Windows

WSL path: `/home/personal/cod_lin/CAE_lin/CAE1_lin/`  ← this project root
Windows path: `/mnt/d/cod/CAE1_win/`

**"Take to Windows" / "send to Windows"** — push WSL → Windows:

```bash
rsync -av --delete /home/personal/cod_lin/CAE_lin/CAE1_lin/ /mnt/d/cod/CAE1_win/
```

**"Bring from Windows" / "pull from Windows"** — push Windows → WSL:

```bash
rsync -av --delete /mnt/d/cod/CAE1_win/ /home/personal/cod_lin/CAE_lin/CAE1_lin/
```

To preview changes without applying them, add `--dry-run` to either command.

---

## Repository structure

```
CAE1/
├── CLAUDE.md               ← this file
├── .sdkmanrc               ← pins Java 8 (auto-switches on cd)
├── opt4j/                  ← the project
│   ├── src/
│   │   ├── Drones/         ← working copy — modify this for new experiments
│   │   └── VRP_XL/         ← original unmodified baseline (read-only reference)
│   ├── lib/                ← all opt4j JARs (compile classpath)
│   ├── plugins/            ← compiled plugin JARs
│   │   ├── CAE_TSP_CSV.jar ← course TSP/Bits plugin (no sources)
│   │   └── VRP_XL.jar      ← VRP multi-objective plugin
│   ├── bin/                ← launchers
│   │   ├── opt4j           ← Linux launcher (needs chmod +x)
│   │   ├── opt4j.bat       ← Windows launcher
│   │   ├── opt4j-JVM1.8.bat  ← Windows launcher with bundled JRE
│   │   └── batch.py        ← headless batch runner (Python)
│   ├── compile.sh          ← run from inside opt4j/ to build VRP_XL.jar
│   └── jre1.8.0_301/       ← bundled Windows JRE — IGNORE on Linux
├── experiments/
│   ├── VRP_MO/             ← active multi-objective VRP experiment
│   └── _ejemplo/           ← completed reference example (read-only)
├── tsp_experiments/        ← TSP mono-objective convergence study
├── docs/
│   ├── Práctica Final/     ← course PDFs (enunciado, rúbrica, guiones, slides)
│   └── informe_latex/      ← LaTeX report project (the deliverable report)
│       ├── main.tex        ← main document — all report sections go here
│       ├── ref.bib         ← BibTeX bibliography (natbib, plainnat style)
│       └── IEEEtran.cls    ← document class (present but using article class)
└── other_software/         ← gnuplot, NetLogo
```

---

## Java setup

- **Required version: Java 8** — course JARs and bundled Windows JRE target `JavaSE-1.8`
- **Managed via sdkman** — installed at `~/.sdkman`
- **Installed versions:** `8.0.482-tem` (this project) · `21.0.7-tem` (system default)
- **Auto-switching:** sdkman switches to Java 8 automatically on `cd` via `.sdkmanrc`
- **Manual switch:** `sdk use java 8.0.482-tem`
- **Verify:** `java -version` → `openjdk version "1.8.0_482"`

---

## Compile command

Run from inside `opt4j/`:

```bash
cd opt4j
./compile.sh
```

Or manually:

```bash
# from inside opt4j/
LIBPATH=$(pwd)/lib
CLASSPATH=$(ls $LIBPATH/*.jar | tr '\n' ':')

find src/Drones -name "*.java" > /tmp/sources.txt
javac -source 8 -target 8 -cp "$CLASSPATH" @/tmp/sources.txt -d /tmp/vrp_bin/
jar cf plugins/VRP_XL.jar -C /tmp/vrp_bin/ .
```

---

## Course plugins

### CAE_TSP_CSV.jar — package `org.opt4j.CAE`

**TSP** (`org.opt4j.CAE.salesman`): `SalesmanProblem`, `SalesmanCreator`, `SalesmanDecoder`, `SalesmanEvaluator`, `SalesmanRoute`, `SalesmanWidgetService`, `SalesmanModule`, `SalesmanWidgetModule`

**Bits** (`org.opt4j.CAE.bits`): `BitsProblem`, `BitsCreator`, `BitsDecoder`, `BitsEvaluator`, `BitsModule`, `SecuenciaBits`

Entry point: `org.opt4j.CAE.CAEModule` — only `.class` files, no source.

### VRP_XL.jar — package `org.opt4j.CAE.VRP`

`VRPProblem`, `VRPCreator`, `VRPDecoder`, `VRPEvaluator`, `VRPRoutes`, `VRPRoute`, `Point`, `VRPModule`, `VRPWidgetModule`, `VRPWidgetService`, `VRPWidgetXLModule`, `VRPWidgetXLService`

Source: `opt4j/src/Drones/` (working copy, edited per experiment) and `opt4j/src/VRP_XL/` (original baseline, do not modify).

---

## Opt4J framework basics

- **Dependency injection via Google Guice** — modules wire components together
- **Key interfaces:** `Creator<G>` · `Decoder<G,P>` · `Decoder<P>` · `Evaluator<P>`
- **Plugin loading** — Opt4J scans `plugins/` at startup; any JAR there is loaded automatically
- **Configuration via XML** — headless run: `opt4j-JVM1.8.bat -s config.xml`
- **Detailed reference:** see [exec_guides_md/module_reference.md](exec_guides_md/module_reference.md)
- **Plugin workflow:** see [exec_guides_md/module_workflow.md](exec_guides_md/module_workflow.md)

---

## Experiments

- **Runner script:** `experiments/VRP_MO/scripts/run_experiments.bat` — runs Opt4J headlessly N times per config
- **Config files:** `experiments/VRP_MO/config/experiments/configN.xml` — must be named exactly `configN.xml`
- **Output:** `experiments/VRP_MO/data/logs/<exp>_<run>.tsv` — one file per run
- **Detailed reference:** see [exec_guides_md/exp_reference.md](exec_guides_md/exp_reference.md)
- **Experiment workflow:** see [exec_guides_md/exp_workflow.md](exec_guides_md/exp_workflow.md)

### WARNING — analysis.py

`experiments/VRP_MO/analysis.py` has **crashed the system** (full shutdown) due to exceeding memory/CPU capacity.

**Do NOT run or suggest running this file without explicit confirmation from the user.**

High-risk operations inside it:
- Compiling/aggregating many `.tsv` log files at once
- Large in-memory merges (left joins, concatenations across runs)
- Any bulk DataFrame operation over the full experiment output

Before executing, always check: number of `.tsv` files to be processed, available RAM, and whether a sampled/chunked approach can replace the full load.

---

## Windows execution

- Use `opt4j\bin\opt4j-JVM1.8.bat` — sets `JAVA_HOME=..\jre1.8.0_301` automatically
- Plugin JARs in `opt4j\plugins\` are picked up automatically on GUI launch
- `.classpath` / `.project` inside JARs have hardcoded paths to the professor's machine — ignore them

---

## Report (LaTeX)

The deliverable report is built from `docs/informe_latex/main.tex`.

**Document setup:**
- Class: `article`, 11pt, A4, 2.5cm margins
- Bibliography: `natbib` package, `plainnat` style, file `ref.bib`
- Citations: `\cite{key}` in text, entries added to `ref.bib`

**Current section structure in `main.tex`** (matches the mandatory report structure):
1. Introducción y Contexto del Problema
2. Modelamiento Formal del Problema de Drones
3. Modelamiento del Algoritmo Genético
4. Descripción del Código Implementado
5. Fase 1: Evaluación de la Convergencia Práctica
6. Fase 2: Análisis Paramétrico → subsection: Factores Mínimos de Estudio
7. Indicadores y Análisis de Resultados
8. Contraste con Búsqueda Aleatoria
9. Interpretación de Soluciones Representativas del Frente de Pareto
10. Conclusiones
11. Aportaciones Individuales
12. Referencias y Recursos Utilizados

**Group members** (already in `\author{}`):
- Andrés Augusto Aragón Dimas — UO316049
- Alejandro Arias Bordás — UO269395
- Alberto Martínez Olivar — UO282069
- Manuel De La Uz González — UO288991
- Juan Camilo España Lopera — UO318200

**Professor:** Jorge Puente Peinador

**Section → work guide block mapping:**

| LaTeX section | Work guide block | Key content |
|---|---|---|
| 1. Introducción y Contexto | Block 1 (15%) | CS, drones, sweeps, routes, candidate solutions, simplifying assumptions |
| 2. Modelamiento Formal | Block 1 (15%) | Mathematical formulation — see [math_formulation_guide.md](exec_guides_md/math_formulation_guide.md) |
| 3. Modelamiento del AG | Block 2 (15%) | Genotype (permutation + separators), phenotype (VRPRoutes), Creator/Decoder/Evaluator role |
| 4. Descripción del Código | Block 2 (15%) | Changes to VRPProblem (Swept class, readSwepts, readCS) and VRPDecoder (nearest-endpoint two-point add) |
| 5. Fase 1 | Block 3 (15%) | Convergence table (C0/C1/C2), alpha=mu=lambda, doubling protocol, decision rationale |
| 6. Fase 2 | Block 4 (20%) | One-factor-at-a-time table; crossover op, crossoverRate, mutationRate, mutation op |
| 6.1 Factores Mínimos | Block 4 (20%) | Which operators tested and why compatible; results per factor with HV/epsilon/stability |
| 7. Indicadores y Análisis | Block 5 (20%) | HV and epsilon per run (10 runs); boxplots; reference/ideal/nadir points documented |
| 8. Contraste Búsqueda Aleatoria | Block 4 (20%) | Random Search same evaluations, 10 runs, same metrics; does GA add value? |
| 9. Interpretación Pareto | Block 6 (10%) | ≥3 representative solutions: few drones / low max distance / compromise; non-useful distance |
| 10. Conclusiones | — | Synthesis of results, operational recommendations |
| 11. Aportaciones Individuales | Block 7 (5%) | Concrete technical contributions per person — not generic descriptions |
| 12. Referencias | Block 7 (5%) | Replace placeholder entry in ref.bib; cite actual sources used |

**LaTeX packages available in main.tex:**
- `graphicx` — `\includegraphics` for figures (gnuplot exports, widget screenshots)
- `booktabs` — `\toprule/\midrule/\bottomrule` for professional tables
- `listings` — code blocks (`\begin{lstlisting}[language=Java]`)
- `subcaption` + `float` — subfigures (`\begin{subfigure}`) and forced placement `[H]`
- `amsmath` — math environments (`equation`, `align`, `cases`)
- `natbib` (plainnat) — author-year citations; `\cite{}`, `\citep{}`, `\citet{}`

**Adding experiment figures:**
1. Export gnuplot plot to PNG/EPS: `set terminal png; set output 'fig.png'` then run the `.plot` script.
2. Place output in `docs/informe_latex/figures/` (create the folder).
3. Include in LaTeX: `\includegraphics[width=\linewidth]{figures/fig.png}`.
4. Wrap in `figure` environment with `\caption{}` and `\label{}`.

**ref.bib notes:**
- The current single entry (`chatterjee1999recursive`) is a placeholder — unrelated to the project.
- Replace with actual sources: Opt4J paper, NSGA-II paper (Deb et al. 2002), course materials as applicable.
- BibTeX key convention used in the file: `authorYYYYkeyword`.

**Known typo in main.tex:** `\author{}` lists Juan Camilo España Lopera as `U0318200` (letter U, not UO). Correct to `UO318200` when finalizing.

**Section 2 status (2026-05-07):** Mathematical formulation of Section 2 is complete and verified. Full backup saved in `exec_guides_md/math_formulation_guide.md` (Version 1). Next sections to write: Section 1 (Introducción) and Section 3 (Modelamiento del AG).

**LaTeX packages added:** `amssymb` — required for `\mathbb{R}` notation used in auxiliary variables.

**Compile (Linux):**
```bash
./docs/informe_latex/compile.sh
```

Or from inside `informe_latex/`:
```bash
./compile.sh
```

Intermediate files go to `out/`, final `main.pdf` is copied to `informe_latex/`. `compile.sh` is gitignored in the group repo.

**Group repo sync:**

`docs/informe_latex/` is a **separate nested git repo** connected to the group's GitHub:
`git@github.com:juancamiloespana/Grupo1_CAE_metaheuristica.git`

Teammates edit via Overleaf and sync with GitHub (Menu → GitHub → Push/Pull).

Daily workflow:
```bash
# before editing — get teammates' latest changes
cd docs/informe_latex
git pull origin main

# after editing — push your changes
git add main.tex ref.bib
git commit -m "your message"
git push origin main
```

Conflicts only happen when two people edit the **same line** simultaneously. Always pull before starting to edit.

---

## What to ignore

- `opt4j/jre1.8.0_301/` — Windows-only PE32 binaries, useless on Linux
- `*.bat` files — Windows only
- `.classpath` / `.project` inside JARs — Eclipse files with hardcoded Windows paths
