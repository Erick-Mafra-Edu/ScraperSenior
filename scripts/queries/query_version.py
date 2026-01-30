#!/usr/bin/env python3
"""Consulta informações sobre versão 6.10.4.105 no Meilisearch"""

import requests
import json

def query_meilisearch(query_term):
    """Busca no Meilisearch"""
    url = 'http://localhost:7700/indexes/senior_docs/search'
    headers = {
        'Authorization': 'Bearer meilisearch_master_key_change_me',
        'Content-Type': 'application/json'
    }
    payload = {'q': query_term, 'limit': 20}
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=5)
        return r.status_code, r.json()
    except Exception as e:
        return None, {'error': str(e)}

if __name__ == '__main__':
    print("=" * 80)
    print("Consultando versão 6.10.4.105 no Meilisearch")
    print("=" * 80)
    
    status, result = query_meilisearch('6.10.4.105')
    
    if status != 200:
        print(f"Status HTTP: {status}")
        print(f"Erro: {result}")
        exit(1)
    
    hits = result.get('hits', [])
    print(f"\nResultados encontrados: {len(hits)}")
    print(f"Tempo de processamento: {result.get('processingTimeMs')}ms\n")
    
    if not hits:
        print("Nenhum documento encontrado para '6.10.4.105'")
        print("\nTentando busca alternativa por 'versão 6.10'...")
        status, result = query_meilisearch('versão 6.10')
        hits = result.get('hits', [])
        print(f"Resultados encontrados: {len(hits)}\n")
    
    for i, hit in enumerate(hits[:10], 1):
        print(f"{i}. {hit.get('title', 'Sem título')}")
        print(f"   Módulo: {hit.get('module', 'N/A')}")
        print(f"   URL: {hit.get('url', 'N/A')[:100]}")
        if 'content' in hit and hit['content']:
            preview = hit['content'][:200].replace('\n', ' ')
            print(f"   Preview: {preview}...")
        print()
