#!/usr/bin/env python3
"""
Scraper completo com Playwright para documentacao.senior.com.br
Extrai articles do site dinamicamente renderizado
"""

import asyncio
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
import json
import re
import sys


class SeniorDocScraper:
    """Scraper para documentação Senior com suporte a JavaScript."""
    
    def __init__(self, base_url, max_pages=20):
        self.base_url = base_url
        self.max_pages = max_pages
        self.output_dir = Path("documentacao")
        self.output_dir.mkdir(exist_ok=True)
        self.visited = set()
        self.saved_count = 0
    
    async def run(self):
        """Executa scraper."""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            print("Instalando Playwright...")
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "playwright"], check=True)
            from playwright.async_api import async_playwright
        
        print(f"\n{'='*70}")
        print(f"SCRAPER SENIOR - Com JavaScript Rendering")
        print(f"URL: {self.base_url}")
        print(f"Max páginas: {self.max_pages}")
        print(f"{'='*70}\n")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
            )
            
            page = await context.new_page()
            
            # Extrair links da página inicial
            print("[1] Coletando links da documentação...")
            links = await self._collect_links(page)
            print(f"    Encontrados {len(links)} links únicos\n")
            
            # Processar cada link
            print("[2] Processando páginas...")
            for i, url in enumerate(links[:self.max_pages], 1):
                if self.saved_count >= self.max_pages:
                    break
                
                if url not in self.visited:
                    self.visited.add(url)
                    await self._scrape_page(page, url, i)
            
            await browser.close()
        
        print(f"\n{'='*70}")
        print(f"✓ Concluído! {self.saved_count} páginas salvas")
        print(f"{'='*70}\n")
    
    async def _collect_links(self, page):
        """Coleta links da documentação."""
        await page.goto(self.base_url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)
        
        # Extrair links do TOC (Table of Contents)
        links = set()
        
        try:
            # Links dos elementos <a> no TOC
            toc_links = await page.evaluate("""
                () => {
                    const links = [];
                    
                    // Procurar links no TOC
                    const toc = document.getElementById('toc');
                    if (toc) {
                        const anchors = toc.querySelectorAll('a[href]');
                        for (let a of anchors) {
                            let href = a.getAttribute('href');
                            if (href && href.startsWith('#')) {
                                links.push(href);
                            }
                        }
                    }
                    
                    return [...new Set(links)]; // Remover duplicatas
                }
            """)
            
            for href in toc_links:
                full_url = urljoin(self.base_url, href)
                if self._same_domain(full_url):
                    links.add(full_url)
        except Exception as e:
            print(f"    Erro coletando links: {e}")
        
        return list(links)[:50]  # Limitar a 50 links
    
    async def _scrape_page(self, page, url, index):
        """Scrapa uma página específica."""
        try:
            print(f"    [{index}] {url[:70]}...", end=" ", flush=True)
            
            # Navegar
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(1)
            
            # Extrair título
            title = await page.evaluate("() => document.title")
            
            # Extrair conteúdo do iframe
            content = await page.evaluate("""
                () => {
                    let text = '';
                    
                    // Tentar iframe topic
                    try {
                        const frame = document.getElementById('topic');
                        if (frame && frame.contentDocument) {
                            text = frame.contentDocument.body.innerText || frame.contentDocument.body.textContent || '';
                        }
                    } catch(e) {}
                    
                    // Fallback
                    if (!text || text.length < 100) {
                        const main = document.querySelector('[role="main"]');
                        if (main) {
                            text = main.innerText || main.textContent || '';
                        }
                    }
                    
                    // Última tentativa
                    if (!text || text.length < 100) {
                        const elements = document.querySelectorAll('article, .content, main, [data-content]');
                        for (let el of elements) {
                            const t = el.innerText || el.textContent;
                            if (t && t.length > text.length) {
                                text = t;
                            }
                        }
                    }
                    
                    return text;
                }
            """)
            
            if content and len(content) > 100:
                # Limpar
                content = ' '.join(content.split())
                
                # Gerar ID
                page_id = urlparse(url).path.strip('/')
                page_id = re.sub(r'[^a-z0-9_-]', '_', page_id.lower())
                if not page_id:
                    page_id = 'index'
                
                # Salvar
                page_dir = self.output_dir / page_id
                page_dir.mkdir(exist_ok=True)
                
                metadata = {
                    "title": title,
                    "url": url,
                    "language": "pt",
                    "source": "senior_docs",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "content_length": len(content),
                }
                
                with open(page_dir / "metadata.json", "w", encoding="utf-8") as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                with open(page_dir / "content.txt", "w", encoding="utf-8") as f:
                    f.write(content)
                
                self.saved_count += 1
                print(f"[OK] ({len(content)} chars)")
            else:
                print("[NO-CONTENT]")
        
        except Exception as e:
            print(f"[ERR] {str(e)[:30]}")
    
    def _same_domain(self, url):
        """Verifica mesmo domínio."""
        try:
            base_domain = urlparse(self.base_url).netloc
            url_domain = urlparse(url).netloc
            return url_domain == base_domain
        except:
            return False


async def main():
    """Main."""
    url = sys.argv[1] if len(sys.argv) > 1 else "https://documentacao.senior.com.br/tecnologia/5.10.4/"
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    scraper = SeniorDocScraper(url, max_pages)
    await scraper.run()


if __name__ == "__main__":
    asyncio.run(main())
