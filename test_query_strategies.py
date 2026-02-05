#!/usr/bin/env python3
"""Test the 3 query parsing strategies"""

import requests
import json

# Test queries
test_cases = [
    ("funções lsp", "auto"),
    ("funções lsp", "quoted"),
    ("funções lsp", "and"),
    ("lsp", "auto"),
    ("implantação modulo", "auto"),
    ("implantação modulo", "quoted"),
    ("implantação modulo", "and"),
]

print("=" * 80)
print("Testing 3 Query Parsing Strategies")
print("=" * 80)

for query, strategy in test_cases:
    print(f"\n{'='*80}")
    print(f"Query: '{query}'")
    print(f"Strategy: {strategy}")
    print('='*80)
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "search_docs",
            "arguments": {
                "query": query,
                "limit": 5,
                "query_strategy": strategy
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
            
            # Show transformation and results
            original = docs['query']
            parsed = docs['parsed_query']
            count = docs['count']
            
            print(f"Original Query: '{original}'")
            print(f"Parsed Query:   '{parsed}'")
            print(f"Results: {count} encontrados")
            
            if count > 0:
                print(f"\nTop 3 resultados:")
                for i, doc in enumerate(docs['results'][:3], 1):
                    title = doc.get('title', 'No title')
                    # Truncate long titles
                    if len(title) > 70:
                        title = title[:67] + "..."
                    print(f"  {i}. {title}")
            else:
                print("❌ Nenhum resultado encontrado")
                
    except Exception as e:
        print(f"❌ Erro: {e}")

print("\n" + "=" * 80)
print("CONCLUSÃO")
print("=" * 80)
print("""
Estratégias Implementadas:
1. 'quoted': Envolve em aspas -> "funções lsp"
   - Procura pela frase exata
   
2. 'and': Usa AND entre termos -> funções AND lsp
   - Procura documentos com TODOS os termos
   
3. 'auto': Inteligente (recomendado)
   - Se tem espaço: tenta 'quoted' primeiro
   - Se sem espaço: mantém como está
""")
