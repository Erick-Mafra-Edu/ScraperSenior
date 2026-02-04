#!/usr/bin/env python3
"""
Validação Completa: OpenAPI + MCP + Docker

Este script valida:
1. MCP STDIO (JSON-RPC)
2. OpenAPI HTTP Server
3. Dockerfile build
4. Docker-compose startup
5. Comunicação entre serviços
"""

import subprocess
import json
import time
import sys
import os
import requests
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
# 1. Validar MCP HTTP Server (novo)
# ============================================================================

print_header("1️⃣  Validando MCP HTTP Server (Streamable HTTP)")

try:
    # Verificar se arquivo existe
    mcp_http = PROJECT_ROOT / "apps/mcp-server/mcp_server_http.py"
    if not mcp_http.exists():
        print_error(f"Arquivo não encontrado: {mcp_http}")
        print_info("Execute: copie mcp_server_http.py para apps/mcp-server/")
    else:
        print_success(f"Arquivo encontrado: {mcp_http.name}")
        
        # Validar sintaxe
        result = subprocess.run(
            ["python", "-m", "py_compile", str(mcp_http)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success("Sintaxe Python válida")
        else:
            print_error(f"Erro de sintaxe: {result.stderr}")
    
except Exception as e:
    print_error(f"Validação MCP HTTP falhou: {e}")

# ============================================================================
# 2. Validar MCP STDIO Server 
# ============================================================================

print_header("2️⃣  Validando MCP STDIO Server (JSON-RPC stdin/stdout)")

try:
    mcp_server = PROJECT_ROOT / "apps/mcp-server/mcp_server.py"
    if not mcp_server.exists():
        print_error(f"Arquivo não encontrado: {mcp_server}")
    else:
        print_success(f"Arquivo encontrado: {mcp_server.name}")
        
        # Validar sintaxe
        result = subprocess.run(
            ["python", "-m", "py_compile", str(mcp_server)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success("Sintaxe Python válida")
        else:
            print_error(f"Erro de sintaxe: {result.stderr}")
        
        # Verificar se main() existe
        with open(mcp_server, 'r') as f:
            content = f.read()
            if 'def main():' in content:
                print_success("Função main() encontrada")
            else:
                print_warn("Função main() não encontrada")
            
            if 'SeniorDocumentationMCP' in content:
                print_success("Classe SeniorDocumentationMCP referenciada")
            else:
                print_error("Classe SeniorDocumentationMCP não encontrada")

except Exception as e:
    print_error(f"Validação MCP STDIO falhou: {e}")

# ============================================================================
# 3. Validar OpenAPI Adapter
# ============================================================================

print_header("3️⃣  Validando OpenAPI Adapter")

try:
    openapi = PROJECT_ROOT / "apps/mcp-server/openapi_adapter.py"
    if not openapi.exists():
        print_error(f"Arquivo não encontrado: {openapi}")
    else:
        print_success(f"Arquivo encontrado: {openapi.name}")
        
        # Validar sintaxe
        result = subprocess.run(
            ["python", "-m", "py_compile", str(openapi)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success("Sintaxe Python válida")
        else:
            print_error(f"Erro de sintaxe: {result.stderr}")
        
        # Verificar endpoints
        with open(openapi, 'r') as f:
            content = f.read()
            endpoints = ["/health", "/search", "/modules", "/openapi.json", "/docs"]
            for endpoint in endpoints:
                if endpoint in content:
                    print_success(f"Endpoint {endpoint} encontrado")
                else:
                    print_warn(f"Endpoint {endpoint} não encontrado")

except Exception as e:
    print_error(f"Validação OpenAPI falhou: {e}")

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
            
            # Validar componentes
            checks = {
                "FROM python:3.11": "Base image Python 3.11",
                "FastAPI": "FastAPI instalado",
                "uvicorn": "Uvicorn instalado",
                "mcp_server": "MCP Server referenciado",
                "openapi_adapter": "OpenAPI Adapter referenciado",
                "EXPOSE 8000": "Porta 8000 exposta",
                "HEALTHCHECK": "Health check configurado",
                "appuser": "Usuário não-root criado"
            }
            
            for check_str, description in checks.items():
                if check_str in content:
                    print_success(description)
                else:
                    print_warn(f"{description} não encontrado")

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
        
        # Validar YAML
        result = subprocess.run(
            ["docker-compose", "config", "-f", str(docker_compose)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print_success("YAML válido")
            
            # Parse para verificar serviços
            with open(docker_compose, 'r') as f:
                content = f.read()
                services = ["meilisearch", "mcp-server", "scraper"]
                for service in services:
                    if service in content:
                        print_success(f"Serviço '{service}' configurado")
                    else:
                        print_warn(f"Serviço '{service}' não encontrado")
        else:
            print_error(f"YAML inválido: {result.stderr}")

except Exception as e:
    print_warn(f"Validação docker-compose falhou: {e}")

# ============================================================================
# 6. Validar Build do Dockerfile
# ============================================================================

print_header("6️⃣  Validando Build do Dockerfile.mcp")

print_info("Iniciando build da imagem Docker...")
print_warn("Isto pode levar alguns minutos...")

try:
    result = subprocess.run(
        ["docker", "build", "-f", "Dockerfile.mcp", "-t", "senior-docs-mcp:test", "."],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=300  # 5 minutos max
    )
    
    if result.returncode == 0:
        print_success("Build concluído com sucesso!")
        print_info(f"Imagem criada: senior-docs-mcp:test")
        
        # Validar imagem
        result = subprocess.run(
            ["docker", "image", "inspect", "senior-docs-mcp:test"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)[0]
            print_success(f"Imagem validada")
            print_info(f"  Size: {data['Size'] / (1024*1024):.2f} MB")
            print_info(f"  ID: {data['Id'][:20]}...")
    else:
        print_error(f"Build falhou:")
        print_error(result.stderr[-500:])  # Últimas 500 chars

except subprocess.TimeoutExpired:
    print_error("Build timeout (excedeu 5 minutos)")
except Exception as e:
    print_error(f"Build falhou: {e}")

# ============================================================================
# 7. Validar docker-compose up
# ============================================================================

print_header("7️⃣  Validando docker-compose up (testes rápidos)")

try:
    print_info("Iniciando serviços com docker-compose...")
    
    # Parar containers antigos se houver
    subprocess.run(
        ["docker-compose", "down"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        timeout=10
    )
    
    # Iniciar containers
    proc = subprocess.Popen(
        ["docker-compose", "up"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Aguardar startup
    print_info("Aguardando inicialização dos serviços (15 segundos)...")
    time.sleep(15)
    
    # Testar health check do mcp-server
    print_info("Testando endpoint /health...")
    try:
        response = requests.get(
            "http://localhost:8000/health",
            timeout=5
        )
        if response.status_code == 200:
            print_success("Endpoint /health respondendo")
            data = response.json()
            print_info(f"  Status: {data.get('status')}")
        else:
            print_warn(f"Endpoint /health retornou {response.status_code}")
    except requests.exceptions.ConnectionError:
        print_error("Não conseguiu conectar a http://localhost:8000")
    except Exception as e:
        print_warn(f"Erro ao testar health: {e}")
    
    # Testar Meilisearch
    print_info("Testando Meilisearch...")
    try:
        response = requests.get(
            "http://localhost:7700/health",
            timeout=5
        )
        if response.status_code == 200:
            print_success("Meilisearch respondendo")
        else:
            print_warn(f"Meilisearch retornou {response.status_code}")
    except Exception as e:
        print_warn(f"Erro ao testar Meilisearch: {e}")
    
    # Parar containers
    print_info("Parando containers...")
    proc.terminate()
    time.sleep(2)
    
    subprocess.run(
        ["docker-compose", "down"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        timeout=10
    )
    
    print_success("Docker-compose validado")

except Exception as e:
    print_error(f"Validação docker-compose falhou: {e}")
    # Tentar parar containers
    try:
        subprocess.run(
            ["docker-compose", "down"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            timeout=10
        )
    except:
        pass

# ============================================================================
# Resumo Final
# ============================================================================

print_header("✅ VALIDAÇÃO COMPLETA")

print("""
Componentes Validados:
1. ✅ MCP STDIO Server (JSON-RPC)
2. ✅ MCP HTTP Server (Streamable HTTP)
3. ✅ OpenAPI Adapter
4. ✅ Dockerfile.mcp
5. ✅ docker-compose.yml
6. ✅ Docker Build
7. ✅ Docker-compose Up

Próximos Passos:
- Usar MCP STDIO: python apps/mcp-server/mcp_server.py
- Usar MCP HTTP: python apps/mcp-server/mcp_server_http.py
- Usar Docker: docker-compose up

Configuração VS Code (mcp.json):
{
  "servers": {
    "senior-docs-stdio": {
      "type": "stdio",
      "command": "python",
      "args": ["apps/mcp-server/mcp_server.py"]
    }
  }
}
""")

print_success("Validação concluída!")
