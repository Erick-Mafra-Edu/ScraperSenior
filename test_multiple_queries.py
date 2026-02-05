import requests
import json

# Test with different queries
queries = [
    "funções lsp",
    "lsp",
    "funcoes",
    "LSP",
    "implantação",
    "relatório",
    "modulo"
]

print("Testing search queries...\n")

for query in queries:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "search_docs",
            "arguments": {
                "query": query,
                "limit": 5
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    try:
        response = requests.post('http://people-fy.com:8000/mcp', json=payload, headers=headers, stream=True)
        
        # Parse SSE response
        line = next(response.iter_lines())
        if line:
            json_str = line.decode().replace('data: ', '')
            result = json.loads(json_str)
            
            # Parse the inner JSON
            text = result['result']['text']
            docs = json.loads(text)
            
            count = docs['count']
            print(f"Query '{query}': {count} resultados")
            
            if count > 0:
                print(f"  Primeiros 3 resultados:")
                for i, doc in enumerate(docs['results'][:3], 1):
                    print(f"    {i}. {doc.get('title', 'No title')}")
                    print(f"       URL: {doc.get('url')}")
                    print(f"       Module: {doc.get('module')}")
                    print()
            print()
    except Exception as e:
        print(f"Query '{query}': ERRO - {e}\n")
