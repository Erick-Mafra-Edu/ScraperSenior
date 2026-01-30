#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server HTTP - Senior Documentation Search
===============================================

Implementação de servidor HTTP com protocolo MCP JSON-RPC para Docker.
Compatível com VS Code MCP protocol.
"""

import json
import asyncio
import sys
import os
from pathlib import Path
from typing import Any, Dict, List
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Forçar UTF-8 para evitar problemas de encoding no Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Importar o MCP Server
sys.path.insert(0, str(Path(__file__).parent))
from mcp_server import SeniorDocumentationMCP, MCPServer

class MCPHTTPHandler(BaseHTTPRequestHandler):
    """Handler HTTP para o protocolo MCP JSON-RPC"""
    
    # Variável de classe para compartilhar o servidor MCP
    mcp_server = None
    request_id_counter = 0
    
    def do_GET(self):
        """Tratador GET para health checks"""
        path = urlparse(self.path).path
        
        if path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "service": "MCP Server - Senior Documentation",
                "mode": "http"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif path == '/ready':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "ready": True,
                "tools": list(self.mcp_server.tools.keys()) if self.mcp_server else []
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif path == '/stats':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            if self.mcp_server and self.mcp_server.doc_search:
                stats = self.mcp_server.doc_search.get_stats()
                response = {
                    "stats": stats,
                    "tools": len(self.mcp_server.tools),
                    "modules": len(self.mcp_server.doc_search.get_modules())
                }
            else:
                response = {"error": "MCP Server not initialized"}
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif path == '/tools':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            if self.mcp_server:
                tools = {
                    name: {
                        "description": info.get("description", ""),
                        "inputSchema": info.get("inputSchema", {})
                    }
                    for name, info in self.mcp_server.tools.items()
                }
                response = {"tools": tools}
            else:
                response = {"error": "MCP Server not initialized", "tools": {}}
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))
    
    def do_POST(self):
        """Tratador POST para protocolo MCP JSON-RPC e REST endpoints"""
        path = urlparse(self.path).path
        
        try:
            # Ler corpo da requisição
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Empty request body"}).encode('utf-8'))
                return
            
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
            
            # ========== REST ENDPOINTS ==========
            if path == '/search':
                # Endpoint REST: POST /search
                self.handle_rest_search(data)
                return
            
            elif path == '/call':
                # Endpoint REST: POST /call
                # DEBUG
                import sys
                print(f"[DEBUG do_POST] Chamando handle_rest_call com data={data}", file=sys.stderr, flush=True)
                self.handle_rest_call(data)
                return
            
            # ========== JSON-RPC ENDPOINTS ==========
            if path == '/' or path == '/messages':
                # Verificar se é um JSON-RPC válido
                if not isinstance(data, dict):
                    self.send_error_response(400, "Invalid JSON-RPC request", None)
                    return
                
                jsonrpc = data.get('jsonrpc')
                method = data.get('method')
                params = data.get('params', {})
                request_id = data.get('id')
                
                # Se é uma notificação (sem id), processar silenciosamente
                if jsonrpc != '2.0':
                    self.send_error_response(400, "Invalid jsonrpc version", request_id)
                    return
                
                # Processar método RPC
                if method == 'initialize':
                    self.handle_initialize(request_id, params)
                elif method == 'resources/list':
                    self.handle_resources_list(request_id)
                elif method == 'tools/list':
                    self.handle_tools_list(request_id)
                elif method == 'tools/call':
                    self.handle_tool_call(request_id, params)
                elif method == 'prompts/list':
                    self.handle_prompts_list(request_id)
                else:
                    self.send_error_response(-32601, f"Method not found: {method}", request_id)
            
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))
        
        except json.JSONDecodeError as e:
            self.send_error_response(400, f"JSON decode error: {str(e)}", None)
        except Exception as e:
            self.send_error_response(500, str(e), None)
    
    def send_response_json(self, request_id: int, result: Any):
        """Enviar resposta JSON-RPC 2.0 de sucesso"""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def send_error_response(self, error_code: int, error_msg: str, request_id=None):
        """Enviar resposta JSON-RPC 2.0 de erro"""
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": error_code,
                "message": error_msg
            }
        }
        if request_id is not None:
            response["id"] = request_id
        
        http_code = 400 if error_code >= 400 else 200
        self.send_response(http_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def handle_initialize(self, request_id: int, params: dict):
        """Responder ao método initialize com schemas das ferramentas"""
        if not self.mcp_server:
            self.send_error_response(503, "Server not initialized", request_id)
            return
        
        # Obter versão do protocolo
        protocol_version = params.get('protocolVersion', '2024-11-05')
        
        # Construir lista de ferramentas com schemas
        tools = []
        for name, info in self.mcp_server.tools.items():
            tool = {
                "name": name,
                "description": info.get("description", ""),
                "inputSchema": info.get("inputSchema", {})
            }
            tools.append(tool)
        
        response = {
            "protocolVersion": protocol_version,
            "capabilities": {
                "resources": {},
                "tools": {},
                "prompts": {}
            },
            "serverInfo": {
                "name": "Senior Documentation MCP",
                "version": "1.0.0"
            },
            "tools": tools
        }
        self.send_response_json(request_id, response)
    
    def handle_resources_list(self, request_id: int):
        """Responder ao método resources/list"""
        response = {
            "resources": []
        }
        self.send_response_json(request_id, response)
    
    def handle_tools_list(self, request_id: int):
        """Responder ao método tools/list"""
        if not self.mcp_server:
            self.send_error_response(503, "Server not initialized", request_id)
            return
        
        tools = []
        for name, info in self.mcp_server.tools.items():
            tool = {
                "name": name,
                "description": info.get("description", ""),
                "inputSchema": info.get("inputSchema", {})
            }
            tools.append(tool)
        
        response = {
            "tools": tools
        }
        self.send_response_json(request_id, response)
    
    def handle_tool_call(self, request_id: int, params: dict):
        """Responder ao método tools/call"""
        if not self.mcp_server:
            self.send_error_response(503, "Server not initialized", request_id)
            return
        
        tool_name = params.get('name')
        tool_args = params.get('arguments', {})
        
        if not tool_name:
            self.send_error_response(400, "Tool name is required", request_id)
            return
        
        try:
            # Chamar a ferramenta
            result = self.mcp_server.handle_tool_call(tool_name, tool_args)
            result_obj = json.loads(result) if isinstance(result, str) else result
            
            response = {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result_obj, ensure_ascii=False)
                    }
                ]
            }
            self.send_response_json(request_id, response)
        except Exception as e:
            self.send_error_response(500, f"Tool error: {str(e)}", request_id)
    
    def handle_prompts_list(self, request_id: int):
        """Responder ao método prompts/list"""
        response = {
            "prompts": []
        }
        self.send_response_json(request_id, response)
    
    def handle_rest_search(self, data: dict):
        """Handler REST para POST /search - Busca simples"""
        if not self.mcp_server:
            self.send_response(503)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Server not initialized"}).encode('utf-8'))
            return
        
        query = data.get('query', '')
        module = data.get('module')
        limit = int(data.get('limit', 5))
        
        if not query:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "query is required"}).encode('utf-8'))
            return
        
        try:
            results = self.mcp_server.doc_search.search(query, module, limit)
            
            response = {
                "query": query,
                "module_filter": module,
                "count": len(results),
                "results": results
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
    
    def handle_rest_call(self, data: dict):
        """Handler REST para POST /call - Chamar ferramenta"""
        if not self.mcp_server:
            self.send_response(503)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Server not initialized"}).encode('utf-8'))
            return
        
        tool_name = data.get('tool')
        tool_args = data.get('params', {})
        
        # NOVO: Retornar info do que recebeu
        return_debug = {
            "RECEBEU_tool": tool_name,
            "RECEBEU_params": tool_args,
            "TIPO_params": str(type(tool_args))
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(return_debug, ensure_ascii=False).encode('utf-8'))
        return
        
        if not tool_name:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "tool name is required"}).encode('utf-8'))
            return
        
        try:
            # DEBUG: Return the args to see what's happening
            result = self.mcp_server.handle_tool_call(tool_name, tool_args)
            result_obj = json.loads(result) if isinstance(result, str) else result
            
            # Add debug info to response
            if isinstance(result_obj, dict):
                result_obj["_debug"] = {
                    "tool_name": tool_name,
                    "tool_args_received": tool_args,
                    "tool_args_keys": list(tool_args.keys()) if isinstance(tool_args, dict) else "NOT A DICT"
                }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result_obj, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suprimir logs padrão"""
        pass

def run_server(host='0.0.0.0', port=8000):
    """Executar servidor HTTP"""
    
    # Inicializar MCP Server
    mcp_server = MCPServer()
    MCPHTTPHandler.mcp_server = mcp_server
    
    # Criar servidor HTTP
    server = HTTPServer((host, port), MCPHTTPHandler)
    
    print(f"[✓] MCP Server HTTP iniciado em http://{host}:{port}")
    print(f"[✓] Endpoints disponíveis:")
    print(f"    - GET  /health   - Verificar saúde do servidor")
    print(f"    - GET  /ready    - Verificar se está pronto")
    print(f"    - GET  /stats    - Estatísticas do servidor")
    print(f"    - GET  /tools    - Listar ferramentas disponíveis")
    print(f"    - POST /call     - Chamar ferramenta")
    print(f"    - POST /search   - Buscar documentos")
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Servidor encerrado")
        server.shutdown()

if __name__ == "__main__":
    # Pegar porta do ambiente ou usar padrão
    port = int(os.getenv('PORT', 8000))
    run_server(port=port)
