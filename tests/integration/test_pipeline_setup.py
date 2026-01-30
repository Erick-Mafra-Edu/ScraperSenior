#!/usr/bin/env python3
"""
Teste rapido do pipeline unificado
Valida todos os componentes antes do Docker
"""

import sys
import subprocess
from pathlib import Path


def test_imports():
    """Testa se todas as dependencias estao instaladas"""
    print("[*] Testando importacoes...")
    
    deps = [
        'aiohttp',
        'meilisearch',
        'requests',
        'bs4',
        'playwright'
    ]
    
    missing = []
    for dep in deps:
        try:
            __import__(dep)
            print(f"   [OK] {dep}")
        except ImportError:
            print(f"   [ERROR] {dep} nao instalado")
            missing.append(dep)
    
    if missing:
        print(f"\n[!] Instalando dependencias faltantes: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
    
    return True


def test_files_exist():
    """Testa se arquivos necessarios existem"""
    print(f"\n[*] Verificando arquivos necessarios...")
    
    files = [
        'src/scraper_modular.py',
        'src/api_zendesk.py',
        'src/zendesk_modular_adapter.py',
        'scraper_config.json',
        'scrape_and_index_all.py',
        'docker_entrypoint.py',
        'Dockerfile',
        'docker-compose.yml',
        'docs_estruturado'
    ]
    
    missing = []
    for file in files:
        if Path(file).exists():
            print(f"   [OK] {file}")
        else:
            print(f"   [!] {file} nao encontrado")
            missing.append(file)
    
    return len(missing) == 0


def test_meilisearch_connection():
    """Testa conexao com Meilisearch"""
    print(f"\n[*] Testando conexao com Meilisearch...")
    
    try:
        import requests
        resp = requests.get("http://localhost:7700/health", timeout=5)
        
        if resp.status_code == 200:
            print(f"   [OK] Meilisearch respondendo em http://localhost:7700")
            return True
        else:
            print(f"   [!] Meilisearch respondeu com status {resp.status_code}")
            return False
    except Exception as e:
        print(f"   [!] Meilisearch nao esta disponivel: {e}")
        print(f"       Inicie com: docker-compose up -d")
        return False


def test_scraper_config():
    """Testa se configuracao do scraper eh valida"""
    print(f"\n[*] Testando configuracao do scraper...")
    
    try:
        import json
        with open('scraper_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"   [OK] scraper_config.json valido")
        print(f"       Secoes: {', '.join(config.keys())}")
        return True
    except Exception as e:
        print(f"   [ERROR] Erro ao ler scraper_config.json: {e}")
        return False


def test_docker_compose():
    """Testa se docker-compose.yml eh valido"""
    print(f"\n[*] Testando docker-compose.yml...")
    
    try:
        result = subprocess.run(
            ["docker-compose", "config"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"   [OK] docker-compose.yml valido")
            return True
        else:
            print(f"   [ERROR] docker-compose.yml invalido:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"   [!] docker-compose nao disponivel: {e}")
        print(f"       Instale com: pip install docker-compose")
        return False


def test_docker():
    """Testa se Docker esta disponivel"""
    print(f"\n[*] Testando Docker...")
    
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"   [OK] {result.stdout.strip()}")
            return True
        else:
            print(f"   [ERROR] Docker nao respondeu")
            return False
    except Exception as e:
        print(f"   [!] Docker nao esta instalado: {e}")
        return False


def main():
    """Executa todos os testes"""
    print(f"\n{'='*80}")
    print("TESTE RAPIDO - PIPELINE UNIFICADO")
    print(f"{'='*80}\n")
    
    tests = [
        ("Importacoes", test_imports),
        ("Arquivos necessarios", test_files_exist),
        ("Configuracao scraper", test_scraper_config),
        ("Docker", test_docker),
        ("Docker Compose", test_docker_compose),
        ("Meilisearch (opcional)", test_meilisearch_connection),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            result = test_func()
            results[name] = result
        except Exception as e:
            print(f"   [ERROR] {e}")
            results[name] = False
    
    # Resumo
    print(f"\n{'='*80}")
    print("RESUMO DOS TESTES")
    print(f"{'='*80}\n")
    
    for name, result in results.items():
        status = "[OK]" if result else "[!]"
        print(f"{status} {name}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} testes passaram\n")
    
    if passed == total:
        print("[OK] Sistema pronto! Use:")
        print(f"    docker-compose up -d")
        return 0
    else:
        print("[!] Alguns testes falharam. Corrija os erros acima.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
