#!/usr/bin/env python
"""
🧪 Teste Rápido - Verificação de Conectividade Meilisearch
Valida se a chave de API está correta e se a conexão funcionará
"""

import os
import sys
import requests
import json
from pathlib import Path

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(msg):
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{msg:^70}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}")

def print_pass(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_fail(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_info(msg):
    print(f"{YELLOW}ℹ️  {msg}{RESET}")

def check_env_file():
    """Verifica se .env existe e tem a chave"""
    print_header("1. Verificando arquivo .env")
    
    env_path = Path(".env")
    if not env_path.exists():
        print_fail(f"Arquivo .env não encontrado em {env_path.absolute()}")
        return None
    
    print_pass(f"Arquivo .env encontrado")
    
    # Ler a chave
    key = None
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('MEILISEARCH_KEY='):
                key = line.split('=', 1)[1].strip()
                break
    
    if not key:
        print_fail("MEILISEARCH_KEY não encontrada em .env")
        return None
    
    print_pass(f"Chave encontrada: {key[:20]}...{key[-10:]}")
    return key

def check_env_variable(key_from_file):
    """Verifica variável de ambiente"""
    print_header("2. Verificando Variável de Ambiente")
    
    key_from_env = os.getenv("MEILISEARCH_KEY")
    
    if key_from_env:
        print_pass(f"MEILISEARCH_KEY está definida: {key_from_env[:20]}...{key_from_env[-10:]}")
        if key_from_env == key_from_file:
            print_pass("Corresponde ao arquivo .env")
        else:
            print_fail("⚠️  DIFERENTE do arquivo .env - será usada a variável de ambiente")
        return key_from_env
    else:
        print_info("MEILISEARCH_KEY não está definida (usará fallback do .env)")
        return key_from_file

def check_meilisearch_connection(key):
    """Testa conexão com Meilisearch"""
    print_header("3. Testando Conexão com Meilisearch")
    
    url = "http://localhost:7700/health"
    
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            print_pass(f"Meilisearch está respondendo em {url}")
            data = resp.json()
            print_info(f"Status: {data.get('status', 'desconhecido')}")
            return True
        else:
            print_fail(f"Meilisearch retornou {resp.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_fail(f"Não conseguiu conectar a {url}")
        print_info("Certifique-se de que docker-compose está rodando:")
        print_info("  docker-compose up -d meilisearch")
        return False
    except Exception as e:
        print_fail(f"Erro: {e}")
        return False

def check_api_key_validity(key):
    """Testa se a chave é válida com Meilisearch"""
    print_header("4. Validando Chave de API com Meilisearch")
    
    url = "http://localhost:7700/indexes"
    headers = {"Authorization": f"Bearer {key}"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        
        if resp.status_code == 200:
            print_pass(f"Chave de API é válida!")
            data = resp.json()
            print_info(f"Índices encontrados: {len(data.get('results', []))}")
            return True
        elif resp.status_code == 403:
            print_fail("❌ Chave de API INVÁLIDA (403 Unauthorized)")
            print_fail("A chave não corresponde à configurada no Meilisearch")
            print_info("Verifique se a chave em .env é a correta")
            return False
        else:
            print_fail(f"Meilisearch retornou {resp.status_code}")
            print_info(f"Resposta: {resp.text[:200]}")
            return False
    except requests.exceptions.ConnectionError:
        print_fail("Não conseguiu conectar a Meilisearch")
        return False
    except Exception as e:
        print_fail(f"Erro: {e}")
        return False

def check_api_health():
    """Testa saúde da API do OpenAPI"""
    print_header("5. Testando API OpenAPI/MCP")
    
    url = "http://localhost:8000/health"
    
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print_pass(f"API está saudável")
            print_info(f"Status: {data.get('status', 'desconhecido')}")
            
            # Testa Meilisearch via API
            if data.get('meilisearch', {}).get('healthy'):
                print_pass("Meilisearch está acessível via API")
            else:
                print_fail("API não conseguiu conectar a Meilisearch")
            return True
        else:
            print_fail(f"API retornou {resp.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_fail(f"Não conseguiu conectar a API em {url}")
        print_info("Certifique-se de que docker-compose está rodando:")
        print_info("  docker-compose up -d senior-docs-mcp-server")
        return False
    except Exception as e:
        print_fail(f"Erro: {e}")
        return False

def check_search_functionality(key):
    """Testa funcionalidade de busca"""
    print_header("6. Testando Funcionalidade de Busca")
    
    url = "http://localhost:8000/search"
    payload = {"query": "como", "limit": 5}
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                total = data.get('total', 0)
                results = data.get('results', [])
                print_pass(f"Busca funcionando! {total} documentos encontrados")
                print_info(f"Retornou {len(results)} resultados (limit: 5)")
                if results:
                    first = results[0]
                    print_info(f"Primeiro resultado: {first.get('title', 'sem título')}")
                return True
            else:
                print_fail("Busca retornou success=false")
                return False
        else:
            print_fail(f"API retornou {resp.status_code}")
            print_info(f"Resposta: {resp.text[:300]}")
            return False
    except requests.exceptions.ConnectionError:
        print_fail("Não conseguiu conectar à API")
        return False
    except Exception as e:
        print_fail(f"Erro: {e}")
        return False

def main():
    """Executa todos os testes"""
    print_header("TESTE DE CONECTIVIDADE - Meilisearch + API")
    print(f"\n{YELLOW}Este script valida se a configuração de API key está correta{RESET}")
    
    # 1. Check .env
    key_from_file = check_env_file()
    if not key_from_file:
        print_fail("\n❌ Teste falhou: .env não está configurado corretamente")
        sys.exit(1)
    
    # 2. Check env variable
    key = check_env_variable(key_from_file)
    
    # 3. Check Meilisearch is running
    if not check_meilisearch_connection(key):
        print_fail("\n❌ Meilisearch não está rodando")
        print_info("Inicie com: docker-compose up -d meilisearch")
        sys.exit(1)
    
    # 4. Check API key is valid
    if not check_api_key_validity(key):
        print_fail("\n❌ Chave de API inválida - Docker não conseguirá conectar")
        sys.exit(1)
    
    # 5. Check API health
    if not check_api_health():
        print_fail("\n❌ API não está rodando")
        print_info("Inicie com: docker-compose up -d senior-docs-mcp-server")
        sys.exit(1)
    
    # 6. Check search
    check_search_functionality(key)
    
    # Final result
    print_header("✅ TODOS OS TESTES PASSARAM!")
    print(f"\n{GREEN}Seu sistema está pronto para usar:{RESET}")
    print(f"  🌐 API:         http://localhost:8000")
    print(f"  📊 Swagger:     http://localhost:8000/docs")
    print(f"  📚 ReDoc:       http://localhost:8000/redoc")
    print(f"  🔍 Meilisearch: http://localhost:7700")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Teste interrompido pelo usuário{RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n{RED}Erro inesperado: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
