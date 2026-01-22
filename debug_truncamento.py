#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Debug - Análise de Truncamento no Scraping
======================================================

Identifica documentos truncados e verifica o impacto da perda de conteúdo
"""

import json
from pathlib import Path
from collections import defaultdict

def analyze_truncation():
    """Analisa o arquivo JSONL para encontrar truncamentos"""
    
    jsonl_file = Path('docs_indexacao_detailed.jsonl')
    
    if not jsonl_file.exists():
        print(f"❌ Arquivo não encontrado: {jsonl_file}")
        return
    
    truncated_docs = []
    total_loss_chars = 0
    stats = defaultdict(int)
    
    print("\n" + "="*80)
    print("🔍 ANÁLISE DE TRUNCAMENTO NO SCRAPING")
    print("="*80 + "\n")
    
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                doc = json.loads(line)
                
                # Verificar se há truncamento
                if 'content_length' in doc:
                    original_size = doc['content_length']
                    indexed_size = len(doc.get('content', ''))
                    
                    if indexed_size < original_size:
                        loss_ratio = (original_size - indexed_size) / original_size * 100
                        
                        if loss_ratio > 50:  # Mais de 50% perdido
                            truncated_docs.append({
                                'line': line_num,
                                'title': doc.get('title', 'N/A'),
                                'module': doc.get('module', 'N/A'),
                                'original': original_size,
                                'indexed': indexed_size,
                                'loss_ratio': loss_ratio,
                                'loss_chars': original_size - indexed_size
                            })
                            total_loss_chars += (original_size - indexed_size)
                            stats['high_loss'] += 1
                        else:
                            stats['medium_loss'] += 1
                    else:
                        stats['no_loss'] += 1
            
            except json.JSONDecodeError as e:
                print(f"⚠️  Erro ao decodificar linha {line_num}: {e}")
    
    # Relatório
    print(f"📊 ESTATÍSTICAS GERAIS")
    print(f"├─ Documentos sem truncamento: {stats['no_loss']}")
    print(f"├─ Documentos com perda moderada (10-50%): {stats['medium_loss']}")
    print(f"├─ Documentos com perda severa (>50%): {stats['high_loss']}")
    print(f"└─ Total de caracteres perdidos: {total_loss_chars:,} chars\n")
    
    if truncated_docs:
        print(f"🚨 TOP 10 DOCUMENTOS COM MAIOR TRUNCAMENTO\n")
        print(f"{'#':<3} {'Módulo':<20} {'Título':<35} {'Perda':<10} {'Chars Perdidos'}")
        print("-" * 90)
        
        for i, doc in enumerate(sorted(truncated_docs, key=lambda x: x['loss_chars'], reverse=True)[:10], 1):
            title = doc['title'][:32] + '...' if len(doc['title']) > 32 else doc['title']
            print(f"{i:<3} {doc['module']:<20} {title:<35} {doc['loss_ratio']:>6.1f}%  {doc['loss_chars']:>12,} chars")
    
    # Análise de padrões
    print(f"\n🔎 ANÁLISE DE PADRÕES DE TRUNCAMENTO\n")
    
    by_module = defaultdict(lambda: {'truncated': 0, 'total': 0, 'total_loss': 0})
    
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                doc = json.loads(line)
                module = doc.get('module', 'unknown')
                by_module[module]['total'] += 1
                
                if 'content_length' in doc:
                    original = doc['content_length']
                    indexed = len(doc.get('content', ''))
                    if indexed < original:
                        by_module[module]['truncated'] += 1
                        by_module[module]['total_loss'] += (original - indexed)
            except:
                pass
    
    print("Módulo com maior perda de conteúdo:\n")
    print(f"{'Módulo':<30} {'Docs Truncados':<18} {'Total Chars Perdidos'}")
    print("-" * 65)
    
    for module, data in sorted(by_module.items(), key=lambda x: x[1]['total_loss'], reverse=True)[:5]:
        truncation_rate = data['truncated'] / data['total'] * 100 if data['total'] > 0 else 0
        print(f"{module:<30} {data['truncated']}/{data['total']} ({truncation_rate:.1f}%)  {data['total_loss']:>15,} chars")
    
    # Recomendações
    print(f"\n💡 RECOMENDAÇÕES\n")
    
    if stats['high_loss'] > 0:
        print(f"1️⃣  Aumentar limite de indexação:")
        print(f"   Atual: 5000 caracteres")
        print(f"   Recomendado: 20000-50000 caracteres")
        print(f"   Arquivo: src/scraper_unificado.py (linha 549)")
        print()
    
    print(f"2️⃣  Tipos de documentos mais afetados:")
    affected_modules = [m for m, d in by_module.items() if d['truncated'] > 0]
    for module in affected_modules[:3]:
        print(f"   • {module}")
    print()
    
    print(f"3️⃣  Comandos de reparo:\n")
    print(f"   # Editar scraper:")
    print(f"   code src/scraper_unificado.py")
    print(f"")
    print(f"   # Reindexar:")
    print(f"   python reindex_all_docs.py")
    print(f"")
    print(f"   # Reiniciar Docker:")
    print(f"   docker-compose restart mcp-server")

if __name__ == '__main__':
    analyze_truncation()
