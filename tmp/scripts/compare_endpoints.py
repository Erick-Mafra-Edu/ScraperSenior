#!/usr/bin/env python3
"""Compare /search vs /call endpoints"""

import requests
import json

print("=" * 80)
print("COMPARACAO /search vs /call")
print("=" * 80)

# Test 1: /search (funciona)
print("\n1. POST /search (REST endpoint - FUNCIONA)")
payload = {"query": "Impostos", "limit": 2}
r = requests.post("http://localhost:8000/search", json=payload)
data = r.json()
print(f"   Status: {r.status_code}")
print(f"   Resultados: {data.get('count', 0)}")

# Test 2: /call com search_docs (NAO funciona)
print("\n2. POST /call com search_docs (MCP endpoint - NAO FUNCIONA)")
payload = {
    "tool": "search_docs",
    "params": {"query": "Impostos", "limit": 2}
}
r = requests.post("http://localhost:8000/call", json=payload)
data = r.json()
print(f"   Status: {r.status_code}")
print(f"   Response: {json.dumps(data, indent=2, ensure_ascii=False)}")

# Test 3: /call com list_modules (FUNCIONA)
print("\n3. POST /call com list_modules (MCP endpoint - FUNCIONA)")
payload = {
    "tool": "list_modules",
    "params": {}
}
r = requests.post("http://localhost:8000/call", json=payload)
data = r.json()
print(f"   Status: {r.status_code}")
print(f"   Modules: {len(data.get('modules', []))}")
