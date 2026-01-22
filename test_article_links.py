#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar extração de links em artigos
================================================

Este script demonstra como usar as novas funcionalidades do scraper:
1. parse_senior_doc_link() - Parseia links diretos Senior
2. extract_article_links() - Extrai links de tabelas/funções em artigos
3. scrape_direct_link() - Scrapa um link direto completo

Exemplos de uso:
    python test_article_links.py --direct "https://documentacao.senior.com.br/..."
    python test_article_links.py --parse "https://documentacao.senior.com.br/tecnologia/5.10.4/#lsp/funcoes/gerais.html..."
"""

import asyncio
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from scraper_unificado import SeniorDocScraper

async def test_parse_link(url: str):
    """Testa parsing de link Senior"""
    print("\n" + "="*90)
    print("[TESTE] Parsing de Link Senior")
    print("="*90 + "\n")
    
    scraper = SeniorDocScraper()
    info = scraper.parse_senior_doc_link(url)
    
    print(f"URL Original:")
    print(f"  {url}\n")
    
    print(f"Informações Extraídas:")
    print(f"  Módulo: {info['module']}")
    print(f"  Versão: {info['version']}")
    print(f"  Base URL: {info['base_url']}")
    print(f"  Arquivo: {info['file_path']}")
    print(f"  TocPath: {info['toc_path']}")
    
    if info['breadcrumb']:
        print(f"  Breadcrumb: {' > '.join(info['breadcrumb'])}")
    else:
        print(f"  Breadcrumb: (não encontrado)")
    
    print()

async def test_direct_link(url: str):
    """Testa scraping de link direto"""
    print("\n" + "="*90)
    print("[TESTE] Scraping de Link Direto")
    print("="*90 + "\n")
    
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("[ERRO] Playwright não instalado. Execute: pip install playwright")
        return
    
    scraper = SeniorDocScraper()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        try:
            success = await scraper.scrape_direct_link(url, page)
            
            if success:
                print(f"\n[SUCESSO] Documentos obtidos: {len(scraper.documents)}")
                if scraper.documents:
                    doc = scraper.documents[0]
                    print(f"  Título: {doc['title']}")
                    print(f"  Caracteres: {doc['total_chars']}")
                    print(f"  Headers: {len(doc['headers'])}")
                    print(f"  Links encontrados: {len(doc['links'])}")
            
        finally:
            await browser.close()

async def test_article_links_detection():
    """Demonstra a detecção de links em artigos"""
    print("\n" + "="*90)
    print("[TESTE] Extração de Links de Artigo")
    print("="*90 + "\n")
    
    print("""
Este teste requer uma página carregada com conteúdo.

O método extract_article_links() busca por:
1. Links em tabelas (comum em índices de funções)
2. Links em listas de definição
3. Links em divs de conteúdo (arquivos .htm e .html)

Exemplo de uso em scrape_module():
    article_links = await scraper.extract_article_links(page, absolute_url)
    for link in article_links:
        print(f"  - {link['text']} -> {link['absolute_url']}")
    """)

async def main():
    """Função principal"""
    print("\n" + "="*90)
    print("[TESTE] Novas Funcionalidades do Scraper")
    print("="*90)
    
    # Exemplo de URL Senior (descomente para testar com uma URL real)
    example_url = "https://documentacao.senior.com.br/tecnologia/5.10.4/#lsp/funcoes/gerais.html%3FTocPath%3DTecnologia%7CFerramentas%2520de%2520Apoio%7CLSP%2520-%2520Linguagem%2520Senior%2520de%2520Programa%25C3%25A7%25C3%25A3o%7CFun%25C3%25A7%25C3%25B5es%7CFun%25C3%25A7%25C3%25B5es%2520Gerais%7C_____0"
    
    # Teste 1: Parse de link
    await test_parse_link(example_url)
    
    # Teste 2: Informações sobre extração de artigo
    await test_article_links_detection()
    
    # Teste 3: Scraping de link direto (requer conexão)
    print("\n" + "="*90)
    print("[INFO] Para testar scraping de link direto:")
    print("="*90)
    print("""
    python test_article_links.py --direct "https://documentacao.senior.com.br/..."
    
    Isto irá:
    1. Navegar para a URL especificada
    2. Extrair título, conteúdo e metadados
    3. Extrair links de tabelas/funções
    4. Salvar documentos em docs_estruturado/
    5. Gerar JSONL para indexação
    """)
    
    print("\n" + "="*90)
    print("[INFO] Resumo das Novas Funcionalidades:")
    print("="*90)
    print("""
    1. parse_senior_doc_link(url)
       - Extrai módulo, versão, breadcrumb de URLs Senior diretas
       - Parseia TocPath codificado em URL
    
    2. extract_article_links(page, current_url)
       - 3 estratégias de busca: tabelas, listas, conteúdo
       - Filtra links relativos e constrói URLs absolutas
       - Retorna lista de links com metadata
    
    3. scrape_direct_link(direct_url, page)
       - Scrapa uma URL direta completa
       - Extrai breadcrumb do TocPath
       - Salva documento com metadados
    
    4. scrape_module() melhorado
       - Agora extrai e processa links de artigos automaticamente
       - Scrapa funções/itens linkados em tabelas
       - Aumenta cobertura de documentação
    """)

if __name__ == "__main__":
    asyncio.run(main())
