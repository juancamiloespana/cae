@echo off
REM Cambiar al directorio del proyecto (directorio padre de scripts)
cd /d "%~dp0.."

set "PYTHON_CMD=python"
set "SCRIPT=src\run_experiments.py"
set "OPT4J_CMD=..\..\opt4j\bin\opt4j-JVM1.8.bat"
set "EXP_DIR=config\experiments"
set "LOG_DIR=data\logs"
set "RESULTS_DIR=data\results"
if "%~1"=="" (
    set "RUNS=5"
) else (
    set "RUNS=%~1"
)

echo.
echo ==========================================
echo  Lanzando experimentos de optimizacion
echo ==========================================
echo.

%PYTHON_CMD% %SCRIPT% ^
  --opt4j-cmd %OPT4J_CMD% ^
  --exp-dir %EXP_DIR% ^
  --log-dir %LOG_DIR% ^
  --results-dir %RESULTS_DIR% ^
  --runs %RUNS%

pause
