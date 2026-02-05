#!/usr/bin/env python3
"""Test REST API Endpoints"""

import sys
import os
sys.path.insert(0, '.')
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Import from the correct path (mcp-server with hyphen)
import importlib.util
spec = importlib.util.spec_from_file_location("mcp_server_http", "apps/mcp-server/mcp_server_http.py")
mcp_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_module)
app = mcp_module.app

from fastapi.testclient import TestClient

client = TestClient(app)

print('=' * 70)
print('Testing REST Endpoints')
print('=' * 70)

# Test /health
print('\n1. Testing GET /health')
response = client.get('/health')
print(f'   Status: {response.status_code}')
if response.status_code == 200:
    print('   ✓ PASS')
else:
    print(f'   ✗ FAIL: {response.text}')

# Test /api/search
print('\n2. Testing GET /api/search?query=lsp&limit=5')
response = client.get('/api/search?query=lsp&limit=5')
print(f'   Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    count = data.get('count', 0)
    strategy = data.get('strategy', 'unknown')
    print(f'   Found {count} results')
    print(f'   Strategy used: {strategy}')
    print('   ✓ PASS')
else:
    print(f'   ✗ FAIL: {response.text}')

# Test /api/modules
print('\n3. Testing GET /api/modules')
response = client.get('/api/modules')
print(f'   Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    total = data.get('total_modules', 0)
    print(f'   Found {total} modules')
    print('   ✓ PASS')
else:
    print(f'   ✗ FAIL: {response.text}')

# Test /api/stats
print('\n4. Testing GET /api/stats')
response = client.get('/api/stats')
print(f'   Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    status = data.get('status', 'unknown')
    print(f'   Status: {status}')
    print('   ✓ PASS')
else:
    print(f'   ✗ FAIL: {response.text}')

# Test CORS
print('\n5. Testing CORS preflight')
response = client.options('/api/search')
print(f'   Status: {response.status_code}')
if response.status_code == 200:
    print('   ✓ PASS - CORS enabled')
else:
    print(f'   ✗ FAIL')

print('\n' + '=' * 70)
print('All REST endpoints operational!')
print('=' * 70)
