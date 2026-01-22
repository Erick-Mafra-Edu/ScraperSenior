#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Pipeline CI/CD para Senior Documentation Scraper
    
.DESCRIPTION
    Executa validações, testes e deploy automático
    
.EXAMPLE
    .\ci_pipeline.ps1 -Action RunTests
    .\ci_pipeline.ps1 -Action Full
    .\ci_pipeline.ps1 -Action Docker
#>

param(
    [ValidateSet("RunTests", "Docker", "Full", "ValidateData", "Report")]
    [string]$Action = "Full"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Colors
$GREEN = [System.ConsoleColor]::Green
$RED = [System.ConsoleColor]::Red
$YELLOW = [System.ConsoleColor]::Yellow
$CYAN = [System.ConsoleColor]::Cyan

function Write-Header {
    param([string]$Text)
    Write-Host "`n" + ("="*80) -ForegroundColor $CYAN
    Write-Host $Text -ForegroundColor $CYAN
    Write-Host ("="*80) -ForegroundColor $CYAN
}

function Write-Success {
    param([string]$Text)
    Write-Host "✅ $Text" -ForegroundColor $GREEN
}

function Write-Error {
    param([string]$Text)
    Write-Host "❌ $Text" -ForegroundColor $RED
}

function Write-Warning {
    param([string]$Text)
    Write-Host "⚠️  $Text" -ForegroundColor $YELLOW
}

function Test-DockerServices {
    Write-Header "🐳 Verificando Docker Services"
    
    # Check if docker-compose is installed
    try {
        $version = docker-compose --version
        Write-Success "Docker Compose: $version"
    }
    catch {
        Write-Error "Docker Compose não instalado"
        return $false
    }
    
    # Check if containers are running
    try {
        $running = docker-compose ps --services --filter "status=running"
        $expected = @("senior-docs-meilisearch", "senior-docs-mcp-server")
        
        foreach ($service in $expected) {
            if ($running -contains $service) {
                Write-Success "Serviço $service está rodando"
            } else {
                Write-Warning "Serviço $service não está rodando"
            }
        }
    }
    catch {
        Write-Error "Erro ao verificar serviços: $_"
        return $false
    }
    
    return $true
}

function Start-DockerServices {
    Write-Header "🚀 Iniciando Serviços Docker"
    
    Write-Host "Executando: docker-compose up -d --build"
    docker-compose up -d --build
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Serviços iniciados com sucesso"
        
        # Wait for services to be healthy
        Write-Host "Aguardando serviços ficarem saudáveis..."
        Start-Sleep -Seconds 5
        
        return $true
    } else {
        Write-Error "Erro ao iniciar serviços"
        return $false
    }
}

function Run-Tests {
    Write-Header "🧪 Executando Testes"
    
    $testScript = "run_ci_pipeline.py"
    
    if (-not (Test-Path $testScript)) {
        Write-Error "Script de testes não encontrado: $testScript"
        return $false
    }
    
    Write-Host "Executando: python $testScript"
    python $testScript
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Testes completados com sucesso"
        return $true
    } else {
        Write-Error "Alguns testes falharam (código de saída: $LASTEXITCODE)"
        return $false
    }
}

function Validate-Data {
    Write-Header "📊 Validando Dados"
    
    # Check if JSONL file exists and has content
    $jsonlFile = "docs_indexacao_detailed.jsonl"
    
    if (Test-Path $jsonlFile) {
        $lineCount = (Get-Content $jsonlFile | Measure-Object -Line).Lines
        Write-Success "Arquivo $jsonlFile encontrado com $lineCount linhas"
    } else {
        Write-Error "Arquivo $jsonlFile não encontrado"
        return $false
    }
    
    # Validate JSON structure
    Write-Host "Validando estrutura JSON..."
    python -c @"
import json
with open('$jsonlFile', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        try:
            json.loads(line)
        except:
            print(f'Erro na linha {i}')
            exit(1)
print('✅ Estrutura JSON válida')
"@
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Dados validados com sucesso"
        return $true
    } else {
        Write-Error "Erro ao validar dados"
        return $false
    }
}

function Show-Report {
    Write-Header "📋 Relatório de Testes"
    
    $reportFile = "test_report.json"
    
    if (Test-Path $reportFile) {
        $report = Get-Content $reportFile | ConvertFrom-Json
        
        Write-Host "Timestamp: $($report.timestamp)"
        Write-Host "Testes executados: $($report.summary.total_tests)"
        Write-Host "Passaram: $($report.summary.passed)"
        Write-Host "Falharam: $($report.summary.failed)"
        Write-Host "Taxa de sucesso: $($report.summary.success_rate)"
        Write-Host "Status: $($report.summary.status)"
        
        Write-Host "`nDetalhes dos testes:"
        foreach ($test in $report.tests.PSObject.Properties) {
            $status = if ($test.Value.passed) { "✅" } else { "❌" }
            Write-Host "  $status $($test.Name)"
        }
    } else {
        Write-Warning "Arquivo de relatório não encontrado: $reportFile"
    }
}

function Main {
    Write-Host "`n🎯 CI/CD Pipeline - Senior Documentation Scraper`n" -ForegroundColor $CYAN
    Write-Host "Ação: $Action`n" -ForegroundColor $CYAN
    
    $success = $true
    
    switch ($Action) {
        "Docker" {
            Test-DockerServices
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "Iniciando Docker services..."
                Start-DockerServices
            }
        }
        
        "ValidateData" {
            Validate-Data
            $success = $LASTEXITCODE -eq 0
        }
        
        "RunTests" {
            Run-Tests
            $success = $LASTEXITCODE -eq 0
        }
        
        "Report" {
            Show-Report
        }
        
        "Full" {
            # 1. Docker
            Write-Header "FASE 1: Docker"
            Test-DockerServices
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "Iniciando Docker services..."
                Start-DockerServices
                if ($LASTEXITCODE -ne 0) { $success = $false }
            }
            
            # 2. Validate
            if ($success) {
                Write-Header "FASE 2: Validação"
                Validate-Data
                if ($LASTEXITCODE -ne 0) { $success = $false }
            }
            
            # 3. Tests
            if ($success) {
                Write-Header "FASE 3: Testes"
                Run-Tests
                if ($LASTEXITCODE -ne 0) { $success = $false }
            }
            
            # 4. Report
            Write-Header "FASE 4: Relatório"
            Show-Report
        }
    }
    
    if ($success) {
        Write-Header "✅ PIPELINE COMPLETADO COM SUCESSO"
    } else {
        Write-Header "❌ PIPELINE FALHOU"
        exit 1
    }
}

# Execute main
Main
