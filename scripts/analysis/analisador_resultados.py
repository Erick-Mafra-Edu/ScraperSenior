#!/usr/bin/env python3
"""
Visualizador de estrutura de documentação e análise de JSONL
"""

import json
from pathlib import Path
from collections import defaultdict


def analyze_structure():
    """Analisa estrutura de pastas e metadados"""
    
    print("\n" + "="*90)
    print("[ANÁLISE] Documentação Estruturada")
    print("="*90 + "\n")
    
    # Carregar metadata
    meta_file = Path("docs_metadata.json")
    if not meta_file.exists():
        print("[ERRO] docs_metadata.json não encontrado")
        return
    
    with open(meta_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Análise por módulo
    print("[MÓDULOS]")
    for module, stats in metadata['statistics']['by_module'].items():
        print(f"\n  📦 {module}")
        print(f"     Tipo: {stats['type'].upper()}")
        print(f"     Páginas: {stats['pages']}")
        print(f"     Conteúdo: {stats['total_chars']:,} caracteres ({stats['total_chars']/1024:.1f} KB)")
        print(f"     Média por página: {stats['total_chars']//stats['pages']:,} chars")
    
    # Sumário geral
    total = metadata['statistics']['total_pages']
    total_size = metadata['statistics']['total_chars']
    
    print(f"\n[SUMÁRIO]")
    print(f"  Total de páginas: {total}")
    print(f"  Total de conteúdo: {total_size:,} caracteres ({total_size/1024:.1f} KB)")
    print(f"  Arquivo JSONL: {metadata['output_jsonl']}")
    print(f"  Timestamp: {metadata['timestamp']}\n")
    
    # Analisar JSONL
    print("[ARQUIVO JSONL]")
    jsonl_file = Path(metadata['output_jsonl'])
    
    if jsonl_file.exists():
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            docs = [json.loads(line) for line in f if line.strip()]
        
        print(f"  Documentos indexáveis: {len(docs)}")
        print(f"  Tamanho do arquivo: {jsonl_file.stat().st_size / 1024:.1f} KB")
        
        # Análise de tags
        tags_count = defaultdict(int)
        for doc in docs:
            for tag in doc.get('tags', []):
                tags_count[tag] += 1
        
        print(f"\n  Tags mais frequentes:")
        for tag, count in sorted(tags_count.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    • {tag}: {count} documentos")
    
    # Estrutura de pastas
    print(f"\n[ESTRUTURA DE PASTAS]")
    docs_dir = Path("docs_estruturado")
    
    def count_depth(path, max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            return
        
        try:
            items = list(path.iterdir())
            dirs = [i for i in items if i.is_dir()]
            files = [i for i in items if i.is_file()]
            
            if files:
                print(f"  {'  ' * current_depth}📄 {len(files)} arquivo(s)")
            
            if dirs:
                for d in dirs[:3]:
                    print(f"  {'  ' * current_depth}📁 {d.name}/")
                    count_depth(d, max_depth, current_depth + 1)
                
                if len(dirs) > 3:
                    print(f"  {'  ' * current_depth}... ({len(dirs) - 3} mais diretórios)")
        except:
            pass
    
    count_depth(docs_dir)
    
    print("\n" + "="*90 + "\n")


def analyze_jsonl_content():
    """Analisa conteúdo do JSONL"""
    
    print("\n[AMOSTRA DE DOCUMENTOS JSONL]")
    
    jsonl_file = Path("docs_indexacao.jsonl")
    if not jsonl_file.exists():
        print("Arquivo não encontrado!")
        return
    
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        docs = [json.loads(line) for line in f if line.strip()]
    
    print(f"\nTotal de {len(docs)} documentos\n")
    
    for i, doc in enumerate(docs[:3], 1):
        print(f"\n[DOCUMENTO {i}]")
        print(f"  Título: {doc['title'][:60]}")
        print(f"  URL: {doc['url'][:70]}")
        print(f"  Módulo: {doc['module']}")
        print(f"  Categoria: {doc['category']}")
        print(f"  Breadcrumb: {doc['breadcrumb'][:80]}")
        print(f"  Conteúdo: {len(doc['content'])} caracteres")
        print(f"  Headers: {len(doc['headers'])}")
        print(f"  Tags: {doc['tags']}")
    
    print("\n")


if __name__ == "__main__":
    analyze_structure()
    analyze_jsonl_content()
