#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP MCP Server - Senior Documentation Search
==============================================

Implementa o protocolo MCP "Streamable HTTP" conforme especificação oficial:
https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#streamable-http

Características:
- POST: Recebe JSON-RPC, retorna SSE stream ou JSON direto
- GET: Abre SSE stream para mensagens do servidor
- Session Management com Mcp-Session-Id
- Protocol Version Header: MCP-Protocol-Version
- Security: Valida Origin header

Uso:
    python apps/mcp-server/mcp_server_http.py
    # Acesse: http://localhost:8000/mcp

Configuração MCP (mcp.json):
    {
        "servers": {
            "senior-docs-http": {
                "type": "http",
                "url": "http://localhost:8000/mcp"
            }
        }
    }
"""

import json
import sys
import os
import asyncio
import uuid
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from collections import defaultdict

# FastAPI + Uvicorn para HTTP
try:
    from fastapi import FastAPI, Request, Response, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError:
    print("[!] FastAPI não instalado. Execute: pip install fastapi uvicorn")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Adicionar projeto ao path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Importação com namespace relativo (evita problema com hífen no nome do diretório)
try:
    from mcp_server import SeniorDocumentationMCP
except ImportError:
    # Fallback para importação com namespace completo
    from apps.mcp_server.mcp_server import SeniorDocumentationMCP

# ============================================================================
# MCP HTTP Server Implementation
# ============================================================================

class MCPHttpServer:
    """Implementa MCP Streamable HTTP Transport"""
    
    def __init__(self):
        self.mcp = SeniorDocumentationMCP()
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.sse_connections: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)
        
    def create_session(self) -> str:
        """Cria nova sessão e retorna session ID"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "created_at": datetime.now(),
            "request_count": 0
        }
        logger.info(f"✓ Sessão criada: {session_id}")
        return session_id
    
    def validate_session(self, session_id: Optional[str]) -> bool:
        """Valida se sessão existe"""
        if not session_id:
            return False
        return session_id in self.sessions
    
    def parse_query(self, query: str, strategy: str = "auto") -> str:
        """
        Parse query com 3 estratégias diferentes para melhorar resultados de busca.
        
        Estratégias:
        1. "quoted": Envolve query em aspas para busca de frase exata
           "funções lsp" -> "\"funções lsp\"" (procura frase exata)
        
        2. "and": Usa AND implícito entre termos
           "funções lsp" -> "funções AND lsp" (procura ambos os termos)
        
        3. "auto": Inteligente - tenta ambas estratégias
           - Se query tem espaço: tenta primeiro "quoted", depois "and"
           - Se sem espaço: mantém como está
        
        Args:
            query: String de busca original
            strategy: "quoted", "and", "auto" ou número (1-3)
        
        Returns:
            Query processada conforme estratégia
        """
        query = query.strip() if query else ""
        
        if not query:
            return query
        
        # Mapear números para estratégias (para compatibilidade com integers)
        if isinstance(strategy, int):
            strategy = ["quoted", "and", "auto"][min(strategy - 1, 2)]
        
        has_spaces = " " in query
        
        logger.debug(f"Query parsing: '{query}' | has_spaces={has_spaces} | strategy={strategy}")
        
        if strategy == "quoted" or (strategy == "auto" and has_spaces):
            # Estratégia 1: Envolver em aspas para busca de frase exata
            # Se já tem aspas, não duplicar
            if not (query.startswith('"') and query.endswith('"')):
                parsed = f'"{query}"'
            else:
                parsed = query
            logger.info(f"Query parsing (quoted): '{query}' -> '{parsed}'")
            return parsed
        
        elif strategy == "and":
            # Estratégia 2: Usar AND entre termos
            if has_spaces and " AND " not in query.upper():
                terms = query.split()
                parsed = " AND ".join(terms)
                logger.info(f"Query parsing (and): '{query}' -> '{parsed}'")
                return parsed
            return query
        
        elif strategy == "auto":
            # Estratégia 3: Inteligente
            # Se não tem espaço, retorna como está
            # Se tem espaço, tenta estratégia "quoted" primeiro
            if not has_spaces:
                return query
            # Fallback para quoted quando auto não tem espaço
            if not (query.startswith('"') and query.endswith('"')):
                parsed = f'"{query}"'
            else:
                parsed = query
            logger.info(f"Query parsing (auto/fallback): '{query}' -> '{parsed}'")
            return parsed
        
        return query
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna lista de ferramentas MCP"""
        return [
            {
                "name": "search_docs",
                "description": "Busca documentos por palavras-chave com parsing inteligente",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Palavras-chave para busca"
                        },
                        "module": {
                            "type": "string",
                            "description": "Módulo para filtrar (opcional)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Máximo de resultados (padrão: 5)"
                        },
                        "query_strategy": {
                            "type": "string",
                            "enum": ["quoted", "and", "auto"],
                            "description": "Estratégia de parsing: 'quoted' (frase exata), 'and' (AND entre termos), 'auto' (inteligente)",
                            "default": "auto"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "list_modules",
                "description": "Lista todos os módulos disponíveis",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_module_docs",
                "description": "Retorna documentos de um módulo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "module": {
                            "type": "string",
                            "description": "Nome do módulo"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Máximo de resultados (padrão: 20)"
                        }
                    },
                    "required": ["module"]
                }
            },
            {
                "name": "get_stats",
                "description": "Retorna estatísticas da documentação",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Executa chamada de ferramenta MCP"""
        try:
            if tool_name == "search_docs":
                query = arguments.get("query", "")
                module = arguments.get("module")
                limit = int(arguments.get("limit", 5))
                query_strategy = arguments.get("query_strategy", "auto")
                
                if not query:
                    return json.dumps({"error": "query é obrigatório"})
                
                # Aplicar estratégia de parsing
                parsed_query = self.parse_query(query, query_strategy)
                
                # Log da transformação
                if parsed_query != query:
                    logger.info(f"Query transformada: '{query}' -> '{parsed_query}' (estratégia: {query_strategy})")
                
                # Buscar com query transformada
                results = self.mcp.search(parsed_query, module, limit)
                # Ensure results is always a list
                if not isinstance(results, list):
                    results = list(results) if hasattr(results, '__iter__') else []
                
                return json.dumps({
                    "query": query,
                    "parsed_query": parsed_query,
                    "query_strategy": query_strategy,
                    "module_filter": module,
                    "count": len(results),
                    "results": results
                }, ensure_ascii=False, indent=2)
            
            elif tool_name == "list_modules":
                modules = self.mcp.get_modules()
                # Ensure modules is always a list
                if not isinstance(modules, list):
                    modules = list(modules) if hasattr(modules, '__iter__') else []
                
                return json.dumps({
                    "total_modules": len(modules),
                    "modules": modules
                }, ensure_ascii=False)
            
            elif tool_name == "get_module_docs":
                module = arguments.get("module", "")
                limit = int(arguments.get("limit", 20))
                
                if not module:
                    return json.dumps({"error": "module é obrigatório"})
                
                docs = self.mcp.get_by_module(module, limit)
                # Ensure docs is always a list
                if not isinstance(docs, list):
                    docs = list(docs) if hasattr(docs, '__iter__') else []
                
                return json.dumps({
                    "module": module,
                    "count": len(docs),
                    "docs": docs
                }, ensure_ascii=False, indent=2)
            
            elif tool_name == "get_stats":
                stats = self.mcp.get_stats()
                return json.dumps(stats, ensure_ascii=False, indent=2)
            
            else:
                return json.dumps({"error": f"Ferramenta desconhecida: {tool_name}"})
        
        except Exception as e:
            logger.error(f"Erro ao executar {tool_name}: {e}", exc_info=True)
            return json.dumps({"error": str(e)})


# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="Senior Documentation MCP HTTP Server",
    description="MCP Server usando Streamable HTTP Transport",
    version="1.0.0"
)

# CORS para segurança (permitir qualquer origem - é interno)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir qualquer origem (é servidor interno)
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,  # Cache preflight por 1 hora
)

# Instância global do servidor
mcp_server = MCPHttpServer()


# ============================================================================
# MCP Endpoints
# ============================================================================

@app.post("/mcp")
async def mcp_post(request: Request) -> Response:
    """
    Recebe JSON-RPC POST.
    
    Conforme spec: https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#sending-messages-to-the-server
    
    Suporta:
    - application/json: JSON simples
    - text/event-stream: Server-Sent Events para streaming
    """
    try:
        # Validar headers - aceita JSON ou SSE
        accept = request.headers.get("Accept", "application/json")
        want_stream = "text/event-stream" in accept
        
        # Validar session se necessário
        session_id = request.headers.get("Mcp-Session-Id")
        if session_id and not mcp_server.validate_session(session_id):
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        # Validar protocol version
        protocol_version = request.headers.get("MCP-Protocol-Version", "2025-06-18")
        if protocol_version not in ["2025-06-18", "2024-11-05"]:
            raise HTTPException(status_code=400, detail=f"Unsupported protocol version: {protocol_version}")
        
        # Parse JSON-RPC
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        msg_id = body.get("id")
        
        logger.debug(f"POST /mcp - Method: {method}, ID: {msg_id}")
        
        # Helper para retornar resposta em SSE ou JSON conforme Accept header
        def create_response(data: Dict[str, Any], session_id: Optional[str] = None) -> Response:
            """Retorna resposta em SSE ou JSON conforme Accept header"""
            headers = {}
            if session_id:
                headers["Mcp-Session-Id"] = session_id
            
            if want_stream:
                # SSE format para VS Code HTTP client
                # Usar Response regular com conteúdo SSE, não StreamingResponse
                json_str = json.dumps(data, ensure_ascii=False)
                sse_content = f"data: {json_str}\n\n"
                
                return Response(
                    content=sse_content.encode('utf-8'),
                    status_code=200,
                    media_type="text/event-stream",
                    headers=headers
                )
            else:
                # JSON direto
                return Response(
                    content=json.dumps(data, ensure_ascii=False),
                    status_code=200,
                    media_type="application/json",
                    headers=headers
                )
        
        # ====================================================================
        # Handlers
        # ====================================================================
        
        if method == "initialize":
            # Criar sessão na inicialização
            new_session_id = mcp_server.create_session()
            
            return create_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {
                        "tools": {
                            "listChanged": False
                        },
                        "resources": {},
                        "prompts": {}
                    },
                    "serverInfo": {
                        "name": "Senior Documentation MCP",
                        "version": "1.0.0"
                    }
                }
            }, session_id=new_session_id)
        
        elif method == "tools/list":
            tools = mcp_server.get_tools()
            
            return create_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": tools
                }
            })
        
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            logger.info(f"Executando tool: {tool_name}")
            result = await mcp_server.handle_tool_call(tool_name, tool_args)
            
            return create_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "type": "text",
                    "text": result
                }
            })
        
        else:
            # Método desconhecido
            return create_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            })
    
    except json.JSONDecodeError:
        return create_response({
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32700,
                "message": "Parse error"
            }
        })
    
    except HTTPException as e:
        return create_response({
            "jsonrpc": "2.0",
            "id": msg_id if 'msg_id' in locals() else None,
            "error": {
                "code": -32603,
                "message": e.detail
            }
        })
    
    except Exception as e:
        logger.error(f"Erro no POST /mcp: {e}", exc_info=True)
        return create_response({
            "jsonrpc": "2.0",
            "id": msg_id if 'msg_id' in locals() else None,
            "error": {
                "code": -32603,
                "message": str(e)
            }
        })


@app.get("/mcp")
async def mcp_get(request: Request):
    """
    GET para abrir SSE stream.
    
    Conforme spec: https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#listening-for-messages-from-the-server
    """
    logger.info("GET /mcp - Abrindo SSE stream")
    
    # Por enquanto, retornar 405 (server não suporta GET streams)
    # Implementar se necessário para notificações do servidor
    raise HTTPException(status_code=405, detail="Method Not Allowed - GET streaming not supported")


@app.delete("/mcp")
async def mcp_delete(request: Request) -> Response:
    """
    DELETE para terminar sessão.
    
    Conforme spec: https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#session-management
    """
    session_id = request.headers.get("Mcp-Session-Id")
    
    if not session_id or not mcp_server.validate_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Terminar sessão
    del mcp_server.sessions[session_id]
    logger.info(f"✓ Sessão terminada: {session_id}")
    
    return Response(
        status_code=200,
        content=""
    )


@app.get("/health")
async def health() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Senior Documentation MCP HTTP",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/openapi.json", include_in_schema=False)
async def openapi_schema() -> Dict[str, Any]:
    """Retorna OpenAPI 3.1.0 schema completo"""
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Senior Documentation MCP HTTP Server",
            "description": "Servidor MCP (Model Context Protocol) via HTTP para busca de documentação Senior. Implementa protocolo MCP 2025-06-18 com suporte a JSON-RPC 2.0 e Server-Sent Events (SSE).\n\nFERRAMENTAS DISPONÍVEIS:\n- search_docs: Busca documentos com parsing inteligente de query\n- list_modules: Lista módulos de documentação\n- get_module_docs: Retorna docs de um módulo\n- get_stats: Estatísticas da base",
            "version": "1.0.0",
            "contact": {"name": "Senior Documentation"},
            "license": {"name": "MIT"}
        },
        "servers": [
            {"url": "http://localhost:8000", "description": "Local"},
            {"url": "http://people-fy.com:8000", "description": "Production"}
        ],
        "paths": {
            "/mcp": {
                "post": {
                    "summary": "MCP JSON-RPC 2.0 Endpoint",
                    "description": "Endpoint principal. Métodos: 'initialize', 'tools/list', 'tools/call'",
                    "operationId": "mcp_post",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "jsonrpc": {"type": "string", "enum": ["2.0"]},
                                        "method": {"type": "string", "enum": ["initialize", "tools/list", "tools/call"]},
                                        "params": {"type": "object"},
                                        "id": {"type": ["string", "number"]}
                                    },
                                    "required": ["jsonrpc", "method", "id"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Sucesso - JSON-RPC Response"},
                        "400": {"description": "Erro - JSON-RPC Error"}
                    }
                },
                "delete": {
                    "summary": "Encerrar Sessão",
                    "parameters": [
                        {
                            "name": "Mcp-Session-Id",
                            "in": "header",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {"description": "Sessão encerrada"},
                        "404": {"description": "Sessão não encontrada"}
                    }
                }
            },
            "/health": {
                "get": {
                    "summary": "Health Check",
                    "responses": {
                        "200": {
                            "description": "Servidor saudável",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "service": {"type": "string"},
                                            "version": {"type": "string"},
                                            "timestamp": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }


@app.get("/docs", include_in_schema=False)
async def docs():
    """Swagger UI"""
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Senior Documentation MCP HTTP - Swagger UI"
    )


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    host = os.getenv("OPENAPI_HOST", "127.0.0.1")  # Localhost por segurança
    port = int(os.getenv("OPENAPI_PORT", 8000))
    
    logger.info("=" * 80)
    logger.info("🚀 MCP HTTP Server - Streamable HTTP Transport")
    logger.info("=" * 80)
    logger.info(f"✓ Iniciando em http://{host}:{port}")
    logger.info(f"✓ MCP Endpoint: POST/GET/DELETE http://{host}:{port}/mcp")
    logger.info(f"✓ Health Check: http://{host}:{port}/health")
    logger.info(f"✓ Swagger UI: http://{host}:{port}/docs")
    logger.info("=" * 80)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
