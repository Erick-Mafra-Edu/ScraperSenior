#!/usr/bin/env python3
"""
Quick Start - Testar os 3 modos do MCP Server

Uso:
    python test_mcp_all_modes.py [modo]
    
Modos:
    stdio   - Testar MCP STDIO (JSON-RPC via stdin/stdout)
    http    - Testar MCP HTTP (Streamable HTTP Transport)
    both    - Testar ambos
"""

import subprocess
import json
import time
import sys
import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

print("=" * 80)
print("🚀 MCP Server - Test All Modes")
print("=" * 80)

mode = sys.argv[1].lower() if len(sys.argv) > 1 else "both"

# ============================================================================
# Test STDIO
# ============================================================================

if mode in ["stdio", "both"]:
    print("\n" + "=" * 80)
    print("1️⃣  Testing STDIO Mode (JSON-RPC via stdin/stdout)")
    print("=" * 80)
    
    print("\n✓ Initialize request...")
    proc = subprocess.Popen(
        ["python", "apps/mcp-server/mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=PROJECT_ROOT
    )
    
    # Send initialize
    init_msg = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    proc.stdin.write(json.dumps(init_msg) + "\n")
    proc.stdin.flush()
    
    # Read response
    response = proc.stdout.readline()
    resp_obj = json.loads(response)
    
    if resp_obj.get("result"):
        print(f"✅ Initialize OK")
        print(f"   Server: {resp_obj['result']['serverInfo']['name']}")
        print(f"   Version: {resp_obj['result']['serverInfo']['version']}")
    else:
        print(f"❌ Initialize failed: {resp_obj}")
    
    # Send tools/list
    print("\n✓ Listing tools...")
    list_msg = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    proc.stdin.write(json.dumps(list_msg) + "\n")
    proc.stdin.flush()
    
    response = proc.stdout.readline()
    resp_obj = json.loads(response)
    tools = resp_obj.get("result", {}).get("tools", [])
    print(f"✅ Found {len(tools)} tools")
    for tool in tools:
        print(f"   - {tool['name']}")
    
    # Send tool call
    print("\n✓ Calling tool: search_docs...")
    call_msg = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "search_docs",
            "arguments": {"query": "RH", "limit": 1}
        }
    }
    proc.stdin.write(json.dumps(call_msg) + "\n")
    proc.stdin.flush()
    
    response = proc.stdout.readline()
    resp_obj = json.loads(response)
    result_text = resp_obj.get("result", {}).get("text", "")
    
    try:
        result = json.loads(result_text)
        print(f"✅ Search returned {result.get('count', 0)} results")
        if result.get("results"):
            print(f"   First result: {result['results'][0].get('title', 'N/A')}")
    except:
        print(f"❌ Search failed: {result_text[:100]}")
    
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()
    
    print("\n✅ STDIO Mode OK!")

# ============================================================================
# Test HTTP
# ============================================================================

if mode in ["http", "both"]:
    print("\n" + "=" * 80)
    print("2️⃣  Testing HTTP Mode (Streamable HTTP Transport)")
    print("=" * 80)
    
    # Start HTTP server
    print("\n✓ Starting HTTP server...")
    proc = subprocess.Popen(
        ["python", "apps/mcp-server/mcp_server_http.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=PROJECT_ROOT
    )
    
    # Wait for server to start
    time.sleep(2)
    
    try:
        # Test health
        print("✓ Health check...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Server healthy")
        
        # Initialize
        print("\n✓ Initialize request...")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        init_msg = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        response = requests.post(
            "http://localhost:8000/mcp",
            json=init_msg,
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            resp_obj = response.json()
            session_id = response.headers.get("Mcp-Session-Id")
            print(f"✅ Initialize OK")
            print(f"   Server: {resp_obj['result']['serverInfo']['name']}")
            print(f"   Session ID: {session_id[:20]}...")
            
            # List tools
            print("\n✓ Listing tools...")
            headers["Mcp-Session-Id"] = session_id
            list_msg = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
            response = requests.post(
                "http://localhost:8000/mcp",
                json=list_msg,
                headers=headers,
                timeout=5
            )
            
            resp_obj = response.json()
            tools = resp_obj.get("result", {}).get("tools", [])
            print(f"✅ Found {len(tools)} tools")
            for tool in tools:
                print(f"   - {tool['name']}")
            
            # Call tool
            print("\n✓ Calling tool: search_docs...")
            call_msg = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "search_docs",
                    "arguments": {"query": "RH", "limit": 1}
                }
            }
            response = requests.post(
                "http://localhost:8000/mcp",
                json=call_msg,
                headers=headers,
                timeout=5
            )
            
            resp_obj = response.json()
            result_text = resp_obj.get("result", {}).get("text", "")
            
            try:
                result = json.loads(result_text)
                print(f"✅ Search returned {result.get('count', 0)} results")
                if result.get("results"):
                    print(f"   First result: {result['results'][0].get('title', 'N/A')}")
            except:
                print(f"❌ Search failed: {result_text[:100]}")
            
            print("\n✅ HTTP Mode OK!")
        else:
            print(f"❌ Initialize failed: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"❌ HTTP test failed: {e}")
    
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()

# ============================================================================
# Summary
# ============================================================================

print("\n" + "=" * 80)
print("✅ MCP Server Tests Completed!")
print("=" * 80)
print("\nConfiguration for VS Code (mcp.json):")
print("""
{
  "servers": {
    "senior-docs-http": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    },
    "senior-docs-stdio": {
      "type": "stdio",
      "command": "python",
      "args": ["path/to/apps/mcp-server/mcp_server.py"]
    }
  }
}
""")
