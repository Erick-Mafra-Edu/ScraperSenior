#!/usr/bin/env python3
"""Test MCP server directly"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp_server import MCPServer

# Initialize
print("Initializing MCP Server...")
server = MCPServer()

print(f"Tools available: {list(server.tools.keys())}")
print()

# Test search_docs
print("=" * 60)
print("TEST: search_docs with query='HCM'")
print("=" * 60)

result = server.handle_tool_call('search_docs', {'query': 'HCM'})
print(f"Result type: {type(result)}")

# Parse result
result_obj = json.loads(result) if isinstance(result, str) else result
print(f"Result keys: {list(result_obj.keys()) if isinstance(result_obj, dict) else 'NOT A DICT'}")
print()
print("Result preview:")
print(json.dumps(result_obj, indent=2, ensure_ascii=False)[:1000])
