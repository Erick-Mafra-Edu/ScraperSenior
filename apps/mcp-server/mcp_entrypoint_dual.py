#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entrypoint Dual-Mode para MCP Server
====================================

Permite executar o MCP Server em dois modos:
1. MCP Mode (stdio): Para integração com Claude Desktop/Cursor IDE
2. OpenAPI Mode (HTTP): Para acesso via API REST com documentação Swagger

Uso:
    # Modo OpenAPI (padrão em Docker)
    python mcp_entrypoint_dual.py --mode openapi
    
    # Modo MCP (padrão para IDE)
    python mcp_entrypoint_dual.py --mode mcp
    
    # Ambos os modos simultaneamente (MCP + OpenAPI)
    python mcp_entrypoint_dual.py --mode both
    
    # Detectar automaticamente baseado em environment
    python mcp_entrypoint_dual.py  # --mode auto

Environment Variables:
    MCP_MODE: Modo de execução (auto|mcp|openapi|both)
    MEILISEARCH_URL: URL do Meilisearch (padrão: http://localhost:7700)
    MEILISEARCH_KEY: API key do Meilisearch
    OPENAPI_HOST: Host para OpenAPI (padrão: 0.0.0.0)
    OPENAPI_PORT: Port para OpenAPI (padrão: 8000)
    MCP_STDIO: Usar stdio para MCP (padrão: true em Docker)
"""

import sys
import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Optional
import argparse
import subprocess
import threading
from datetime import datetime

# Adicionar diretório do projeto ao path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# ============================================================================
# Configuração de Logging
# ============================================================================

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================================================
# Detecção de Ambiente
# ============================================================================

def is_docker() -> bool:
    """Verifica se está rodando em Docker"""
    return os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER") == "true"


def is_ide_mode() -> bool:
    """Verifica se está em modo IDE (VS Code, Cursor, etc)"""
    # Se há variáveis de ambiente de IDE, usar MCP
    ide_vars = ["VSCODE_PID", "CURSOR_PID", "PYCHARM_MATPLOTLIB_INTERACTIVE"]
    return any(var in os.environ for var in ide_vars)


def detect_mode() -> str:
    """Detecta o modo apropriado automaticamente"""
    
    if is_docker():
        logger.info("📦 Detectado ambiente Docker - usando modo OpenAPI")
        return "openapi"
    elif is_ide_mode():
        logger.info("💻 Detectado IDE (VS Code/Cursor) - usando modo MCP")
        return "mcp"
    else:
        logger.info("🤷 Modo não detectado - usando OpenAPI como padrão")
        return "openapi"


# ============================================================================
# Modo MCP (stdio)
# ============================================================================

async def run_mcp_mode():
    """
    Executa o servidor MCP usando stdio.
    Adequado para integração com IDEs como VS Code e Cursor.
    """
    logger.info("🔌 Iniciando MCP Server em modo stdio...")
    
    try:
        from apps.mcp_server.mcp_server import main as mcp_main
        
        logger.info("✅ MCP Server iniciado com sucesso")
        logger.info("   Aguardando conexões via stdio...")
        logger.info("   Configure em: ~/.config/claude_desktop_config.json")
        
        await mcp_main()
    
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar MCP Server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# ============================================================================
# Modo OpenAPI (HTTP REST)
# ============================================================================

async def run_openapi_mode():
    """
    Executa o servidor OpenAPI com FastAPI/Uvicorn.
    Adequado para acesso via HTTP REST e documentação Swagger.
    """
    logger.info("🌐 Iniciando OpenAPI Server em modo HTTP...")
    
    try:
        from apps.mcp_server.openapi_adapter import create_app
        import uvicorn
        
        app = create_app(
            meilisearch_url=os.getenv(
                "MEILISEARCH_URL",
                "http://meilisearch:7700"  # Default para Docker
            ),
            api_key=os.getenv("MEILISEARCH_KEY")
        )
        
        host = os.getenv("OPENAPI_HOST", "0.0.0.0")
        port = int(os.getenv("OPENAPI_PORT", 8000))
        
        logger.info(f"✅ OpenAPI Server configurado")
        logger.info(f"   Host: {host}")
        logger.info(f"   Port: {port}")
        logger.info(f"   Documentação: http://localhost:{port}/docs")
        logger.info(f"   ReDoc: http://localhost:{port}/redoc")
        
        config = uvicorn.Config(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar OpenAPI Server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# ============================================================================
# Modo Dual (MCP + OpenAPI simultaneamente)
# ============================================================================

async def run_both_modes():
    """
    Executa tanto MCP quanto OpenAPI simultaneamente em threads separadas.
    
    Útil para:
    - Desenvolvimento local (IDE + teste de API)
    - Docker com suporte a ambas as integrações
    """
    logger.info("🚀 Iniciando modo DUAL (MCP + OpenAPI)...")
    
    # Criar tasks para ambos os modos
    mcp_task = asyncio.create_task(run_mcp_mode())
    openapi_task = asyncio.create_task(run_openapi_mode())
    
    try:
        # Aguardar qualquer um dos servidores encerrar
        done, pending = await asyncio.wait(
            [mcp_task, openapi_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Se um encerrou, cancelar o outro
        for task in pending:
            task.cancel()
        
        logger.info("⏹️  Um dos servidores foi encerrado, encerrando ambos...")
    
    except KeyboardInterrupt:
        logger.info("⏹️  Encerrando ambos os servidores...")
        mcp_task.cancel()
        openapi_task.cancel()


# ============================================================================
# Main
# ============================================================================

async def main():
    """Função principal que inicia o modo apropriado"""
    
    # Parsear argumentos
    parser = argparse.ArgumentParser(
        description="Entrypoint Dual-Mode para MCP Server Senior Documentation"
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "mcp", "openapi", "both"],
        default=os.getenv("MCP_MODE", "auto"),
        help="Modo de execução"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="MCP Server v1.0.0"
    )
    
    args = parser.parse_args()
    
    # Determinar modo
    mode = args.mode
    if mode == "auto":
        mode = detect_mode()
    
    logger.info(f"╔{'='*60}╗")
    logger.info(f"║ MCP Server - Senior Documentation                    ║")
    logger.info(f"║ Mode: {mode.upper():<47} ║")
    logger.info(f"║ Timestamp: {datetime.now().isoformat():<28} ║")
    logger.info(f"╚{'='*60}╝")
    logger.info("")
    
    # Forçar UTF-8 em Windows
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass
    
    # Executar o modo apropriado
    try:
        if mode == "mcp":
            await run_mcp_mode()
        elif mode == "openapi":
            await run_openapi_mode()
        elif mode == "both":
            await run_both_modes()
        else:
            logger.error(f"Modo desconhecido: {mode}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("⏹️  Servidor encerrado pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Saindo...")
        sys.exit(0)
