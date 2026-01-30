#!/usr/bin/env python3
"""
Scraper avançado com suporte a JavaScript
Específico para documentação Senior com iframes
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
import json
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
import re


class SeniorDocsScraper:
    """Scraper especializado para documentação Senior."""
    
    def __init__(self, base_url, max_pages=50):
        self.base_url = base_url
        self.max_pages = max_pages
        self.output_dir = Path("documentacao")
        self.output_dir.mkdir(exist_ok=True)
        
        self.visited = set()
        self.to_visit = [base_url]
        self.pages_saved = 0
    
    async def run(self):
        """Executa o scraper."""
        print(f"\n{'='*70}")
        print(f"SCRAPING SENIOR DOCS: {self.base_url}")
        print(f"Max pages: {self.max_pages}")
        print(f"{'='*70}\n")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            while self.to_visit and self.pages_saved < self.max_pages:
                url = self.to_visit.pop(0)
                
                if url in self.visited:
                    continue
                
                self.visited.add(url)
                
                # Apenas mesmo dominio
                if not self._same_domain(url):
                    continue
                
                try:
                    print(f"[{self.pages_saved + 1}] {url}")
                    
                    page = await context.new_page()
                    
                    # Goto
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                    
                    # Aguarda conteudo
                    await asyncio.sleep(1)
                    
                    # Tenta buscar conteudo do iframe "topic"
                    try:
                        iframe = page.frames[1] if len(page.frames) > 1 else None
                        if iframe:
                            await asyncio.sleep(0.5)
                            iframe_html = await iframe.content()
                            # Tenta extrair de iframe
                            if self._extract_from_html(url, iframe_html):
                                self.pages_saved += 1
                                await page.close()
                                continue
                    except:
                        pass
                    
                    # Fallback: tenta page content
                    html = await page.content()
                    if self._extract_from_html(url, html):
                        self.pages_saved += 1
                    
                    # Procura links
                    if self.pages_saved < self.max_pages:
                        links = await page.evaluate("""
                            () => {
                                return Array.from(document.querySelectorAll('a[href]'))
                                    .map(a => a.href)
                                    .filter(href => href && !href.includes('javascript'))
                            }
                        """)
                        
                        for link in links:
                            clean_link = link.split('#')[0]
                            if clean_link not in self.visited and self._same_domain(clean_link):
                                if clean_link not in self.to_visit:
                                    self.to_visit.append(clean_link)
                    
                    await page.close()
                
                except PlaywrightTimeout:
                    print(f"    [TIMEOUT]")
                except Exception as e:
                    print(f"    [ERROR] {str(e)[:60]}")
            
            await context.close()
            await browser.close()
        
        print(f"\n{'='*70}")
        print(f"DONE! Saved {self.pages_saved} pages")
        print(f"{'='*70}\n")
    
    def _extract_from_html(self, url, html):
        """Extrai conteudo do HTML."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Titulo
            title = None
            for tag in soup.find_all(['h1', 'h2', 'title']):
                text = tag.get_text(strip=True)
                if text and len(text) > 3:
                    title = text
                    break
            
            if not title:
                title = url.split('/')[-1] or "index"
            
            # Conteudo - remove scripts, styles, nav
            for tag in soup.find_all(['script', 'style', 'nav', 'aside']):
                tag.decompose()
            
            # Procura por divs com classe 'content' ou similar
            content = ""
            for container_class in ['content', 'article', 'main', 'body-content', 'topic-content']:
                containers = soup.find_all(class_=container_class)
                for container in containers:
                    text = container.get_text(separator=' ', strip=True)
                    if len(text) > len(content):
                        content = text
            
            # Fallback para body
            if not content or len(content) < 150:
                body = soup.find('body')
                if body:
                    content = body.get_text(separator=' ', strip=True)
            
            # Filtra UI elements
            content = self._clean_content(content)
            
            if len(content) < 150:
                return False
            
            # Limita tamanho
            content = content[:60000]
            
            # Salva
            page_id = urlparse(url).path
            page_id = re.sub(r'[/\\.]+', '_', page_id).strip('_')
            if not page_id:
                page_id = 'index'
            
            page_dir = self.output_dir / page_id
            page_dir.mkdir(exist_ok=True, parents=True)
            
            metadata = {
                "title": title,
                "url": url,
                "path": urlparse(url).path,
                "language": "pt",
                "source": "senior_docs",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            
            with open(page_dir / "metadata.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            with open(page_dir / "content.txt", "w", encoding="utf-8") as f:
                f.write(content)
            
            return True
        
        except Exception as e:
            return False
    
    def _clean_content(self, text):
        """Limpa conteudo de UI."""
        # Remove excesso de espacos
        text = ' '.join(text.split())
        
        # Remove frases comuns de UI
        ui_patterns = [
            r'Username \* Email Address \*.*?submit',
            r'Create Profile.*?new profile',
            r'Email Notifications.*?Help system',
            r'Log Console \d+ms',
            r'Encontramos.*?resultado',
        ]
        
        for pattern in ui_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        
        return ' '.join(text.split())
    
    def _same_domain(self, url):
        """Verifica mesmo dominio."""
        base_parsed = urlparse(self.base_url)
        url_parsed = urlparse(url)
        return url_parsed.netloc == base_parsed.netloc


async def main():
    """Main."""
    import sys
    
    url = sys.argv[1] if len(sys.argv) > 1 else "https://documentacao.senior.com.br"
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    scraper = SeniorDocsScraper(url, max_pages)
    await scraper.run()


if __name__ == "__main__":
    asyncio.run(main())
