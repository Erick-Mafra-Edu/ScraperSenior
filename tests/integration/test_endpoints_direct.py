#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste direto dos endpoints do MCP Server
"""

import requests
import json

print("\n" + "="*80)
print("🧪 TESTE DIRETO DOS ENDPOINTS MCP")
print("="*80 + "\n")

base_url = "http://localhost:8000"

# Teste 1: Health
print("1️⃣  GET /health\n")
try:
    r = requests.get(f"{base_url}/health")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}\n")
except Exception as e:
    print(f"   ✗ Erro: {e}\n")

# Teste 2: Stats
print("2️⃣  GET /stats\n")
try:
    r = requests.get(f"{base_url}/stats")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}\n")
except Exception as e:
    print(f"   ✗ Erro: {e}\n")

# Teste 3: Ready
print("3️⃣  GET /ready\n")
try:
    r = requests.get(f"{base_url}/ready")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}\n")
except Exception as e:
    print(f"   ✗ Erro: {e}\n")

# Teste 4: Tools
print("4️⃣  GET /tools\n")
try:
    r = requests.get(f"{base_url}/tools")
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        tools = r.json()
        print(f"   Ferramentas disponíveis: {len(tools)}")
        for tool in tools:
            print(f"      • {tool.get('name', 'N/A')}")
    else:
        print(f"   Response: {r.text}")
    print()
except Exception as e:
    print(f"   ✗ Erro: {e}\n")

# Teste 5: Search (POST)
print("5️⃣  POST /search\n")
try:
    r = requests.post(f"{base_url}/search", json={"query": "versão"})
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.text[:500]}\n")
except Exception as e:
    print(f"   ✗ Erro: {e}\n")

# Teste 6: Call (POST)
print("6️⃣  POST /call - search_senior_docs\n")
try:
    r = requests.post(f"{base_url}/call", json={
        "tool": "search_senior_docs",
        "arguments": {"query": "Gestão"}
    })
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        result = r.json()
        print(f"   Results: {len(result.get('results', []))} encontrados")
        for res in result.get('results', [])[:3]:
            print(f"      • {res.get('title', 'N/A')}")
    else:
        print(f"   Response: {r.text[:500]}")
    print()
except Exception as e:
    print(f"   ✗ Erro: {e}\n")

print("="*80)
