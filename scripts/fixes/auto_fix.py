#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-fix para corrigir problemas encontrados pelo CI/CD
"""

import json
import sys
from pathlib import Path


def fix_jsonl_documents():
    """Adiciona campos faltantes ao JSONL"""
    print("\n[*] Corrigindo JSONL: Adicionando IDs e módulos\n")
    
    input_file = Path("docs_indexacao_detailed.jsonl")
    
    if not input_file.exists():
        print("[!] Arquivo nao encontrado")
        return False
    
    fixed_docs = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            
            try:
                doc = json.loads(line)
                
                # Adicionar ID se faltar
                if 'id' not in doc:
                    doc['id'] = f"doc_{i}"
                
                # Adicionar módulo se faltar
                if 'module' not in doc:
                    # Extrair do breadcrumb
                    if 'breadcrumb' in doc and len(doc['breadcrumb']) > 0:
                        doc['module'] = doc['breadcrumb'][0].replace(' ', '_').upper()
                    else:
                        doc['module'] = "UNKNOWN"
                
                # Garantir título não vazio
                if 'title' not in doc or not doc['title'] or doc['title'].strip() == '':
                    if 'breadcrumb' in doc and len(doc['breadcrumb']) > 1:
                        doc['title'] = doc['breadcrumb'][-1]
                    else:
                        doc['title'] = f"Documento {i}"
                
                # Garantir que fields obrigatórios existem
                for field in ['url', 'breadcrumb', 'text_content']:
                    if field not in doc:
                        doc[field] = ""
                
                fixed_docs.append(doc)
                print(f"[+] Doc {i}: id={doc['id']}, module={doc['module'][:20]}")
                
            except json.JSONDecodeError as e:
                print(f"[!] Erro em linha {i}: {e}")
                return False
    
    # Salvar arquivo corrigido
    with open(input_file, 'w', encoding='utf-8') as f:
        for doc in fixed_docs:
            f.write(json.dumps(doc, ensure_ascii=False) + '\n')
    
    print(f"\n[+] Arquivo corrigido: {len(fixed_docs)} documentos")
    return True


def verify_fixes():
    """Verifica se correções foram aplicadas"""
    print("\n[*] Verificando correções\n")
    
    input_file = Path("docs_indexacao_detailed.jsonl")
    
    if not input_file.exists():
        print("[!] Arquivo nao encontrado")
        return False
    
    all_ok = True
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            
            doc = json.loads(line)
            
            # Verificar campos obrigatórios
            required = ['id', 'title', 'url', 'module', 'breadcrumb']
            missing = [f for f in required if f not in doc or not doc[f]]
            
            if missing:
                print(f"[-] Doc {i}: Faltam {missing}")
                all_ok = False
            else:
                print(f"[+] Doc {i}: OK (id={doc['id']}, module={doc['module']})")
    
    return all_ok


def main():
    """Executa correções"""
    print("="*80)
    print("[*] AUTO-FIX - Corrigindo problemas do CI/CD")
    print("="*80)
    
    # Step 1: Fix JSONL
    if not fix_jsonl_documents():
        print("[!] Erro ao corrigir JSONL")
        return False
    
    # Step 2: Verify
    if not verify_fixes():
        print("[!] Verificacao falhou")
        return False
    
    print("\n" + "="*80)
    print("[+] AUTO-FIX COMPLETO")
    print("="*80)
    print("\nProximos passos:")
    print("1. Reindexar Meilisearch: python index_meilisearch.py")
    print("2. Reiniciar MCP: docker-compose restart mcp-server")
    print("3. Rodar testes: python run_tests.py\n")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
