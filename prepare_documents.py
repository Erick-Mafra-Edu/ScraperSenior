#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preparar documentos com campos obrigatórios para MCP
"""

import json
from pathlib import Path

print("\n" + "="*80)
print("📦 PREPARANDO DOCUMENTOS PARA MCP")
print("="*80 + "\n")

input_file = Path("docs_para_mcp.jsonl")
output_file = Path("docs_indexacao_detailed.jsonl")

if not input_file.exists():
    print(f"❌ Arquivo {input_file} não encontrado")
    exit(1)

docs = []
with open(input_file) as f:
    for idx, line in enumerate(f, 1):
        if line.strip():
            doc = json.loads(line)
            
            # Adicionar campos obrigatórios
            doc['id'] = f"doc_{idx}"
            doc['module'] = "GESTAO DE PESSOAS HCM"  # Módulo do qual veio
            
            # Garantir que campos existam (mesmo que vazios)
            if 'breadcrumb' not in doc:
                doc['breadcrumb'] = []
            if 'headers' not in doc:
                doc['headers'] = []
            if 'paragraphs' not in doc:
                doc['paragraphs'] = []
            
            docs.append(doc)
            
            print(f"   ✓ Documento {idx}: {doc.get('title', 'SEM TÍTULO')[:50]}")

# Salvar com campos completos
with open(output_file, 'w', encoding='utf-8') as f:
    for doc in docs:
        f.write(json.dumps(doc, ensure_ascii=False) + '\n')

print(f"\n✓ {len(docs)} documentos preparados e salvos em: {output_file}")
print("\n📝 Próximo passo:")
print("   docker-compose restart mcp-server")
