#!/bin/bash
# Setup rápido para MCP OpenAPI Server
# Compatível com macOS, Linux e Windows (via WSL)

set -e

echo "================================================"
echo "Setup: MCP OpenAPI Server para Meilisearch"
echo "================================================"
echo ""

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado!"
    echo "   Instalar em: https://nodejs.org/ (v18+)"
    exit 1
fi

echo "✓ Node.js: $(node --version)"
echo "✓ npm: $(npm --version)"
echo ""

# Instalar ferramenta global
echo "📦 Instalando mcp-openapi-server..."
npm install -g @ivotoby/openapi-mcp-server

echo ""
echo "✅ Instalação completa!"
echo ""

# Próximos passos
echo "================================================"
echo "📋 Próximos passos:"
echo "================================================"
echo ""
echo "1️⃣  Iniciar Meilisearch:"
echo "   docker-compose up meilisearch -d"
echo ""
echo "2️⃣  Testar MCP OpenAPI Server (HTTP Mode):"
echo "   npx @ivotoby/openapi-mcp-server \\"
echo "     --api-base-url http://localhost:7700 \\"
echo "     --openapi-spec http://localhost:7700/openapi.json \\"
echo "     --headers 'Authorization:Bearer 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa' \\"
echo "     --transport http \\"
echo "     --port 3000"
echo ""
echo "3️⃣  Testar (em outro terminal):"
echo "   curl http://localhost:3000/health"
echo ""
echo "4️⃣  Configurar Claude Desktop (MCP Mode):"
echo "   - macOS: ~/Library/Application\\ Support/Claude/claude_desktop_config.json"
echo "   - Windows: %APPDATA%\\Claude\\claude_desktop_config.json"
echo ""
echo "   Adicionar:"
echo '   {'
echo '     "mcpServers": {'
echo '       "meilisearch-openapi": {'
echo '         "command": "npx",'
echo '         "args": ["-y", "@ivotoby/openapi-mcp-server"],'
echo '         "env": {'
echo '           "API_BASE_URL": "http://localhost:7700",'
echo '           "OPENAPI_SPEC_PATH": "http://localhost:7700/openapi.json",'
echo '           "API_HEADERS": "Authorization:Bearer 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa"'
echo '         }'
echo '       }'
echo '     }'
echo '   }'
echo ""
echo "5️⃣  Restart Claude Desktop e use a ferramenta!"
echo ""
echo "================================================"
echo "📚 Documentação:"
echo "   docs/guides/DUAL_MCP_OPENAPI_GUIDE.md"
echo "================================================"
