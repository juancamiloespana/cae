#!/usr/bin/env sh
# Cambiar al directorio del proyecto (directorio padre de scripts)
cd "dirname $0/.."

PYTHON_CMD="python3"
SCRIPT="src/run_experiments.py"
OPT4J_CMD="../../opt4j/bin/opt4j"
EXP_DIR="config/experiments"
LOG_DIR="data/logs"
RESULTS_DIR="data/results"
RUNS="30"
TOTAL="5"

echo ""
echo "=========================================="
echo "  Lanzando experimentos de optimizacion"
echo "=========================================="
echo ""

$PYTHON_CMD $SCRIPT \
  --opt4j-cmd "$OPT4J_CMD" \
  --exp-dir "$EXP_DIR" \
  --log-dir "$LOG_DIR" \
  --results-dir "$RESULTS_DIR" \
  --runs $RUNS \
  --total $TOTAL

# Variantes comentadas:
# $PYTHON_CMD $SCRIPT --opt4j-cmd "$OPT4J_CMD" --results-dir "$RESULTS_DIR" --runs $RUNS --total $TOTAL --force-rerun
# $PYTHON_CMD $SCRIPT --opt4j-cmd "$OPT4J_CMD" --results-dir "$RESULTS_DIR" --runs 3 --experiments 3,5 --force-rerun
