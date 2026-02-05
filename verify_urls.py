#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

print("=" * 70)
print("VERIFICAÇÃO: URLs nos Documentos")
print("=" * 70)

with open('docs_indexacao_detailed.jsonl', 'r', encoding='utf-8') as f:
    for i in range(5):
        line = f.readline()
        if line.strip():
            doc = json.loads(line)
            title = doc.get('title', 'N/A')
            url = doc.get('url', '❌ SEM URL')
            module = doc.get('module', 'N/A')
            
            print(f"\n{i+1}. Título: {title}")
            print(f"   Módulo: {module}")
            print(f"   URL: {url}")

print("\n" + "=" * 70)
print("✅ Verificação concluída")
print("=" * 70)
