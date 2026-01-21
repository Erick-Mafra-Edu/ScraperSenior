#!/usr/bin/env python3
"""
Scraper completo para documentacao.senior.com.br
Carrega JavaScript, explora links dinamicamente, indexa tudo
"""

import asyncio
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
import json
import re
import sys
from collections import deque


class CompleteDocScraper:
    """Scraper completo com exploração de links e JS rendering."""
    
    def __init__(self, base_url, max_pages=100):
        self.base_url = base_url
        self.max_pages = max_pages
        self.output_dir = Path("documentacao")
        self.output_dir.mkdir(exist_ok=True)
        
        self.visited = set()
        self.to_visit = deque([base_url])
        self.saved_count = 0
        self.error_count = 0
        
        # Padrões a ignorar
        self.ignore_patterns = [
            r'javascript:',
            r'#home\.htm',
            r'%3F',  # URL encoded ?
        ]
    
    async def run(self):
        """Executa scraper completo."""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            print("Instalando Playwright...")
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "playwright"], check=True)
            from playwright.async_api import async_playwright
        
        print(f"\n{'='*70}")
        print(f"SCRAPER COMPLETO - Documentacao Senior")
        print(f"Base URL: {self.base_url}")
        print(f"Max páginas: {self.max_pages}")
        print(f"{'='*70}\n")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
            )
            
            page = await context.new_page()
            
            # Fase 1: Coletamento de links
            print("[FASE 1] Coletando links da documentação...\n")
            await self._collect_all_links(page)
            
            print(f"\nTotal de links para processar: {len(self.to_visit)}")
            print(f"Limite: {self.max_pages}\n")
            
            # Fase 2: Scraping
            print("[FASE 2] Scrapeando páginas...\n")
            index = 1
            while self.to_visit and self.saved_count < self.max_pages:
                url = self.to_visit.popleft()
                
                if url in self.visited:
                    continue
                
                self.visited.add(url)
                await self._scrape_page(page, url, index)
                index += 1
            
            await browser.close()
        
        print(f"\n{'='*70}")
        print(f"CONCLUÍDO!")
        print(f"  Páginas salvas: {self.saved_count}")
        print(f"  Erros: {self.error_count}")
        print(f"  URLs visitadas: {len(self.visited)}")
        print(f"{'='*70}\n")
    
    async def _collect_all_links(self, page):
        """Coleta todos os links de todas as páginas do TOC."""
        try:
            await page.goto(self.base_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)
            
            print("  Extraindo links do Table of Contents...")
            
            links = await page.evaluate("""
                () => {
                    const links = [];
                    const toc = document.getElementById('toc');
                    
                    if (toc) {
                        // Coletar todos os links do TOC
                        const anchors = toc.querySelectorAll('a[href]');
                        const seen = new Set();
                        
                        for (let a of anchors) {
                            let href = a.getAttribute('href');
                            if (href && href.startsWith('#') && !seen.has(href)) {
                                links.push(href);
                                seen.add(href);
                            }
                        }
                    }
                    
                    return links;
                }
            """)
            
            print(f"    Encontrados {len(links)} links únicos no TOC")
            
            # Adicionar à fila
            for href in links:
                full_url = urljoin(self.base_url, href)
                if self._should_visit(full_url):
                    self.to_visit.append(full_url)
        
        except Exception as e:
            print(f"    Erro coletando links: {e}")
    
    async def _scrape_page(self, page, url, index):
        """Scrapa uma página."""
        try:
            # Mostrar progresso
            short_url = url[:60] + "..." if len(url) > 60 else url
            print(f"  [{index:3d}] {short_url}", end=" ", flush=True)
            
            # Navegar
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(1.5)  # Aguardar renderização
            
            # Extrair título
            title = await page.evaluate("() => document.title")
            
            # Extrair conteúdo
            content = await page.evaluate("""
                () => {
                    let text = '';
                    
                    // Tentar iframe topic (conteúdo principal)
                    try {
                        const frame = document.getElementById('topic');
                        if (frame && frame.contentDocument) {
                            text = frame.contentDocument.body.innerText || 
                                  frame.contentDocument.body.textContent || '';
                        }
                    } catch(e) {}
                    
                    // Se não achou, tentar main content
                    if (!text || text.length < 100) {
                        const main = document.querySelector('[role="main"]');
                        if (main) {
                            text = main.innerText || main.textContent || '';
                        }
                    }
                    
                    // Última tentativa: buscar elementos com conteúdo
                    if (!text || text.length < 100) {
                        const candidates = document.querySelectorAll(
                            'article, .content, main, [class*="content"], [class*="article"]'
                        );
                        
                        for (let el of candidates) {
                            const t = el.innerText || el.textContent || '';
                            if (t.length > text.length && t.length > 200) {
                                text = t;
                            }
                        }
                    }
                    
                    return text.trim();
                }
            """)
            
            # Validar e salvar
            if content and len(content) > 150:
                # Limpar conteúdo
                content = ' '.join(content.split())[:50000]  # Max 50k chars
                
                # Gerar ID único
                page_id = self._generate_page_id(url)
                
                # Salvar
                page_dir = self.output_dir / page_id
                page_dir.mkdir(exist_ok=True)
                
                # Metadata
                metadata = {
                    "title": title,
                    "url": url,
                    "language": "pt",
                    "source": "senior_complete",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "content_length": len(content),
                }
                
                with open(page_dir / "metadata.json", "w", encoding="utf-8") as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                with open(page_dir / "content.txt", "w", encoding="utf-8") as f:
                    f.write(content)
                
                self.saved_count += 1
                print(f"✓ ({len(content):5d} chars)")
            else:
                print("✗ (conteúdo insuficiente)")
        
        except asyncio.TimeoutError:
            print("✗ (timeout)")
            self.error_count += 1
        except Exception as e:
            error_msg = str(e)[:20]
            print(f"✗ ({error_msg})")
            self.error_count += 1
    
    def _generate_page_id(self, url):
        """Gera ID único para página."""
        # Extrair path e fragmento
        parsed = urlparse(url)
        
        # Combinar path + fragment
        path = parsed.path.strip('/')
        fragment = parsed.fragment.strip('/')
        
        # Combinar
        page_id = f"{path}_{fragment}".strip('_')
        
        # Limpar caracteres inválidos
        import re
        page_id = re.sub(r'[^a-z0-9_-]', '_', page_id.lower())
        page_id = re.sub(r'_{2,}', '_', page_id)  # Remover underscores múltiplos
        
        if not page_id or page_id == 'index':
            page_id = f"page_{self.saved_count}"
        
        return page_id
    
    def _should_visit(self, url):
        """Verifica se deve visitar URL."""
        # Verificar domínio
        try:
            base_domain = urlparse(self.base_url).netloc
            url_domain = urlparse(url).netloc
            if url_domain != base_domain:
                return False
        except:
            return False
        
        # Verificar padrões ignorados
        for pattern in self.ignore_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        return True


async def main():
    """Main."""
    url = sys.argv[1] if len(sys.argv) > 1 else "https://documentacao.senior.com.br/tecnologia/5.10.4/"
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    scraper = CompleteDocScraper(url, max_pages)
    await scraper.run()
    
    # Mostrar resumo
    print("\n" + "="*70)
    print("PRÓXIMO PASSO: Indexar documentos com:")
    print("  python index_all_docs.py")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
