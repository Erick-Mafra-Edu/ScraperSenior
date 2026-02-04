#!/usr/bin/env python3
"""
Validação: OpenAPI + MCP + Dockerfile (sem Docker run)

Este script valida:
1. MCP STDIO (JSON-RPC) - Arquivo e sintaxe
2. MCP HTTP Server - Arquivo e sintaxe
3. OpenAPI Adapter - Arquivo e sintaxe
4. Dockerfile.mcp - Configuração
5. docker-compose.yml - Validação YAML
"""

import subprocess
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warn(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"ℹ️  {text}")

# ============================================================================
# 1. Validar MCP STDIO Server 
# ============================================================================

print_header("1️⃣  Validando MCP STDIO Server (JSON-RPC stdin/stdout)")

try:
    mcp_server = PROJECT_ROOT / "apps/mcp-server/mcp_server.py"
    if not mcp_server.exists():
        print_error(f"Arquivo não encontrado: {mcp_server}")
    else:
        print_success(f"Arquivo encontrado: {mcp_server.name}")
        
        # Validar sintaxe
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(mcp_server)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success("Sintaxe Python válida ✓")
        else:
            print_error(f"Erro de sintaxe: {result.stderr}")
        
        # Verificar estrutura
        with open(mcp_server, 'r') as f:
            content = f.read()
            
            checks = {
                'class MCPServer': 'Classe MCPServer',
                'class SeniorDocumentationMCP': 'Classe SeniorDocumentationMCP',
                'def main()': 'Função main()',
                'def handle_tool_call': 'Método handle_tool_call()',
                'def search': 'Método search()',
                'def get_modules': 'Método get_modules()',
            }
            
            for check_str, desc in checks.items():
                if check_str in content:
                    print_success(f"{desc} ✓")
                else:
                    print_error(f"{desc} não encontrado")

except Exception as e:
    print_error(f"Validação MCP STDIO falhou: {e}")

# ============================================================================
# 2. Validar MCP HTTP Server (novo)
# ============================================================================

print_header("2️⃣  Validando MCP HTTP Server (Streamable HTTP)")

try:
    mcp_http = PROJECT_ROOT / "apps/mcp-server/mcp_server_http.py"
    if not mcp_http.exists():
        print_warn(f"Arquivo não encontrado: mcp_server_http.py")
        print_info("Este é um novo arquivo, pode não estar ainda criado")
    else:
        print_success(f"Arquivo encontrado: {mcp_http.name}")
        
        # Validar sintaxe
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(mcp_http)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success("Sintaxe Python válida ✓")
        else:
            print_error(f"Erro de sintaxe: {result.stderr}")
        
        # Verificar estrutura
        with open(mcp_http, 'r') as f:
            content = f.read()
            
            checks = {
                'class MCPHttpServer': 'Classe MCPHttpServer',
                'def create_session': 'Método create_session()',
                '@app.post("/mcp")': 'Endpoint POST /mcp',
                '@app.get("/mcp")': 'Endpoint GET /mcp (SSE)',
                '@app.delete("/mcp")': 'Endpoint DELETE /mcp (Session)',
                'Mcp-Session-Id': 'Session management',
                'MCP-Protocol-Version': 'Protocol version validation',
            }
            
            for check_str, desc in checks.items():
                if check_str in content:
                    print_success(f"{desc} ✓")
                else:
                    print_warn(f"{desc} não encontrado")

except Exception as e:
    print_error(f"Validação MCP HTTP falhou: {e}")

# ============================================================================
# 3. Validar OpenAPI Adapter
# ============================================================================

print_header("3️⃣  Validando OpenAPI Adapter")

try:
    openapi = PROJECT_ROOT / "apps/mcp-server/openapi_adapter.py"
    if not openapi.exists():
        print_warn(f"Arquivo não encontrado: openapi_adapter.py")
    else:
        print_success(f"Arquivo encontrado: {openapi.name}")
        
        # Validar sintaxe
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(openapi)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success("Sintaxe Python válida ✓")
        else:
            print_error(f"Erro de sintaxe: {result.stderr}")
        
        # Verificar estrutura
        with open(openapi, 'r') as f:
            content = f.read()
            
            checks = {
                'def create_app': 'Função create_app()',
                '@app.get("/health")': 'Endpoint /health',
                '@app.post("/search")': 'Endpoint /search',
                '@app.get("/modules")': 'Endpoint /modules',
                '@app.get("/openapi.json")': 'Endpoint /openapi.json',
                '@app.get("/docs")': 'Swagger UI',
                'SeniorDocumentationMCP': 'Integração MCP',
            }
            
            for check_str, desc in checks.items():
                if check_str in content:
                    print_success(f"{desc} ✓")
                else:
                    print_warn(f"{desc} não encontrado")

except Exception as e:
    print_warn(f"Validação OpenAPI falhou: {e}")

# ============================================================================
# 4. Validar Dockerfile.mcp
# ============================================================================

print_header("4️⃣  Validando Dockerfile.mcp")

try:
    dockerfile = PROJECT_ROOT / "Dockerfile.mcp"
    if not dockerfile.exists():
        print_error(f"Arquivo não encontrado: {dockerfile}")
    else:
        print_success(f"Arquivo encontrado: {dockerfile.name}")
        
        with open(dockerfile, 'r') as f:
            content = f.read()
            
            # Validar componentes principais
            checks = {
                "FROM python:3.11-slim": "Base image Python 3.11-slim",
                "pip install": "Instalação de dependências",
                "COPY": "Cópia de arquivos",
                "EXPOSE 8000": "Porta 8000 exposta",
                "HEALTHCHECK": "Health check configurado",
                "appuser": "Usuário não-root (appuser)",
                "apps/mcp-server": "MCP Server copiado",
                "libs": "Libs copiadas",
            }
            
            for check_str, description in checks.items():
                if check_str in content:
                    print_success(f"{description} ✓")
                else:
                    print_warn(f"{description} não encontrado")
            
            # Verificar CMD
            if 'CMD' in content:
                # Extrair CMD
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('CMD'):
                        print_info(f"CMD: {line}")
                        if 'mcp_server' in line or 'openapi_adapter' in line or 'mcp_entrypoint' in line:
                            print_success("Entrypoint configurado corretamente ✓")
                        break
            else:
                print_error("CMD não encontrado")

except Exception as e:
    print_error(f"Validação Dockerfile falhou: {e}")

# ============================================================================
# 5. Validar docker-compose.yml
# ============================================================================

print_header("5️⃣  Validando docker-compose.yml")

try:
    docker_compose = PROJECT_ROOT / "docker-compose.yml"
    if not docker_compose.exists():
        print_error(f"Arquivo não encontrado: {docker_compose}")
    else:
        print_success(f"Arquivo encontrado: {docker_compose.name}")
        
        with open(docker_compose, 'r') as f:
            content = f.read()
            
            # Validar YAML com docker-compose config
            result = subprocess.run(
                ["docker-compose", "config", "-f", str(docker_compose)],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print_success("YAML válido ✓")
                
                # Verificar serviços
                services = ["meilisearch", "mcp-server", "scraper"]
                for service in services:
                    if service in content:
                        print_success(f"Serviço '{service}' configurado ✓")
                    else:
                        print_warn(f"Serviço '{service}' não encontrado")
                
                # Verificar configurações importantes
                if "depends_on:" in content and "meilisearch" in content:
                    print_success("Dependências configuradas ✓")
                
                if "environment:" in content:
                    print_success("Variáveis de ambiente configuradas ✓")
                
                if "networks:" in content:
                    print_success("Rede Docker configurada ✓")
            else:
                print_error(f"YAML inválido: {result.stderr[:200]}")

except Exception as e:
    print_warn(f"Validação docker-compose falhou: {e}")

# ============================================================================
# 6. Resumo e Recomendações
# ============================================================================

print_header("📋 RESUMO DA VALIDAÇÃO")

print("""
✅ Componentes Principais:
  1. MCP STDIO Server (JSON-RPC stdin/stdout) - Para VS Code/IDE
  2. MCP HTTP Server (Streamable HTTP) - Para APIs e remoto
  3. OpenAPI Adapter - Para documentação e testes
  4. Dockerfile.mcp - Para Docker container
  5. docker-compose.yml - Para orquestração

🚀 Como Usar:

1️⃣  LOCAL - STDIO (Recomendado para Dev)
   Configure em VS Code (mcp.json):
   {
     "servers": {
       "senior-docs": {
         "type": "stdio",
         "command": "python",
         "args": ["apps/mcp-server/mcp_server.py"]
       }
     }
   }

2️⃣  LOCAL - HTTP Server
   Terminal 1: python apps/mcp-server/mcp_server_http.py
   Terminal 2: curl -X POST http://localhost:8000/mcp \\
     -H "Content-Type: application/json" \\
     -d '{
       "jsonrpc":"2.0",
       "id":1,
       "method":"initialize",
       "params":{}
     }'

3️⃣  LOCAL - OpenAPI
   Terminal 1: python apps/mcp-server/openapi_adapter.py
   Browser: http://localhost:8000/docs

4️⃣  DOCKER - Dual-Mode
   docker-compose up mcp-server
   # Ambos MCP + HTTP rodam juntos

📝 Protocolo JSON-RPC:
   - STDIO: Linhas JSON via stdin/stdout (simples, eficiente)
   - HTTP: POST com JSON body (conforme spec MCP official)
   - OpenAPI: FastAPI com Swagger/ReDoc

✨ Próximas Etapas:
   [ ] Fazer commit dos novos servidores
   [ ] Testar comunicação STDIO no VS Code
   [ ] Testar HTTP com curl/Postman
   [ ] Fazer docker-compose up para verificar integração
   [ ] Configurar no VS Code mcp.json final
""")

print_success("Validação concluída!")
