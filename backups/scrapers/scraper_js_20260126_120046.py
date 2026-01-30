#!/usr/bin/env python3
"""
Scraper avançado com Playwright para JavaScript-heavy sites
Extrai conteúdo real dos iframes após renderização completa
"""

import asyncio
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
import json
import re


async def scrape_with_playwright():
    """Scraper usando Playwright para JavaScript rendering."""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("Playwright não instalado. Instalando...")
        import subprocess
        import sys
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "playwright"], check=True)
        from playwright.async_api import async_playwright
    
    output_dir = Path("documentacao")
    output_dir.mkdir(exist_ok=True)
    
    # URLs para testar
    urls = [
        "https://documentacao.senior.com.br/tecnologia/5.10.4/#geradores/relatorios/definit.htm",
        "https://documentacao.senior.com.br/tecnologia/5.10.3/",
    ]
    
    async with async_playwright() as p:
        # Usar Chromium para melhor compatibilidade
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        )
        
        page = await context.new_page()
        
        for url in urls:
            print(f"\n{'='*70}")
            print(f"Scraping: {url}")
            print(f"{'='*70}\n")
            
            try:
                # Navegar para página
                print("[1] Navegando...")
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # Aguardar iframes carregarem
                print("[2] Aguardando iframes carregarem...")
                await asyncio.sleep(3)
                
                # Tentar extrair do iframe principal
                print("[3] Extraindo conteúdo do iframe...")
                
                # Esperar iframe 'topic' ficar visível
                try:
                    await page.wait_for_selector('iframe#topic', timeout=5000)
                except:
                    print("   ⚠️  iframe#topic não encontrado")
                
                # Obter conteúdo da página principal
                page_html = await page.content()
                
                # Tenta extrair título do documento
                title_match = re.search(r'<title[^>]*>([^<]+)</title>', page_html)
                title = title_match.group(1) if title_match else "Sem título"
                
                print(f"   Título: {title}")
                
                # Tenta extrair conteúdo do iframe via JavaScript
                print("[4] Extraindo conteúdo via JavaScript...")
                
                content = await page.evaluate("""
                    () => {
                        let text = '';
                        
                        // Tentar extrair do iframe topic
                        try {
                            const topicFrame = document.getElementById('topic');
                            if (topicFrame && topicFrame.contentDocument) {
                                const content = topicFrame.contentDocument.body;
                                text += content.innerText || content.textContent || '';
                            }
                        } catch(e) { console.log('Erro ao acessar topic frame'); }
                        
                        // Tentar extrair do corpo principal
                        if (!text) {
                            const main = document.querySelector('[role="main"]');
                            if (main) {
                                text = main.innerText || main.textContent || '';
                            }
                        }
                        
                        // Fallback: tentar todas as divs com conteúdo
                        if (!text || text.length < 100) {
                            const divs = Array.from(document.querySelectorAll('div, article, main, section'));
                            for (let div of divs) {
                                const t = div.innerText;
                                if (t && t.length > text.length && t.length > 200) {
                                    text = t;
                                    break;
                                }
                            }
                        }
                        
                        return text;
                    }
                """)
                
                if content:
                    # Limpar espaços em branco excessivos
                    content = ' '.join(content.split())
                    print(f"   Conteúdo extraído: {len(content)} caracteres")
                    
                    # Salvar
                    page_id = urlparse(url).path
                    page_id = page_id.strip('/').replace('/', '_').replace('#', '_')
                    if not page_id:
                        page_id = 'index'
                    
                    page_dir = output_dir / page_id
                    page_dir.mkdir(exist_ok=True)
                    
                    # Metadata
                    metadata = {
                        "title": title,
                        "url": url,
                        "section": urlparse(url).path.split('/')[1] if '/' in urlparse(url).path else "root",
                        "language": "pt",
                        "source": "scraped_js",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "content_length": len(content),
                    }
                    
                    with open(page_dir / "metadata.json", "w", encoding="utf-8") as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)
                    
                    with open(page_dir / "content.txt", "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    print(f"   ✓ Salvo em: {page_dir.name}/")
                else:
                    print("   [!] Nenhum conteúdo extraído")
            
            except Exception as e:
                print(f"   [!] Erro: {e}")
        
        await browser.close()


async def main():
    print("\n" + "="*70)
    print("SCRAPER COM PLAYWRIGHT - JavaScript Rendering")
    print("="*70)
    
    await scrape_with_playwright()
    
    print("\n" + "="*70)
    print("Scraping concluído!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from collections import deque


class PlaywrightScraper:
    """Scraper que executa JavaScript para carregar conteúdo."""
    
    def __init__(self, base_url, max_pages=20):
        self.base_url = base_url
        self.max_pages = max_pages
        self.output_dir = Path("documentacao")
        self.output_dir.mkdir(exist_ok=True)
        
        self.visited = set()
        self.queue = deque([base_url])
        self.pages_saved = 0
        
        self.browser = None
        self.context = None
    
    async def run(self):
        """Executa o scraper."""
        print(f"\n{'='*70}")
        print(f"SCRAPING (com JavaScript): {self.base_url}")
        print(f"{'='*70}\n")
        
        async with async_playwright() as p:
            # Inicia browser
            self.browser = await p.chromium.launch(headless=True)
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            while self.queue and self.pages_saved < self.max_pages:
                url = self.queue.popleft()
                
                if url in self.visited:
                    continue
                
                self.visited.add(url)
                
                # Only same domain
                if not self._same_domain(url):
                    continue
                
                try:
                    print(f"[{self.pages_saved + 1}] Scraping: {url}")
                    
                    page = await self.context.new_page()
                    
                    try:
                        # Aguarda página carregar
                        await page.goto(url, wait_until="networkidle", timeout=30000)
                        
                        # Aguarda iframes carregarem
                        await asyncio.sleep(2)
                        
                        # Obtem HTML renderizado
                        html = await page.content()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extrai e salva
                        if await self._save_page(url, soup):
                            self.pages_saved += 1
                        
                        # Encontra mais links
                        if self.pages_saved < self.max_pages:
                            for link in soup.find_all('a', href=True):
                                href = link['href']
                                next_url = urljoin(url, href)
                                next_url = next_url.split('#')[0]
                                
                                if next_url not in self.visited and self._same_domain(next_url):
                                    self.queue.append(next_url)
                    
                    finally:
                        await page.close()
                
                except PlaywrightTimeout:
                    print(f"   [!] Timeout: {url}")
                except Exception as e:
                    print(f"   [!] Error: {e}")
            
            await self.context.close()
            await self.browser.close()
        
        print(f"\n{'='*70}")
        print(f"DONE! Saved {self.pages_saved} pages")
        print(f"{'='*70}\n")
    
    async def _save_page(self, url, soup):
        """Salva uma página."""
        try:
            # Titulo
            title = soup.find('h1')
            if title:
                title = title.get_text(strip=True)
            else:
                title = soup.title
                if title:
                    title = title.get_text(strip=True)
                else:
                    title = url.split('/')[-1] or "index"
            
            # Conteudo - procura em iframes ou divs
            content = ""
            
            # Tenta achar conteudo em elementos comuns
            for selector in ['main', 'article', '[role="main"]', 'div[id*="content"]']:
                elements = soup.select(selector)
                for elem in elements:
                    text = elem.get_text(separator=' ', strip=True)
                    if len(text) > len(content):
                        content = text
            
            # Se nao achou, tenta body
            if not content or len(content) < 100:
                body = soup.find('body')
                if body:
                    content = body.get_text(separator=' ', strip=True)
            
            # Filtra conteudo de UI (buttons, forms, etc)
            unwanted = ['username', 'email address', 'password', 'submit', 'cancel']
            content_lower = content.lower()
            for word in unwanted:
                if content_lower.count(word) > 3:
                    # Parece ser form/UI, nao conteudo real
                    return False
            
            if len(content) < 100:
                return False
            
            # Limpa
            content = ' '.join(content.split())[:50000]
            
            # ID
            page_id = urlparse(url).path
            page_id = page_id.strip('/').replace('/', '_').replace('.', '_')
            if not page_id or page_id == '':
                page_id = 'index'
            
            # Salva
            page_dir = self.output_dir / page_id
            page_dir.mkdir(exist_ok=True)
            
            metadata = {
                "title": title,
                "url": url,
                "section": urlparse(url).path.split('/')[1] if '/' in urlparse(url).path else "root",
                "language": "pt",
                "source": "scraped_js",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            
            with open(page_dir / "metadata.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            with open(page_dir / "content.txt", "w", encoding="utf-8") as f:
                f.write(content)
            
            return True
        
        except Exception as e:
            print(f"   Error saving: {e}")
            return False
    
    def _same_domain(self, url):
        """Verifica se mesmo dominio."""
        base_parsed = urlparse(self.base_url)
        url_parsed = urlparse(url)
        return url_parsed.netloc == base_parsed.netloc


async def main():
    """Main."""
    import sys
    
    url = sys.argv[1] if len(sys.argv) > 1 else "https://documentacao.senior.com.br"
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    scraper = PlaywrightScraper(url, max_pages)
    await scraper.run()


if __name__ == "__main__":
    asyncio.run(main())
