#!/usr/bin/env python3
import requests
import json

# Try different MCP method names
methods_to_try = [
    "tools/call",
    "call_tool", 
    "resource/list",
    "search_docs"
]

query = "funções lsp"
limit = 5

for method in methods_to_try:
    print(f"\n{'='*60}")
    print(f"Testing method: {method}")
    print('='*60)
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": {
            "name": "search_docs",
            "arguments": {
                "query": query,
                "limit": limit
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.post('http://people-fy.com:8000/mcp', json=payload, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if "result" in result:
            print(f"✅ Success! Found {len(result.get('result', {}).get('content', []))} items")
            # Print first content item
            if result.get("result", {}).get("content"):
                content = result["result"]["content"][0]
                text = content.get("text", "")
                if text:
                    # Parse the JSON response text
                    try:
                        docs = json.loads(text)
                        print(f"\n📄 Found {len(docs)} documents:")
                        for i, doc in enumerate(docs[:5], 1):
                            print(f"\n{i}. {doc.get('title', 'No title')}")
                            print(f"   URL: {doc.get('url', 'No URL')}")
                            print(f"   Module: {doc.get('module', 'Unknown')}")
                    except:
                        print(text[:500])
        elif "error" in result:
            print(f"❌ Error: {result['error']['message']}")
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
            
    except Exception as e:
        print(f"❌ Exception: {e}")

print("\n" + "="*60)
print("Testing with SSE Accept header...")
print("="*60)

payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "search_docs",
        "arguments": {
            "query": query,
            "limit": limit
        }
    }
}

headers = {
    "Content-Type": "application/json",
    "Accept": "text/event-stream"
}

try:
    response = requests.post('http://people-fy.com:8000/mcp', json=payload, headers=headers, stream=True, timeout=10)
    print(f"Status: {response.status_code}")
    
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))
            
except Exception as e:
    print(f"Exception: {e}")
