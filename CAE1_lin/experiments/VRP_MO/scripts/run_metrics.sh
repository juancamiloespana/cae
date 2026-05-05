#!/usr/bin/env sh
# Cambiar al directorio del proyecto (directorio padre de scripts)
cd "dirname $0/.."

PYTHON_CMD="python3"
SCRIPT="src/run_metrics.py"
LOG_DIR="data/logs"
POINTS_FILE="config/reference-points/points.txt"
NOBJ="2"
OUT_DIR="data/results"

echo ""
echo "=========================================="
echo "  Calculando metricas (HV y Epsilon)"
echo "=========================================="
echo ""

$PYTHON_CMD $SCRIPT \
  --log-dir "$LOG_DIR" \
  --points "$POINTS_FILE" \
  --nobj $NOBJ \
  --out-dir "$OUT_DIR"

# Variantes comentadas:
# $PYTHON_CMD $SCRIPT --log-dir "$LOG_DIR" --points "$POINTS_FILE" --nobj $NOBJ --out-dir "$OUT_DIR" --epsilon-ref-mode global
# $PYTHON_CMD $SCRIPT --log-dir "$LOG_DIR" --points "$POINTS_FILE" --nobj $NOBJ --out-dir "$OUT_DIR" --experiments 3,5
