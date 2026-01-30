"""
Adapter - Senior Documentation Scraper

Implementação concreta de IDocumentScraper para documentação Senior.
Suporta MadCap Flare e Astro com detecção automática de formato.
"""

import asyncio
import hashlib
from datetime import datetime
from typing import List, Optional, AsyncIterator
from urllib.parse import urlparse, unquote
import re

from libs.scrapers.ports import IDocumentScraper, IContentExtractor, IUrlResolver
from libs.scrapers.domain import Document, ScrapingResult, DocumentType, DocumentSource


class SeniorDocAdapter(IDocumentScraper):
    """
    Adapter para scraping de documentação Senior.
    
    Suporta:
    - MadCap Flare (iframe#topic + hash navigation)
    - Astro (aside#sidebar + hierarquia de menu)
    - Release Notes (âncoras #version.htm)
    
    Detecta automaticamente o formato e extrai conteúdo hierárquico.
    """
    
    def __init__(
        self,
        extractor: IContentExtractor,
        url_resolver: IUrlResolver,
        max_retries: int = 3,
        timeout: int = 30000,
    ):
        """
        Inicializa adapter.
        
        Args:
            extractor: Content extractor (ex: PlaywrightExtractor)
            url_resolver: URL resolver
            max_retries: Máximo de tentativas por página
            timeout: Timeout em milissegundos
        """
        self.extractor = extractor
        self.url_resolver = url_resolver
        self.max_retries = max_retries
        self.timeout = timeout
        
        self._visited_urls = set()
    
    async def scrape(self, url: str, **kwargs) -> Document:
        """
        Scrape uma única URL.
        
        Args:
            url: URL do documento
            **kwargs: Argumentos adicionais
        
        Returns:
            Document: Documento extraído
        """
        page = await self.extractor.navigate(url, timeout=self.timeout)
        
        try:
            # Detectar formato
            doc_format = await self._detect_format(page)
            
            # Extrair conteúdo baseado no formato
            if doc_format == "madcap":
                doc = await self._scrape_madcap_page(page, url)
            elif doc_format == "astro":
                doc = await self._scrape_astro_page(page, url)
            else:
                doc = await self._scrape_generic_page(page, url)
            
            return doc
            
        finally:
            await self.extractor.close_page(page)
    
    async def scrape_multiple(
        self,
        urls: List[str],
        **kwargs
    ) -> AsyncIterator[Document]:
        """
        Scrape múltiplas URLs.
        
        Args:
            urls: Lista de URLs
            **kwargs: Argumentos adicionais
        
        Yields:
            Document: Documentos extraídos
        """
        for url in urls:
            if url in self._visited_urls:
                continue
            
            try:
                doc = await self.scrape(url)
                self._visited_urls.add(url)
                yield doc
            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")
                continue
    
    async def scrape_all(self, base_url: str, **kwargs) -> ScrapingResult:
        """
        Scrape todas as páginas a partir de URL base.
        
        Descobre navegação automaticamente e extrai todo o site.
        
        Args:
            base_url: URL base
            **kwargs: Argumentos adicionais
        
        Returns:
            ScrapingResult: Resultado completo
        """
        started_at = datetime.now()
        documents = []
        errors = []
        successful = 0
        failed = 0
        
        page = await self.extractor.navigate(base_url, timeout=self.timeout)
        
        try:
            # Detectar formato e descobrir links
            doc_format = await self._detect_format(page)
            
            if doc_format == "madcap":
                links = await self._discover_madcap_links(page, base_url)
            elif doc_format == "astro":
                links = await self._discover_astro_links(page, base_url)
            else:
                links = [base_url]
            
            await self.extractor.close_page(page)
            
            # Scrape todos os links descobertos
            async for doc in self.scrape_multiple(links):
                documents.append(doc)
                successful += 1
            
        except Exception as e:
            errors.append(str(e))
            failed += 1
        
        finished_at = datetime.now()
        
        return ScrapingResult(
            documents=tuple(documents),
            total_documents=len(documents),
            successful_scrapes=successful,
            failed_scrapes=failed,
            skipped_urls=0,
            started_at=started_at,
            finished_at=finished_at,
            source_urls=(base_url,),
            errors=tuple(errors),
            warnings=tuple(),
        )
    
    def supports_url(self, url: str) -> bool:
        """
        Verifica se suporta a URL.
        
        Args:
            url: URL a verificar
        
        Returns:
            bool: True se suporta
        """
        return "documentacao.senior.com.br" in url.lower()
    
    def get_source_name(self) -> str:
        """Retorna nome da fonte"""
        return "senior_documentation"
    
    async def validate_url(self, url: str) -> bool:
        """
        Valida se URL é acessível.
        
        Args:
            url: URL a validar
        
        Returns:
            bool: True se válida
        """
        if not self.supports_url(url):
            return False
        
        try:
            page = await self.extractor.navigate(url, timeout=10000)
            await self.extractor.close_page(page)
            return True
        except Exception:
            return False
    
    async def estimate_documents(self, base_url: str) -> int:
        """
        Estima número de documentos.
        
        Args:
            base_url: URL base
        
        Returns:
            int: Estimativa
        """
        try:
            page = await self.extractor.navigate(base_url, timeout=self.timeout)
            
            # Contar links de navegação
            nav_links = await self.extractor.extract_links(page, "nav a, aside a")
            await self.extractor.close_page(page)
            
            return len(nav_links)
            
        except Exception:
            return 0
    
    async def close(self) -> None:
        """Fecha recursos"""
        await self.extractor.close()
        self._visited_urls.clear()
    
    # ============ MÉTODOS PRIVADOS ============
    
    async def _detect_format(self, page) -> str:
        """Detecta formato da documentação (madcap, astro, generic)"""
        # MadCap: tem iframe#topic
        has_iframe = await self.extractor.wait_for_element(page, "iframe#topic", timeout=2000)
        if has_iframe:
            return "madcap"
        
        # Astro: tem aside#sidebar
        has_sidebar = await self.extractor.wait_for_element(page, "aside#sidebar", timeout=2000)
        if has_sidebar:
            return "astro"
        
        return "generic"
    
    async def _scrape_madcap_page(self, page, url: str) -> Document:
        """Extrai conteúdo de página MadCap Flare"""
        # Aguardar iframe carregar
        await self.extractor.wait_for_element(page, "iframe#topic", timeout=self.timeout)
        
        # Mudar contexto para iframe
        iframe = await page.query_selector("iframe#topic")
        frame = await iframe.content_frame()
        
        # Extrair título
        title = await self._extract_text_safe(frame, "h1, h2, .title")
        if not title:
            title = await page.title()
        
        # Extrair conteúdo
        content = await self._extract_text_safe(frame, "body, .content, article")
        
        # Extrair headers
        headers = []
        for tag in ["h1", "h2", "h3", "h4"]:
            header_texts = await self._extract_texts_safe(frame, tag)
            headers.extend(header_texts)
        
        # Extrair breadcrumb (do parent frame)
        breadcrumb = await self._extract_breadcrumb_madcap(page)
        
        # Extrair módulo da URL
        module = self.url_resolver.extract_module(url)
        
        # Determinar tipo de documento
        doc_type = self._determine_doc_type(url, title)
        
        # Gerar ID único
        doc_id = hashlib.md5(url.encode()).hexdigest()
        
        return Document(
            id=doc_id,
            url=url,
            title=title,
            content=content,
            module=module,
            doc_type=doc_type,
            source=DocumentSource.SENIOR_MADCAP,
            breadcrumb=breadcrumb,
            headers=headers,
            scraped_at=datetime.now(),
        )
    
    async def _scrape_astro_page(self, page, url: str) -> Document:
        """Extrai conteúdo de página Astro"""
        # Extrair título
        title = await self._extract_text_safe(page, "h1, .title")
        if not title:
            title = await page.title()
        
        # Extrair conteúdo principal
        content = await self._extract_text_safe(page, "main, article, .content")
        
        # Extrair headers
        headers = []
        for tag in ["h1", "h2", "h3"]:
            header_texts = await self._extract_texts_safe(page, tag)
            headers.extend(header_texts)
        
        # Extrair breadcrumb
        breadcrumb = await self._extract_breadcrumb_astro(page)
        
        # Extrair módulo
        module = self.url_resolver.extract_module(url)
        
        # Tipo de documento
        doc_type = self._determine_doc_type(url, title)
        
        # ID único
        doc_id = hashlib.md5(url.encode()).hexdigest()
        
        return Document(
            id=doc_id,
            url=url,
            title=title,
            content=content,
            module=module,
            doc_type=doc_type,
            source=DocumentSource.SENIOR_ASTRO,
            breadcrumb=breadcrumb,
            headers=headers,
            scraped_at=datetime.now(),
        )
    
    async def _scrape_generic_page(self, page, url: str) -> Document:
        """Extrai conteúdo genérico"""
        title = await page.title()
        content = await self._extract_text_safe(page, "body")
        module = self.url_resolver.extract_module(url)
        doc_id = hashlib.md5(url.encode()).hexdigest()
        
        return Document(
            id=doc_id,
            url=url,
            title=title,
            content=content,
            module=module,
            doc_type=DocumentType.TECHNICAL_DOC,
            source=DocumentSource.UNKNOWN,
            scraped_at=datetime.now(),
        )
    
    async def _discover_madcap_links(self, page, base_url: str) -> List[str]:
        """Descobre links de navegação MadCap"""
        # Expandir menu
        await self._expand_madcap_menu(page)
        
        # Extrair todos os links
        links = await self.extractor.extract_links(page, "nav a, .menu a, .toc a")
        
        # Resolver para URLs absolutas
        absolute_links = []
        for link in links:
            resolved = self.url_resolver.resolve(base_url, link)
            if resolved and resolved not in absolute_links:
                absolute_links.append(resolved)
        
        return absolute_links
    
    async def _discover_astro_links(self, page, base_url: str) -> List[str]:
        """Descobre links de navegação Astro"""
        links = await self.extractor.extract_links(page, "aside#sidebar a")
        
        absolute_links = []
        for link in links:
            resolved = self.url_resolver.resolve(base_url, link)
            if resolved and resolved not in absolute_links:
                absolute_links.append(resolved)
        
        return absolute_links
    
    async def _expand_madcap_menu(self, page, max_rounds: int = 5) -> None:
        """Expande menu MadCap para revelar todos os links"""
        for _ in range(max_rounds):
            # Clicar em expansores (+, >, etc.)
            expanders = await page.query_selector_all(
                ".tree-node-collapsed, .menu-item.collapsed, [aria-expanded='false']"
            )
            
            if not expanders:
                break
            
            for expander in expanders[:10]:  # Limitar por segurança
                try:
                    await expander.click()
                    await asyncio.sleep(0.1)
                except Exception:
                    continue
    
    async def _extract_breadcrumb_madcap(self, page) -> List[str]:
        """Extrai breadcrumb de página MadCap"""
        breadcrumb_texts = await self._extract_texts_safe(
            page,
            ".breadcrumb a, .breadcrumbs a, nav[aria-label='breadcrumb'] a"
        )
        return breadcrumb_texts
    
    async def _extract_breadcrumb_astro(self, page) -> List[str]:
        """Extrai breadcrumb de página Astro"""
        breadcrumb_texts = await self._extract_texts_safe(
            page,
            "nav[aria-label='Breadcrumb'] a, .breadcrumb a"
        )
        return breadcrumb_texts
    
    def _determine_doc_type(self, url: str, title: str) -> DocumentType:
        """Determina tipo de documento baseado em URL e título"""
        url_lower = url.lower()
        title_lower = title.lower()
        
        # Release notes
        if any(term in url_lower for term in ["notas-da-versao", "release-note", "changelog"]):
            return DocumentType.RELEASE_NOTE
        
        if any(term in title_lower for term in ["versão", "release", "changelog"]):
            return DocumentType.RELEASE_NOTE
        
        # API docs
        if any(term in url_lower for term in ["api", "endpoint", "webservice"]):
            return DocumentType.API_DOC
        
        # Tutorial
        if any(term in title_lower for term in ["tutorial", "guia", "como fazer"]):
            return DocumentType.TUTORIAL
        
        # Default: documentação técnica
        return DocumentType.TECHNICAL_DOC
    
    async def _extract_text_safe(self, page_or_frame, selector: str) -> str:
        """Extrai texto com fallback para vazio"""
        try:
            element = await page_or_frame.query_selector(selector)
            if element:
                return (await element.inner_text()).strip()
            return ""
        except Exception:
            return ""
    
    async def _extract_texts_safe(self, page_or_frame, selector: str) -> List[str]:
        """Extrai múltiplos textos com fallback para lista vazia"""
        try:
            elements = await page_or_frame.query_selector_all(selector)
            texts = []
            for element in elements:
                text = (await element.inner_text()).strip()
                if text:
                    texts.append(text)
            return texts
        except Exception:
            return []
