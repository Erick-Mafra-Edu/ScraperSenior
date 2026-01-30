#!/usr/bin/env python3
import meilisearch

client = meilisearch.Client('http://localhost:7700', 'meilisearch_master_key_change_me')
index = client.get_index('documentation')

# Test search
results = index.search('Help Center')
print(f"✅ Resultados encontrados para 'Help Center': {len(results['hits'])}")
print("\nPrimeiros 5 resultados:")
for i, hit in enumerate(results['hits'][:5], 1):
    print(f"  {i}. {hit.get('title', 'N/A')[:70]}...")
    print(f"     Fonte: {hit.get('source', 'N/A')}")
    print()

# Get stats
stats = index.get_stats()
print(f"\n📊 Estatísticas do índice:")
print(f"   Total de documentos: {stats.number_of_documents}")
print(f"   Está indexando: {stats.is_indexing}")
