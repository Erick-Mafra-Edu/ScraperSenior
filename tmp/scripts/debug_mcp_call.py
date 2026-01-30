#!/usr/bin/env python3
"""Debug MCP call endpoint"""

import requests
import json

# Test 1: search_docs with query
print("Test 1: search_docs with query")
payload = {
    "tool": "search_docs",
    "params": {"query": "HCM"}
}
r = requests.post("http://localhost:8000/call", json=payload)
print(f"  Status: {r.status_code}")
response = r.json()
print(f"  Response: {json.dumps(response, indent=2, ensure_ascii=False)[:300]}")

# Test 2: get_stats
print("\nTest 2: get_stats")
payload = {
    "tool": "get_stats",
    "params": {}
}
r = requests.post("http://localhost:8000/call", json=payload)
print(f"  Status: {r.status_code}")
response = r.json()
print(f"  Response: {json.dumps(response, indent=2, ensure_ascii=False)}")

# Test 3: list_modules
print("\nTest 3: list_modules")
payload = {
    "tool": "list_modules",
    "params": {}
}
r = requests.post("http://localhost:8000/call", json=payload)
print(f"  Status: {r.status_code}")
response = r.json()
print(f"  Response: {json.dumps(response, indent=2, ensure_ascii=False)[:300]}")
