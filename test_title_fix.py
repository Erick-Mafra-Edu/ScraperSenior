#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testa a extração de títulos corrigida
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def test_title_extraction():
    """Testa extração de título com o novo código"""
    
    # Carregar módulos
    with open("modulos_descobertos.json") as f:
        modulos = json.load(f)
    
    module_name = "GESTAO DE PESSOAS HCM"
    base_url = modulos[module_name]['url']
    
    print("\n" + "="*80)
    print("[TESTE] Extração de Títulos - Código Corrigido")
    print("="*80 + "\n")
    
    urls_to_test = [
        f"{base_url}#home.htm%3FTocPath%3DGest%25C3%25A3o%2520de%2520Pessoas%2520-%2520Manual%2520do%2520Usu%25C3%25A1rio%7C_____0",
        f"{base_url}#manual-processos/gestao-de-pessoas.htm%3FTocPath%3DGest%25C3%25A3o%2520de%2520Pessoas%2520-%2520Manual%2520do%2520Usu%25C3%25A1rio%7CManual%2520por%2520processos%7C_____0",
    ]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        for idx, url in enumerate(urls_to_test, 1):
            print(f"[{idx}] Testando URL:")
            print(f"    {url[:80]}...")
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                await asyncio.sleep(1)
                
                # Usar o NOVO código de extração
                content = await page.evaluate("""
                    () => {
                        // Função auxiliar para extrair título (NOVO CÓDIGO)
                        const extractTitle = () => {
                            // Primeiro, tentar encontrar h1 dentro do iframe#topic
                            try {
                                const iframeTitle = document.querySelector('iframe#topic')?.contentDocument
                                    ?.querySelector('h1')?.textContent?.trim();
                                if (iframeTitle) return iframeTitle;
                            } catch (e) {
                                // CORS ou iframe não acessível
                            }
                            
                            // Se não encontrou no iframe, tentar h1 no document raiz
                            const h1 = document.querySelector('h1')?.textContent?.trim();
                            if (h1) return h1;
                            
                            // Fallback para document.title
                            const docTitle = document.title?.trim();
                            if (docTitle && docTitle.length > 0) return docTitle;
                            
                            // Último recurso: tentar qualquer h2 se não houver h1
                            const h2 = document.querySelector('h2')?.textContent?.trim();
                            if (h2) return h2;
                            
                            return 'SEM TÍTULO';
                        };
                        
                        return {
                            title: extractTitle(),
                            chars: document.body.textContent.length
                        };
                    }
                """)
                
                print(f"    ✓ Título: {content['title'][:70]}")
                print(f"    ✓ Caracteres: {content['chars']}")
                print()
                
            except Exception as e:
                print(f"    ✗ Erro: {e}\n")
        
        await browser.close()
    
    print("="*80)
    print("[✓] TESTE CONCLUÍDO")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_title_extraction())
