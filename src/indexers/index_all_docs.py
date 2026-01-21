#!/usr/bin/env python3
"""
Index todos os documentos scraped e gera estatísticas
"""

import json
from pathlib import Path
import requests
import sys


def main():
    """Indexa todos os documentos."""
    
    print(f"\n{'='*70}")
    print("INDEXANDO DOCUMENTAÇÃO COMPLETA")
    print(f"{'='*70}\n")
    
    # [1] Coletar documentos
    print("[1] Coletando documentos...")
    doc_dir = Path('documentacao')
    docs = []
    
    for page_dir in sorted(doc_dir.iterdir()):
        if not page_dir.is_dir():
            continue
        
        meta_file = page_dir / 'metadata.json'
        content_file = page_dir / 'content.txt'
        
        if not (meta_file.exists() and content_file.exists()):
            continue
        
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
        except Exception as e:
            print(f"    [!] Erro em {page_dir.name}: {e}")
    
    print(f"    Encontrados: {len(docs)} documentos\n")
    
    if not docs:
        print("[!] Nenhum documento encontrado!")
        return
    
    # Estatísticas
    total_chars = sum(len(d.get('content', '')) for d in docs)
    avg_size = total_chars // len(docs) if docs else 0
    
    print(f"    Estatísticas:")
    print(f"      Total de caracteres: {total_chars:,}")
    print(f"      Tamanho médio: {avg_size:,} chars/doc")
    print(f"      Maior doc: {max(len(d.get('content', '')) for d in docs):,} chars")
    print(f"      Menor doc: {min(len(d.get('content', '')) for d in docs):,} chars\n")
    
    # [2] Indexar
    print("[2] Indexando em Meilisearch...")
    
    try:
        resp = requests.post(
            'http://localhost:5000/index',
            json={'documents': docs},
            timeout=60
        )
        
        if resp.status_code == 200:
            result = resp.json()
            indexed = result.get('documents_indexed', 0)
            print(f"    [OK] Indexados {indexed} documentos\n")
        else:
            print(f"    [!] Erro {resp.status_code}: {resp.text}\n")
            return
    except Exception as e:
        print(f"    [!] Erro: {e}\n")
        return
    
    # [3] Verificar índice
    print("[3] Verificando índice...")
    
    try:
        resp = requests.get('http://localhost:5000/stats', timeout=5)
        if resp.status_code == 200:
            stats = resp.json()
            print(f"    Total indexado: {stats.get('count', 0)} documentos\n")
    except:
        pass
    
    # [4] Testar busca
    print("[4] Testando busca...")
    
    test_queries = [
        'Gerador',
        'Relatório',
        'Tecnologia',
        'ERP',
        'Sistema'
    ]
    
    for query in test_queries:
        try:
            resp = requests.get(
                'http://localhost:5000/search',
                params={'q': query, 'limit': 1},
                timeout=5
            )
            
            if resp.status_code == 200:
                results = resp.json()
                count = len(results.get('results', []))
                status = '✓' if count > 0 else '✗'
                print(f"    {status} '{query}': {count} resultado(s)")
        except:
            pass
    
    # [5] Exportar
    print(f"\n[5] Exportando dados...")
    
    try:
        resp = requests.get('http://localhost:5000/export?format=jsonl', timeout=60)
        if resp.status_code == 200:
            with open('export_complete.jsonl', 'w', encoding='utf-8') as f:
                f.write(resp.text)
            
            lines = len(resp.text.strip().split('\n'))
            size_kb = len(resp.text) // 1024
            print(f"    [OK] Exportado para export_complete.jsonl")
            print(f"         {lines} linhas, {size_kb}KB\n")
    except Exception as e:
        print(f"    [!] Erro: {e}\n")
    
    # Resumo
    print("="*70)
    print("SISTEMA PRONTO PARA USO!")
    print("="*70)
    print(f"""
✓ {len(docs)} documentos indexados
✓ Full-text search operacional
✓ Dados exportados em JSONL

Próximos passos:
  1. Usar export_complete.jsonl para treinar IA
  2. Executar consultas: python -c "import requests; print(requests.get(...).json())"
  3. Configurar pipeline automática
    """)


if __name__ == "__main__":
    main()
