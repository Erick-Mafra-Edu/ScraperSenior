#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server with Health Check Endpoint
====================================

Wrapper para executar MCP Server com suporte a health checks via HTTP.
Útil para Docker containers.
"""

import json
import os
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp_server import MCPServer


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Handler para health check HTTP"""
    
    server_instance = None
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service': 'MCP Server - Senior Documentation',
                'mode': 'local' if self.server_instance.doc_search.use_local else 'meilisearch'
            }
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path == '/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            stats = self.server_instance.doc_search.get_stats()
            self.wfile.write(json.dumps(stats).encode())
        
        elif self.path == '/ready':
            # Ready check - returns 200 if service is ready
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'ready': True,
                'timestamp': datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'error': 'Not found',
                'available_endpoints': ['/health', '/stats', '/ready']
            }
            self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def run_health_check_server(mcp_server, host='0.0.0.0', port=8000):
    """Run health check HTTP server in background"""
    HealthCheckHandler.server_instance = mcp_server
    
    server = HTTPServer((host, port), HealthCheckHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    
    print(f"[✓] Health check server listening on {host}:{port}")
    return server


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Server with Health Checks")
    parser.add_argument("--meilisearch-url", default="http://localhost:7700", help="URL do Meilisearch")
    parser.add_argument("--api-key", default="meilisearch_master_key", help="Chave de API")
    parser.add_argument("--health-port", type=int, default=8000, help="Porta para health checks")
    parser.add_argument("--health-host", default="0.0.0.0", help="Host para health checks")
    
    args = parser.parse_args()
    
    # Use environment variables if available
    meilisearch_url = os.getenv('MEILISEARCH_URL', args.meilisearch_url)
    api_key = os.getenv('MEILISEARCH_KEY', args.api_key)
    health_port = int(os.getenv('HEALTH_CHECK_PORT', args.health_port))
    health_host = os.getenv('HEALTH_CHECK_HOST', args.health_host)
    
    print("\n" + "="*80)
    print("[MCP SERVER] Senior Documentation Search")
    print("="*80 + "\n")
    
    # Create MCP server
    mcp_server = MCPServer()
    
    # Print server info
    modules = mcp_server.doc_search.get_modules()
    stats = mcp_server.doc_search.get_stats()
    
    print("[MÓDULOS DISPONÍVEIS]\n")
    for i, module in enumerate(modules, 1):
        print(f"  {i}. {module}")
    
    print(f"\n[ESTATÍSTICAS]\n")
    print(f"  Total de documentos: {stats.get('total_documents', 'N/A')}")
    print(f"  Módulos: {len(modules)}")
    print(f"  Fonte: {stats.get('source', 'N/A')}")
    
    # Start health check server
    print(f"\n[HEALTH CHECK]")
    run_health_check_server(mcp_server, health_host, health_port)
    
    # Print available endpoints
    print(f"\n[ENDPOINTS DISPONÍVEIS]")
    print(f"  • GET http://{health_host}:{health_port}/health - Health status")
    print(f"  • GET http://{health_host}:{health_port}/stats - Statistics")
    print(f"  • GET http://{health_host}:{health_port}/ready - Readiness probe")
    
    # Print MCP tools
    print(f"\n[FERRAMENTAS MCP DISPONÍVEIS]")
    for tool_name, tool_info in mcp_server.tools.items():
        print(f"  • {tool_name}")
        print(f"    {tool_info['description']}")
    
    print(f"\n[STATUS]\n")
    print(f"  ✓ MCP Server pronto para integração")
    print(f"  ✓ Health checks ativados")
    print(f"  ✓ Modo: {'local (JSONL)' if mcp_server.doc_search.use_local else 'Meilisearch'}")
    print(f"\n{'='*80}\n")
    
    # Keep running
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Encerrando servidor...")
        sys.exit(0)


if __name__ == "__main__":
    main()
