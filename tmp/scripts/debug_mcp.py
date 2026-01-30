#!/usr/bin/env python3
"""Debug MCP Server Connection"""

import json
import meilisearch
import sys
from pathlib import Path

print("="*80)
print("DEBUG - MCP Server Connection")
print("="*80)

# Test Meilisearch connection
print("\n1. Testando conexão com Meilisearch...")
try:
    client = meilisearch.Client("http://localhost:7700", "meilisearch_master_key_change_me")
    health = client.health()
    print(f"   ✅ Meilisearch conectado: {health}")
    
    # Try to get documentation index
    try:
        index = client.get_index("documentation")
        stats = index.get_stats()
        print(f"   ✅ Índice 'documentation' encontrado: {stats.number_of_documents} documentos")
        
        # Test search
        result = index.search("ERP", {"limit": 3})
        print(f"   ✅ Busca funcionando: {result['estimatedTotalHits']} resultados para 'ERP'")
        
    except Exception as e:
        print(f"   ❌ Erro com índice 'documentation': {e}")
        
except Exception as e:
    print(f"   ❌ Erro ao conectar com Meilisearch: {e}")

# Test local file
print("\n2. Testando arquivo local...")
index_file = Path("docs_unified/unified_documentation.jsonl")
if index_file.exists():
    count = sum(1 for _ in open(index_file, 'r', encoding='utf-8'))
    print(f"   ✅ Arquivo encontrado: {count} documentos")
else:
    print(f"   ❌ Arquivo não encontrado: {index_file}")

# Test MCP server
print("\n3. Testando servidor MCP HTTP...")
import urllib.request
import json

try:
    response = urllib.request.urlopen("http://localhost:8000/stats")
    data = json.loads(response.read().decode())
    print(f"   ✅ Servidor respondendo:")
    print(f"      Documentos: {data['stats']['total_documents']}")
    print(f"      Fonte: {data['stats']['source']}")
    print(f"      Módulos: {data['modules']}")
except Exception as e:
    print(f"   ❌ Erro ao acessar servidor: {e}")

print("\n" + "="*80)
