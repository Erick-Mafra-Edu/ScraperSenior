"""
Adapter - Zendesk Scraper

Implementação concreta de IDocumentScraper para Zendesk Help Center.
Extrai artigos, categorias e seções via API REST.
"""

import hashlib
from datetime import datetime
from typing import List, Optional, AsyncIterator
import aiohttp

from libs.scrapers.ports import IDocumentScraper
from libs.scrapers.domain import Document, ScrapingResult, DocumentType, DocumentSource


class ZendeskAdapter(IDocumentScraper):
    """
    Adapter para scraping de Zendesk Help Center.
    
    Usa API REST do Zendesk para extrair artigos de forma eficiente.
    API: https://suporte.senior.com.br/api/v2/help_center/pt-br/
    """
    
    def __init__(
        self,
        base_url: str = "https://suporte.senior.com.br/api/v2/help_center/pt-br",
        timeout: int = 30,
    ):
        """
        Inicializa adapter.
        
        Args:
            base_url: URL base da API Zendesk
            timeout: Timeout em segundos
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _ensure_session(self):
        """Garante que session está criada"""
        if self._session is None:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
    
    async def scrape(self, url: str, **kwargs) -> Document:
        """
        Scrape um artigo específico.
        
        Args:
            url: URL do artigo
            **kwargs: article_id pode ser passado para otimizar
        
        Returns:
            Document: Artigo extraído
        """
        await self._ensure_session()
        
        # Extrair article_id da URL ou usar kwargs
        article_id = kwargs.get("article_id") or self._extract_article_id(url)
        
        if not article_id:
            raise ValueError(f"Cannot extract article_id from {url}")
        
        # Buscar artigo via API
        api_url = f"{self.base_url}/articles/{article_id}"
        
        async with self._session.get(api_url) as response:
            response.raise_for_status()
            data = await response.json()
        
        article = data.get("article", {})
        
        return self._article_to_document(article)
    
    async def scrape_multiple(
        self,
        urls: List[str],
        **kwargs
    ) -> AsyncIterator[Document]:
        """
        Scrape múltiplos artigos.
        
        Args:
            urls: Lista de URLs
            **kwargs: Argumentos adicionais
        
        Yields:
            Document: Artigos extraídos
        """
        for url in urls:
            try:
                doc = await self.scrape(url)
                yield doc
            except Exception as e:
                print(f"Error scraping Zendesk article {url}: {str(e)}")
                continue
    
    async def scrape_all(self, base_url: str, **kwargs) -> ScrapingResult:
        """
        Scrape todos os artigos do Zendesk.
        
        Args:
            base_url: URL base (ignorado, usa API)
            **kwargs: Argumentos adicionais
        
        Returns:
            ScrapingResult: Todos os artigos
        """
        started_at = datetime.now()
        documents = []
        errors = []
        successful = 0
        failed = 0
        
        await self._ensure_session()
        
        try:
            # Buscar todos os artigos via API paginada
            page = 1
            has_more = True
            
            while has_more:
                api_url = f"{self.base_url}/articles?page={page}&per_page=100"
                
                async with self._session.get(api_url) as response:
                    response.raise_for_status()
                    data = await response.json()
                
                articles = data.get("articles", [])
                
                for article in articles:
                    try:
                        doc = self._article_to_document(article)
                        documents.append(doc)
                        successful += 1
                    except Exception as e:
                        errors.append(str(e))
                        failed += 1
                
                # Verificar se tem mais páginas
                has_more = data.get("next_page") is not None
                page += 1
        
        except Exception as e:
            errors.append(f"Failed to fetch articles: {str(e)}")
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
        """Verifica se suporta a URL"""
        return "suporte.senior.com.br" in url.lower()
    
    def get_source_name(self) -> str:
        """Retorna nome da fonte"""
        return "zendesk"
    
    async def validate_url(self, url: str) -> bool:
        """Valida se URL é acessível"""
        if not self.supports_url(url):
            return False
        
        try:
            await self._ensure_session()
            async with self._session.head(url, timeout=10) as response:
                return response.status == 200
        except Exception:
            return False
    
    async def estimate_documents(self, base_url: str) -> int:
        """Estima número de documentos"""
        try:
            await self._ensure_session()
            
            # Buscar primeira página para ver total
            api_url = f"{self.base_url}/articles?page=1&per_page=1"
            
            async with self._session.get(api_url) as response:
                response.raise_for_status()
                data = await response.json()
            
            return data.get("count", 0)
            
        except Exception:
            return 0
    
    async def close(self) -> None:
        """Fecha recursos"""
        if self._session:
            await self._session.close()
            self._session = None
    
    def _article_to_document(self, article: dict) -> Document:
        """Converte artigo Zendesk para Document"""
        article_id = str(article.get("id"))
        title = article.get("title", "")
        body = article.get("body", "")
        url = article.get("html_url", "")
        
        # Remover HTML tags do body (simplificado)
        import re
        content = re.sub(r'<[^>]+>', '', body)
        
        # Extrair módulo/categoria
        section_id = article.get("section_id")
        module = f"zendesk-section-{section_id}" if section_id else "zendesk"
        
        # ID único
        doc_id = hashlib.md5(article_id.encode()).hexdigest()
        
        return Document(
            id=doc_id,
            url=url,
            title=title,
            content=content,
            module=module,
            doc_type=DocumentType.HELP_ARTICLE,
            source=DocumentSource.ZENDESK,
            scraped_at=datetime.now(),
            metadata={
                "article_id": article_id,
                "section_id": section_id,
                "category_id": article.get("category_id"),
                "created_at": article.get("created_at"),
                "updated_at": article.get("updated_at"),
            }
        )
    
    def _extract_article_id(self, url: str) -> Optional[str]:
        """Extrai article_id da URL"""
        import re
        match = re.search(r'/articles/(\d+)', url)
        if match:
            return match.group(1)
        return None
