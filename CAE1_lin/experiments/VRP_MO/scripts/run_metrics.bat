@echo off
REM Cambiar al directorio del proyecto (directorio padre de scripts)
cd /d "%~dp0.."

set "PYTHON_CMD=python"
set "SCRIPT=src\run_metrics.py"
set "LOG_DIR=data\logs"
set "POINTS_FILE=config\reference-points\points.txt"
set "NOBJ=2"
set "OUT_DIR=data\results"

echo.
echo ==========================================
echo  Calculando metricas (HV y Epsilon)
echo ==========================================
echo.

%PYTHON_CMD% %SCRIPT% ^
  --log-dir %LOG_DIR% ^
  --points %POINTS_FILE% ^
  --nobj %NOBJ% ^
  --out-dir %OUT_DIR%

pause
