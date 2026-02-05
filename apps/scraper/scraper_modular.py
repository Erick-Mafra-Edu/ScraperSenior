#!/usr/bin/env python3
"""
Scraper Modular e Extensível para Documentação Senior
Baseado em configuração JSON com suporte a JavaScript, tratamento de lixo e limites customizáveis
"""

import asyncio
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from collections import deque
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Set, Tuple
import hashlib


@dataclass
class PageMetadata:
    """Metadados da página"""
    url: str
    title: str = ""
    breadcrumb: List[str] = None
    module: str = ""
    scraped_at: str = ""
    scrape_duration_ms: int = 0
    content_length: int = 0
    charset: str = "utf-8"
    
    def __post_init__(self):
        if self.breadcrumb is None:
            self.breadcrumb = []


class ConfigManager:
    """Gerencia configurações do scraper"""
    
    def __init__(self, config_path: str = "scraper_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração JSON"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"⚠️  Arquivo {self.config_path} não encontrado. Usando padrões.")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuração padrão"""
        return {
            "scraper": {"base_url": "https://documentacao.senior.com.br", "max_pages": 100},
            "extraction": {"max_content_length": 50000, "min_content_length": 100},
            "cleanup": {"garbage_patterns": [], "garbage_sequences": []},
            "javascript_handling": {"enable_js_interaction": True, "click_and_wait": []},
            "selectors": {"title": ["h1"], "content": ["#main-content"], "skip": []},
            "links": {"follow_patterns": [], "ignore_patterns": []},
            "output": {"format": "jsonl", "save_directory": "docs_scraped"}
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Acessa configuração por caminho (ex: 'extraction.max_content_length')"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
        
        return value if value is not None else default


class GarbageCollector:
    """Remove lixo e caracteres indesejados do conteúdo"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.garbage_patterns = config.get("cleanup.garbage_patterns", [])
        self.garbage_sequences = config.get("cleanup.garbage_sequences", [])
        self.normalize_whitespace = config.get("cleanup.normalize_whitespace", True)
        self.remove_empty_lines = config.get("cleanup.remove_empty_lines", True)
    
    def clean(self, content: str) -> str:
        """Remove lixo do conteúdo"""
        if not content:
            return ""
        
        # Remove padrões de lixo
        for pattern in self.garbage_patterns:
            try:
                if pattern == "\\s+":
                    content = re.sub(r'\s+', ' ', content)
                elif pattern == "\\n{3,}":
                    content = re.sub(r'\n{3,}', '\n\n', content)
                else:
                    content = re.sub(pattern, '', content)
            except re.error:
                print(f"⚠️  Padrão regex inválido: {pattern}")
        
        # Processa sequências de lixo
        for seq in self.garbage_sequences:
            pattern = seq.get('pattern', '')
            action = seq.get('action', 'remove')
            
            try:
                if action == 'remove':
                    content = re.sub(pattern, '', content)
                elif action == 'skip':
                    # Marca para pular elemento (durante HTML parsing)
                    pass
            except re.error:
                print(f"⚠️  Padrão inválido: {pattern}")
        
        # Normaliza espaços em branco
        if self.normalize_whitespace:
            content = re.sub(r'[ \t]+', ' ', content)
            content = content.strip()
        
        # Remove linhas vazias
        if self.remove_empty_lines:
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            content = '\n'.join(lines)
        
        return content
    
    def is_garbage(self, text: str) -> bool:
        """Detecta se texto é lixo"""
        garbage_keywords = ['anúncio', 'publicidade', 'cookie', 'rastreamento', 'analytics']
        return any(kw in text.lower() for kw in garbage_keywords)


class ContentExtractor:
    """Extrai conteúdo das páginas"""
    
    def __init__(self, config: ConfigManager, garbage_collector: GarbageCollector):
        self.config = config
        self.gc = garbage_collector
        self.max_length = config.get("extraction.max_content_length", 50000)
        self.min_length = config.get("extraction.min_content_length", 100)
    
    async def extract_title(self, page) -> str:
        """Extrai título da página"""
        title_selectors = self.config.get("selectors.title", ["h1"])
        max_length = self.config.get("extraction.max_title_length", 500)
        
        for selector in title_selectors:
            try:
                title = await page.text_content(selector)
                if title:
                    title = self.gc.clean(title)[:max_length]
                    return title
            except:
                continue
        
        return ""
    
    async def extract_content(self, page) -> str:
        """Extrai conteúdo principal da página (com suporte a iframes)"""
        content_selectors = self.config.get("selectors.content", ["#main-content"])
        skip_selectors = self.config.get("selectors.skip", [])
        
        content = ""
        
        # Tenta extrair de iframes (suporte MadCap Flare)
        try:
            frames = page.frames
            if len(frames) > 1:
                for frame in frames[1:]:  # Pula frame principal
                    try:
                        text = await frame.text_content('body')
                        if text and len(text) > len(content):
                            content = text
                    except:
                        pass
        except:
            pass
        
        # Se não encontrou em iframes, procura na página principal
        if not content:
            for selector in content_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        # Remove elementos a ignorar
                        for skip_sel in skip_selectors:
                            try:
                                await page.evaluate(f"() => document.querySelectorAll('{skip_sel}').forEach(el => el.remove())")
                            except:
                                pass
                        
                        # Extrai texto
                        text = await element.text_content()
                        if text:
                            content = text
                            break
                except:
                    continue
        
        if not content:
            # Fallback: pega todo o conteúdo visível
            content = await page.text_content('body')
        
        # Limpa conteúdo
        content = self.gc.clean(content)
        
        # Respeita limites de comprimento
        if len(content) > self.max_length:
            content = content[:self.max_length]
            content = content.rsplit(' ', 1)[0] + '...'
        
        if len(content) < self.min_length:
            return ""
        
        return content
    
    async def extract_breadcrumb(self, page) -> List[str]:
        """Extrai breadcrumb/navegação"""
        breadcrumb_selectors = self.config.get("selectors.breadcrumb", [".breadcrumb"])
        max_depth = self.config.get("extraction.max_breadcrumb_depth", 8)
        
        for selector in breadcrumb_selectors:
            try:
                items = await page.query_selector_all(f"{selector} li, {selector} a, {selector} span")
                if items:
                    breadcrumb = []
                    for item in items[:max_depth]:
                        text = await item.text_content()
                        if text and not self.gc.is_garbage(text):
                            breadcrumb.append(self.gc.clean(text))
                    
                    return breadcrumb
            except:
                continue
        
        return []


class JavaScriptHandler:
    """Gerencia interações com JavaScript"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.enable_js = config.get("javascript_handling.enable_js_interaction", True)
    
    async def execute_cleanup_scripts(self, page):
        """Executa scripts de limpeza (remove modais, anúncios, etc)"""
        if not self.enable_js:
            return
        
        scripts = self.config.get("javascript_handling.execute_scripts", [])
        
        for script_obj in scripts:
            try:
                script_code = script_obj.get('script', '')
                await page.evaluate(script_code)
            except:
                pass
    
    async def handle_dynamic_content(self, page):
        """Trata conteúdo dinâmico (clica em links com #, expande elementos)"""
        if not self.enable_js:
            return
        
        click_configs = self.config.get("javascript_handling.click_and_wait", [])
        
        for click_cfg in click_configs:
            selector = click_cfg.get('selector', '')
            wait_ms = click_cfg.get('wait_ms', 500)
            detect_change = click_cfg.get('detect_change', {})
            
            try:
                # Encontra elementos
                elements = await page.query_selector_all(selector)
                
                for element in elements[:5]:  # Limita a 5 cliques
                    try:
                        await element.click()
                        await asyncio.sleep(wait_ms / 1000)
                        
                        # Detecta mudanças
                        monitor_sel = detect_change.get('monitor_selector', '')
                        if monitor_sel:
                            try:
                                await page.wait_for_selector(monitor_sel, timeout=wait_ms)
                            except:
                                pass
                    except:
                        pass
            except:
                pass


class LinkExtractor:
    """Extrai e valida links com suporte a navegação por âncora"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.follow_patterns = config.get("links.follow_patterns", [])
        self.ignore_patterns = config.get("links.ignore_patterns", [])
        self.internal_only = config.get("links.internal_only", True)
        self.visited: Set[str] = set()
    
    def normalize_anchor_url(self, url: str) -> str:
        """Normaliza URLs com âncoras para extração via JavaScript clique"""
        if '#' not in url:
            return url
        
        base, anchor = url.rsplit('#', 1)
        
        # Remove .htm/.html do final da âncora (MadCap Flare)
        anchor = anchor.replace('.htm', '').replace('.html', '')
        
        return base + '#' + anchor
    
    def should_follow(self, url: str) -> bool:
        """Decide se deve seguir um link"""
        if not url or url in self.visited:
            return False
        
        # Normaliza e adiciona à visitados
        normalized = self.normalize_anchor_url(url)
        
        # Verifica padrões a ignorar
        for pattern in self.ignore_patterns:
            if pattern in normalized:
                return False
        
        # Se internal_only, verifica domínios permitidos
        if self.internal_only and self.follow_patterns:
            if not any(domain in normalized for domain in self.follow_patterns):
                return False
        
        return True
    
    async def extract_links(self, page) -> List[str]:
        """Extrai links da página"""
        try:
            links = await page.evaluate("""
                () => Array.from(document.querySelectorAll('a[href]'))
                    .map(a => a.href)
                    .filter(href => href && href.length > 0)
            """)
            
            valid_links = []
            for link in links:
                if self.should_follow(link):
                    self.visited.add(link)
                    valid_links.append(link)
            
            return valid_links
        except:
            return []


class ModularScraper:
    """Scraper modular baseado em configuração"""
    
    def __init__(self, config_path: str = "scraper_config.json"):
        self.config = ConfigManager(config_path)
        self.gc = GarbageCollector(self.config)
        self.extractor = ContentExtractor(self.config, self.gc)
        self.js_handler = JavaScriptHandler(self.config)
        self.link_extractor = LinkExtractor(self.config)
        
        # Estado
        self.to_visit = deque()
        self.visited: Set[str] = set()
        self.documents: List[Dict[str, Any]] = []
        
        # Estatísticas
        self.stats = {
            'pages_scraped': 0,
            'pages_failed': 0,
            'total_content_length': 0,
            'start_time': None,
            'end_time': None
        }
    
    async def scrape(self):
        """Executa scraping completo"""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            print("Instalando Playwright...")
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "playwright"], check=True)
            from playwright.async_api import async_playwright
        
        self.stats['start_time'] = datetime.now(timezone.utc)
        base_url = self.config.get("scraper.base_url")
        max_pages = self.config.get("scraper.max_pages", 100)
        
        print(f"\n{'='*80}")
        print(f"SCRAPER MODULAR - Documentação Senior")
        print(f"{'='*80}")
        print(f"Base URL: {base_url}")
        print(f"Máx. páginas: {max_pages}")
        print(f"Config: {self.config.config_path}")
        print(f"{'='*80}\n")
        
        self.to_visit.append(base_url)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.config.get("scraper.headless", True)
            )
            context = await browser.new_context(
                viewport=self.config.get("scraper.viewport", {"width": 1920, "height": 1080})
            )
            page = await context.new_page()
            
            page_count = 0
            while self.to_visit and page_count < max_pages:
                url = self.to_visit.popleft()
                
                if url in self.visited:
                    continue
                
                self.visited.add(url)
                
                print(f"[{page_count+1}/{max_pages}] Scrapeando: {url[:80]}...", end=" ", flush=True)
                
                success = await self._scrape_page(page, url)
                
                if success:
                    print("✅")
                    page_count += 1
                else:
                    print("❌")
                    self.stats['pages_failed'] += 1
            
            await browser.close()
        
        self.stats['end_time'] = datetime.now(timezone.utc)
        self._save_documents()
        self._print_report()
    
    async def _scrape_page(self, page, url: str) -> bool:
        """Scrapa uma página individual"""
        try:
            timeout = self.config.get("scraper.timeout_ms", 30000)
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            await asyncio.sleep(0.5)
            
            # Limpa a página (remove modais, anúncios)
            await self.js_handler.execute_cleanup_scripts(page)
            
            # Trata conteúdo dinâmico
            await self.js_handler.handle_dynamic_content(page)
            
            # Extrai dados
            start_time = datetime.now()
            title = await self.extractor.extract_title(page)
            content = await self.extractor.extract_content(page)
            breadcrumb = await self.extractor.extract_breadcrumb(page)
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            if not content:
                return False
            
            # Cria documento
            doc = {
                'id': hashlib.md5(url.encode()).hexdigest()[:16],
                'url': url,
                'title': title or self._extract_title_from_url(url),
                'content': content,
                'breadcrumb': breadcrumb,
                'module': self._extract_module(breadcrumb, url),
                'metadata': asdict(PageMetadata(
                    url=url,
                    title=title,
                    breadcrumb=breadcrumb,
                    scraped_at=datetime.now(timezone.utc).isoformat(),
                    scrape_duration_ms=duration_ms,
                    content_length=len(content)
                ))
            }
            
            self.documents.append(doc)
            self.stats['pages_scraped'] += 1
            self.stats['total_content_length'] += len(content)
            
            # Extrai links para continuação
            if self.stats['pages_scraped'] < self.config.get("scraper.max_pages", 100):
                new_links = await self.link_extractor.extract_links(page)
                self.to_visit.extend(new_links)
            
            return True
        
        except Exception as e:
            return False
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extrai título da URL como fallback"""
        path = urlparse(url).path
        return path.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
    
    def _extract_module(self, breadcrumb: List[str], url: str) -> str:
        """Extrai módulo do breadcrumb ou URL"""
        if breadcrumb and len(breadcrumb) > 1:
            return breadcrumb[0]
        
        path = urlparse(url).path
        parts = [p for p in path.split('/') if p]
        return parts[0] if parts else "Documentação"
    
    def _path_to_full_url(self, breadcrumb: List[str], url_hint: str = None) -> str:
        """
        Converte caminho de breadcrumb para URL completo.
        
        Suporta dois domínios:
        - documentacao.senior.com.br (padrão para documentação técnica)
        - suporte.senior.com.br (para suporte/Zendesk)
        
        Exemplos:
        ["BI", "Apresentação"] → "https://documentacao.senior.com.br/bi/apresentacao/"
        ["Help Center", "LSP"] → "https://suporte.senior.com.br/help-center/lsp/"
        """
        if not breadcrumb:
            return "https://documentacao.senior.com.br/"
        
        # Detectar domínio baseado no breadcrumb ou hint
        domain = "documentacao.senior.com.br"  # Padrão
        
        # Palavras-chave que indicam domínio suporte.senior.com.br
        suporte_keywords = ['help center', 'suporte', 'zendesk', 'faq', 'ticket', 'support']
        first_part_lower = breadcrumb[0].lower() if breadcrumb else ""
        
        if any(kw in first_part_lower for kw in suporte_keywords):
            domain = "suporte.senior.com.br"
        
        # Também verificar no hint se fornecido
        if url_hint:
            if 'suporte' in url_hint.lower():
                domain = "suporte.senior.com.br"
            elif 'documentacao' in url_hint.lower():
                domain = "documentacao.senior.com.br"
        
        # Converter para lowercase e substituir espaços/underscores por hífens
        path_parts = []
        for part in breadcrumb:
            # Remove caracteres especiais e normaliza
            normalized = part.lower()
            normalized = normalized.replace("_", "-")
            normalized = normalized.replace(" ", "-")
            # Remove múltiplos hífens
            normalized = re.sub(r'-+', '-', normalized)
            # Remove caracteres não alfanuméricos (exceto hífens)
            normalized = re.sub(r'[^a-z0-9-]', '', normalized)
            if normalized:
                path_parts.append(normalized)
        
        path = "/".join(path_parts)
        return f"https://{domain}/{path}/"
    
    def _save_documents(self):
        """Salva documentos em arquivo"""
        output_format = self.config.get("output.format", "jsonl")
        output_dir = Path(self.config.get("output.save_directory", "docs_scraped"))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format == "jsonl":
            filepath = output_dir / f"scraped_{timestamp}.jsonl"
            with open(filepath, 'w', encoding='utf-8') as f:
                for doc in self.documents:
                    # Garantir URL completo
                    if isinstance(doc, dict):
                        if 'url' in doc and not doc['url'].startswith('http'):
                            breadcrumb = doc.get('breadcrumb', [])
                            doc['url'] = self._path_to_full_url(breadcrumb)
                    f.write(json.dumps(doc, ensure_ascii=False) + '\n')
        
        elif output_format == "json":
            filepath = output_dir / f"scraped_{timestamp}.json"
            # Garantir URLs completos antes de salvar
            for doc in self.documents:
                if isinstance(doc, dict):
                    if 'url' in doc and not doc['url'].startswith('http'):
                        breadcrumb = doc.get('breadcrumb', [])
                        doc['url'] = self._path_to_full_url(breadcrumb)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Documentos salvos em: {filepath}")
    
    def _print_report(self):
        """Imprime relatório de scraping"""
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        print(f"\n{'='*80}")
        print(f"RELATÓRIO DE SCRAPING")
        print(f"{'='*80}")
        print(f"Páginas scrapeadas: {self.stats['pages_scraped']}")
        print(f"Páginas com erro: {self.stats['pages_failed']}")
        print(f"Total de links visitados: {len(self.visited)}")
        print(f"Conteúdo total extraído: {self.stats['total_content_length']:,} caracteres")
        print(f"Tempo total: {duration:.2f}s")
        
        if self.stats['pages_scraped'] > 0:
            avg_content = self.stats['total_content_length'] / self.stats['pages_scraped']
            print(f"Média por página: {avg_content:.0f} caracteres")
        
        print(f"{'='*80}\n")


async def main():
    scraper = ModularScraper("scraper_config.json")
    await scraper.scrape()


if __name__ == "__main__":
    asyncio.run(main())
