#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste integrado: Scraper + Busca de Notas de Versão
Valida títulos capturados e procura por release notes
"""

import asyncio
import json
from pathlib import Path
from src.scraper_unificado import SeniorDocScraper
from playwright.async_api import async_playwright


async def test_scraper_with_titles():
    """
    1. Executa scraper com correção de títulos
    2. Testa busca por notas de versão
    """
    
    print("\n" + "="*80)
    print("[TESTE INTEGRADO] Scraper + Títulos + Notas de Versão")
    print("="*80 + "\n")
    
    # Carregar módulos
    with open("modulos_descobertos.json") as f:
        modulos = json.load(f)
    
    scraper = SeniorDocScraper()
    all_docs = []
    
    # PASSO 1: Scrape com novo código
    print("📍 PASSO 1: Executando Scraper com Correção de Títulos\n")
    
    modules_to_test = ["GESTAO DE PESSOAS HCM"]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        for module_name in modules_to_test:
            if module_name not in modulos:
                print(f"   ⏭️  Pulando {module_name} (não encontrado)")
                continue
            
            base_url = modulos[module_name]['url']
            print(f"   🔄 Scraping: {module_name}")
            print(f"      URL: {base_url[:60]}...")
            
            try:
                docs = await scraper.scrape_module(module_name, base_url, page)
                
                if not docs:
                    print(f"      ⚠️  Scraper retornou None ou lista vazia")
                    continue
                
                all_docs.extend(docs)
                
                # Análise de títulos
                with_titles = sum(1 for doc in docs if doc.get('title', '').strip())
                without_titles = len(docs) - with_titles
                
                print(f"      ✓ {len(docs)} documentos capturados")
                print(f"      ✓ {with_titles} com títulos")
                if without_titles > 0:
                    print(f"      ✗ {without_titles} sem títulos")
                
                # Mostrar exemplos
                print(f"\n      📝 Exemplos de títulos capturados:")
                for doc in docs[:5]:
                    title = doc.get('title', 'SEM TÍTULO')[:60]
                    chars = doc.get('text_content', '')[:40]
                    print(f"         • {title}")
                    if chars:
                        print(f"           Preview: {chars}...")
                
            except Exception as e:
                print(f"      ✗ Erro: {e}")
        
        await browser.close()
    
    # PASSO 2: Testar busca de notas de versão
    print(f"\n\n📍 PASSO 2: Testando Busca de Notas de Versão\n")
    
    # Procurar por documentos relacionados a versões
    release_keywords = ['versão', 'notas de versão', 'release notes', 'v6', '6.10']
    
    for keyword in release_keywords:
        matching_docs = [
            doc for doc in all_docs 
            if keyword.lower() in doc.get('title', '').lower() or
               keyword.lower() in doc.get('url', '').lower()
        ]
        
        if matching_docs:
            print(f"   🔍 Busca por '{keyword}':")
            print(f"      Encontrados: {len(matching_docs)} documento(s)")
            for doc in matching_docs[:3]:
                print(f"         • {doc.get('title', 'SEM TÍTULO')}")
                print(f"           URL: {doc.get('url', 'N/A')[:70]}")
    
    # PASSO 3: Análise de qualidade
    print(f"\n\n📍 PASSO 3: Análise de Qualidade dos Dados\n")
    
    if all_docs:
        # Estatísticas
        avg_title_len = sum(len(doc.get('title', '')) for doc in all_docs) / len(all_docs)
        avg_content_len = sum(len(doc.get('text_content', '')) for doc in all_docs) / len(all_docs)
        docs_with_title = sum(1 for doc in all_docs if doc.get('title', '').strip())
        docs_with_content = sum(1 for doc in all_docs if doc.get('text_content', '').strip())
        
        print(f"   📊 Estatísticas Gerais:")
        print(f"      • Total de documentos: {len(all_docs)}")
        print(f"      • Documentos com título: {docs_with_title}/{len(all_docs)} ({docs_with_title*100//len(all_docs)}%)")
        print(f"      • Documentos com conteúdo: {docs_with_content}/{len(all_docs)} ({docs_with_content*100//len(all_docs)}%)")
        print(f"      • Comprimento médio título: {avg_title_len:.0f} caracteres")
        print(f"      • Comprimento médio conteúdo: {avg_content_len:.0f} caracteres")
        
        # Verificação de release notes
        release_notes_docs = [
            doc for doc in all_docs
            if 'versão' in doc.get('title', '').lower() or
               'notas' in doc.get('title', '').lower() or
               'release' in doc.get('title', '').lower()
        ]
        
        print(f"\n   📦 Documentos de Release Notes:")
        print(f"      • Total encontrados: {len(release_notes_docs)}")
        if release_notes_docs:
            for doc in release_notes_docs[:3]:
                print(f"         ✓ {doc.get('title', 'SEM TÍTULO')}")
        else:
            print(f"         ℹ️  Nenhum documento específico de release notes nesta busca")
    
    print("\n" + "="*80)
    print("[✓] TESTE CONCLUÍDO COM SUCESSO")
    print("="*80 + "\n")
    
    return all_docs


if __name__ == "__main__":
    docs = asyncio.run(test_scraper_with_titles())
    
    if docs:
        print("📝 PRÓXIMOS PASSOS:")
        print("   1. Indexar documentos: python src/indexers/index_all_docs.py")
        print("   2. Reiniciar MCP: docker-compose restart mcp-server")
        print("   3. Testar MCP: python test_mcp_search.py")
