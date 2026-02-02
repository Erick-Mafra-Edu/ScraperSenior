@echo off
REM Build script para Docker multi-worker (Windows)

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ════════════════════════════════════════════════════════════════
echo Building Multi-Worker Docker Images
echo ════════════════════════════════════════════════════════════════

REM Build main image
echo 📦 Building senior-docs-scraper:latest...
docker build -t senior-docs-scraper:latest -f Dockerfile "%SCRIPT_DIR%..\.."

REM Build worker-specific image
echo 📦 Building senior-docs-scraper:worker...
docker build -t senior-docs-scraper:worker -f Dockerfile.worker "%SCRIPT_DIR%..\.."

REM Build MCP Server image
echo 📦 Building senior-docs-mcp:latest...
docker build -t senior-docs-mcp:latest -f Dockerfile.mcp "%SCRIPT_DIR%..\.."

echo.
echo ════════════════════════════════════════════════════════════════
echo ✅ Build completo!
echo ════════════════════════════════════════════════════════════════
echo.
echo Imagens disponíveis:
echo   • senior-docs-scraper:latest (LEGACY/ORCHESTRATOR/WORKER)
echo   • senior-docs-scraper:worker (Worker otimizado)
echo   • senior-docs-mcp:latest (MCP Server)
echo.
echo Próximos passos:
echo   cd infra\docker
echo   docker-compose -f docker-compose.workers.yml up -d
echo.

pause
