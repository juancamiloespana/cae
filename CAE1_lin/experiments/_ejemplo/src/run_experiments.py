#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Sequence


CONFIG_RE = re.compile(r"^config(\d+)\.xml$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Lanza multiples ejecuciones de experimentos Opt4J."
        )
    )

    parser.add_argument(
        "--opt4j-cmd",
        required=True,
        nargs="+",
        help=(
            "Comando para lanzar Opt4J. Se puede pasar como lista de tokens. "
            "Ejemplo Windows: --opt4j-cmd ..\\..\\opt4j-JVM1.8.bat "
            "Ejemplo Linux/macOS: --opt4j-cmd ../../opt4j-JVM1.8.sh"
        ),
    )
    parser.add_argument(
        "--exp-dir",
        default="experimentos",
        help="Carpeta con configN.xml",
    )
    parser.add_argument(
        "--log-dir",
        default="log",
        help="Carpeta donde guardar log/<exp>_<run>.tsv",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=30,
        help="Numero de ejecuciones por experimento",
    )
    parser.add_argument(
        "--total",
        type=int,
        default=None,
        help=(
            "Numero total de experimentos esperados. "
            "Si no se indica, se detectan automaticamente desde exp-dir."
        ),
    )
    parser.add_argument(
        "--experiments",
        default=None,
        help="Lista opcional de experimentos, por ejemplo: 1,2,5",
    )
    parser.add_argument(
        "--force-rerun",
        action="store_true",
        help="Reejecuta una corrida aunque ya exista log/<exp>_<run>.tsv",
    )
    parser.add_argument(
        "--output-file",
        default="output.tsv",
        help="Fichero temporal generado por Opt4J",
    )
    parser.add_argument(
        "--results-dir",
        default="data/results",
        help="Carpeta de resultados donde se creara plots/ParetoRunsExpA_vs_ExpB.plot",
    )
    parser.add_argument(
        "--workdir",
        default=".",
        help="Directorio de trabajo desde el que ejecutar Opt4J",
    )

    args = parser.parse_args()

    if args.runs <= 0:
        parser.error("--runs debe ser > 0")

    if args.total is not None and args.total <= 0:
        parser.error("--total debe ser > 0")

    if args.experiments is not None:
        args.experiments = parse_experiment_list(args.experiments)

    return args


def parse_experiment_list(text: str) -> List[int]:
    values = []
    seen = set()
    for token in text.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            exp_id = int(token)
        except ValueError as exc:
            raise ValueError(f"Identificador de experimento no valido: {token!r}") from exc
        if exp_id <= 0:
            raise ValueError(f"Los identificadores deben ser positivos: {token!r}")
        if exp_id not in seen:
            values.append(exp_id)
            seen.add(exp_id)
    if not values:
        raise ValueError("La lista de experimentos esta vacia")
    return sorted(values)


def discover_experiments(exp_dir: Path) -> List[int]:
    if not exp_dir.is_dir():
        raise FileNotFoundError(f"No existe la carpeta de experimentos: {exp_dir}")

    found = []
    for path in exp_dir.iterdir():
        if not path.is_file():
            continue
        m = CONFIG_RE.match(path.name)
        if m:
            found.append(int(m.group(1)))

    if not found:
        raise ValueError(f"No se encontraron ficheros configN.xml en {exp_dir}")

    return sorted(found)


def build_experiment_list(exp_dir: Path, total: int | None, selected: List[int] | None) -> List[int]:
    if selected is not None:
        for exp_id in selected:
            config = exp_dir / f"config{exp_id}.xml"
            if not config.is_file():
                raise FileNotFoundError(f"No existe {config}")
        return selected

    if total is not None:
        experiment_ids = list(range(1, total + 1))
        for exp_id in experiment_ids:
            config = exp_dir / f"config{exp_id}.xml"
            if not config.is_file():
                raise FileNotFoundError(f"No existe {config}")
        return experiment_ids

    return discover_experiments(exp_dir)


def ensure_exists(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"No existe {label}: {path}")


def run_command(cmd: Sequence[str], cwd: Path) -> None:
    result = subprocess.run(cmd, cwd=str(cwd))
    if result.returncode != 0:
        raise RuntimeError(f"El comando fallo con codigo {result.returncode}: {' '.join(cmd)}")


def run_opt4j(
    opt4j_cmd: Sequence[str],
    config_file: Path,
    workdir: Path,
) -> None:
    cmd = list(opt4j_cmd)
    launcher = Path(cmd[0])
    if not launcher.is_absolute():
        candidate = (workdir / launcher).resolve()
        if candidate.exists():
            cmd[0] = str(candidate)

    cmd += ["-s", str(config_file)]
    run_command(cmd, cwd=workdir)


def select_30fronts_experiments(experiment_ids: Sequence[int]) -> tuple[int, int]:
    if not experiment_ids:
        raise ValueError("No hay experimentos para seleccionar en ParetoRunsExpA_vs_ExpB.plot")
    if len(experiment_ids) == 1:
        return experiment_ids[0], experiment_ids[0]
    return experiment_ids[0], experiment_ids[1]


def write_30fronts_plot(
    results_dir: Path,
    log_dir: Path,
    exp1: int,
    exp2: int,
    max_run_id: int,
) -> Path:
    plots_dir = results_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    rel_log_dir = os.path.relpath(log_dir.resolve(), plots_dir.resolve()).replace("\\", "/")

    path = plots_dir / "ParetoRunsExpA_vs_ExpB.plot"
    with path.open("w", encoding="utf-8") as fh:
        fh.write("# 30 pareto front approximations from experiments exp1 vs exp2\n")
        fh.write("# Auto-generated by run_experiments.py\n")
        fh.write("# Change exp1/exp2/run_end/obj columns in gnuplot and use: replot\n\n")
        fh.write(f'data_dir="{rel_log_dir}"\n')
        fh.write(f"exp1={exp1}\n")
        fh.write(f"exp2={exp2}\n")
        fh.write("run_start=1\n")
        fh.write(f"run_end={max_run_id}\n")
        fh.write("obj_x_col=4\n")
        fh.write("obj_y_col=5\n\n")
        fh.write("set grid\n")
        fh.write("set xlabel 'Objective column '.obj_x_col\n")
        fh.write("set ylabel 'Objective column '.obj_y_col\n")
        fh.write("set yrange [*:*]\n")
        fh.write("set title 'Experiments '.exp1.' vs '.exp2.': Pareto Front Approximations of runs '.run_start.'..'.run_end\n")
        fh.write("# TIP: set xrange [0:<value>] / set yrange [0:<value>] if needed\n")
        fh.write("plot data_dir.'/'.exp1.'_'.run_start.'.tsv' using obj_x_col:obj_y_col title sprintf('Exp %d',exp1) smooth unique lt 1,\\\n")
        fh.write("     for [i=run_start+1:run_end] data_dir.'/'.exp1.'_'.i.'.tsv' using obj_x_col:obj_y_col smooth unique lt 1 notitle,\\\n")
        fh.write("     data_dir.'/'.exp1.'_'.run_start.'.tsv' using obj_x_col:obj_y_col w p lt 1 notitle,\\\n")
        fh.write("     for [i=run_start+1:run_end] data_dir.'/'.exp1.'_'.i.'.tsv' using obj_x_col:obj_y_col w p lt 1 notitle,\\\n")
        fh.write("     data_dir.'/'.exp2.'_'.run_start.'.tsv' using obj_x_col:obj_y_col title sprintf('Exp %d',exp2) smooth unique lt 2,\\\n")
        fh.write("     for [i=run_start+1:run_end] data_dir.'/'.exp2.'_'.i.'.tsv' using obj_x_col:obj_y_col smooth unique lt 2 notitle,\\\n")
        fh.write("     data_dir.'/'.exp2.'_'.run_start.'.tsv' using obj_x_col:obj_y_col w p lt 2 notitle,\\\n")
        fh.write("     for [i=run_start+1:run_end] data_dir.'/'.exp2.'_'.i.'.tsv' using obj_x_col:obj_y_col w p lt 2 notitle\n")
        fh.write("\n")
        fh.write("pause -1 'Press Enter to continue'\n")

    return path


def main() -> int:
    args = parse_args()

    workdir = Path(args.workdir).resolve()
    exp_dir = (workdir / args.exp_dir).resolve()
    log_dir = (workdir / args.log_dir).resolve()
    results_dir = (workdir / args.results_dir).resolve()
    output_file = (workdir / args.output_file).resolve()

    ensure_exists(workdir, "workdir")
    ensure_exists(exp_dir, "exp_dir")

    log_dir.mkdir(parents=True, exist_ok=True)

    experiment_ids = build_experiment_list(exp_dir, args.total, args.experiments)

    print("==========================================")
    print(f"Experimentos      : {experiment_ids}")
    print(f"Ejecuciones/run   : {args.runs}")
    print(f"Directorio base   : {workdir}")
    print(f"Carpeta configs   : {exp_dir}")
    print(f"Carpeta logs      : {log_dir}")
    print(f"Carpeta resultados: {results_dir}")
    print(f"Salida temporal   : {output_file}")
    print(f"Comando OPT4J     : {' '.join(args.opt4j_cmd)}")
    print("==========================================\n")

    for exp_id in experiment_ids:
        config_file = exp_dir / f"config{exp_id}.xml"
        ensure_exists(config_file, f"config del experimento {exp_id}")

        print("------------------------------------------")
        print(f"Experimento {exp_id}")
        print(f"Configuracion: {config_file}")
        print("------------------------------------------")

        shutil.copy2(config_file, log_dir / f"config-exp{exp_id}.xml")

        for run_id in range(1, args.runs + 1):
            run_log_file = log_dir / f"{exp_id}_{run_id}.tsv"

            if run_log_file.exists() and not args.force_rerun:
                print(f"[Experimento {exp_id} - RUN {run_id}/{args.runs}] Ya existe {run_log_file.name}. Se omite.")
                continue

            if run_log_file.exists() and args.force_rerun:
                print(f"[Experimento {exp_id} - RUN {run_id}/{args.runs}] Ya existe {run_log_file.name}. Se reejecuta (--force-rerun).")
            else:
                print(f"[Experimento {exp_id} - RUN {run_id}/{args.runs}] Ejecutando...")

            if output_file.exists():
                output_file.unlink()

            run_opt4j(args.opt4j_cmd, config_file, workdir)

            if not output_file.is_file():
                raise RuntimeError(
                    f"No se ha generado {output_file}. "
                    "Revisa que el XML exporte la traza solo en la ultima generacion."
                )

            shutil.copy2(output_file, run_log_file)

    exp1_30fronts, exp2_30fronts = select_30fronts_experiments(experiment_ids)
    compare_30fronts_path = write_30fronts_plot(
        results_dir,
        log_dir,
        exp1_30fronts,
        exp2_30fronts,
        args.runs,
    )

    print("\n==========================================")
    print("Todas las ejecuciones han finalizado.")
    print("==========================================")
    print(f"Script gnuplot 30 Fronts Compare: {compare_30fronts_path.resolve()}")

    print("\nProceso completado correctamente.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise