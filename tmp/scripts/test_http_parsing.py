#!/usr/bin/env python3
"""Test HTTP parsing"""

import requests
import json

# Test with explicit JSON
print("Test 1: Explicit JSON payload")
payload = json.dumps({
    "tool": "search_docs",
    "params": {
        "query": "Impostos"
    }
})
print(f"Payload: {payload}")

r = requests.post(
    "http://localhost:8000/call",
    data=payload,
    headers={"Content-Type": "application/json"}
)
print(f"Response: {r.text}\n")

# Test 2: Using json parameter
print("Test 2: Using requests.post json parameter")
r = requests.post(
    "http://localhost:8000/call",
    json={
        "tool": "search_docs",
        "params": {
            "query": "Impostos"
        }
    }
)
print(f"Response: {r.text}\n")

# Test 3: Minimal params
print("Test 3: Minimal params")
r = requests.post(
    "http://localhost:8000/call",
    json={
        "tool": "search_docs",
        "params": {"query": "test"}
    }
)
print(f"Response: {r.text}")
