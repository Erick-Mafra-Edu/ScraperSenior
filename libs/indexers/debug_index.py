#!/usr/bin/env python3
import json
from pathlib import Path
import requests

# Ler documentos
doc_dir = Path('documentacao')
docs = []

for page_dir in sorted(doc_dir.iterdir()):
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
                print(f"  Documento: {page_dir.name} ({len(content)} chars)")
            except Exception as e:
                print(f"  Erro lendo {page_dir.name}: {e}")

print(f"\n[*] Total: {len(docs)} documentos\n")

# Indexar
if docs:
    print("[*] Enviando para API...")
    try:
        resp = requests.post('http://localhost:5000/index', 
                            json={'documents': docs}, 
                            timeout=30)
        
        print(f"[*] Status: {resp.status_code}")
        print(f"[*] Response:")
        print(json.dumps(resp.json(), indent=2))
    except Exception as e:
        print(f"[!] Erro: {e}")
