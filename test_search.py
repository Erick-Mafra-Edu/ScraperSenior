#!/usr/bin/env python3
import meilisearch

import os
client = meilisearch.Client(
    os.getenv('MEILISEARCH_URL', 'http://localhost:7700'),
    os.getenv('MEILISEARCH_KEY', '5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa')
)
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
