#!/usr/bin/env python3
import json

print("=== Verificando arquivo de índice ===\n")
with open('docs_indexacao_detailed.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total de linhas: {len(lines)}")

if lines:
    first = json.loads(lines[0])
    print(f"\nPrimeiro doc:")
    print(f"  Módulo: {first.get('module')}")
    print(f"  Título: {first.get('title')[:60]}...")
    print(f"  Chaves: {list(first.keys())}")
    
    if len(lines) > 1:
        last = json.loads(lines[-1])
        print(f"\nÚltimo doc:")
        print(f"  Módulo: {last.get('module')}")
        print(f"  Título: {last.get('title')[:60]}...")

# Contar por módulo
modules = {}
for line in lines:
    doc = json.loads(line)
    mod = doc.get('module', 'SEM_MODULO')
    modules[mod] = modules.get(mod, 0) + 1

print(f"\nDocumentos por módulo:")
for mod, count in sorted(modules.items()):
    print(f"  {mod}: {count}")

print(f"\nTamanho do arquivo: {sum(len(line) for line in lines)} bytes")
