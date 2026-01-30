#!/usr/bin/env python3
"""Direct test of search_docs"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.mcp_server import MCPServer

mcp = MCPServer()

# Test 1
result = mcp.handle_tool_call('search_docs', {'query': 'HCM'})
print(f"Result type: {type(result)}")
print(f"Result length: {len(result)}")
print(f"First 200 chars: {result[:200]}")

# Test 2
result = mcp.handle_tool_call('search_docs', {})
print(f"\nWith empty params: {result}")
