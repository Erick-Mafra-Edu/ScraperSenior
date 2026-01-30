#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Executa o scraper com as novas alterações
Testa um módulo completo para validar que títulos estão sendo capturados
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright
from src.scraper_unificado import SeniorDocScraper


async def execute_scraper_with_fix():
    """Executa scraper com alterações"""
    
    print("\n" + "="*80)
    print("[EXECUÇÃO] Scraper com Correção de Títulos")
    print("="*80 + "\n")
    
    # Carregar módulos
    modulos_file = Path("modulos_descobertos.json")
    with open(modulos_file) as f:
        modulos = json.load(f)
    
    scraper = SeniorDocScraper()
    
    # Testar módulo GESTAO DE PESSOAS HCM (maior, melhor para teste)
    module_name = "GESTAO DE PESSOAS HCM"
    base_url = modulos[module_name]['url']
    
    print(f"🔄 Scraping do módulo: {module_name}")
    print(f"📍 URL base: {base_url}")
    print(f"⏱️  Iniciando...\n")
    
    try:
        # Usar Playwright para criar a página
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1920, "height": 1080})
            
            try:
                await scraper.scrape_module(module_name, base_url, page)
                
                docs = scraper.documents  # Pega os documentos coletados
                
                print(f"\n✅ SCRAPING CONCLUÍDO!")
                print(f"📊 Total de documentos: {len(docs)}")
                
                # Análise de títulos
                docs_with_title = sum(1 for doc in docs if doc.get('title', '').strip())
                docs_without_title = len(docs) - docs_with_title
                
                print(f"\n📝 ANÁLISE DE TÍTULOS:")
                print(f"   ✅ Com título: {docs_with_title}/{len(docs)} ({100*docs_with_title/len(docs):.1f}%)")
                print(f"   ❌ Sem título: {docs_without_title}")
                
                # Mostrar estatísticas de conteúdo
                print(f"\n📈 CONTEÚDO CAPTURADO:")
                
                total_chars = sum(len(doc.get('text_content', '')) for doc in docs)
                avg_chars = total_chars // len(docs) if docs else 0
                
                print(f"   Total de caracteres: {total_chars:,}")
                print(f"   Média por documento: {avg_chars:,}")
                
                # Headers
                total_headers = sum(len(doc.get('headers', [])) for doc in docs)
                print(f"   Total de headers: {total_headers}")
                
                # Links
                total_links = sum(len(doc.get('links', [])) for doc in docs)
                print(f"   Total de links: {total_links}")
                
                # Listar primeiros 10 documentos com títulos
                print(f"\n📄 PRIMEIROS 10 DOCUMENTOS:")
                print(f"{'#':<3} {'Título':<50} {'Chars':<8} {'Headers':<8}")
                print("-" * 75)
                
                for idx, doc in enumerate(docs[:10], 1):
                    title = doc.get('title', 'SEM TÍTULO')[:48]
                    chars = len(doc.get('text_content', ''))
                    headers = len(doc.get('headers', []))
                    print(f"{idx:<3} {title:<50} {chars:<8} {headers:<8}")
                
                # Buscar documento mais longo
                if docs:
                    longest = max(docs, key=lambda d: len(d.get('text_content', '')))
                    print(f"\n🏆 MAIOR DOCUMENTO:")
                    print(f"   Título: {longest.get('title', 'SEM TÍTULO')[:70]}")
                    print(f"   Caracteres: {len(longest.get('text_content', ''))}")
                    print(f"   URL: {longest.get('url', '')[:70]}")
                
                # Listar títulos únicos (amostra)
                unique_titles = set(doc.get('title', '') for doc in docs)
                print(f"\n🏷️  TÍTULOS ÚNICOS: {len(unique_titles)}")
                print("   Amostra de títulos:")
                for title in list(unique_titles)[:5]:
                    if title.strip():
                        print(f"     ✓ {title[:60]}")
                
            finally:
                await browser.close()
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("[✓] EXECUÇÃO CONCLUÍDA")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(execute_scraper_with_fix())
