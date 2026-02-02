#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server HTTP Docker Wrapper
==============================

Wrapper HTTP para o MCP Server melhorado.
Integra com Meilisearch e suporta protocolo JSON-RPC 2.0.

Suporta tanto HTTP/REST quanto JSON-RPC para máxima flexibilidade.
"""

import json
import asyncio
import sys
import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import threading

# UTF-8 para Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Importar o MCP Server melhorado
sys.path.insert(0, str(Path(__file__).parent))
from mcp_server_improved import SeniorDocumentationMCP, get_mcp_server


class MCPHTTPHandler(BaseHTTPRequestHandler):
    """Handler HTTP para o protocolo MCP JSON-RPC"""
    
    # Variável de classe para compartilhar o servidor MCP
    mcp_server = None
    
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
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        
        elif path == '/ready':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "ready": True,
                "tools": list(self.mcp_server.tools.keys()) if self.mcp_server else []
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        
        elif path == '/stats':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "operational",
                "tools": len(self.mcp_server.tools) if self.mcp_server else 0,
                "modules": 0,  # Será calculado por get_stats
                "meilisearch": self.mcp_server.meilisearch_url if self.mcp_server else "N/A"
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        
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
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}, ensure_ascii=False).encode('utf-8'))
    
    def do_POST(self):
        """Tratador POST para JSON-RPC e REST"""
        path = urlparse(self.path).path
        
        try:
            # Ler corpo
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error_json(400, "Empty request body")
                return
            
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
            
            # ========== JSON-RPC ENDPOINTS ==========
            if path in ['/', '/messages']:
                # JSON-RPC 2.0
                self.handle_jsonrpc(data)
                return
            
            # ========== REST ENDPOINTS ==========
            elif path == '/search':
                # REST: Buscar documentos
                self.handle_rest_search(data)
                return
            
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Not found"}, ensure_ascii=False).encode('utf-8'))
        
        except json.JSONDecodeError:
            self.send_error_json(400, "Invalid JSON")
        except Exception as e:
            self.send_error_json(500, str(e))
    
    def handle_jsonrpc(self, data: dict):
        """Processar requisição JSON-RPC 2.0"""
        jsonrpc = data.get('jsonrpc')
        method = data.get('method')
        params = data.get('params', {})
        request_id = data.get('id')
        
        if jsonrpc != '2.0':
            self.send_error_json(400, "Invalid jsonrpc version", request_id)
            return
        
        if not method:
            self.send_error_json(400, "Method is required", request_id)
            return
        
        # Distribuir para handlers
        if method == 'initialize':
            self.handle_initialize(request_id, params)
        elif method == 'tools/list':
            self.handle_tools_list(request_id)
        elif method == 'tools/call':
            self.handle_tool_call(request_id, params)
        else:
            self.send_error_json(-32601, f"Method not found: {method}", request_id)
    
    def handle_initialize(self, request_id: int, params: dict):
        """Responder a initialize"""
        tools = []
        for name, info in self.mcp_server.tools.items():
            tool = {
                "name": name,
                "description": info.get("description", ""),
                "inputSchema": info.get("inputSchema", {})
            }
            tools.append(tool)
        
        response = {
            "protocolVersion": "2024-11-05",
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
        
        self.send_json_response(request_id, response)
    
    def handle_tools_list(self, request_id: int):
        """Responder a tools/list"""
        tools = []
        for name, info in self.mcp_server.tools.items():
            tool = {
                "name": name,
                "description": info.get("description", ""),
                "inputSchema": info.get("inputSchema", {})
            }
            tools.append(tool)
        
        response = {"tools": tools}
        self.send_json_response(request_id, response)
    
    def handle_tool_call(self, request_id: int, params: dict):
        """Responder a tools/call"""
        tool_name = params.get('name')
        tool_args = params.get('arguments', {})
        
        if not tool_name:
            self.send_error_json(400, "Tool name is required", request_id)
            return
        
        try:
            # Executar ferramenta de forma assíncrona
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(
                self.mcp_server.call_tool(tool_name, tool_args)
            )
            loop.close()
            
            # Parsear resultado
            result_obj = json.loads(result) if isinstance(result, str) else result
            
            # Formatar como MCP
            response = {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result_obj, ensure_ascii=False)
                    }
                ]
            }
            
            self.send_json_response(request_id, response)
        except Exception as e:
            self.send_error_json(500, f"Tool error: {str(e)}", request_id)
    
    def handle_rest_search(self, data: dict):
        """Handler REST: POST /search"""
        try:
            query = data.get('query', '')
            module = data.get('module')
            limit = int(data.get('limit', 5))
            
            if not query:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "query is required"}, ensure_ascii=False).encode('utf-8'))
                return
            
            # Executar busca
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(
                self.mcp_server.handle_search_docs(query, module, limit)
            )
            loop.close()
            
            result_obj = json.loads(result)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result_obj, ensure_ascii=False).encode('utf-8'))
        
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}, ensure_ascii=False).encode('utf-8'))
    
    def send_json_response(self, request_id: int, result):
        """Enviar resposta JSON-RPC sucesso"""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def send_error_json(self, error_code: int, error_msg: str, request_id=None):
        """Enviar resposta JSON-RPC erro"""
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
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suprimir logs HTTP padrão"""
        pass


def run_server(host='0.0.0.0', port=8000):
    """Executar servidor HTTP MCP"""
    
    # Inicializar MCP Server
    mcp_server = SeniorDocumentationMCP()
    MCPHTTPHandler.mcp_server = mcp_server
    
    # Criar servidor HTTP
    server = HTTPServer((host, port), MCPHTTPHandler)
    
    print(f"\n[✓] MCP Server iniciado em http://{host}:{port}")
    print(f"[✓] Protocolos suportados:")
    print(f"    - JSON-RPC 2.0 (para VS Code / Copilot Desktop)")
    print(f"    - REST HTTP (para testes e integração)")
    print(f"\n[✓] Endpoints disponíveis:")
    print(f"    JSON-RPC: POST / ou POST /messages")
    print(f"    Health:   GET /health")
    print(f"    Tools:    GET /tools | tools/list (JSON-RPC)")
    print(f"    Search:   POST /search (REST)")
    print(f"\n[✓] Ferramentas MCP:")
    for tool_name, tool_info in mcp_server.tools.items():
        print(f"    - {tool_name}: {tool_info.get('description', 'N/A')}")
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Servidor encerrado")
        server.shutdown()


if __name__ == "__main__":
    # Pegar porta do ambiente
    port = int(os.getenv('PORT', 8000))
    run_server(port=port)
