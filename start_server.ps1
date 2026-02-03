#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start OpenAPI Server com Virtual Environment

.DESCRIPTION
    Ativa o venv e inicia o servidor OpenAPI

.PARAMETER Reload
    Ativar reload automático em desenvolvimento

.PARAMETER Port
    Porta para o servidor (default: 8000)

.PARAMETER Host
    Host para bind (default: 0.0.0.0)

.PARAMETER LogLevel
    Nível de logging (default: info)

.EXAMPLE
    .\start_server.ps1
    .\start_server.ps1 -Reload
    .\start_server.ps1 -Port 9000 -LogLevel debug

.NOTES
    Requer venv ativado ou script irá ativar
#>

param(
    [switch]$Reload = $false,
    [int]$Port = 8000,
    [string]$Host = "0.0.0.0",
    [string]$LogLevel = "info"
)

$ErrorActionPreference = "Stop"

# Verificar se venv existe
if (-not (Test-Path "venv")) {
    Write-Host "❌ Erro: Virtual environment não encontrado em venv\" -ForegroundColor Red
    Write-Host ""
    Write-Host "Execute primeiro:" -ForegroundColor Yellow
    Write-Host "  .\setup_venv.ps1" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Ativar venv
$activateScript = ".\venv\Scripts\Activate.ps1"
& $activateScript
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao ativar virtual environment" -ForegroundColor Red
    exit 1
}

# Construir argumentos
$args_list = @(
    "run_openapi_server.py"
    "--host", $Host
    "--port", $Port
    "--log-level", $LogLevel
)

if ($Reload) {
    $args_list += "--reload"
}

# Mostrar info
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host " 🚀 INICIANDO OPENAPI SERVER" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " ✓ Virtual environment: ATIVADO" -ForegroundColor Green
Write-Host " • Host: $Host" -ForegroundColor Gray
Write-Host " • Porta: $Port" -ForegroundColor Gray
Write-Host " • Log Level: $LogLevel" -ForegroundColor Gray
if ($Reload) {
    Write-Host " • Reload: HABILITADO" -ForegroundColor Yellow
}
Write-Host ""
Write-Host " 📖 Endpoints:" -ForegroundColor Cyan
Write-Host "   • Swagger:  http://localhost:$Port/docs" -ForegroundColor Yellow
Write-Host "   • ReDoc:    http://localhost:$Port/redoc" -ForegroundColor Yellow
Write-Host "   • API:      http://localhost:$Port/" -ForegroundColor Yellow
Write-Host ""
Write-Host " Pressione CTRL+C para parar" -ForegroundColor Gray
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Iniciar servidor
python @args_list

# Tratar saída
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Servidor encerrou com erro (código: $LASTEXITCODE)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "⏹️  Servidor parado" -ForegroundColor Yellow
Write-Host ""
