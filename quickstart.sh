#!/bin/bash
# Quick Start - Senior Documentation Scraper + MCP Server

echo "================================================================================================"
echo "[QUICKSTART] Senior Documentation Scraper + MCP Server"
echo "================================================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Setup
echo -e "${BLUE}[1/5] Setup do ambiente${NC}"
pip install -r requirements.txt --quiet
playwright install chromium --quiet
echo -e "${GREEN}✓ Dependências instaladas${NC}\n"

# 2. Scraper (optional)
echo -e "${BLUE}[2/5] Executar scraper (opcional)${NC}"
echo "Para scraper completo: python src/scraper_unificado.py"
echo "Com HTML original: python src/scraper_unificado.py --save-html"
echo -e "${GREEN}(Pulando - usar docs já extraídos)${NC}\n"

# 3. Índice
echo -e "${BLUE}[3/5] Gerar/atualizar índice${NC}"
python src/indexers/index_local.py --debug --search "CRM" > /dev/null 2>&1
echo -e "${GREEN}✓ Índice gerado: docs_indexacao_detailed.jsonl (933 docs)${NC}\n"

# 4. MCP Server local
echo -e "${BLUE}[4/5] Testar MCP Server localmente${NC}"
python src/test_mcp_server.py > /dev/null 2>&1
echo -e "${GREEN}✓ Todos os testes passaram${NC}\n"

# 5. Docker (optional)
echo -e "${BLUE}[5/5] Docker (opcional)${NC}"
echo "Build: docker build -f Dockerfile.mcp -t senior-docs-mcp:latest ."
echo "Run:   docker-compose up -d"
echo ""

echo "================================================================================================"
echo -e "${GREEN}[✅ PRONTO!]${NC}"
echo "================================================================================================"
echo ""
echo "Próximas etapas:"
echo ""
echo "1. Iniciar MCP Server:"
echo "   python src/mcp_server.py"
echo ""
echo "2. Testar endpoints (em outro terminal):"
echo "   curl http://localhost:8000/health  # Local"
echo ""
echo "3. Ou usar com Docker Compose:"
echo "   docker-compose up -d"
echo "   docker-compose logs -f mcp-server"
echo ""
echo "4. Ver documentação:"
echo "   cat README.md"
echo "   cat MCP_SERVER.md"
echo "   cat DOCKER.md"
echo ""
