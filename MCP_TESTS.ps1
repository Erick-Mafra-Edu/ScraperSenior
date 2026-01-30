#!/usr/bin/env pwsh
# MCP Server - Automated Test Suite
# Executa todos os 10 testes e valida as respostas
# Uso: .\MCP_TESTS.ps1

param(
    [string]$Url = "http://localhost:8000/",
    [int]$TimeoutSeconds = 30
)

# Configuração
$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

# Cores
$Green = 'Green'
$Red = 'Red'
$Yellow = 'Yellow'
$Cyan = 'Cyan'

# Contadores
$totalTests = 0
$passedTests = 0
$failedTests = 0

function Write-TestHeader {
    param([int]$Number, [string]$Name)
    Write-Host "`n" + ("=" * 80) -ForegroundColor $Cyan
    Write-Host "TEST #$Number`: $Name" -ForegroundColor $Cyan
    Write-Host ("=" * 80) -ForegroundColor $Cyan
}

function Write-Result {
    param([bool]$Passed, [string]$Message)
    $status = if ($Passed) { "PASS" } else { "FAIL" }
    $symbol = if ($Passed) { "[+]" } else { "[!]" }
    $color = if ($Passed) { $Green } else { $Red }
    Write-Host "$symbol $status - $Message" -ForegroundColor $color
}

function Test-MCP {
    param(
        [int]$TestNumber,
        [string]$TestName,
        [hashtable]$RequestBody,
        [scriptblock]$Validation
    )
    
    $script:totalTests++
    Write-TestHeader -Number $TestNumber -Name $TestName
    
    try {
        # Executar requisição
        $body = $RequestBody | ConvertTo-Json
        Write-Host "Enviando requisição..." -ForegroundColor $Yellow
        
        $response = Invoke-WebRequest -Uri $Url `
            -Method Post `
            -ContentType "application/json" `
            -Body $body `
            -UseBasicParsing `
            -TimeoutSec $TimeoutSeconds
        
        if ($response.StatusCode -ne 200) {
            Write-Result $false "HTTP Status: $($response.StatusCode)"
            $script:failedTests++
            return
        }
        
        Write-Result $true "HTTP Status: 200"
        
        # Parse response
        $result = $response.Content | ConvertFrom-Json
        
        # Executar validações
        $validationResult = & $Validation -Result $result
        
        if ($validationResult.Success) {
            $script:passedTests++
            Write-Result $true $validationResult.Message
            Write-Host "Validações: $($validationResult.Details)" -ForegroundColor $Green
        } else {
            $script:failedTests++
            Write-Result $false $validationResult.Message
            Write-Host "Detalhes: $($validationResult.Details)" -ForegroundColor $Red
        }
        
    } catch {
        $script:failedTests++
        Write-Result $false "Exceção: $($_.Exception.Message)"
    }
}

# ============================================================================
# TESTE 1: Initialize
# ============================================================================
Test-MCP -TestNumber 1 -TestName "Initialize - Handshake Protocolo MCP" `
    -RequestBody @{
        jsonrpc = "2.0"
        id = 1
        method = "initialize"
        params = @{ protocolVersion = "2024-11-05" }
    } `
    -Validation {
        param($Result)
        
        $checks = @()
        $passed = $true
        
        # Validações
        if ($Result.jsonrpc -ne "2.0") { $checks += "jsonrpc != 2.0"; $passed = $false }
        if ($Result.id -ne 1) { $checks += "id != 1"; $passed = $false }
        if (-not $Result.result.serverInfo) { $checks += "serverInfo ausente"; $passed = $false }
        if ($Result.result.serverInfo.name -ne "Senior Documentation MCP") { $checks += "serverInfo.name incorreto"; $passed = $false }
        if (-not $Result.result.capabilities) { $checks += "capabilities ausente"; $passed = $false }
        
        if ($passed) {
            @{ Success = $true; Message = "Initialize respondeu corretamente"; Details = "serverInfo.name='Senior Documentation MCP'" }
        } else {
            @{ Success = $false; Message = "Initialize falhou"; Details = ($checks -join ", ") }
        }
    }

# ============================================================================
# TESTE 2: Tools List
# ============================================================================
Test-MCP -TestNumber 2 -TestName "Tools List - Listar Ferramentas" `
    -RequestBody @{
        jsonrpc = "2.0"
        id = 2
        method = "tools/list"
        params = @{}
    } `
    -Validation {
        param($Result)
        
        $checks = @()
        $passed = $true
        
        $tools = $Result.result.tools
        if ($tools.Count -lt 4) { $checks += "menos de 4 ferramentas"; $passed = $false }
        
        $searchDocs = $tools | Where-Object { $_.name -eq "search_docs" }
        if (-not $searchDocs) { $checks += "search_docs não encontrada"; $passed = $false }
        if ($searchDocs -and -not ($searchDocs.inputSchema.required -contains "query")) { $checks += "search_docs sem required:query"; $passed = $false }
        
        $listModules = $tools | Where-Object { $_.name -eq "list_modules" }
        if (-not $listModules) { $checks += "list_modules não encontrada"; $passed = $false }
        
        $getModuleDocs = $tools | Where-Object { $_.name -eq "get_module_docs" }
        if (-not $getModuleDocs) { $checks += "get_module_docs não encontrada"; $passed = $false }
        if ($getModuleDocs -and -not ($getModuleDocs.inputSchema.required -contains "module")) { $checks += "get_module_docs sem required:module"; $passed = $false }
        
        if ($passed) {
            @{ Success = $true; Message = "4 ferramentas com inputSchema válido"; Details = "search_docs, list_modules, get_module_docs, get_stats" }
        } else {
            @{ Success = $false; Message = "Tools/list incompleto"; Details = ($checks -join ", ") }
        }
    }

# ============================================================================
# TESTE 3: Search Docs - BPM
# ============================================================================
Test-MCP -TestNumber 3 -TestName "Search Docs - Buscar por 'BPM'" `
    -RequestBody @{
        jsonrpc = "2.0"
        id = 3
        method = "tools/call"
        params = @{
            name = "search_docs"
            arguments = @{ query = "BPM"; limit = 5 }
        }
    } `
    -Validation {
        param($Result)
        
        $checks = @()
        $passed = $true
        
        $data = $Result.result.content[0].text | ConvertFrom-Json
        
        if ($data.query -ne "BPM") { $checks += "query != BPM"; $passed = $false }
        if ($data.count -le 0) { $checks += "nenhum resultado"; $passed = $false }
        if (-not $data.results) { $checks += "results ausente"; $passed = $false }
        if ($data.results[0] -and -not $data.results[0].module) { $checks += "resultado sem module"; $passed = $false }
        
        if ($passed) {
            @{ Success = $true; Message = "Search encontrou resultados"; Details = "$($data.count) documentos de BPM" }
        } else {
            @{ Success = $false; Message = "Search falhou"; Details = ($checks -join ", ") }
        }
    }

# ============================================================================
# TESTE 4: Search Docs - Folha
# ============================================================================
Test-MCP -TestNumber 4 -TestName "Search Docs - Buscar por 'folha'" `
    -RequestBody @{
        jsonrpc = "2.0"
        id = 4
        method = "tools/call"
        params = @{
            name = "search_docs"
            arguments = @{ query = "folha"; limit = 3 }
        }
    } `
    -Validation {
        param($Result)
        
        $data = $Result.result.content[0].text | ConvertFrom-Json
        
        if ($data.query -ne "folha") {
            @{ Success = $false; Message = "query incorreta"; Details = "query=$($data.query)" }
        } else {
            @{ Success = $true; Message = "Query 'folha' processada"; Details = "$($data.count) resultados encontrados" }
        }
    }

# ============================================================================
# TESTE 5: Search Docs Filtrado - HCM
# ============================================================================
Test-MCP -TestNumber 5 -TestName "Search Docs - 'folha' em HCM" `
    -RequestBody @{
        jsonrpc = "2.0"
        id = 5
        method = "tools/call"
        params = @{
            name = "search_docs"
            arguments = @{
                query = "folha"
                module = "GESTAO_DE_PESSOAS_HCM"
                limit = 3
            }
        }
    } `
    -Validation {
        param($Result)
        
        $checks = @()
        $passed = $true
        
        $data = $Result.result.content[0].text | ConvertFrom-Json
        
        if ($data.query -ne "folha") { $checks += "query != folha"; $passed = $false }
        if ($data.module_filter -ne "GESTAO_DE_PESSOAS_HCM") { $checks += "module_filter != HCM"; $passed = $false }
        
        if ($data.count -gt 0) {
            foreach ($result in $data.results) {
                if ($result.module -ne "GESTAO_DE_PESSOAS_HCM") {
                    $checks += "resultado com module != HCM"
                    $passed = $false
                    break
                }
            }
        }
        
        if ($passed) {
            @{ Success = $true; Message = "Filtro por módulo funcionou"; Details = "Module: GESTAO_DE_PESSOAS_HCM" }
        } else {
            @{ Success = $false; Message = "Filtro falhou"; Details = ($checks -join ", ") }
        }
    }

# ============================================================================
# TESTE 6: List Modules
# ============================================================================
Test-MCP -TestNumber 6 -TestName "List Modules - 17 Módulos" `
    -RequestBody @{
        jsonrpc = "2.0"
        id = 6
        method = "tools/call"
        params = @{
            name = "list_modules"
            arguments = @{}
        }
    } `
    -Validation {
        param($Result)
        
        $checks = @()
        $passed = $true
        
        $data = $Result.result.content[0].text | ConvertFrom-Json
        
        if ($data.total_modules -ne 17) { $checks += "total_modules != 17"; $passed = $false }
        if ($data.modules.Count -ne 17) { $checks += "array modules != 17"; $passed = $false }
        
        $expectedModules = @("BPM", "GESTAO_DE_PESSOAS_HCM", "GESTAO_DE_RELACIONAMENTO_CRM")
        foreach ($mod in $expectedModules) {
            if ($mod -notin $data.modules) {
                $checks += "módulo ausente: $mod"
                $passed = $false
            }
        }
        
        if ($passed) {
            @{ Success = $true; Message = "17 módulos encontrados"; Details = "BPM, HCM, CRM, ..." }
        } else {
            @{ Success = $false; Message = "Módulos incompleto"; Details = ($checks -join ", ") }
        }
    }

# ============================================================================
# TESTE 7: Get Module Docs
# ============================================================================
Test-MCP -TestNumber 7 -TestName "Get Module Docs - Documentos de BPM" `
    -RequestBody @{
        jsonrpc = "2.0"
        id = 7
        method = "tools/call"
        params = @{
            name = "get_module_docs"
            arguments = @{ module = "BPM"; limit = 2 }
        }
    } `
    -Validation {
        param($Result)
        
        $checks = @()
        $passed = $true
        
        $data = $Result.result.content[0].text | ConvertFrom-Json
        
        if ($data.module -ne "BPM") { $checks += "module != BPM"; $passed = $false }
        if ($data.count -le 0) { $checks += "nenhum documento"; $passed = $false }
        if ($data.results.Count -gt 2) { $checks += "excedeu limit"; $passed = $false }
        
        if ($data.count -gt 0) {
            foreach ($result in $data.results) {
                if ($result.module -ne "BPM") {
                    $checks += "documento com module != BPM"
                    $passed = $false
                    break
                }
            }
        }
        
        if ($passed) {
            @{ Success = $true; Message = "Documentos de BPM retornados"; Details = "$($data.count) documentos" }
        } else {
            @{ Success = $false; Message = "Get Module Docs falhou"; Details = ($checks -join ", ") }
        }
    }

# ============================================================================
# TESTE 8: Get Stats
# ============================================================================
Test-MCP -TestNumber 8 -TestName "Get Stats - Estatísticas" `
    -RequestBody @{
        jsonrpc = "2.0"
        id = 8
        method = "tools/call"
        params = @{
            name = "get_stats"
            arguments = @{}
        }
    } `
    -Validation {
        param($Result)
        
        $checks = @()
        $passed = $true
        
        $data = $Result.result.content[0].text | ConvertFrom-Json
        
        if ($data.total_documents -le 0) { $checks += "total_documents menor ou igual a 0"; $passed = $false }
        if ($data.total_modules -ne 17) { $checks += "total_modules nao igual a 17"; $passed = $false }
        if ($data.total_documents -lt 933) { $checks += "documentos menor que 933"; $passed = $false }
        
        if ($passed) {
            @{ Success = $true; Message = "Estatísticas válidas"; Details = "$($data.total_documents) docs, $($data.total_modules) módulos" }
        } else {
            @{ Success = $false; Message = "Stats inválido"; Details = ($checks -join ", ") }
        }
    }

# ============================================================================
# TESTE 9: Error Handling - Query Vazia
# ============================================================================
Test-MCP -TestNumber 9 -TestName "Error Handling - Query Vazia" `
    -RequestBody @{
        jsonrpc = "2.0"
        id = 9
        method = "tools/call"
        params = @{
            name = "search_docs"
            arguments = @{ query = "" }
        }
    } `
    -Validation {
        param($Result)
        
        if ($Result.error -or $Result.result.count -eq 0) {
            @{ Success = $true; Message = "Erro tratado corretamente"; Details = "Query vazia rejeitada" }
        } else {
            @{ Success = $false; Message = "Query vazia não foi rejeitada"; Details = "$($Result.result.count) resultados" }
        }
    }

# ============================================================================
# TESTE 10: Error Handling - Módulo Inexistente
# ============================================================================
Test-MCP -TestNumber 10 -TestName "Error Handling - Módulo Inexistente" `
    -RequestBody @{
        jsonrpc = "2.0"
        id = 10
        method = "tools/call"
        params = @{
            name = "get_module_docs"
            arguments = @{ module = "MODULO_INEXISTENTE" }
        }
    } `
    -Validation {
        param($Result)
        
        $data = $Result.result.content[0].text | ConvertFrom-Json
        
        if ($data.count -eq 0 -and $data.results.Count -eq 0) {
            @{ Success = $true; Message = "Módulo inexistente retorna vazio"; Details = "count=0, results=[]" }
        } else {
            @{ Success = $false; Message = "Comportamento inesperado"; Details = "count=$($data.count)" }
        }
    }

# ============================================================================
# RESUMO FINAL
# ============================================================================
Write-Host "`n" + ("=" * 80) -ForegroundColor $Cyan
Write-Host "RESUMO DE TESTES" -ForegroundColor $Cyan
Write-Host ("=" * 80) -ForegroundColor $Cyan

Write-Host "Total de Testes: $totalTests" -ForegroundColor $Yellow
Write-Host "Passados: $passedTests" -ForegroundColor $Green
Write-Host "Falhados: $failedTests" -ForegroundColor $Red

$percentage = [math]::Round(($passedTests / $totalTests) * 100, 2)
Write-Host "Taxa de Sucesso: $percentage%" -ForegroundColor $(if ($percentage -eq 100) { $Green } else { $Yellow })

Write-Host "`n" + ("=" * 80) -ForegroundColor $Cyan

if ($failedTests -eq 0) {
    Write-Host "✓ TODOS OS TESTES PASSARAM!" -ForegroundColor $Green
    exit 0
} else {
    Write-Host "✗ $failedTests teste(s) falharam" -ForegroundColor $Red
    exit 1
}
