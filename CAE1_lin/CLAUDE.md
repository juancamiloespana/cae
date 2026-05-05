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
├── docs/                   ← course PDFs
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

---

## Windows execution

- Use `opt4j\bin\opt4j-JVM1.8.bat` — sets `JAVA_HOME=..\jre1.8.0_301` automatically
- Plugin JARs in `opt4j\plugins\` are picked up automatically on GUI launch
- `.classpath` / `.project` inside JARs have hardcoded paths to the professor's machine — ignore them

---

## What to ignore

- `opt4j/jre1.8.0_301/` — Windows-only PE32 binaries, useless on Linux
- `*.bat` files — Windows only
- `.classpath` / `.project` inside JARs — Eclipse files with hardcoded Windows paths
