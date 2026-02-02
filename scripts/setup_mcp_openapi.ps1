# Setup para MCP OpenAPI Server (Windows)
# Requer: Node.js v18+, npm, Docker

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Setup: MCP OpenAPI Server para Meilisearch" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Node.js
Write-Host "Verificando Node.js..." -ForegroundColor Yellow
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js não encontrado!" -ForegroundColor Red
    Write-Host "   Instalar em: https://nodejs.org/ (v18+)" -ForegroundColor Yellow
    exit 1
}

$nodeVersion = & node --version
$npmVersion = & npm --version

Write-Host "✓ Node.js: $nodeVersion" -ForegroundColor Green
Write-Host "✓ npm: $npmVersion" -ForegroundColor Green
Write-Host ""

# Instalar ferramenta global
Write-Host "📦 Instalando mcp-openapi-server..." -ForegroundColor Yellow
npm install -g @ivotoby/openapi-mcp-server

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Instalação completa!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Erro na instalação!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1️⃣  Iniciar Meilisearch:" -ForegroundColor Yellow
Write-Host "   docker-compose up meilisearch -d" -ForegroundColor Gray
Write-Host ""

Write-Host "2️⃣  Testar MCP OpenAPI Server (HTTP Mode):" -ForegroundColor Yellow
Write-Host "   npx @ivotoby/openapi-mcp-server `` " -ForegroundColor Gray
Write-Host "     --api-base-url http://localhost:7700 `` " -ForegroundColor Gray
Write-Host "     --openapi-spec http://localhost:7700/openapi.json `` " -ForegroundColor Gray
Write-Host "     --headers 'Authorization:Bearer 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa' `` " -ForegroundColor Gray
Write-Host "     --transport http `` " -ForegroundColor Gray
Write-Host "     --port 3000" -ForegroundColor Gray
Write-Host ""

Write-Host "3️⃣  Testar (em outro terminal):" -ForegroundColor Yellow
Write-Host "   curl http://localhost:3000/health" -ForegroundColor Gray
Write-Host ""

Write-Host "4️⃣  Configurar Claude Desktop:" -ForegroundColor Yellow
Write-Host "   Arquivo: %APPDATA%\Claude\claude_desktop_config.json" -ForegroundColor Gray
Write-Host ""
Write-Host '   Adicionar:' -ForegroundColor Gray
Write-Host '{' -ForegroundColor Gray
Write-Host '  "mcpServers": {' -ForegroundColor Gray
Write-Host '    "meilisearch-openapi": {' -ForegroundColor Gray
Write-Host '      "command": "npx",' -ForegroundColor Gray
Write-Host '      "args": ["-y", "@ivotoby/openapi-mcp-server"],' -ForegroundColor Gray
Write-Host '      "env": {' -ForegroundColor Gray
Write-Host '        "API_BASE_URL": "http://localhost:7700",' -ForegroundColor Gray
Write-Host '        "OPENAPI_SPEC_PATH": "http://localhost:7700/openapi.json",' -ForegroundColor Gray
Write-Host '        "API_HEADERS": "Authorization:Bearer 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa"' -ForegroundColor Gray
Write-Host '      }' -ForegroundColor Gray
Write-Host '    }' -ForegroundColor Gray
Write-Host '  }' -ForegroundColor Gray
Write-Host '}' -ForegroundColor Gray
Write-Host ""

Write-Host "5️⃣  Restart Claude Desktop e use a ferramenta!" -ForegroundColor Yellow
Write-Host ""

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "📚 Documentação:" -ForegroundColor Cyan
Write-Host "   docs/guides/DUAL_MCP_OPENAPI_GUIDE.md" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
