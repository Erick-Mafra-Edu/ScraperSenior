#!/usr/bin/env python3
"""
Test Docker Auto-Indexing
===========================
Valida que os documentos foram indexados automaticamente
e que o MCP Server está servindo dados corretamente
"""

import requests
import time
import json
from datetime import datetime


def test_meilisearch_health():
    """Testa healthcheck do Meilisearch"""
    print("\n[TEST 1] Meilisearch Health Check...")
    
    try:
        response = requests.get("http://localhost:7700/health", timeout=5)
        
        if response.status_code == 200:
            print("    [OK] Meilisearch is healthy")
            return True
        else:
            print(f"    [FAIL] Status {response.status_code}")
            return False
    
    except Exception as e:
        print(f"    [FAIL] {e}")
        return False


def test_index_exists():
    """Testa se o índice 'documentation' foi criado"""
    print("\n[TEST 2] Index Existence...")
    
    try:
        headers = {"Authorization": "Bearer meilisearch_master_key_change_me"}
        response = requests.get(
            "http://localhost:7700/indexes/documentation",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            doc_count = data.get("numberOfDocuments", 0)
            print(f"    [OK] Index 'documentation' exists with {doc_count} documents")
            return True
        else:
            print(f"    [FAIL] Status {response.status_code}")
            return False
    
    except Exception as e:
        print(f"    [FAIL] {e}")
        return False


def test_document_count():
    """Testa a contagem de documentos"""
    print("\n[TEST 3] Document Count...")
    
    try:
        headers = {"Authorization": "Bearer meilisearch_master_key_change_me"}
        response = requests.get(
            "http://localhost:7700/indexes/documentation",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            doc_count = data.get("numberOfDocuments", 0)
            
            if doc_count >= 3:  # Mínimo esperado
                print(f"    [OK] {doc_count} documents indexed (>= 3)")
                return True
            else:
                print(f"    [FAIL] Only {doc_count} documents (expected >= 3)")
                return False
    
    except Exception as e:
        print(f"    [FAIL] {e}")
        return False


def test_search_query():
    """Testa uma busca no índice"""
    print("\n[TEST 4] Search Query...")
    
    try:
        headers = {"Authorization": "Bearer meilisearch_master_key_change_me"}
        response = requests.post(
            "http://localhost:7700/indexes/documentation/search",
            json={"q": ""},  # Query vazia retorna todos
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            hits = data.get("hits", [])
            
            if len(hits) > 0:
                print(f"    [OK] Search returned {len(hits)} results")
                print(f"         First result: {hits[0].get('title', 'N/A')}")
                return True
            else:
                print(f"    [FAIL] No results returned")
                return False
    
    except Exception as e:
        print(f"    [FAIL] {e}")
        return False


def test_mcp_server_health():
    """Testa healthcheck do MCP Server"""
    print("\n[TEST 5] MCP Server Health Check...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        
        if response.status_code == 200:
            print("    [OK] MCP Server is healthy")
            return True
        else:
            print(f"    [FAIL] Status {response.status_code}")
            return False
    
    except Exception as e:
        print(f"    [FAIL] {e}")
        return False


def test_mcp_modules():
    """Testa se MCP Server retorna módulos"""
    print("\n[TEST 6] MCP Server Modules...")
    
    try:
        response = requests.get("http://localhost:8000/modules", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                print(f"    [OK] MCP Server returned {len(data)} modules")
                print(f"         Modules: {', '.join([m.get('name', 'unknown') for m in data[:3]])}")
                return True
            else:
                print(f"    [FAIL] No modules returned or empty list")
                return False
        else:
            print(f"    [FAIL] Status {response.status_code}")
            return False
    
    except Exception as e:
        print(f"    [FAIL] {e}")
        return False


def test_mcp_search():
    """Testa busca via MCP Server"""
    print("\n[TEST 7] MCP Server Search...")
    
    try:
        response = requests.get(
            "http://localhost:8000/search",
            params={"q": "documentation"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, dict):
                results = data.get("results", [])
                print(f"    [OK] Search via MCP returned {len(results)} results")
                return True
            else:
                print(f"    [FAIL] Unexpected response format")
                return False
        else:
            print(f"    [FAIL] Status {response.status_code}")
            return False
    
    except Exception as e:
        print(f"    [FAIL] {e}")
        return False


def main():
    """Executa todos os testes"""
    
    print("="*70)
    print("DOCKER AUTO-INDEXING VALIDATION TESTS")
    print("="*70)
    
    # Aguarda um pouco para o servidor inicializar
    print("\n[*] Aguardando servidores iniciarem...")
    time.sleep(5)
    
    tests = [
        ("Meilisearch Health", test_meilisearch_health),
        ("Index Exists", test_index_exists),
        ("Document Count", test_document_count),
        ("Search Query", test_search_query),
        ("MCP Server Health", test_mcp_server_health),
        ("MCP Server Modules", test_mcp_modules),
        ("MCP Server Search", test_mcp_search),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n[ERROR] Unexpected error in {test_name}: {e}")
            results[test_name] = False
    
    # Resumo
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({100*passed//total}%)")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! Docker auto-indexing is working correctly.")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Check the output above.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
