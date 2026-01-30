#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEBUG SCRAPER - Rastreamento Detalhado do Scraping
Mostra cada passo, botões clicados, links encontrados, etc.
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from src.scraper_unificado import SeniorDocScraper
from playwright.async_api import async_playwright
import sys


class DebugScraper(SeniorDocScraper):
    """Scraper com debug detalhado"""
    
    def __init__(self, save_html=False, debug=True):
        super().__init__(save_html=save_html)
        self.debug = debug
        self.debug_log = []
        self.click_count = 0
        self.link_count = 0
    
    def log_debug(self, level: str, message: str, data: dict = None):
        """Registra mensagem de debug"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message,
            'data': data
        }
        self.debug_log.append(log_entry)
        
        # Exibir em tempo real
        prefix = {
            'INFO': '📌',
            'DEBUG': '🔍',
            'SUCCESS': '✓',
            'WARNING': '⚠️',
            'ERROR': '❌'
        }.get(level, '•')
        
        print(f"[{timestamp}] {prefix} {level:<8} {message}")
        if data:
            for key, val in data.items():
                print(f"        └─ {key}: {val}")
    
    async def scrape_page_debug(self, page, url: str, base_url: str = None):
        """Scrapa página com debug detalhado"""
        self.log_debug('DEBUG', f'Navegando para página', {'url': url})
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            self.log_debug('SUCCESS', 'Página carregada com sucesso')
        except Exception as e:
            self.log_debug('ERROR', 'Falha ao carregar página', {'erro': str(e)})
            return None
        
        # Aguardar iframe carregar se MadCap
        await asyncio.sleep(1)
        
        # Extrair conteúdo
        content = await page.evaluate("""
            () => {
                const result = {
                    title: document.querySelector('h1')?.textContent?.trim() || 'Sem título',
                    url: window.location.href,
                    text_content: '',
                    total_chars: 0,
                    headers: [],
                    links: [],
                    buttons: [],
                    forms: [],
                    menus: []
                };
                
                // Procurar conteúdo principal
                let main = document.querySelector('iframe#topic')?.contentDocument?.body;
                if (!main) {
                    main = document.querySelector('main') || 
                           document.querySelector('[role="main"]') ||
                           document.querySelector('article') ||
                           document.querySelector('[class*="content"]');
                }
                
                if (!main) main = document.body;
                
                result.text_content = main.textContent;
                result.total_chars = result.text_content.length;
                
                // Headers
                main.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(h => {
                    const text = h.textContent.trim();
                    if (text) result.headers.push(text);
                });
                
                // Links
                document.querySelectorAll('a[href]').forEach(a => {
                    const href = a.getAttribute('href');
                    const text = a.textContent.trim();
                    if (text && text.length > 0) {
                        result.links.push({
                            text: text.substring(0, 50),
                            href: href,
                            type: href.startsWith('#') ? 'anchor' : 'external'
                        });
                    }
                });
                
                // Botões
                document.querySelectorAll('button').forEach(btn => {
                    const text = btn.textContent.trim();
                    if (text) result.buttons.push(text.substring(0, 50));
                });
                
                // Forms
                document.querySelectorAll('form').forEach((form, idx) => {
                    const inputs = form.querySelectorAll('input, select, textarea').length;
                    result.forms.push({
                        index: idx,
                        inputs: inputs,
                        id: form.id || 'sem-id'
                    });
                });
                
                // Menus/Navs
                document.querySelectorAll('nav, [role="navigation"], .menu, .sidebar').forEach((nav, idx) => {
                    result.menus.push({
                        index: idx,
                        id: nav.id || nav.className || 'menu-' + idx,
                        items: nav.querySelectorAll('li, a').length
                    });
                });
                
                return result;
            }
        """)
        
        # Logar achados
        if content:
            self.log_debug('SUCCESS', f'Conteúdo extraído', {
                'título': content['title'][:50],
                'caracteres': content['total_chars'],
                'headers': len(content['headers']),
                'links': len(content['links']),
                'botões': len(content['buttons']),
                'formulários': len(content['forms']),
                'menus': len(content['menus'])
            })
            
            if content['links']:
                self.log_debug('DEBUG', 'Links encontrados (primeiros 5):', {
                    'total': len(content['links']),
                    'primeiro': content['links'][0] if content['links'] else None
                })
                self.link_count += len(content['links'])
            
            if content['buttons']:
                self.log_debug('DEBUG', f'Botões encontrados: {len(content["buttons"])}', {
                    'botões': ', '.join(content['buttons'][:3])
                })
            
            if content['menus']:
                self.log_debug('DEBUG', 'Menus/Navegações encontradas:', {
                    'total': len(content['menus']),
                    'items': ', '.join(str(m['items']) for m in content['menus'][:3])
                })
        
        return content
    
    async def expand_menus_debug(self, page):
        """Expande menus com log detalhado"""
        self.log_debug('INFO', 'Iniciando expansão de menus')
        
        for round_num in range(5):
            collapsed_count = await page.evaluate("""
                () => {
                    const toc = document.getElementById('toc');
                    if (!toc) return 0;
                    
                    const collapsed = toc.querySelectorAll('li.tree-node-collapsed');
                    let clicked = 0;
                    
                    collapsed.forEach(item => {
                        const link = item.querySelector('a');
                        if (link) {
                            const href = link.getAttribute('href');
                            const text = link.textContent.trim();
                            
                            // Log do click (será capturado no Python)
                            link.dataset.debugClicked = 'true';
                            
                            if (!href || href.startsWith('javascript:') || !href.startsWith('#')) {
                                link.click();
                                clicked++;
                            }
                        }
                    });
                    
                    return clicked;
                }
            """)
            
            if collapsed_count > 0:
                self.log_debug('DEBUG', f'Rodada {round_num + 1}', {
                    'itens clicados': collapsed_count,
                    'total clicks': self.click_count + collapsed_count
                })
                self.click_count += collapsed_count
                await asyncio.sleep(0.5)
            else:
                self.log_debug('SUCCESS', f'Menus totalmente expandidos após {round_num + 1} rodadas', {
                    'total clicks': self.click_count
                })
                break
        
        await asyncio.sleep(1)
    
    async def extract_links_debug(self, page):
        """Extrai links com debug"""
        self.log_debug('INFO', 'Extraindo links de navegação')
        
        links = await page.evaluate("""
            () => {
                const result = [];
                const seen = new Set();
                
                const toc = document.getElementById('toc');
                if (!toc) return result;
                
                toc.querySelectorAll('a[href*="#"]').forEach(link => {
                    const href = link.getAttribute('href');
                    const text = link.textContent?.trim();
                    
                    if (href && text && text.length > 0 && !seen.has(href)) {
                        result.push({
                            text: text,
                            href: href,
                            visible: link.offsetParent !== null,
                            parent: link.closest('li')?.className || 'root'
                        });
                        seen.add(href);
                    }
                });
                
                return result;
            }
        """)
        
        self.log_debug('SUCCESS', f'Links extraídos: {len(links)}', {
            'links visíveis': sum(1 for l in links if l['visible']),
            'links ocultos': sum(1 for l in links if not l['visible']),
            'primeiro link': links[0]['text'][:50] if links else 'nenhum'
        })
        
        return links
    
    async def scrape_module_debug(self, module_name: str, base_url: str):
        """Scrapa módulo com debug completo"""
        print("\n" + "="*100)
        print(f"[MÓDULO] {module_name.upper()}")
        print("="*100 + "\n")
        
        self.log_debug('INFO', f'Iniciando scraping do módulo', {'módulo': module_name, 'url': base_url})
        
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            import subprocess, sys
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "playwright"], check=True)
            from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1920, "height": 1080})
            
            # Primeira navegação
            self.log_debug('INFO', 'Navegando para página inicial')
            await page.goto(base_url, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(2)
            
            # Expandir menus
            await self.expand_menus_debug(page)
            
            # Extrair links
            all_links = await self.extract_links_debug(page)
            
            self.log_debug('INFO', f'Total de itens para processar: {len(all_links)}')
            
            # Processar alguns links com debug
            processed = 0
            skipped = 0
            errors = 0
            
            for i, link in enumerate(all_links[:10]):  # Testar com primeiros 10
                self.log_debug('DEBUG', f'Processando {i + 1}/{min(10, len(all_links))}', {
                    'texto': link['text'][:40],
                    'href': link['href'][:50],
                    'visível': link['visible']
                })
                
                absolute_url = self.build_absolute_url(base_url, link['href'])
                
                if not absolute_url:
                    self.log_debug('WARNING', 'URL absoluta inválida', {'href original': link['href']})
                    skipped += 1
                    continue
                
                try:
                    content = await self.scrape_page_debug(page, absolute_url, base_url)
                    if content and content['total_chars'] >= 100:
                        processed += 1
                    else:
                        self.log_debug('WARNING', 'Conteúdo insuficiente', {
                            'caracteres': content['total_chars'] if content else 0
                        })
                except Exception as e:
                    self.log_debug('ERROR', 'Erro ao processar página', {'erro': str(e)[:50]})
                    errors += 1
                
                await asyncio.sleep(0.5)
            
            await browser.close()
        
        # Resumo
        print("\n" + "-"*100)
        self.log_debug('INFO', 'Resumo do módulo', {
            'processado': processed,
            'pulado': skipped,
            'erros': errors,
            'total links': len(all_links),
            'total clicks': self.click_count
        })
        print("-"*100 + "\n")


async def main():
    """Executa debug do scraper"""
    
    print("\n" + "╔" + "="*98 + "╗")
    print("║" + " DEBUG SCRAPER - Rastreamento Detalhado ".center(98) + "║")
    print("╚" + "="*98 + "╝\n")
    
    # Carregar módulos
    modulos_file = Path("modulos_descobertos.json")
    if not modulos_file.exists():
        print("[ERRO] modulos_descobertos.json não encontrado")
        return
    
    with open(modulos_file, 'r', encoding='utf-8') as f:
        modulos_dict = json.load(f)
    
    # Testar com primeiro módulo (GESTAO DE PESSOAS HCM)
    test_module = "GESTAO DE PESSOAS HCM"
    if test_module not in modulos_dict:
        test_module = list(modulos_dict.keys())[0]
    
    test_url = modulos_dict[test_module]['url']
    
    print(f"[TESTE] Usando módulo: {test_module}")
    print(f"[TESTE] URL: {test_url}\n")
    
    scraper = DebugScraper(save_html=False, debug=True)
    
    await scraper.scrape_module_debug(test_module, test_url)
    
    # Salvar log
    log_file = Path("debug_scraper_log.json")
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(scraper.debug_log, f, ensure_ascii=False, indent=2)
    
    print(f"\n[✓] Log salvo em: {log_file}")
    print(f"[✓] Total de mensagens de debug: {len(scraper.debug_log)}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
