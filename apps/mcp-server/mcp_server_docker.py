#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAPI Server - Senior Documentation Search (Docker)
======================================================

Servidor FastAPI com OpenAPI specification para busca em documentação Senior.
Substitui o servidor MCP HTTP customizado pelo openapi_adapter que fornece:
- OpenAPI 3.1.0 specification
- Swagger UI em /docs
- ReDoc em /redoc
- Endpoints REST padrão
- FastAPI auto-documentation

Para VS Code / MCP: Use mcp_server.py (stdio mode) ou mcp_entrypoint_dual.py
"""

import sys
import os
from pathlib import Path
import asyncio
import logging

# Forçar UTF-8 para evitar problemas de encoding no Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Setup paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Importar OpenAPI adapter
try:
    from apps.mcp_server.openapi_adapter import create_app
except ImportError:
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from openapi_adapter import create_app
    except ImportError as e:
        logger.error(f"Erro ao importar openapi_adapter: {e}")
        sys.exit(1)

import uvicorn

async def main():
    """Iniciar servidor FastAPI com OpenAPI adapter"""
    
    logger.info("=" * 70)
    logger.info("🚀 INICIANDO SERVIDOR OPENAPI (Docker Mode)")
    logger.info("=" * 70)
    
    # Configurações
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    meilisearch_url = os.getenv("MEILISEARCH_URL", "http://localhost:7700")
    meilisearch_key = os.getenv("MEILISEARCH_KEY", "5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa")
    
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Log Level: {log_level}")
    logger.info(f"Meilisearch: {meilisearch_url}")
    logger.info("=" * 70)
    
    # Criar aplicação FastAPI
    app = create_app(
        meilisearch_url=meilisearch_url,
        api_key=meilisearch_key
    )
    
    # Configurar e iniciar servidor Uvicorn
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level=log_level,
        access_log=True,
        reload=False
    )
    
    server = uvicorn.Server(config)
    
    logger.info("")
    logger.info("📚 ENDPOINTS DISPONÍVEIS:")
    logger.info(f"  • GET  http://{host}:{port}/")
    logger.info(f"  • GET  http://{host}:{port}/health")
    logger.info(f"  • POST http://{host}:{port}/search")
    logger.info(f"  • GET  http://{host}:{port}/modules")
    logger.info(f"  • GET  http://{host}:{port}/stats")
    logger.info("")
    logger.info("📖 DOCUMENTAÇÃO:")
    logger.info(f"  • Swagger:  http://{host}:{port}/docs")
    logger.info(f"  • ReDoc:    http://{host}:{port}/redoc")
    logger.info("")
    logger.info("📋 SCHEMA OPENAPI:")
    logger.info(f"  • Auto-gerado:   http://{host}:{port}/openapi.json")
    logger.info(f"  • Do arquivo:    http://{host}:{port}/api/openapi.json")
    logger.info("")
    logger.info("=" * 70)
    logger.info("")
    
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("")
        logger.info("⏹️  Servidor parado pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}", exc_info=True)
        sys.exit(1)
