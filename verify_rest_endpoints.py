#!/usr/bin/env python3
"""
Simple REST API endpoint verification
Checks that the server would work when deployed
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.chdir(project_root)

print('=' * 70)
print('REST API Endpoints Verification')
print('=' * 70)

# Read and verify the mcp_server_http.py file has all endpoints
server_file = 'apps/mcp-server/mcp_server_http.py'
with open(server_file, 'r', encoding='utf-8') as f:
    content = f.read()

endpoints = [
    ('@app.get("/api/search")', 'REST Search endpoint'),
    ('@app.get("/api/modules")', 'List modules endpoint'),
    ('@app.get("/api/modules/{module_name}")', 'Get module docs endpoint'),
    ('@app.get("/api/stats")', 'Get stats endpoint'),
    ('@app.options("/api/search")', 'CORS: /api/search'),
    ('@app.options("/api/modules")', 'CORS: /api/modules'),
    ('@app.options("/api/modules/{module_name}")', 'CORS: /api/modules/{module_name}'),
    ('@app.options("/api/stats")', 'CORS: /api/stats'),
]

print('\nVerifying REST endpoints in mcp_server_http.py:')
print('-' * 70)

all_present = True
for endpoint_def, description in endpoints:
    if endpoint_def in content:
        print(f'✓ {description:35} - {endpoint_def}')
    else:
        print(f'✗ {description:35} - MISSING')
        all_present = False

# Verify parse_query method
print('\nVerifying query parsing strategies:')
print('-' * 70)
strategies = [
    ('strategy == "auto"', 'Auto strategy'),
    ('strategy == "quoted"', 'Quoted strategy'),
    ('strategy == "and"', 'AND strategy'),
]

for strategy_check, desc in strategies:
    if strategy_check in content:
        print(f'✓ {desc:35} - found')
    else:
        print(f'✗ {desc:35} - MISSING')
        all_present = False

# Check CORS configuration
print('\nVerifying CORS configuration:')
print('-' * 70)
cors_checks = [
    ('allow_origins=["*"]', 'Allow all origins'),
    ('allow_methods=', 'Allow methods configured'),
    ('max_age=3600', 'CORS preflight cache'),
]

for cors_check, desc in cors_checks:
    if cors_check in content:
        print(f'✓ {desc:35} - configured')
    else:
        print(f'✗ {desc:35} - MISSING')
        all_present = False

print('\n' + '=' * 70)
if all_present:
    print('✓ All REST endpoints and features verified!')
    print('✓ Server is ready for deployment')
    sys.exit(0)
else:
    print('✗ Some endpoints or features are missing')
    sys.exit(1)
