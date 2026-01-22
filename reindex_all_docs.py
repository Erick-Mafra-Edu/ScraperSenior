#!/usr/bin/env python3
"""Reindexar documentação completa do Senior"""
import os
import json
from pathlib import Path

docs_dir = Path('docs_estruturado')
output_file = 'docs_indexacao_detailed.jsonl'

documents = []
doc_id = 0

print("=== Indexando documentação Senior ===\n")

# Percorrer todos os módulos
for module_dir in sorted(docs_dir.iterdir()):
    if not module_dir.is_dir():
        continue
    
    module_name = module_dir.name
    if module_name == 's':  # Ignorar pasta 's' 
        continue
    
    print(f"Processando módulo: {module_name}")
    
    # Procurar arquivos em subpastas
    content_files = []
    for subdir in module_dir.glob('*'):
        if subdir.is_dir():
            # Procurar content.txt ou .txt na subpasta
            content_file = subdir / 'content.txt'
            if content_file.exists():
                content_files.append((subdir.name, content_file))
    
    print(f"  Encontrados: {len(content_files)} documentos")
    
    for title_from_dir, content_file in content_files:
        try:
            content = content_file.read_text(encoding='utf-8', errors='ignore')
            
            title = title_from_dir.replace('_', ' ').replace('-', ' ')
            
            doc_id += 1
            doc = {
                'id': f'{module_name}_{doc_id}',
                'title': title,
                'module': module_name,
                'content': content[:1000],  # Primeiros 1000 chars
                'file': content_file.name,
                'url': f'/{module_name}/{title_from_dir}/'
            }
            
            documents.append(doc)
        except Exception as e:
            print(f"  ❌ Erro ao processar {title_from_dir}: {e}")

print(f"\n✓ Total de documentos indexados: {len(documents)}\n")

# Salvar em JSONL
with open(output_file, 'w', encoding='utf-8') as f:
    for doc in documents:
        f.write(json.dumps(doc, ensure_ascii=False) + '\n')

print(f"✓ Arquivo salvo: {output_file}\n")

# Resumo por módulo
modules = {}
for doc in documents:
    mod = doc['module']
    modules[mod] = modules.get(mod, 0) + 1

print("Documentos por módulo:")
for mod in sorted(modules.keys()):
    print(f"  {mod}: {modules[mod]}")
