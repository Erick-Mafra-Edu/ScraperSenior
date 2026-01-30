#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Indexar documentos rapidamente para testes
"""

import json
from pathlib import Path

# Carregar documentos que foram scrapados
docs_file = Path("docs_para_mcp.jsonl")

if not docs_file.exists():
    print("❌ Arquivo docs_para_mcp.jsonl não encontrado")
    print("Execute primeiro: python test_mcp_titles.py")
    exit(1)

# Ler documentos
docs = []
with open(docs_file) as f:
    for line in f:
        docs.append(json.loads(line))

print(f"\n✓ Carregados {len(docs)} documentos de {docs_file}\n")

# Salvar em docs_indexacao.jsonl (formato que o MCP usa)
output_file = Path("docs_indexacao.jsonl")
with open(output_file, 'w', encoding='utf-8') as f:
    for doc in docs:
        f.write(json.dumps(doc, ensure_ascii=False) + '\n')

print(f"✓ Salvos em {output_file}")
print(f"\n📝 Próximos passos:")
print(f"   docker-compose restart mcp-server")
print(f"   sleep 5")
print(f"   python test_mcp_search.py")
