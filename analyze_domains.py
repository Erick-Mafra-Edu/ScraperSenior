#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from collections import defaultdict

urls_by_domain = defaultdict(list)
urls_by_module = defaultdict(list)

with open('docs_indexacao_detailed.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= 50:  # Primeiros 50
            break
        doc = json.loads(line)
        url = doc.get('url', '')
        module = doc.get('module', 'N/A')
        
        # Extrair domínio
        if 'suporte' in url:
            domain = 'suporte.senior.com.br'
        elif 'documentacao' in url:
            domain = 'documentacao.senior.com.br'
        else:
            domain = 'relativo'
        
        urls_by_domain[domain].append(url)
        urls_by_module[module].append({'domain': domain, 'url': url})

print("=" * 70)
print("DOMÍNIOS ENCONTRADOS")
print("=" * 70)
for domain, urls in urls_by_domain.items():
    print(f"\n{domain}: {len(urls)} URL(s)")
    print(f"  Exemplo: {urls[0][:90]}")

print("\n" + "=" * 70)
print("MÓDULOS E SEUS DOMÍNIOS")
print("=" * 70)
for module, items in urls_by_module.items():
    domains = set(item['domain'] for item in items)
    print(f"\n{module}:")
    for domain in domains:
        count = sum(1 for item in items if item['domain'] == domain)
        print(f"  - {domain}: {count} URL(s)")
        # Exemplo
        for item in items:
            if item['domain'] == domain:
                print(f"    {item['url'][:80]}")
                break
