#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Start OpenAPI Server with openapi.json hosting
===============================================

Inicia o servidor FastAPI com suporte a OpenAPI specification.
Serve o arquivo openapi.json da raiz do projeto nos endpoints:
- GET /api/openapi.json (arquivo do disco)
- GET /openapi.json (FastAPI auto-gerado)

Uso:
    python run_openapi_server.py [--host 0.0.0.0] [--port 8000]

Endpoints:
    GET  /                    - Info da API
    GET  /health              - Health check
    POST /search              - Buscar documentos
    GET  /modules             - Listar módulos
    GET  /modules/{name}      - Docs de um módulo
    GET  /stats               - Estatísticas
    GET  /docs                - Swagger UI
    GET  /redoc               - ReDoc UI
    GET  /openapi.json        - Schema OpenAPI (auto-gerado)
    GET  /api/openapi.json    - Schema OpenAPI (arquivo disco)
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Adicionar o diretório do projeto ao Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Check and install dependencies
def check_dependencies():
    """Verifica e instala dependências necessárias"""
    required_packages = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'pydantic': 'pydantic',
        'meilisearch': 'meilisearch'
    }
    
    missing_packages = []
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"⚠️  Dependências faltando: {', '.join(missing_packages)}")
        print(f"   Instalando via pip...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                *missing_packages
            ])
            print(f"✓ Dependências instaladas com sucesso!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar dependências: {e}")
            print(f"   Tente manualmente: pip install {' '.join(missing_packages)}")
            sys.exit(1)

check_dependencies()

# Importar o adapter
try:
    from apps.mcp_server.openapi_adapter import create_app
except ImportError as e:
    print(f"⚠️  Tentando fallback para import relativo...")
    # Tentar fallback
    sys.path.insert(0, str(project_root / "apps" / "mcp-server"))
    try:
        from openapi_adapter import create_app
    except ImportError as e2:
        print(f"❌ Falha em ambas tentativas de import")
        print(f"   Erro 1: {e}")
        print(f"   Erro 2: {e2}")
        sys.exit(1)

import uvicorn
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Função principal para iniciar o servidor"""
    
    parser = argparse.ArgumentParser(
        description="Inicia o servidor FastAPI com OpenAPI specification"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("HOST", "0.0.0.0"),
        help="Host para bind do servidor (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", 8000)),
        help="Porta do servidor (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Ativar reload automático em desenvolvimento"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=os.getenv("LOG_LEVEL", "info").lower(),
        choices=["critical", "error", "warning", "info", "debug"],
        help="Nível de logging (default: info)"
    )
    parser.add_argument(
        "--meilisearch-url",
        type=str,
        default=os.getenv("MEILISEARCH_URL", "http://localhost:7700"),
        help="URL do Meilisearch (default: http://localhost:7700)"
    )
    parser.add_argument(
        "--meilisearch-key",
        type=str,
        default=os.getenv("MEILISEARCH_KEY", "meilisearch_master_key"),
        help="API Key do Meilisearch"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("🚀 INICIANDO SERVIDOR OPENAPI COM HOSTAGEM DE openapi.json")
    logger.info("=" * 70)
    logger.info(f"Host: {args.host}")
    logger.info(f"Porta: {args.port}")
    logger.info(f"Reload: {args.reload}")
    logger.info(f"Log Level: {args.log_level}")
    logger.info(f"Meilisearch: {args.meilisearch_url}")
    logger.info("=" * 70)
    
    # Verificar se openapi.json existe
    openapi_file = project_root / "openapi.json"
    if openapi_file.exists():
        logger.info(f"✓ Arquivo openapi.json encontrado: {openapi_file}")
    else:
        logger.warning(f"⚠ Arquivo openapi.json não encontrado em: {openapi_file}")
        logger.warning("  O servidor ainda funcionará, mas /api/openapi.json usará fallback")
    
    # Criar aplicação FastAPI
    app = create_app(
        meilisearch_url=args.meilisearch_url,
        api_key=args.meilisearch_key
    )
    
    # Configurar e iniciar servidor
    config = uvicorn.Config(
        app,
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        access_log=True,
        reload=args.reload
    )
    
    server = uvicorn.Server(config)
    
    logger.info("")
    logger.info("📚 ENDPOINTS DISPONÍVEIS:")
    logger.info(f"  • GET  http://{args.host}:{args.port}/")
    logger.info(f"  • GET  http://{args.host}:{args.port}/health")
    logger.info(f"  • POST http://{args.host}:{args.port}/search")
    logger.info(f"  • GET  http://{args.host}:{args.port}/modules")
    logger.info(f"  • GET  http://{args.host}:{args.port}/stats")
    logger.info("")
    logger.info("📖 DOCUMENTAÇÃO:")
    logger.info(f"  • Swagger:  http://{args.host}:{args.port}/docs")
    logger.info(f"  • ReDoc:    http://{args.host}:{args.port}/redoc")
    logger.info("")
    logger.info("📋 SCHEMA OPENAPI:")
    logger.info(f"  • Auto-gerado:   http://{args.host}:{args.port}/openapi.json")
    logger.info(f"  • Do arquivo:    http://{args.host}:{args.port}/api/openapi.json")
    logger.info("")
    logger.info("Pressione CTRL+C para parar o servidor")
    logger.info("=" * 70)
    logger.info("")
    
    try:
        import asyncio
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        logger.info("")
        logger.info("⏹️  Servidor parado pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
