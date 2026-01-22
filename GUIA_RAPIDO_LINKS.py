#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUIA RÁPIDO - Novas Funcionalidades do Scraper
===============================================

Este arquivo mostra exemplos práticos de uso das novas funcionalidades.
"""

# ============================================================================
# 1. PARSING DE LINKS DIRETOS SENIOR
# ============================================================================

from src.scraper_unificado import SeniorDocScraper

scraper = SeniorDocScraper()

# Exemplo 1: Parsear um link direto
url = "https://documentacao.senior.com.br/tecnologia/5.10.4/#lsp/funcoes/gerais.html%3FTocPath%3DTecnologia%7CFerramentas%2520de%2520Apoio%7CLSP%2520-%2520Linguagem%2520Senior%2520de%2520Programa%25C3%25A7%25C3%25A3o%7CFun%25C3%25A7%25C3%25B5es%7CFun%25C3%25A7%25C3%25B5es%2520Gerais%7C_____0"

info = scraper.parse_senior_doc_link(url)

print("=" * 80)
print("1. PARSING DE LINK DIRETO")
print("=" * 80)
print(f"Módulo: {info['module']}")
print(f"Versão: {info['version']}")
print(f"Arquivo: {info['file_path']}")
print(f"Breadcrumb: {' > '.join(info['breadcrumb'])}")
print()

# ============================================================================
# 2. IDENTIFICAR SE É LINK SENIOR
# ============================================================================

print("=" * 80)
print("2. IDENTIFICAR LINK SENIOR")
print("=" * 80)

is_senior_link = scraper.identify_senior_doc_links(url)
print(f"É um link Senior? {is_senior_link}")
print()

# ============================================================================
# 3. SCRAPING ASSÍNCRONO - Exemplo de uso
# ============================================================================

print("=" * 80)
print("3. SCRAPING ASSÍNCRONO - Como usar")
print("=" * 80)

async_example = """
import asyncio
from playwright.async_api import async_playwright
from src.scraper_unificado import SeniorDocScraper

async def scrape_exemplo():
    scraper = SeniorDocScraper()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Opção 1: Scraping direto de um link
        url = "https://documentacao.senior.com.br/tecnologia/5.10.4/#..."
        success = await scraper.scrape_direct_link(url, page)
        
        if success:
            print(f"Documentos obtidos: {len(scraper.documents)}")
        
        # Opção 2: Scraping de um módulo (agora com extração de links)
        base_url = "https://documentacao.senior.com.br/tecnologia/5.10.4/"
        await scraper.scrape_module("TECNOLOGIA", base_url, page)
        
        # Gerar arquivo JSONL para indexação
        jsonl_file = scraper.generate_jsonl()
        print(f"JSONL gerado: {jsonl_file}")
        
        await browser.close()

# Executar
asyncio.run(scrape_exemplo())
"""

print(async_example)
print()

# ============================================================================
# 4. EXTRAÇÃO DE LINKS DE ARTIGOS
# ============================================================================

print("=" * 80)
print("4. EXTRAÇÃO DE LINKS DE ARTIGOS (Assíncrono)")
print("=" * 80)

extract_example = """
# Este método é usado automaticamente por scrape_module()
# Mas você pode usá-lo diretamente também:

async def extract_links_exemplo(page, url):
    scraper = SeniorDocScraper()
    
    # Navegar até a página
    await page.goto(url, wait_until="networkidle", timeout=20000)
    await asyncio.sleep(1)
    
    # Extrair links
    links = await scraper.extract_article_links(page, url)
    
    print(f"Encontrados {len(links)} links:")
    for link in links:
        print(f"  - {link['text']}")
        print(f"    URL: {link['absolute_url']}")
        print(f"    Tipo: {link['type']}")
        print()

# Links encontrados podem ser:
# - table_link: Links em tabelas (comum em índices de funções)
# - list_link: Links em listas de definição
# - content_link: Links em divs de conteúdo
"""

print(extract_example)
print()

# ============================================================================
# 5. FLUXO COMPLETO
# ============================================================================

print("=" * 80)
print("5. FLUXO COMPLETO - PASSO A PASSO")
print("=" * 80)

flow = """
MÉTODO 1: Scraping de um módulo (recomendado)
=============================================

import asyncio
from playwright.async_api import async_playwright
from src.scraper_unificado import SeniorDocScraper

async def scrape_tecnologia():
    scraper = SeniorDocScraper()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        # Scraping do módulo TECNOLOGIA
        base_url = "https://documentacao.senior.com.br/tecnologia/5.10.4/"
        await scraper.scrape_module("TECNOLOGIA", base_url, page)
        
        print(f"Total de documentos: {len(scraper.documents)}")
        
        # Gerar JSONL
        jsonl_file = scraper.generate_jsonl()
        print(f"Arquivo gerado: {jsonl_file}")
        
        await browser.close()

asyncio.run(scrape_tecnologia())


MÉTODO 2: Scraping direto de um link específico
================================================

async def scrape_link_direto():
    scraper = SeniorDocScraper()
    url = "https://documentacao.senior.com.br/tecnologia/5.10.4/#lsp/funcoes/gerais.html..."
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        success = await scraper.scrape_direct_link(url, page)
        
        if success:
            print(f"Documentos obtidos: {len(scraper.documents)}")
            # Salvar um a um ou gerar JSONL
        
        await browser.close()

asyncio.run(scrape_link_direto())
"""

print(flow)
print()

# ============================================================================
# 6. ESTRUTURA DE DADOS RETORNADOS
# ============================================================================

print("=" * 80)
print("6. ESTRUTURA DE DADOS RETORNADOS")
print("=" * 80)

structures = """
parse_senior_doc_link() retorna:
{
    'base_url': 'https://documentacao.senior.com.br/tecnologia/5.10.4/',
    'module': 'tecnologia',
    'version': '5.10.4',
    'file_path': 'lsp/funcoes/gerais.html',
    'toc_path': 'Tecnologia|Ferramentas de Apoio|LSP - Linguagem Senior...',
    'breadcrumb': ['Tecnologia', 'Ferramentas de Apoio', 'LSP - Linguagem...']
}

extract_article_links() retorna:
[
    {
        'text': 'AlfaParaInt',
        'href': 'gerais/alfaparaint.htm',
        'absolute_url': 'https://documentacao.senior.com.br/tecnologia/5.10.4/lsp/funcoes/gerais/alfaparaint.htm',
        'type': 'table_link'
    },
    {
        'text': 'ArqExiste',
        'href': 'gerais/arqexiste.htm',
        'absolute_url': 'https://documentacao.senior.com.br/tecnologia/5.10.4/lsp/funcoes/gerais/arqexiste.htm',
        'type': 'table_link'
    },
    ...
]

scraper.documents contém:
[
    {
        'title': 'Funções Gerais',
        'url': 'https://documentacao.senior.com.br/tecnologia/5.10.4/#...',
        'breadcrumb': ['TECNOLOGIA', 'Ferramentas de Apoio', 'LSP', 'Funções', 'Funções Gerais'],
        'text_content': '... conteúdo da página (50K chars) ...',
        'total_chars': 12345,
        'headers': ['Funções Gerais', 'Nome', 'Descrição'],
        'paragraphs': [...],
        'lists': [...],
        'links': [...]
    },
    {
        'title': 'AlfaParaInt',
        'url': 'https://documentacao.senior.com.br/tecnologia/5.10.4/lsp/funcoes/gerais/alfaparaint.htm',
        'breadcrumb': ['TECNOLOGIA', 'Ferramentas de Apoio', 'LSP', 'Funções', 'Funções Gerais', 'AlfaParaInt'],
        'text_content': '... documentação da função AlfaParaInt ...',
        'total_chars': 5678,
        ...
    },
    ...
]
"""

print(structures)
print()

# ============================================================================
# 7. TESTES
# ============================================================================

print("=" * 80)
print("7. TESTES DISPONÍVEIS")
print("=" * 80)

tests = """
# Testar parsing de links
python test_parse_link.py

# Testar todas as funcionalidades
python test_article_links.py

# Testar com URL real (requer conexão)
python test_article_links.py --direct "https://documentacao.senior.com.br/..."
"""

print(tests)
print()

# ============================================================================
# 8. DICAS E BOAS PRÁTICAS
# ============================================================================

print("=" * 80)
print("8. DICAS E BOAS PRÁTICAS")
print("=" * 80)

tips = """
✓ Use scrape_module() para scraping completo de um módulo
  - Detecta automaticamente links em artigos
  - Scrapa subpáginas com breadcrumb expandido
  - Maior cobertura de documentação

✓ Use parse_senior_doc_link() para análise de URLs
  - Pode ser usado para construir URLs dinamicamente
  - Extrai metadados sem fazer scraping
  - Útil para validar links

✓ Personalize extract_article_links() se necessário
  - Modifique as estratégias de busca no JavaScript
  - Adicione filtros específicos se houver muito ruído
  - Retorna links com tipo para processamento diferenciado

✓ Configure timeouts apropriados
  - MadCap Flare: 20s (iframes demoram)
  - Astro moderno: 10-15s
  - Fallback para domcontentloaded

✓ Use breadcrumb expandido para organização
  - Facilita busca hierárquica
  - Melhora contexto em resultados de busca
  - Permite navegação estruturada

✓ Monitore estatísticas
  scraper.metadata['statistics'] contém:
  - total_pages: Total de páginas scraped
  - total_chars: Total de caracteres indexados
  - by_module: Estatísticas por módulo
  - navigation_stats: Sucessos/falhas de navegação
"""

print(tips)
print()

print("=" * 80)
print("FIM DO GUIA RÁPIDO")
print("=" * 80)
print()
print("Para mais detalhes, consulte: SUPORTE_LINKS_ARTIGOS.md")
