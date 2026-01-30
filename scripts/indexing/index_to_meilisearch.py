#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Indexar documentos JSONL rapidamente no Meilisearch
"""

import json
import requests
from pathlib import Path

# Configuração do Meilisearch
MEILISEARCH_URL = "http://localhost:7700"
MEILISEARCH_INDEX = "senior-docs"

print("\n" + "="*80)
print("📦 INDEXANDO DOCUMENTOS NO MEILISEARCH")
print("="*80 + "\n")

# Carregar documentos do JSONL
docs_file = Path("docs_indexacao.jsonl")

if not docs_file.exists():
    print(f"❌ Arquivo {docs_file} não encontrado")
    exit(1)

docs = []
with open(docs_file) as f:
    for line in f:
        docs.append(json.loads(line))

print(f"[1] Carregados {len(docs)} documentos\n")

# Enviar para Meilisearch
print(f"[2] Enviando para {MEILISEARCH_URL}\n")

try:
    # Criar/limpar índice
    requests.delete(f"{MEILISEARCH_URL}/indexes/{MEILISEARCH_INDEX}")
    
    # Indexar documentos
    response = requests.post(
        f"{MEILISEARCH_URL}/indexes/{MEILISEARCH_INDEX}/documents",
        json=docs
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"   ✓ Documentos indexados com sucesso")
        print(f"   ✓ Task ID: {result.get('taskUid', 'N/A')}\n")
    else:
        print(f"   ✗ Erro: {response.status_code}")
        print(f"   {response.text}\n")

except Exception as e:
    print(f"   ✗ Erro: {e}\n")

# Verificar índice
print(f"[3] Verificando índice\n")

try:
    response = requests.get(f"{MEILISEARCH_URL}/indexes/{MEILISEARCH_INDEX}")
    
    if response.status_code == 200:
        index = response.json()
        print(f"   ✓ Índice encontrado")
        print(f"   ✓ Total de documentos: {index.get('numberOfDocuments', 0)}\n")
    else:
        print(f"   ✗ Índice não encontrado\n")

except Exception as e:
    print(f"   ✗ Erro: {e}\n")

print("="*80)
print("✅ INDEXAÇÃO CONCLUÍDA")
print("="*80 + "\n")

print("📝 Próximos passos:")
print("   1. Aguardar 3 segundos")
print("   2. python test_mcp_search.py\n")
