@echo off
REM ============================================================================
REM Start OpenAPI Server with Virtual Environment
REM ============================================================================
REM
REM Este script ativa o venv e inicia o servidor OpenAPI
REM
REM Uso:
REM     start_server.bat
REM     start_server.bat --reload
REM     start_server.bat --port 9000
REM
REM ============================================================================

setlocal enabledelayedexpansion

REM Verificar se venv existe
if not exist venv (
    echo ❌ Erro: Virtual environment não encontrado em venv\
    echo.
    echo Execute primeiro:
    echo   setup_venv.bat
    echo.
    pause
    exit /b 1
)

REM Ativar venv
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Erro ao ativar virtual environment
    pause
    exit /b 1
)

REM Construir argumentos
set "ARGS="
if "%~1"=="" (
    set "ARGS=--log-level info"
) else (
    set "ARGS=%*"
)

REM Mostrar info
echo.
echo ============================================================================
echo  🚀 INICIANDO OPENAPI SERVER
echo ============================================================================
echo.
echo  Virtual environment: ATIVADO
echo  Argumentos: !ARGS!
echo.
echo  Endpoints:
echo  • Swagger:  http://localhost:8000/docs
echo  • ReDoc:    http://localhost:8000/redoc
echo  • API:      http://localhost:8000/
echo.
echo  Pressione CTRL+C para parar
echo ============================================================================
echo.

REM Iniciar servidor
python run_openapi_server.py !ARGS!

REM Tratar saída
if errorlevel 1 (
    echo.
    echo ❌ Servidor encerrado com erro
    pause
    exit /b 1
)

echo.
echo ⏹️  Servidor parado
echo.
