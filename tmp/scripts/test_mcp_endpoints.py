#!/usr/bin/env python3
"""Test MCP Server endpoints"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("="*80)
print("TESTE DE ENDPOINTS MCP")
print("="*80)

# Test 1: Health check
print("\n1. Health Check")
try:
    r = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {r.status_code}")
    print(f"   {json.dumps(r.json(), indent=2)}")
except Exception as e:
    print(f"   Erro: {e}")

# Test 2: Tools list
print("\n2. Ferramentas Disponíveis")
try:
    r = requests.get(f"{BASE_URL}/tools")
    data = r.json()
    print(f"   {json.dumps(data, indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"   Erro: {e}")

# Test 3: Search with REST endpoint
print("\n3. REST Search - 'Impostos'")
try:
    payload = {"query": "Impostos", "limit": 3}
    r = requests.post(f"{BASE_URL}/search", json=payload)
    data = r.json()
    print(f"   Status: {r.status_code}")
    print(f"   Resultados encontrados: {len(data.get('results', []))}")
    for i, doc in enumerate(data.get('results', [])[:2], 1):
        print(f"\n   {i}. {doc.get('title', 'N/A')[:70]}")
        print(f"      Fonte: {doc.get('source', 'N/A')}")
        print(f"      Módulo: {doc.get('module', 'N/A')}")
except Exception as e:
    print(f"   Erro: {e}")

# Test 4: Search with MCP /call endpoint
print("\n4. MCP Tool Call - search_docs")
try:
    payload = {
        "tool": "search_docs",
        "params": {
            "query": "HCM Impostos",
            "limit": 3
        }
    }
    r = requests.post(f"{BASE_URL}/call", json=payload)
    data = r.json()
    print(f"   Status: {r.status_code}")
    if "error" in data:
        print(f"   Erro: {data['error']}")
    else:
        results = data.get('result', {}).get('results', [])
        print(f"   Resultados encontrados: {len(results)}")
        for i, doc in enumerate(results[:2], 1):
            print(f"\n   {i}. {doc.get('title', 'N/A')[:70]}")
            print(f"      Fonte: {doc.get('source', 'N/A')}")
except Exception as e:
    print(f"   Erro: {e}")

# Test 5: Get available modules
print("\n5. Módulos Disponíveis")
try:
    payload = {
        "tool": "list_modules",
        "params": {}
    }
    r = requests.post(f"{BASE_URL}/call", json=payload)
    data = r.json()
    modules = data.get('result', {}).get('modules', [])
    print(f"   Total de módulos: {len(modules)}")
    for mod in modules[:5]:
        print(f"   - {mod}")
    if len(modules) > 5:
        print(f"   ... e mais {len(modules) - 5}")
except Exception as e:
    print(f"   Erro: {e}")

# Test 6: Get stats
print("\n6. Estatísticas")
try:
    payload = {
        "tool": "get_stats",
        "params": {}
    }
    r = requests.post(f"{BASE_URL}/call", json=payload)
    data = r.json()
    stats = data.get('result', {})
    print(f"   {json.dumps(stats, indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"   Erro: {e}")

print("\n" + "="*80)
