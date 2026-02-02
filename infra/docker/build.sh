#!/bin/bash
# Build script para Docker multi-worker

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

echo "════════════════════════════════════════════════════════════════"
echo "Building Multi-Worker Docker Images"
echo "════════════════════════════════════════════════════════════════"

cd "$SCRIPT_DIR"

# Build main image (supports all 3 modes)
echo "📦 Building senior-docs-scraper:latest..."
docker build -t senior-docs-scraper:latest -f Dockerfile "$REPO_ROOT"

# Build worker-specific image (optional, lightweight)
echo "📦 Building senior-docs-scraper:worker..."
docker build -t senior-docs-scraper:worker -f Dockerfile.worker "$REPO_ROOT"

# Build MCP Server image
echo "📦 Building senior-docs-mcp:latest..."
docker build -t senior-docs-mcp:latest -f Dockerfile.mcp "$REPO_ROOT"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Build completo!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Imagens disponíveis:"
echo "  • senior-docs-scraper:latest (LEGACY/ORCHESTRATOR/WORKER)"
echo "  • senior-docs-scraper:worker (Worker otimizado)"
echo "  • senior-docs-mcp:latest (MCP Server)"
echo ""
echo "Próximos passos:"
echo "  cd infra/docker"
echo "  docker-compose -f docker-compose.workers.yml up -d"
echo ""
