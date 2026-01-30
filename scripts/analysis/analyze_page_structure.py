#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisa a estrutura real da página para entender como extrair títulos corretamente
"""

import asyncio
from playwright.async_api import async_playwright


async def analyze():
    """Analisa estrutura da página"""
    
    url = "https://documentacao.senior.com.br/gestao-de-pessoas-hcm/6.10.4/#home.htm%3FTocPath%3DGest%25C3%25A3o%2520de%2520Pessoas%2520-%2520Manual%2520do%2520Usu%25C3%25A1rio%7C_____0"
    
    print("\n" + "="*80)
    print("[ANÁLISE] Estrutura da Página")
    print("="*80 + "\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        print(f"Navegando para: {url[:80]}...")
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        await asyncio.sleep(2)
        
        # Analisar estrutura HTML
        structure = await page.evaluate("""
            () => {
                const result = {
                    // Verificar iframes
                    iframes: {
                        total: document.querySelectorAll('iframe').length,
                        ids: Array.from(document.querySelectorAll('iframe')).map(i => i.id || 'sem-id'),
                        details: []
                    },
                    // Título
                    titles: {
                        document_title: document.title,
                        h1: document.querySelector('h1')?.textContent?.trim() || 'NÃO ENCONTRADO',
                        main_title: document.querySelector('main h1')?.textContent?.trim() || 'NÃO ENCONTRADO',
                        page_title: document.querySelector('[class*="title"]')?.textContent?.trim() || 'NÃO ENCONTRADO'
                    },
                    // Estrutura do body
                    body: {
                        text_length: document.body.textContent.length,
                        html_main: document.querySelector('main') ? 'SIM' : 'NÃO',
                        article: document.querySelector('article') ? 'SIM' : 'NÃO',
                        data_role_main: document.querySelector('[data-role="main"]') ? 'SIM' : 'NÃO'
                    },
                    // Buscar h1 em diferentes lugares
                    h1_locations: {
                        'document h1': document.querySelector('h1') ? 'SIM' : 'NÃO',
                        'main h1': document.querySelector('main h1') ? 'SIM' : 'NÃO',
                        'article h1': document.querySelector('article h1') ? 'SIM' : 'NÃO',
                        'iframe h1': []
                    }
                };
                
                // Analisar conteúdo de cada iframe
                document.querySelectorAll('iframe').forEach((iframe, idx) => {
                    try {
                        const content = iframe.contentDocument;
                        if (content) {
                            result.iframes.details.push({
                                id: iframe.id,
                                name: iframe.name,
                                h1: content.querySelector('h1')?.textContent?.trim() || 'NÃO',
                                title: content.querySelector('title')?.textContent || 'NÃO',
                                body_text_length: content.body?.textContent?.length || 0,
                                body_html: content.body?.innerHTML?.substring(0, 200) || 'VAZIO'
                            });
                            
                            if (content.querySelector('h1')) {
                                result.h1_locations['iframe h1'].push(iframe.id);
                            }
                        }
                    } catch (e) {
                        // CORS ou acesso negado
                    }
                });
                
                return result;
            }
        """)
        
        print("📋 IFRAMES:")
        print(f"   Total: {structure['iframes']['total']}")
        print(f"   IDs: {structure['iframes']['ids']}")
        
        if structure['iframes']['details']:
            for detail in structure['iframes']['details']:
                print(f"\n   iframe [{detail['id']}]:")
                print(f"     - Nome: {detail['name']}")
                print(f"     - H1: {detail['h1'][:50] if detail['h1'] != 'NÃO' else 'NÃO ENCONTRADO'}")
                print(f"     - Caracteres: {detail['body_text_length']}")
                print(f"     - HTML (primeiros 200): {detail['body_html'][:100]}...")
        
        print("\n📄 TÍTULOS:")
        for key, value in structure['titles'].items():
            print(f"   {key}: {value[:60] if isinstance(value, str) else value}")
        
        print("\n🏗️  ESTRUTURA DO BODY:")
        for key, value in structure['body'].items():
            print(f"   {key}: {value}")
        
        print("\n🔍 LOCALIZAÇÕES DE H1:")
        for key, value in structure['h1_locations'].items():
            print(f"   {key}: {value}")
        
        # Verificar seletores CSS específicos
        print("\n🎯 SELETORES ESPECÍFICOS:")
        selectors_to_test = [
            'h1',
            'h2',
            '.topic-title',
            '[class*="title"]',
            '[data-title]',
            '.document-header',
            '.page-title',
            '[role="heading"]',
            'iframe#topic [role="heading"]',
            'iframe#topic h1'
        ]
        
        for selector in selectors_to_test:
            count = await page.locator(selector).count()
            if count > 0:
                text = await page.locator(selector).first.text_content()
                print(f"   ✓ '{selector}': {count} elemento(s) | Texto: {text[:60] if text else 'VAZIO'}")
        
        await browser.close()
    
    print("\n" + "="*80)
    print("[✓] ANÁLISE CONCLUÍDA")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(analyze())
