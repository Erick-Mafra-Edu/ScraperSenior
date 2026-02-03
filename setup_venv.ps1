#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Setup Virtual Environment com dependências para OpenAPI Server

.DESCRIPTION
    Este script:
    1. Cria um virtual environment Python
    2. Instala as dependências necessárias
    3. Fornece instruções para usar

.EXAMPLE
    .\setup_venv.ps1

.NOTES
    Requer Python 3.8+ instalado e no PATH
#>

param(
    [switch]$NoPlaywright = $false
)

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host " SETUP - Virtual Environment com Dependências" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "[CHECK] Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro: Python não encontrado no PATH" -ForegroundColor Red
    Write-Host "   Instale Python 3.8+ de https://www.python.org" -ForegroundColor Red
    Write-Host "   Certifique-se de marcar 'Add Python to PATH' durante instalação" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green

# Criar virtual environment
Write-Host ""
Write-Host "[1/4] Criando virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  Virtual environment já existe em: venv\" -ForegroundColor Yellow
    Write-Host "   Usando ambiente existente" -ForegroundColor Yellow
} else {
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao criar virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Virtual environment criado com sucesso" -ForegroundColor Green
}

# Ativar virtual environment
Write-Host ""
Write-Host "[2/4] Ativando virtual environment..." -ForegroundColor Yellow
$activateScript = ".\venv\Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    Write-Host "❌ Erro: Script de ativação não encontrado" -ForegroundColor Red
    exit 1
}
& $activateScript
Write-Host "✓ Virtual environment ativado" -ForegroundColor Green
Write-Host "   (Você verá '(venv)' no prompt)" -ForegroundColor Gray

# Upgrade pip
Write-Host ""
Write-Host "[3/4] Atualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel *>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Pip atualizado" -ForegroundColor Green
} else {
    Write-Host "⚠️  Aviso: Erro ao atualizar pip (continuando...)" -ForegroundColor Yellow
}

# Instalar dependências
Write-Host ""
Write-Host "[4/4] Instalando dependências..." -ForegroundColor Yellow
$requirementsFile = "requirements.txt"
if (Test-Path $requirementsFile) {
    Write-Host "   Instalando de: $requirementsFile" -ForegroundColor Gray
    pip install -r $requirementsFile
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao instalar dependências" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠️  Arquivo $requirementsFile não encontrado" -ForegroundColor Yellow
    Write-Host "   Instalando pacotes essenciais..." -ForegroundColor Gray
    pip install fastapi uvicorn pydantic meilisearch playwright
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao instalar pacotes" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✓ Dependências instaladas com sucesso" -ForegroundColor Green

# Instalar Playwright browsers (opcional)
if (-not $NoPlaywright) {
    Write-Host ""
    Write-Host "[OPCIONAL] Instalando Playwright browsers..." -ForegroundColor Yellow
    python -m playwright install chromium *>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Playwright browsers instalados" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Aviso: Erro ao instalar Playwright browsers (continuando...)" -ForegroundColor Yellow
    }
}

# Mostrar próximos passos
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Green
Write-Host " ✅ SETUP COMPLETO" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. O virtual environment está ATIVADO" -ForegroundColor Green
Write-Host "     (Você verá '(venv)' no prompt)" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Para INICIAR o servidor OpenAPI:" -ForegroundColor Cyan
Write-Host "     python run_openapi_server.py --reload" -ForegroundColor Yellow
Write-Host ""
Write-Host "  3. Acesse a documentação em:" -ForegroundColor Cyan
Write-Host "     http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "  4. Para DESATIVAR o virtual environment:" -ForegroundColor Cyan
Write-Host "     deactivate" -ForegroundColor Yellow
Write-Host ""
Write-Host "  5. Para REATIVAR depois:" -ForegroundColor Cyan
Write-Host "     .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Green
Write-Host ""

Write-Host "💡 DICA: Você pode iniciar o servidor agora com:" -ForegroundColor Cyan
Write-Host "         python run_openapi_server.py --reload" -ForegroundColor Yellow
Write-Host ""
