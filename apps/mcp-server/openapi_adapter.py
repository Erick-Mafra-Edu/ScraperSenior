#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAPI Adapter para MCP Server
===============================

Converte o MCP Server em uma API REST padrão com documentação OpenAPI automática.
Permite usar o MCP Server como uma API HTTP tradicional, mantendo compatibilidade
com MCP (stdio) quando necessário.

Recursos:
- Documentação Swagger automática em /docs
- Documentação ReDoc em /redoc
- Schema OpenAPI em /openapi.json
- Suporte a CORS para requisições cross-origin
- Health checks e métricas
- Suporte a múltiplas formas de autenticação
- Paginação automática de resultados

Instalação:
    pip install fastapi uvicorn pydantic

Uso:
    # HTTP apenas (FastAPI)
    python apps/mcp-server/openapi_adapter.py
    
    # MCP (stdio) apenas
    python apps/mcp-server/mcp_server.py
    
    # Ambos via entrypoint dual
    python apps/mcp-server/mcp_entrypoint_dual.py --mode both

Endpoints:
    GET  /health           - Health check
    GET  /stats            - Estatísticas da documentação
    POST /search           - Buscar documentos
    GET  /modules          - Listar módulos
    GET  /modules/{name}   - Obter docs de um módulo
    GET  /docs/swagger     - UI Swagger
    GET  /docs/redoc       - UI ReDoc
    GET  /openapi.json     - Schema OpenAPI
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import logging
from datetime import datetime
import asyncio

# Adicionar diretório do projeto ao path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# FastAPI e dependências
from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing_extensions import Annotated
import uvicorn

# Importar o MCP Server
try:
    from apps.mcp_server.mcp_server import SeniorDocumentationMCP
except ImportError:
    try:
        # Fallback para import relativo
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from mcp_server import SeniorDocumentationMCP
    except ImportError as e:
        print(f"❌ Erro ao importar MCP Server: {e}")
        sys.exit(1)

# ============================================================================
# Configuração de Logging
# ============================================================================

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================================================
# Modelos Pydantic (Schema OpenAPI)
# ============================================================================

class SearchRequest(BaseModel):
    """Requisição de busca com múltiplos critérios"""
    
    query: Annotated[
        str,
        Field(
            description="Texto ou palavras-chave para buscar na documentação",
            min_length=1,
            max_length=500,
            example="como configurar banco de dados"
        )
    ]
    
    module: Annotated[
        Optional[str],
        Field(
            description="Filtrar resultados por módulo específico (opcional)",
            example="RH"
        )
    ] = None
    
    limit: Annotated[
        int,
        Field(
            description="Número máximo de resultados",
            ge=1,
            le=100
        )
    ] = 10
    
    offset: Annotated[
        int,
        Field(
            description="Offset para paginação",
            ge=0
        )
    ] = 0


class DocumentResponse(BaseModel):
    """Modelo de resposta para um documento encontrado"""
    
    id: str = Field(description="ID único do documento")
    title: str = Field(description="Título do documento")
    module: str = Field(description="Módulo ao qual pertence")
    breadcrumb: Optional[str] = Field(
        description="Caminho hierárquico do documento"
    )
    content_preview: str = Field(
        description="Preview do conteúdo (primeiras 200 caracteres)"
    )
    content: Optional[str] = Field(
        description="Conteúdo completo do documento (opcional)"
    )
    html: Optional[str] = Field(
        description="HTML original do documento (opcional)"
    )
    url: Optional[str] = Field(description="URL original do documento")
    score: Optional[float] = Field(
        description="Score de relevância da busca (0-100)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadados adicionais"
    )


class SearchResponse(BaseModel):
    """Resposta para busca com paginação"""
    
    success: bool = Field(description="Se a busca foi bem-sucedida")
    query: str = Field(description="Query executada")
    total: int = Field(description="Total de resultados encontrados")
    limit: int = Field(description="Limite de resultados")
    offset: int = Field(description="Offset usado")
    results: List[DocumentResponse] = Field(
        description="Lista de documentos encontrados"
    )
    execution_time_ms: float = Field(
        description="Tempo de execução da busca em milissegundos"
    )


class ModuleInfo(BaseModel):
    """Informações sobre um módulo"""
    
    name: str = Field(description="Nome do módulo")
    doc_count: int = Field(description="Número de documentos do módulo")
    description: Optional[str] = Field(
        description="Descrição do módulo"
    )


class ModulesResponse(BaseModel):
    """Resposta com lista de módulos"""
    
    success: bool = Field(description="Se a operação foi bem-sucedida")
    total_modules: int = Field(description="Total de módulos")
    modules: List[ModuleInfo] = Field(description="Lista de módulos")


class ModuleDocsResponse(BaseModel):
    """Resposta com documentação de um módulo"""
    
    success: bool = Field(description="Se a operação foi bem-sucedida")
    module: str = Field(description="Nome do módulo")
    total_docs: int = Field(description="Total de documentos no módulo")
    documents: List[DocumentResponse] = Field(
        description="Lista de documentos do módulo"
    )


class StatsResponse(BaseModel):
    """Estatísticas da documentação"""
    
    success: bool = Field(description="Se a operação foi bem-sucedida")
    total_documents: int = Field(description="Total de documentos indexados")
    total_modules: int = Field(description="Total de módulos")
    modules: Dict[str, int] = Field(
        description="Contagem de documentos por módulo"
    )
    index_name: str = Field(description="Nome do índice")
    meilisearch_version: Optional[str] = Field(
        description="Versão do Meilisearch"
    )
    last_indexed: Optional[str] = Field(
        description="Última data de indexação"
    )


class HealthResponse(BaseModel):
    """Resposta de health check"""
    
    status: str = Field(description="Status do serviço (healthy/unhealthy)")
    timestamp: str = Field(description="Timestamp do check")
    version: str = Field(description="Versão do MCP Server")
    meilisearch: Dict[str, Any] = Field(
        description="Status do Meilisearch"
    )


# ============================================================================
# FastAPI Application
# ============================================================================

def create_app(meilisearch_url: Optional[str] = None, api_key: Optional[str] = None) -> FastAPI:
    """
    Cria e configura a aplicação FastAPI com OpenAPI adapter
    
    Args:
        meilisearch_url: URL do Meilisearch
        api_key: API key do Meilisearch
    
    Returns:
        FastAPI application configurada
    """
    
    app = FastAPI(
        title="Senior Documentation API",
        description="API OpenAPI para busca em documentação Senior com integração Meilisearch",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        servers=[
            {
                "url": "http://localhost:8000",
                "description": "Servidor local"
            },
            {
                "url": "http://people-fy.com:8000",
                "description": "Servidor externo (people-fy.com)"
            },
            {
                "url": "http://senior-docs-mcp-server:8000",
                "description": "Servidor Docker interno"
            }
        ]
    )
    
    # ====================================================================
    # CORS Middleware
    # ====================================================================
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Em produção, restringir isso
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # ====================================================================
    # Inicialização do MCP Server
    # ====================================================================
    
    meilisearch_url = meilisearch_url or os.getenv(
        "MEILISEARCH_URL",
        "http://localhost:7700"
    )
    api_key = api_key or os.getenv(
        "MEILISEARCH_KEY",
        "meilisearch_master_key"
    )
    
    logger.info(f"Inicializando MCP Server com Meilisearch: {meilisearch_url}")
    
    try:
        mcp_server = SeniorDocumentationMCP(
            meilisearch_url=meilisearch_url,
            api_key=api_key
        )
        logger.info("✅ MCP Server inicializado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar MCP Server: {e}")
        mcp_server = None
    
    # ====================================================================
    # Endpoints OpenAPI
    # ====================================================================
    
    @app.get(
        "/health",
        response_model=HealthResponse,
        summary="Health Check",
        description="Verifica a saúde do serviço e conectividade com Meilisearch",
        tags=["Sistema"]
    )
    async def health_check() -> HealthResponse:
        """
        Health check do MCP Server.
        
        Verifica:
        - Status do servidor MCP
        - Conectividade com Meilisearch
        - Versão dos serviços
        
        Returns:
            HealthResponse com status detalhado
        """
        try:
            if not mcp_server:
                raise HTTPException(
                    status_code=503,
                    detail="MCP Server não foi inicializado"
                )
            
            # Tentar conectar ao Meilisearch
            meilisearch_status = await mcp_server.health_check()
            
            return HealthResponse(
                status="healthy" if meilisearch_status else "unhealthy",
                timestamp=datetime.now().isoformat(),
                version="1.0.0",
                meilisearch={
                    "url": meilisearch_url,
                    "healthy": meilisearch_status
                }
            )
        except Exception as e:
            logger.error(f"Health check falhou: {e}")
            raise HTTPException(status_code=503, detail=str(e))
    
    @app.post(
        "/search",
        response_model=SearchResponse,
        summary="Buscar Documentos",
        description="Busca documentação com múltiplos critérios de filtro",
        tags=["Busca"],
        responses={
            200: {"description": "Busca realizada com sucesso"},
            400: {"description": "Parâmetros inválidos"},
            503: {"description": "Meilisearch indisponível"}
        }
    )
    async def search_documents(
        request: SearchRequest
    ) -> SearchResponse:
        """
        Busca documentos na base de dados.
        
        Args:
            request: Requisição de busca com query e filtros
        
        Returns:
            SearchResponse com documentos encontrados e metadados
            
        Example:
            ```json
            {
                "query": "configurar banco de dados",
                "module": "RH",
                "limit": 10,
                "offset": 0
            }
            ```
        """
        try:
            if not mcp_server:
                raise HTTPException(
                    status_code=503,
                    detail="MCP Server não foi inicializado"
                )
            
            import time
            start_time = time.time()
            
            # Chamar MCP Server para busca
            results = await mcp_server.search(
                query=request.query,
                module=request.module,
                limit=request.limit,
                offset=request.offset
            )
            
            execution_time = (time.time() - start_time) * 1000  # ms
            
            # Converter resultados para modelo Pydantic
            documents = []
            for result in results.get("documents", []):
                documents.append(DocumentResponse(
                    id=result.get("id", ""),
                    title=result.get("title", ""),
                    module=result.get("module", ""),
                    breadcrumb=result.get("breadcrumb"),
                    content_preview=result.get("content", "")[:200],
                    content=result.get("content"),
                    html=result.get("html"),
                    url=result.get("url"),
                    score=result.get("score"),
                    metadata=result.get("metadata", {})
                ))
            
            return SearchResponse(
                success=True,
                query=request.query,
                total=results.get("total", len(documents)),
                limit=request.limit,
                offset=request.offset,
                results=documents,
                execution_time_ms=execution_time
            )
        
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get(
        "/modules",
        response_model=ModulesResponse,
        summary="Listar Módulos",
        description="Retorna lista de todos os módulos disponíveis",
        tags=["Módulos"]
    )
    async def list_modules() -> ModulesResponse:
        """
        Lista todos os módulos disponíveis.
        
        Returns:
            ModulesResponse com lista de módulos e contagem
        """
        try:
            if not mcp_server:
                raise HTTPException(
                    status_code=503,
                    detail="MCP Server não foi inicializado"
                )
            
            modules_data = await mcp_server.get_modules()
            
            modules = [
                ModuleInfo(
                    name=name,
                    doc_count=count,
                    description=None
                )
                for name, count in modules_data.get("modules", {}).items()
            ]
            
            return ModulesResponse(
                success=True,
                total_modules=len(modules),
                modules=modules
            )
        
        except Exception as e:
            logger.error(f"Erro ao listar módulos: {e}")
            raise HTTPException(status_code=503, detail=str(e))
    
    @app.get(
        "/modules/{module_name}",
        response_model=ModuleDocsResponse,
        summary="Obter Documentação do Módulo",
        description="Retorna toda a documentação de um módulo específico",
        tags=["Módulos"]
    )
    async def get_module_docs(
        module_name: Annotated[
            str,
            Field(description="Nome do módulo")
        ]
    ) -> ModuleDocsResponse:
        """
        Retorna toda a documentação de um módulo.
        
        Args:
            module_name: Nome do módulo (ex: 'RH', 'Fiscal', 'Financeiro')
        
        Returns:
            ModuleDocsResponse com todos os documentos do módulo
        """
        try:
            if not mcp_server:
                raise HTTPException(
                    status_code=503,
                    detail="MCP Server não foi inicializado"
                )
            
            docs = await mcp_server.get_module_docs(module_name)
            
            documents = [
                DocumentResponse(
                    id=doc.get("id", ""),
                    title=doc.get("title", ""),
                    module=doc.get("module", ""),
                    breadcrumb=doc.get("breadcrumb"),
                    content_preview=doc.get("content", "")[:200],
                    content=doc.get("content"),
                    html=doc.get("html"),
                    url=doc.get("url"),
                    score=None,
                    metadata=doc.get("metadata", {})
                )
                for doc in docs.get("documents", [])
            ]
            
            return ModuleDocsResponse(
                success=True,
                module=module_name,
                total_docs=len(documents),
                documents=documents
            )
        
        except Exception as e:
            logger.error(f"Erro ao obter docs do módulo {module_name}: {e}")
            raise HTTPException(status_code=404, detail=str(e))
    
    @app.get(
        "/stats",
        response_model=StatsResponse,
        summary="Estatísticas da Documentação",
        description="Retorna estatísticas gerais da base de documentação",
        tags=["Informações"]
    )
    async def get_stats() -> StatsResponse:
        """
        Retorna estatísticas da documentação indexada.
        
        Returns:
            StatsResponse com totais e contagem por módulo
        """
        try:
            if not mcp_server:
                raise HTTPException(
                    status_code=503,
                    detail="MCP Server não foi inicializado"
                )
            
            stats = await mcp_server.get_stats()
            
            return StatsResponse(
                success=True,
                total_documents=stats.get("total_documents", 0),
                total_modules=stats.get("total_modules", 0),
                modules=stats.get("modules", {}),
                index_name=stats.get("index_name", "senior_docs"),
                meilisearch_version=stats.get("meilisearch_version"),
                last_indexed=stats.get("last_indexed")
            )
        
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            raise HTTPException(status_code=503, detail=str(e))
    
    @app.get(
        "/",
        tags=["Informações"],
        summary="API Info",
        description="Retorna informações sobre a API"
    )
    async def root():
        """
        Retorna informações sobre a API.
        
        Acesse:
        - `/docs` para Swagger UI
        - `/redoc` para ReDoc
        - `/openapi.json` para schema OpenAPI
        """
        return {
            "name": "Senior Documentation API",
            "version": "1.0.0",
            "description": "API OpenAPI para busca em documentação Senior",
            "docs": {
                "swagger": "http://localhost:8000/docs",
                "redoc": "http://localhost:8000/redoc",
                "schema": "http://localhost:8000/openapi.json"
            },
            "endpoints": {
                "health": "GET /health",
                "search": "POST /search",
                "modules": "GET /modules",
                "module_docs": "GET /modules/{module_name}",
                "stats": "GET /stats"
            }
        }
    
    # ====================================================================
    # Schema OpenAPI - Serve openapi.json from disk
    # ====================================================================
    
    @app.get(
        "/api/openapi.json",
        tags=["OpenAPI"],
        summary="Schema OpenAPI",
        description="Retorna o schema OpenAPI em formato JSON (arquivo disco)",
        include_in_schema=False
    )
    async def get_openapi_schema_from_file():
        """
        Retorna o schema OpenAPI carregado do arquivo openapi.json na raiz do projeto.
        Este endpoint serve a especificação OpenAPI completa como arquivo estático.
        """
        try:
            # Procurar openapi.json na raiz do projeto
            openapi_paths = [
                Path(__file__).parent.parent.parent / "openapi.json",  # raiz/openapi.json
                Path(__file__).parent / "openapi.json",  # apps/mcp-server/openapi.json
                Path.cwd() / "openapi.json"  # current working directory
            ]
            
            openapi_file = None
            for path in openapi_paths:
                if path.exists():
                    openapi_file = path
                    logger.info(f"✓ Arquivo OpenAPI encontrado: {openapi_file}")
                    break
            
            if not openapi_file:
                logger.warning(f"Arquivo openapi.json não encontrado. Procurou em: {openapi_paths}")
                # Fallback: retornar schema gerado pelo FastAPI
                return app.openapi()
            
            # Servir arquivo como resposta JSON
            return FileResponse(
                path=openapi_file,
                media_type="application/json",
                filename="openapi.json"
            )
        
        except Exception as e:
            logger.error(f"Erro ao servir openapi.json: {e}")
            # Fallback: retornar schema gerado pelo FastAPI
            return app.openapi()
    
    return app


# ============================================================================
# Main
# ============================================================================

async def main():
    """Inicia o servidor FastAPI"""
    
    logger.info("🚀 Iniciando OpenAPI Adapter para MCP Server...")
    
    # Criar aplicação
    app = create_app()
    
    # Configurações do Uvicorn
    config = uvicorn.Config(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        access_log=True,
        reload=os.getenv("RELOAD", "false").lower() == "true"
    )
    
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️  OpenAPI Adapter encerrado pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)
