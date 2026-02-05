#!/usr/bin/env python3
"""
Deploy script to pull changes and restart MCP server on people-fy.com

This will:
1. SSH into people-fy.com
2. Pull latest code
3. Kill old MCP server process
4. Start new MCP server in background
"""

import subprocess
import sys
import time

SERVER = "administrator@people-fy.com"
PROJECT_PATH = "ScraperSenior"

commands = [
    # Pull latest code
    f"cd {PROJECT_PATH} && git pull --rebase",
    
    # Kill existing MCP server processes
    "pkill -f 'python.*mcp_server_http' || true",
    
    # Wait a moment
    "sleep 2",
    
    # Start MCP server in background (nohup so it persists after disconnect)
    f"cd {PROJECT_PATH} && nohup python apps/mcp-server/mcp_server_http.py > /tmp/mcp_server.log 2>&1 &",
    
    # Give it time to start
    "sleep 3",
    
    # Check if it's running
    "ps aux | grep -E 'mcp_server_http|uvicorn' | grep -v grep",
]

print("=" * 80)
print("Deploying MCP Server Updates")
print("=" * 80)

full_command = " && ".join(commands)

try:
    result = subprocess.run(
        ["ssh", SERVER, full_command],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("\n✓ Deployment successful!")
    else:
        print(f"\n✗ Deployment failed with code {result.returncode}")
        sys.exit(1)
        
except subprocess.TimeoutExpired:
    print("✗ Command timed out")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("Testing new server...")
print("=" * 80)

# Wait a bit more for server to fully start
time.sleep(2)

# Test with a simple query
import requests
import json

test_payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "search_docs",
        "arguments": {
            "query": "funcoes lsp",
            "limit": 5,
            "query_strategy": "auto"
        }
    }
}

try:
    response = requests.post(
        'http://people-fy.com:8000/mcp',
        json=test_payload,
        headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
        stream=True,
        timeout=5
    )
    
    if response.status_code == 200:
        line = next(response.iter_lines())
        json_str = line.decode().replace('data: ', '')
        result = json.loads(json_str)
        
        text = result['result']['text']
        docs = json.loads(text)
        
        print(f"\nTest Query: 'funcoes lsp'")
        print(f"Results: {docs.get('count', 0)} encontrados")
        print(f"Parsed Query: {docs.get('parsed_query', 'N/A')}")
        
        if docs.get('count', 0) > 0:
            print("✓ Server responding correctly with parsed queries!")
        else:
            print("Note: Query still returned 0 results (Meilisearch limitation)")
    else:
        print(f"✗ Server returned {response.status_code}")
        
except Exception as e:
    print(f"✗ Test failed: {e}")
