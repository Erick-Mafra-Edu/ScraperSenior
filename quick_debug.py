#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QUICK DEBUG - Validação rápida do scraper
Testa navegação e extração sem processar muitas páginas
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def quick_debug():
    """Debug rápido"""
    
    print("\n" + "="*80)
    print("[QUICK DEBUG] Validação do Caminho de Scraping")
    print("="*80 + "\n")
    
    # Carregar um módulo
    modulos_file = Path("modulos_descobertos.json")
    with open(modulos_file) as f:
        modulos = json.load(f)
    
    # Usar GESTAO DE PESSOAS HCM (tem notas de versão)
    module_name = "GESTAO DE PESSOAS HCM"
    base_url = modulos[module_name]['url']
    
    print(f"[1] Iniciando teste com: {module_name}")
    print(f"    URL: {base_url}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        # PASSO 1: Navegar
        print("[2] Navegando para página...")
        try:
            await page.goto(base_url, wait_until="domcontentloaded", timeout=15000)
            print("    ✓ Página carregada com sucesso")
        except Exception as e:
            print(f"    ✗ Erro: {e}")
            await browser.close()
            return
        
        await asyncio.sleep(2)
        
        # PASSO 2: Verificar tipo de documentação
        print("\n[3] Detectando tipo de documentação...")
        doc_type_info = await page.evaluate("""
            () => {
                const info = {
                    has_madcap_toc: !!document.getElementById('toc'),
                    has_astro_sidebar: !!document.getElementById('sidebar-menu'),
                    has_madcap_topic: !!document.getElementById('topic'),
                    title: document.title,
                    url: window.location.href,
                    is_release_notes: (
                        document.title.toLowerCase().includes('versão') ||
                        window.location.href.toLowerCase().includes('notas-da-versao')
                    )
                };
                return info;
            }
        """)
        
        print(f"    Tipo: {'MadCap' if doc_type_info['has_madcap_toc'] else 'Astro' if doc_type_info['has_astro_sidebar'] else 'Desconhecido'}")
        print(f"    Título: {doc_type_info['title'][:60]}")
        print(f"    É notas de versão? {doc_type_info['is_release_notes']}")
        print(f"    URL atual: {doc_type_info['url'][:80]}")
        
        # PASSO 3: Verificar menus
        print("\n[4] Verificando menus/navegação...")
        menu_info = await page.evaluate("""
            () => {
                const info = {
                    toc: document.getElementById('toc'),
                    collapsed_items: 0,
                    expanded_items: 0,
                    visible_links: 0,
                    total_links: 0
                };
                
                const toc = document.getElementById('toc');
                if (toc) {
                    info.collapsed_items = toc.querySelectorAll('li.tree-node-collapsed').length;
                    info.expanded_items = toc.querySelectorAll('li.tree-node-expanded').length;
                    info.visible_links = Array.from(toc.querySelectorAll('a[href]'))
                        .filter(a => a.offsetParent !== null).length;
                    info.total_links = toc.querySelectorAll('a[href]').length;
                }
                
                return info;
            }
        """)
        
        print(f"    Itens collapsed: {menu_info['collapsed_items']}")
        print(f"    Itens expanded: {menu_info['expanded_items']}")
        print(f"    Links visíveis: {menu_info['visible_links']}")
        print(f"    Links totais: {menu_info['total_links']}")
        
        # PASSO 4: Expandir um nível de menus
        if menu_info['collapsed_items'] > 0:
            print(f"\n[5] Expandindo menus (até 3 rodadas)...")
            for rodada in range(3):
                clicked = await page.evaluate("""
                    () => {
                        const toc = document.getElementById('toc');
                        if (!toc) return 0;
                        
                        const collapsed = toc.querySelectorAll('li.tree-node-collapsed');
                        let count = 0;
                        
                        // Clicar apenas nos primeiros 5
                        Array.from(collapsed).slice(0, 5).forEach(item => {
                            const link = item.querySelector('a');
                            if (link && !link.getAttribute('href').startsWith('javascript')) {
                                link.click();
                                count++;
                            }
                        });
                        
                        return count;
                    }
                """)
                
                print(f"    Rodada {rodada + 1}: {clicked} itens clicados")
                if clicked == 0:
                    print(f"    ✓ Menus totalmente expandidos")
                    break
                
                await asyncio.sleep(0.5)
        
        # PASSO 5: Extrair links
        print("\n[6] Extraindo links de navegação...")
        links_info = await page.evaluate("""
            () => {
                const toc = document.getElementById('toc');
                if (!toc) return { total: 0, links: [] };
                
                const links = [];
                const seen = new Set();
                
                toc.querySelectorAll('a[href*="#"]').forEach(a => {
                    const href = a.getAttribute('href');
                    const text = a.textContent.trim();
                    
                    if (href && text && !seen.has(href)) {
                        links.push({
                            text: text.substring(0, 50),
                            href: href.substring(0, 80),
                            visible: a.offsetParent !== null,
                            parent_level: a.closest('li')?.querySelectorAll(':scope > ul li').length || 0
                        });
                        seen.add(href);
                    }
                });
                
                return { total: links.length, links: links.slice(0, 5) };
            }
        """)
        
        print(f"    Total de links encontrados: {links_info['total']}")
        print(f"    Primeiros 5 links:")
        for i, link in enumerate(links_info['links'], 1):
            visibility = "✓ visível" if link['visible'] else "✗ oculto"
            print(f"      {i}. {link['text'][:40]} ({visibility})")
            print(f"         href: {link['href']}")
        
        # PASSO 6: Testar scraping de um link
        print(f"\n[7] Testando scraping de uma página...")
        if links_info['links']:
            test_link = links_info['links'][0]
            test_url = base_url + test_link['href'] if test_link['href'].startswith('#') else test_link['href']
            
            print(f"    URL de teste: {test_url}")
            
            try:
                await page.goto(test_url, wait_until="domcontentloaded", timeout=10000)
                await asyncio.sleep(1)
                
                content_info = await page.evaluate("""
                    () => {
                        let main = document.querySelector('iframe#topic')?.contentDocument?.body;
                        if (!main) main = document.querySelector('main') || document.querySelector('[role="main"]') || document.body;
                        
                        return {
                            title: document.querySelector('h1')?.textContent?.trim() || 'Sem título',
                            chars: main.textContent.length,
                            headers: main.querySelectorAll('h2, h3, h4').length,
                            paragraphs: main.querySelectorAll('p').length,
                            images: main.querySelectorAll('img').length,
                            buttons: document.querySelectorAll('button').length,
                            forms: document.querySelectorAll('form').length
                        };
                    }
                """)
                
                print(f"    ✓ Página scrapada com sucesso")
                print(f"      Título: {content_info['title'][:50]}")
                print(f"      Caracteres: {content_info['chars']}")
                print(f"      Headers: {content_info['headers']}")
                print(f"      Parágrafos: {content_info['paragraphs']}")
                print(f"      Imagens: {content_info['images']}")
                print(f"      Botões: {content_info['buttons']}")
                print(f"      Formulários: {content_info['forms']}")
                
            except Exception as e:
                print(f"    ✗ Erro ao scraping: {e}")
        
        await browser.close()
    
    print("\n" + "="*80)
    print("[✓] DEBUG CONCLUÍDO")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(quick_debug())
