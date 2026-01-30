#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Scraper com MCP: Valida Títulos + Notas de Versão
"""

import asyncio
import json
from pathlib import Path
from src.scraper_unificado import SeniorDocScraper
from playwright.async_api import async_playwright


async def test_mcp_with_release_notes():
    """Testa scraper, indexação e busca de notas de versão"""
    
    print("\n" + "="*80)
    print("🧪 TESTE MCP - Títulos + Notas de Versão")
    print("="*80 + "\n")
    
    # Carregar módulos
    with open("modulos_descobertos.json") as f:
        modulos = json.load(f)
    
    # PASSO 1: Executar scraper
    print("📍 PASSO 1: Scrapeando com Títulos Corrigidos\n")
    
    scraper = SeniorDocScraper()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        # Scrape do módulo
        module_name = "GESTAO DE PESSOAS HCM"
        base_url = modulos[module_name]['url']
        
        print(f"   Módulo: {module_name}")
        print(f"   URL: {base_url}\n")
        
        await scraper.scrape_module(module_name, base_url, page)
        
        # Coletar documentos do scraper
        docs = scraper.documents
        
        print(f"\n   ✓ {len(docs)} documentos scrapados\n")
        
        await browser.close()
    
    # PASSO 2: Análise de Títulos
    print("\n📍 PASSO 2: Análise de Títulos Capturados\n")
    
    docs_with_titles = [d for d in docs if d.get('title', '').strip()]
    docs_without_titles = len(docs) - len(docs_with_titles)
    
    print(f"   ✓ Documentos com título: {len(docs_with_titles)}/{len(docs)} ({len(docs_with_titles)*100//len(docs)}%)")
    if docs_without_titles > 0:
        print(f"   ✗ Documentos sem título: {docs_without_titles}")
    
    print(f"\n   📝 Exemplos de títulos capturados:")
    for doc in docs_with_titles[:5]:
        print(f"      • {doc['title'][:70]}")
        print(f"        URL: {doc['url'][:80]}")
    
    # PASSO 3: Busca de Notas de Versão
    print(f"\n📍 PASSO 3: Procurando Notas de Versão\n")
    
    keywords = [
        ('versão', 'Documentos com "versão"'),
        ('notas', 'Documentos com "notas"'),
        ('release', 'Documentos com "release"'),
        ('6.10', 'Documentos com "6.10"'),
    ]
    
    for keyword, description in keywords:
        matching = [
            d for d in docs
            if keyword.lower() in d.get('title', '').lower() or
               keyword.lower() in d.get('url', '').lower()
        ]
        
        if matching:
            print(f"   🔍 {description}: {len(matching)}")
            for doc in matching[:2]:
                print(f"      • {doc['title'][:60]}")
        else:
            print(f"   ℹ️  {description}: 0")
    
    # PASSO 4: Estatísticas
    print(f"\n📍 PASSO 4: Estatísticas Gerais\n")
    
    avg_title = sum(len(d.get('title', '')) for d in docs) / len(docs) if docs else 0
    avg_content = sum(d.get('total_chars', 0) for d in docs) / len(docs) if docs else 0
    
    print(f"   📊 Total de documentos: {len(docs)}")
    print(f"   📊 Média de caracteres por título: {avg_title:.0f}")
    print(f"   📊 Média de caracteres por documento: {avg_content:.0f}")
    
    # Encontrar documentos com mais conteúdo
    largest_docs = sorted(docs, key=lambda d: d.get('total_chars', 0), reverse=True)[:3]
    print(f"\n   📄 Documentos maiores:")
    for doc in largest_docs:
        print(f"      • {doc['title'][:50]}: {doc['total_chars']} chars")
    
    # PASSO 5: Preparar para MCP
    print(f"\n📍 PASSO 5: Preparando para MCP\n")
    
    # Salvar em JSONL para indexação
    output_file = Path("docs_para_mcp.jsonl")
    with open(output_file, 'w', encoding='utf-8') as f:
        for doc in docs:
            f.write(json.dumps(doc, ensure_ascii=False) + '\n')
    
    print(f"   ✓ {len(docs)} documentos salvos em: {output_file}")
    print(f"   ✓ Pronto para indexação no MCP\n")
    
    # Próximas ações
    print("="*80)
    print("✅ TESTE CONCLUÍDO COM SUCESSO")
    print("="*80)
    print("\n📋 PRÓXIMAS AÇÕES:")
    print("   1. python src/indexers/index_all_docs.py")
    print("   2. docker-compose restart mcp-server")
    print("   3. curl http://localhost:8000/search?q=notas%20de%20versao\n")
    
    return docs


if __name__ == "__main__":
    asyncio.run(test_mcp_with_release_notes())
