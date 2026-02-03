@echo off
REM ============================================================================
REM Setup Virtual Environment and Install Dependencies
REM ============================================================================
REM
REM Este script:
REM 1. Cria um virtual environment Python
REM 2. Instala as dependências necessárias
REM 3. Fornece instruções para ativar e usar
REM
REM Uso:
REM     setup_venv.bat
REM
REM ============================================================================

echo.
echo ============================================================================
echo  SETUP - Virtual Environment com Dependências
echo ============================================================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Erro: Python não encontrado no PATH
    echo    Instale Python 3.8+ de https://www.python.org
    echo    Certifique-se de marcar "Add Python to PATH" durante instalação
    pause
    exit /b 1
)

echo ✓ Python encontrado
python --version

REM Criar virtual environment
echo.
echo [1/4] Criando virtual environment...
if exist venv (
    echo ⚠️  Virtual environment já existe em: venv\
    echo    Usando ambiente existente
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Erro ao criar virtual environment
        pause
        exit /b 1
    )
    echo ✓ Virtual environment criado com sucesso
)

REM Ativar virtual environment
echo.
echo [2/4] Ativando virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Erro ao ativar virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment ativado

REM Upgrade pip
echo.
echo [3/4] Atualizando pip...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Aviso: Erro ao atualizar pip (continuando...)
) else (
    echo ✓ Pip atualizado
)

REM Instalar dependências
echo.
echo [4/4] Instalando dependências...
set requirements_file=requirements.txt
if exist %requirements_file% (
    echo    Instalando de: %requirements_file%
    pip install -r %requirements_file%
    if errorlevel 1 (
        echo ❌ Erro ao instalar dependências de %requirements_file%
        pause
        exit /b 1
    )
) else (
    echo ⚠️  Arquivo %requirements_file% não encontrado
    echo    Instalando pacotes essenciais...
    pip install fastapi uvicorn pydantic meilisearch playwright
    if errorlevel 1 (
        echo ❌ Erro ao instalar pacotes
        pause
        exit /b 1
    )
)
echo ✓ Dependências instaladas com sucesso

REM Instalar Playwright browsers (opcional)
echo.
echo [OPCIONAL] Instalando Playwright browsers...
python -m playwright install chromium >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Aviso: Erro ao instalar Playwright browsers (continuando...)
) else (
    echo ✓ Playwright browsers instalados
)

REM Mostrar próximos passos
echo.
echo ============================================================================
echo  ✅ SETUP COMPLETO
echo ============================================================================
echo.
echo 📋 PRÓXIMOS PASSOS:
echo.
echo   1. O virtual environment está ATIVADO
echo      (Você verá "(venv)" no prompt)
echo.
echo   2. Para INICIAR o servidor OpenAPI:
echo      python run_openapi_server.py --reload
echo.
echo   3. Acesse a documentação em:
echo      http://localhost:8000/docs
echo.
echo   4. Para DESATIVAR o virtual environment:
echo      deactivate
echo.
echo   5. Para REATIVAR depois:
echo      venv\Scripts\activate.bat
echo.
echo ============================================================================
echo.

REM Manter o prompt aberto
pause
