# MCP Server - Automated Test Suite
# Simple version for PowerShell

param(
    [string]$Url = "http://localhost:8000/"
)

$totalTests = 0
$passedTests = 0
$failedTests = 0

Write-Host "================================================================================`n" -ForegroundColor Cyan
Write-Host "MCP SERVER TEST SUITE" -ForegroundColor Cyan
Write-Host "================================================================================`n" -ForegroundColor Cyan

# TEST 1: Initialize
Write-Host "[TEST 1] Initialize" -ForegroundColor Yellow
$totalTests++
try {
    $body = @{
        jsonrpc = "2.0"
        id = 1
        method = "initialize"
        params = @{ protocolVersion = "2024-11-05" }
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri $Url -Method Post -ContentType "application/json" -Body $body -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    
    if ($result.result.serverInfo.name -eq "Senior Documentation MCP") {
        Write-Host "[+] PASS - Initialize successful`n" -ForegroundColor Green
        $passedTests++
    } else {
        Write-Host "[!] FAIL - Invalid serverInfo`n" -ForegroundColor Red
        $failedTests++
    }
} catch {
    Write-Host "[!] FAIL - $($_.Exception.Message)`n" -ForegroundColor Red
    $failedTests++
}

# TEST 2: Tools List
Write-Host "[TEST 2] Tools List" -ForegroundColor Yellow
$totalTests++
try {
    $body = @{
        jsonrpc = "2.0"
        id = 2
        method = "tools/list"
        params = @{}
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri $Url -Method Post -ContentType "application/json" -Body $body -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    
    if ($result.result.tools.Count -ge 4) {
        Write-Host "[+] PASS - Found $(($result.result.tools | Measure-Object).Count) tools`n" -ForegroundColor Green
        $passedTests++
    } else {
        Write-Host "[!] FAIL - Expected 4+ tools, found $($result.result.tools.Count)`n" -ForegroundColor Red
        $failedTests++
    }
} catch {
    Write-Host "[!] FAIL - $($_.Exception.Message)`n" -ForegroundColor Red
    $failedTests++
}

# TEST 3: Search BPM
Write-Host "[TEST 3] Search Docs - BPM" -ForegroundColor Yellow
$totalTests++
try {
    $body = @{
        jsonrpc = "2.0"
        id = 3
        method = "tools/call"
        params = @{
            name = "search_docs"
            arguments = @{ query = "BPM"; limit = 5 }
        }
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri $Url -Method Post -ContentType "application/json" -Body $body -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    $data = $result.result.content[0].text | ConvertFrom-Json
    
    if ($data.count -gt 0) {
        Write-Host "[+] PASS - Found $($data.count) BPM documents`n" -ForegroundColor Green
        $passedTests++
    } else {
        Write-Host "[!] FAIL - No results for BPM`n" -ForegroundColor Red
        $failedTests++
    }
} catch {
    Write-Host "[!] FAIL - $($_.Exception.Message)`n" -ForegroundColor Red
    $failedTests++
}

# TEST 4: Search folha
Write-Host "[TEST 4] Search Docs - folha" -ForegroundColor Yellow
$totalTests++
try {
    $body = @{
        jsonrpc = "2.0"
        id = 4
        method = "tools/call"
        params = @{
            name = "search_docs"
            arguments = @{ query = "folha"; limit = 3 }
        }
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri $Url -Method Post -ContentType "application/json" -Body $body -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    $data = $result.result.content[0].text | ConvertFrom-Json
    
    if ($data.count -gt 0) {
        Write-Host "[+] PASS - Found $($data.count) documents for folha`n" -ForegroundColor Green
        $passedTests++
    } else {
        Write-Host "[!] FAIL - No results for folha`n" -ForegroundColor Red
        $failedTests++
    }
} catch {
    Write-Host "[!] FAIL - $($_.Exception.Message)`n" -ForegroundColor Red
    $failedTests++
}

# TEST 5: Search Filtered HCM
Write-Host "[TEST 5] Search Docs - folha in HCM" -ForegroundColor Yellow
$totalTests++
try {
    $body = @{
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
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri $Url -Method Post -ContentType "application/json" -Body $body -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    $data = $result.result.content[0].text | ConvertFrom-Json
    
    if ($data.module_filter -eq "GESTAO_DE_PESSOAS_HCM") {
        Write-Host "[+] PASS - Module filter applied correctly`n" -ForegroundColor Green
        $passedTests++
    } else {
        Write-Host "[!] FAIL - Module filter not applied`n" -ForegroundColor Red
        $failedTests++
    }
} catch {
    Write-Host "[!] FAIL - $($_.Exception.Message)`n" -ForegroundColor Red
    $failedTests++
}

# TEST 6: List Modules
Write-Host "[TEST 6] List Modules" -ForegroundColor Yellow
$totalTests++
try {
    $body = @{
        jsonrpc = "2.0"
        id = 6
        method = "tools/call"
        params = @{
            name = "list_modules"
            arguments = @{}
        }
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri $Url -Method Post -ContentType "application/json" -Body $body -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    $data = $result.result.content[0].text | ConvertFrom-Json
    
    if ($data.total_modules -eq 17) {
        Write-Host "[+] PASS - Found 17 modules`n" -ForegroundColor Green
        $passedTests++
    } else {
        Write-Host "[!] FAIL - Expected 17 modules, found $($data.total_modules)`n" -ForegroundColor Red
        $failedTests++
    }
} catch {
    Write-Host "[!] FAIL - $($_.Exception.Message)`n" -ForegroundColor Red
    $failedTests++
}

# TEST 7: Get Module Docs
Write-Host "[TEST 7] Get Module Docs - BPM" -ForegroundColor Yellow
$totalTests++
try {
    $body = @{
        jsonrpc = "2.0"
        id = 7
        method = "tools/call"
        params = @{
            name = "get_module_docs"
            arguments = @{ module = "BPM"; limit = 2 }
        }
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri $Url -Method Post -ContentType "application/json" -Body $body -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    $data = $result.result.content[0].text | ConvertFrom-Json
    
    if ($data.module -eq "BPM" -and $data.count -gt 0) {
        Write-Host "[+] PASS - BPM docs found ($($data.count) docs)`n" -ForegroundColor Green
        $passedTests++
    } else {
        Write-Host "[!] FAIL - No BPM docs found`n" -ForegroundColor Red
        $failedTests++
    }
} catch {
    Write-Host "[!] FAIL - $($_.Exception.Message)`n" -ForegroundColor Red
    $failedTests++
}

# TEST 8: Get Stats
Write-Host "[TEST 8] Get Stats" -ForegroundColor Yellow
$totalTests++
try {
    $body = @{
        jsonrpc = "2.0"
        id = 8
        method = "tools/call"
        params = @{
            name = "get_stats"
            arguments = @{}
        }
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri $Url -Method Post -ContentType "application/json" -Body $body -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    $data = $result.result.content[0].text | ConvertFrom-Json
    
    if ($data.total_documents -ge 933 -and $data.modules -eq 17) {
        Write-Host "[+] PASS - Stats: $($data.total_documents) docs, $($data.modules) modules`n" -ForegroundColor Green
        $passedTests++
    } else {
        Write-Host "[!] FAIL - Invalid stats (docs=$($data.total_documents), modules=$($data.modules))`n" -ForegroundColor Red
        $failedTests++
    }
} catch {
    Write-Host "[!] FAIL - $($_.Exception.Message)`n" -ForegroundColor Red
    $failedTests++
}

# TEST 9: Error - Empty Query
Write-Host "[TEST 9] Error Handling - Empty Query" -ForegroundColor Yellow
$totalTests++
try {
    $body = @{
        jsonrpc = "2.0"
        id = 9
        method = "tools/call"
        params = @{
            name = "search_docs"
            arguments = @{ query = "" }
        }
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri $Url -Method Post -ContentType "application/json" -Body $body -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    $data = $result.result.content[0].text | ConvertFrom-Json
    
    if ($null -eq $data.count -or $data.results.Count -eq 0) {
        Write-Host "[+] PASS - Empty query handled (no results)`n" -ForegroundColor Green
        $passedTests++
    } else {
        Write-Host "[!] FAIL - Empty query returned results`n" -ForegroundColor Red
        $failedTests++
    }
} catch {
    Write-Host "[+] PASS - Error returned (acceptable)`n" -ForegroundColor Green
    $passedTests++
}

# TEST 10: Error - Invalid Module
Write-Host "[TEST 10] Error Handling - Invalid Module" -ForegroundColor Yellow
$totalTests++
try {
    $body = @{
        jsonrpc = "2.0"
        id = 10
        method = "tools/call"
        params = @{
            name = "get_module_docs"
            arguments = @{ module = "NONEXISTENT" }
        }
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri $Url -Method Post -ContentType "application/json" -Body $body -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    $data = $result.result.content[0].text | ConvertFrom-Json
    
    if ($data.count -eq 0) {
        Write-Host "[+] PASS - Invalid module returns empty`n" -ForegroundColor Green
        $passedTests++
    } else {
        Write-Host "[!] FAIL - Invalid module behavior incorrect`n" -ForegroundColor Red
        $failedTests++
    }
} catch {
    Write-Host "[!] FAIL - $($_.Exception.Message)`n" -ForegroundColor Red
    $failedTests++
}

# Summary
Write-Host "================================================================================`n" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "================================================================================`n" -ForegroundColor Cyan
Write-Host "Total Tests:  $totalTests" -ForegroundColor Yellow
Write-Host "Passed:       $passedTests" -ForegroundColor Green
Write-Host "Failed:       $failedTests" -ForegroundColor Red

$percentage = [math]::Round(($passedTests / $totalTests) * 100, 2)
Write-Host "Success Rate: $percentage%`n" -ForegroundColor $(if ($percentage -eq 100) { "Green" } else { "Yellow" })

if ($failedTests -eq 0) {
    Write-Host ">>> ALL TESTS PASSED <<<`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host ">>> $failedTests TEST(S) FAILED <<<`n" -ForegroundColor Red
    exit 1
}
