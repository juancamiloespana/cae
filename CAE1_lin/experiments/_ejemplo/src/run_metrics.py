#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import re
import statistics
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


Point = Tuple[float, ...]
RunEntry = Tuple[int, Path]
ExperimentRuns = Dict[int, List[RunEntry]]


LOG_NAME_RE = re.compile(r"^(\d+)_(\d+)\.tsv$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Calcula HV y epsilon a partir de los frentes almacenados en log/<exp>_<run>.tsv. "
            "Asume que Opt4J escribe los objetivos a partir de la columna 4."
        )
    )
    parser.add_argument(
        "--log-dir",
        required=True,
        help="Carpeta con los ficheros <exp>_<run>.tsv",
    )
    parser.add_argument(
        "--points",
        required=True,
        help="Fichero con dos lineas: punto ideal y punto nadir",
    )
    parser.add_argument(
        "--nobj",
        required=True,
        type=int,
        help="Numero de objetivos",
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Carpeta de salida para HV-ExpN.txt, HVBest-ExpN.txt y metrics-summary.csv",
    )
    parser.add_argument(
        "--experiments",
        default=None,
        help="Lista opcional de experimentos separados por comas, por ejemplo: 1,2,4",
    )
    parser.add_argument(
        "--epsilon-ref-mode",
        choices=("experiment", "global"),
        default="experiment",
        help="Referencia para epsilon: frente combinado del experimento o global",
    )
    strict_group = parser.add_mutually_exclusive_group()
    strict_group.add_argument(
        "--strict-box",
        dest="strict_box",
        action="store_true",
        help="Falla si algun punto cae fuera de la caja ideal-nadir (por defecto)",
    )
    strict_group.add_argument(
        "--allow-outside-box",
        dest="strict_box",
        action="store_false",
        help="Descarta puntos fuera de la caja ideal-nadir en lugar de fallar",
    )
    parser.set_defaults(strict_box=True)

    args = parser.parse_args()

    if args.nobj < 2:
        parser.error("--nobj debe ser >= 2")

    if args.experiments is not None:
        args.experiments = parse_experiment_list(args.experiments)

    return args


def parse_experiment_list(text: str) -> set[int]:
    values: set[int] = set()
    for token in text.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            exp_id = int(token)
        except ValueError as exc:
            raise ValueError(f"Identificador de experimento no valido: {token!r}") from exc
        if exp_id <= 0:
            raise ValueError(f"Los identificadores de experimento deben ser positivos: {token!r}")
        values.add(exp_id)
    if not values:
        raise ValueError("La lista de experimentos esta vacia")
    return values


def read_points(points_path: Path, nobj: int) -> Tuple[List[float], List[float]]:
    if not points_path.is_file():
        raise FileNotFoundError(f"No existe el fichero de puntos: {points_path}")

    lines: List[str] = []
    with points_path.open("r", encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            lines.append(line)

    if len(lines) != 2:
        raise ValueError(
            f"{points_path} debe contener exactamente 2 lineas no vacias: ideal y nadir"
        )

    ideal = parse_point_line(lines[0], nobj, "ideal", points_path)
    nadir = parse_point_line(lines[1], nobj, "nadir", points_path)

    for i, (z_ideal, z_nadir) in enumerate(zip(ideal, nadir), start=1):
        if not z_ideal < z_nadir:
            raise ValueError(
                f"En {points_path}, componente {i}: ideal ({z_ideal}) debe ser < nadir ({z_nadir})"
            )

    return ideal, nadir


def parse_point_line(line: str, nobj: int, label: str, path: Path) -> List[float]:
    parts = line.split()
    if len(parts) != nobj:
        raise ValueError(
            f"Linea {label} de {path} tiene {len(parts)} valores y deberia tener {nobj}"
        )
    try:
        return [float(x) for x in parts]
    except ValueError as exc:
        raise ValueError(f"No se pudo parsear la linea {label} de {path}: {line!r}") from exc


def discover_logs(log_dir: Path, selected_experiments: set[int] | None = None) -> ExperimentRuns:
    if not log_dir.is_dir():
        raise FileNotFoundError(f"No existe la carpeta de logs: {log_dir}")

    experiments: ExperimentRuns = {}

    for path in log_dir.iterdir():
        if not path.is_file():
            continue

        match = LOG_NAME_RE.match(path.name)
        if not match:
            continue

        exp_id = int(match.group(1))
        run_id = int(match.group(2))

        if selected_experiments is not None and exp_id not in selected_experiments:
            continue

        experiments.setdefault(exp_id, []).append((run_id, path))

    if not experiments:
        raise ValueError(f"No se encontraron ficheros <exp>_<run>.tsv en {log_dir}")

    for exp_id in experiments:
        experiments[exp_id].sort(key=lambda item: item[0])

    if selected_experiments is not None:
        missing = selected_experiments.difference(experiments.keys())
        if missing:
            raise ValueError(
                f"No se encontraron logs para los experimentos: {sorted(missing)}"
            )

    return dict(sorted(experiments.items(), key=lambda item: item[0]))


def read_front_tsv(path: Path, nobj: int) -> List[Point]:
    front: List[Point] = []
    expected_min_columns = 3 + nobj  # columnas 1-3: previas; 4..: objetivos

    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh, delimiter="\t")
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ValueError(f"El fichero {path} esta vacio") from exc

        if len(header) < expected_min_columns:
            raise ValueError(
                f"{path}: la cabecera tiene {len(header)} columnas; se esperaban al menos {expected_min_columns}"
            )

        for row_num, row in enumerate(reader, start=2):
            if not row or all(cell.strip() == "" for cell in row):
                continue

            if len(row) < expected_min_columns:
                raise ValueError(
                    f"{path}: fila {row_num} con {len(row)} columnas; se esperaban al menos {expected_min_columns}"
                )

            raw_values = row[3 : 3 + nobj]
            try:
                point = tuple(float(value.strip()) for value in raw_values)
            except ValueError as exc:
                raise ValueError(
                    f"{path}: no se pudieron convertir a float los objetivos de la fila {row_num}: {raw_values}"
                ) from exc

            front.append(point)

    if not front:
        raise ValueError(f"{path}: no se encontraron puntos validos en el frente")

    return front


def check_points_within_box(
    front: Sequence[Point],
    ideal: Sequence[float],
    nadir: Sequence[float],
    strict: bool = True,
) -> List[Point]:
    valid: List[Point] = []
    outside_messages: List[str] = []

    for idx, point in enumerate(front, start=1):
        ok = True
        for j, (value, z_ideal, z_nadir) in enumerate(zip(point, ideal, nadir), start=1):
            if value < z_ideal or value > z_nadir:
                ok = False
                outside_messages.append(
                    f"punto {idx}, objetivo {j}: valor {value} fuera de [{z_ideal}, {z_nadir}]"
                )
        if ok:
            valid.append(point)

    if outside_messages and strict:
        detail = "\n".join(outside_messages[:10])
        extra = ""
        if len(outside_messages) > 10:
            extra = f"\n... y {len(outside_messages) - 10} incidencias mas"
        raise ValueError(
            "Se encontraron puntos fuera de la caja ideal-nadir:\n" + detail + extra
        )

    return valid


def remove_duplicates(front: Sequence[Point]) -> List[Point]:
    # Conserva el orden de primera aparicion.
    return list(dict.fromkeys(front))


def dominates(a: Point, b: Point) -> bool:
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def nondominated(front: Sequence[Point]) -> List[Point]:
    nd: List[Point] = []
    for i, p in enumerate(front):
        dominated = False
        for j, q in enumerate(front):
            if i == j:
                continue
            if dominates(q, p):
                dominated = True
                break
        if not dominated:
            nd.append(p)
    return nd


def normalize_front(front: Sequence[Point], ideal: Sequence[float], nadir: Sequence[float]) -> List[Point]:
    normalized: List[Point] = []
    for point in front:
        norm_point = tuple(
            (value - z_ideal) / (z_nadir - z_ideal)
            for value, z_ideal, z_nadir in zip(point, ideal, nadir)
        )
        normalized.append(norm_point)
    return normalized


def combine_fronts(fronts: Iterable[Sequence[Point]]) -> List[Point]:
    combined: List[Point] = []
    for front in fronts:
        combined.extend(front)
    combined = remove_duplicates(combined)
    combined = nondominated(combined)
    return combined


def hypervolume_2d(front_norm: Sequence[Point]) -> float:
    if not front_norm:
        raise ValueError("No se puede calcular HV de un frente vacio")

    # El frente debe estar no dominado y en [0,1]^2.
    points = sorted(front_norm, key=lambda p: (p[0], p[1]))

    hv = 0.0
    current_y = 1.0

    for point in points:
        x, y = point
        if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
            raise ValueError(f"Punto normalizado fuera de [0,1]^2: {point}")

        incremental_height = current_y - y
        if incremental_height > 0.0:
            hv += (1.0 - x) * incremental_height
            current_y = y

    # Proteccion numerica.
    if hv < 0.0 and math.isclose(hv, 0.0, abs_tol=1e-15):
        hv = 0.0
    if hv > 1.0 and math.isclose(hv, 1.0, abs_tol=1e-15):
        hv = 1.0

    return hv


def epsilon_additive(front_norm: Sequence[Point], ref_norm: Sequence[Point]) -> float:
    if not front_norm:
        raise ValueError("No se puede calcular epsilon de un frente vacio")
    if not ref_norm:
        raise ValueError("No se puede calcular epsilon respecto a una referencia vacia")

    eps = -math.inf

    for r in ref_norm:
        best_for_r = math.inf
        for a in front_norm:
            worst_diff = max(ai - ri for ai, ri in zip(a, r))
            if worst_diff < best_for_r:
                best_for_r = worst_diff
        if best_for_r > eps:
            eps = best_for_r

    return eps


def fmt_float(x: float) -> str:
    return f"{x:.16g}"


def write_hv_exp(out_dir: Path, exp_id: int, rows: Sequence[Tuple[int, float, float]]) -> Path:
    path = out_dir / f"HV-Exp{exp_id}.txt"
    with path.open("w", encoding="utf-8") as fh:
        for _, hv, eps in sorted(rows, key=lambda item: item[0]):
            fh.write(f"{fmt_float(hv)} {fmt_float(eps)}\n")
    return path


def write_hvbest_exp(out_dir: Path, exp_id: int, hv_combined: float) -> Path:
    path = out_dir / f"HVBest-Exp{exp_id}.txt"
    with path.open("w", encoding="utf-8") as fh:
        fh.write(f"{fmt_float(hv_combined)}\n")
    return path


def write_front(path: Path, front: Sequence[Point]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for point in sorted(front):
            fh.write(" ".join(fmt_float(value) for value in point) + "\n")


def write_summary_csv(
    out_dir: Path,
    experiment_rows: Sequence[Tuple[int, int, float, float, float, float, float, float, float]],
) -> Path:
    path = out_dir / "metrics-summary.csv"
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "experiment",
                "runs",
                "hv_mean",
                "hv_std",
                "hv_median",
                "eps_mean",
                "eps_std",
                "eps_median",
                "hv_combined",
            ]
        )
        for row in experiment_rows:
            exp_id, runs, hv_mean, hv_std, hv_median, eps_mean, eps_std, eps_median, hv_combined = row
            writer.writerow(
                [
                    exp_id,
                    runs,
                    fmt_float(hv_mean),
                    fmt_float(hv_std),
                    fmt_float(hv_median),
                    fmt_float(eps_mean),
                    fmt_float(eps_std),
                    fmt_float(eps_median),
                    fmt_float(hv_combined),
                ]
            )
    return path


def mean(values: Sequence[float]) -> float:
    return statistics.fmean(values)


def stdev_or_zero(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    return statistics.stdev(values)


def median(values: Sequence[float]) -> float:
    return statistics.median(values)


def prepare_front(
    path: Path,
    nobj: int,
    ideal: Sequence[float],
    nadir: Sequence[float],
    strict_box: bool,
) -> List[Point]:
    front = read_front_tsv(path, nobj)
    front = check_points_within_box(front, ideal, nadir, strict_box)
    if not front:
        raise ValueError(f"{path}: todos los puntos quedaron descartados por caer fuera de la caja")
    front = remove_duplicates(front)
    front = nondominated(front)
    if not front:
        raise ValueError(f"{path}: el frente ha quedado vacio tras el filtrado no dominado")
    return front


def write_fronts_plot(out_dir: Path, experiment_ids: Sequence[int], has_global: bool) -> Path:
    plots_dir = out_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    path = plots_dir / "RefFronts.plot"

    with path.open("w", encoding="utf-8") as fh:
        fh.write("set terminal wxt\n")
        fh.write("set title 'Pareto Fronts'\n")
        fh.write("set xlabel 'Objective 1'\n")
        fh.write("set ylabel 'Objective 2'\n")
        fh.write("set yrange [*:*]\n")
        fh.write("set grid\n")
        fh.write("set key top right\n")
        fh.write("\n")

        plot_commands: List[str] = []
        for exp_id in experiment_ids:
            filename = f"../RefFront-Exp{exp_id}.txt"
            plot_commands.append(f"'{filename}' with linespoints title 'Exp {exp_id}'")

        if has_global:
            plot_commands.append("'../RefFront-Global.txt' with linespoints title 'Global'")

        fh.write("plot ")
        fh.write(", ".join(plot_commands))
        fh.write("\n")
        fh.write("\n")
        fh.write("pause -1 'Press Enter to continue'\n")

    return path


def write_boxplot_scripts(out_dir: Path, experiment_ids: Sequence[int]) -> Tuple[Path, Path]:
    plots_dir = out_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    rel_data_dir = ".."
    exps = " ".join(str(exp_id) for exp_id in experiment_ids)
    xtics = ", ".join(f'"Exp{exp_id}" {exp_id}' for exp_id in experiment_ids)

    hv_path = plots_dir / "HVBoxplot.plot"
    with hv_path.open("w", encoding="utf-8") as fh:
        fh.write("#\n")
        fh.write("# Boxplot of hypervolume values by experiment\n")
        fh.write("# Auto-generated by run_metrics.py\n")
        fh.write("#\n\n")
        fh.write(f'exps="{exps}"\n')
        fh.write(f'data_dir="{rel_data_dir}"\n\n')
        fh.write("reset\n")
        fh.write("set grid\n")
        fh.write('set title "Quality and Stability of experiments"\n')
        fh.write('set ylabel "Hypervolume"\n')
        fh.write("set style fill solid 0.5 border -1\n")
        fh.write("set style boxplot outliers pointtype 7\n")
        fh.write("set style data boxplot\n")
        fh.write("set boxwidth 0.5\n")
        fh.write("set pointsize 0.5\n")
        fh.write("unset key\n")
        fh.write("set border 2\n")
        fh.write("set xtics nomirror\n")
        fh.write("set ytics nomirror\n")
        fh.write("set yrange [0:1]\n")
        fh.write("set xrange [0.5:*]\n")
        fh.write(f"set xtics ({xtics}) scale 0.0\n")
        fh.write("plot for [i in exps] data_dir.'/HV-Exp'.i.'.txt' using (i+0):1\n")

    eps_path = plots_dir / "EpsilonBoxplot.plot"
    with eps_path.open("w", encoding="utf-8") as fh:
        fh.write("#\n")
        fh.write("# Boxplot of epsilon values by experiment\n")
        fh.write("# Auto-generated by run_metrics.py\n")
        fh.write("#\n\n")
        fh.write(f'exps="{exps}"\n')
        fh.write(f'data_dir="{rel_data_dir}"\n\n')
        fh.write("reset\n")
        fh.write("set grid\n")
        fh.write('set title "Quality and Robustness of experiments"\n')
        fh.write('set ylabel "Epsilon"\n')
        fh.write("set style fill solid 0.5 border -1\n")
        fh.write("set style boxplot outliers pointtype 7\n")
        fh.write("set style data boxplot\n")
        fh.write("set boxwidth 0.5\n")
        fh.write("set pointsize 0.5\n")
        fh.write("unset key\n")
        fh.write("set border 2\n")
        fh.write("set xtics nomirror\n")
        fh.write("set ytics nomirror\n")
        fh.write("set yrange [0:1]\n")
        fh.write(f"set xtics ({xtics}) scale 0.0\n")
        fh.write("plot for [i in exps] data_dir.'/HV-Exp'.i.'.txt' using (i+0):2\n")

    return hv_path, eps_path


def main() -> int:
    args = parse_args()

    if args.nobj != 2:
        raise NotImplementedError(
            "Esta primera version implementa HV exacto solo para nObj=2. "
            "El parseo y epsilon soportan mas objetivos, pero el HV todavia no."
        )

    log_dir = Path(args.log_dir)
    points_path = Path(args.points)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ideal, nadir = read_points(points_path, args.nobj)
    experiments = discover_logs(log_dir, args.experiments)
    clean_fronts: Dict[int, List[Tuple[int, List[Point]]]] = {}

    for exp_id, runs in experiments.items():
        clean_fronts[exp_id] = []
        for run_id, path in runs:
            front = prepare_front(path, args.nobj, ideal, nadir, args.strict_box)
            clean_fronts[exp_id].append((run_id, front))

    global_ref_norm: List[Point] | None = None
    global_ref_raw: List[Point] | None = None

    if args.epsilon_ref_mode == "global":
        global_ref_raw = combine_fronts(
            front for runs in clean_fronts.values() for _, front in runs
        )
        if not global_ref_raw:
            raise ValueError("El frente global combinado ha quedado vacio")
        global_ref_norm = normalize_front(global_ref_raw, ideal, nadir)
        write_front(out_dir / "RefFront-Global.txt", global_ref_raw)

    summary_rows: List[Tuple[int, int, float, float, float, float, float, float, float]] = []

    for exp_id, runs in clean_fronts.items():
        exp_combined_raw = combine_fronts(front for _, front in runs)
        if not exp_combined_raw:
            raise ValueError(f"El frente combinado del experimento {exp_id} ha quedado vacio")

        exp_combined_norm = normalize_front(exp_combined_raw, ideal, nadir)

        write_front(out_dir / f"RefFront-Exp{exp_id}.txt", exp_combined_raw)

        if args.epsilon_ref_mode == "experiment":
            ref_norm = exp_combined_norm
        else:
            ref_norm = global_ref_norm
            assert ref_norm is not None

        run_metrics: List[Tuple[int, float, float]] = []

        for run_id, front_raw in runs:
            front_norm = normalize_front(front_raw, ideal, nadir)
            hv = hypervolume_2d(front_norm)
            eps = epsilon_additive(front_norm, ref_norm)
            run_metrics.append((run_id, hv, eps))

        hv_combined = hypervolume_2d(exp_combined_norm)

        write_hv_exp(out_dir, exp_id, run_metrics)
        write_hvbest_exp(out_dir, exp_id, hv_combined)

        hv_values = [hv for _, hv, _ in run_metrics]
        eps_values = [eps for _, _, eps in run_metrics]

        summary_rows.append(
            (
                exp_id,
                len(run_metrics),
                mean(hv_values),
                stdev_or_zero(hv_values),
                median(hv_values),
                mean(eps_values),
                stdev_or_zero(eps_values),
                median(eps_values),
                hv_combined,
            )
        )

    write_summary_csv(out_dir, summary_rows)

    hv_boxplot_path, eps_boxplot_path = write_boxplot_scripts(out_dir, list(clean_fronts.keys()))
    fronts_plot_path = write_fronts_plot(out_dir, list(clean_fronts.keys()), args.epsilon_ref_mode == "global")

    print("Calculo completado.")
    print(f"Experimentos procesados: {', '.join(str(exp_id) for exp_id in clean_fronts.keys())}")
    print(f"Salidas escritas en: {out_dir.resolve()}")
    print(f"Script gnuplot HV Boxplot: {hv_boxplot_path.resolve()}")
    print(f"Script gnuplot Epsilon Boxplot: {eps_boxplot_path.resolve()}")
    print(f"Script gnuplot Reference Fronts: {fronts_plot_path.resolve()}")
    print("Script gnuplot Index (fijo): scripts/IndexPlots.plot")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise   