#!/usr/bin/env python3
"""Quick test to verify Zendesk documents in Meilisearch"""

import meilisearch
import time

client = meilisearch.Client('http://localhost:7700', 'meilisearch_master_key_change_me')
index = client.get_index('documentation')

# Wait for indexing to complete
print("Aguardando conclusao da indexacao...")
for i in range(30):
    stats = index.get_stats()
    if not stats.is_indexing:
        print(f"Indexacao concluida!")
        break
    print(f"  {i+1}/30 - Ainda indexando... ({stats.number_of_documents} docs)")
    time.sleep(1)

# Test search with Zendesk documents
print("\n=== TESTE DE FILTRO ===")
try:
    result = index.search("", {"filter": 'source = "zendesk_api"', "limit": 5})
    zendesk_count = result.get('estimatedTotalHits', 0)
    print(f"Documentos Zendesk encontrados: {zendesk_count}")
    
    if result.get('hits'):
        print("\nExemplos:")
        for doc in result['hits'][:3]:
            print(f"  - {doc['title'][:60]} (source: {doc.get('source', 'N/A')})")
except Exception as e:
    print(f"Erro ao filtrar: {e}")

# Test search with Website documents
print("\n=== TESTE WEBSITE ===")
try:
    result = index.search("", {"filter": 'source = "website"', "limit": 5})
    website_count = result.get('estimatedTotalHits', 0)
    print(f"Documentos Website encontrados: {website_count}")
except Exception as e:
    print(f"Erro ao filtrar: {e}")

# General search
print("\n=== BUSCA GERAL ===")
try:
    result = index.search("ERP", {"limit": 10})
    print(f"Total encontrado com 'ERP': {result.get('estimatedTotalHits', 0)}")
    
    if result.get('hits'):
        print("\nExemplos de resultados:")
        for doc in result['hits'][:5]:
            print(f"  - {doc['title'][:60]} (source: {doc.get('source', 'N/A')})")
except Exception as e:
    print(f"Erro na busca: {e}")

print("\n=== RESUMO ===")
stats = index.get_stats()
print(f"Total de documentos no indice: {stats.number_of_documents}")
print(f"Indexando: {stats.is_indexing}")
