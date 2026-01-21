#!/usr/bin/env python3
"""Index scraped documents e testar busca"""

import json
from pathlib import Path
import requests

# Ler documentos
doc_dir = Path('documentacao')
docs = []

for page_dir in doc_dir.iterdir():
    if page_dir.is_dir():
        meta_file = page_dir / 'metadata.json'
        content_file = page_dir / 'content.txt'
        
        if meta_file.exists() and content_file.exists():
            try:
                with open(meta_file, encoding='utf-8') as f:
                    meta = json.load(f)
                with open(content_file, encoding='utf-8') as f:
                    content = f.read()
                
                doc = {
                    'id': page_dir.name,
                    **meta,
                    'content': content
                }
                docs.append(doc)
            except:
                pass

print(f'Documentos encontrados: {len(docs)}\n')

# Indexar
if docs:
    print('[1] Indexando...')
    resp = requests.post('http://localhost:5000/index', json={'documents': docs}, timeout=30)
    
    if resp.status_code == 200:
        result = resp.json()
        indexed = result.get('indexed', 0)
        print(f'    [OK] Indexados {indexed} documentos\n')
        
        # Testar busca
        print('[2] Testando busca nos artigos indexados:')
        test_queries = ['Relatorio', 'Gerador', 'modelo', 'DPI', 'Tecnologia']
        for query in test_queries:
            resp = requests.get('http://localhost:5000/search', 
                              params={'q': query, 'limit': 2}, timeout=5)
            if resp.status_code == 200:
                results = resp.json()
                count = len(results.get('results', []))
                print(f'    "{query}": {count} resultado(s)')
                if count > 0:
                    title = results['results'][0].get('title', '')[:50]
                    print(f'      -> {title}')
    else:
        print(f'[ERRO] {resp.status_code}: {resp.text}')
else:
    print('[!] Nenhum documento encontrado para indexar')
