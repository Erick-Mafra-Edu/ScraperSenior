"""
Use Case - Scrape Documentation

Orquestra o processo de scraping de documentação usando os ports (interfaces).
Este use case é independente de implementações específicas.
"""

import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from libs.scrapers.domain import Document, ScrapingResult, DocumentSource
from libs.scrapers.ports import IDocumentScraper, IDocumentRepository


class ScrapeDocumentation:
    """
    Use Case: Scrape Documentation
    
    Coordena o processo de scraping de documentação:
    1. Seleciona scraper apropriado para cada URL
    2. Executa scraping
    3. Persiste documentos
    4. Retorna resultado com estatísticas
    
    Este use case implementa a lógica de negócio core,
    usando apenas interfaces (ports), sem conhecer implementações.
    """
    
    def __init__(
        self,
        scrapers: List[IDocumentScraper],
        repository: IDocumentRepository,
    ):
        """
        Inicializa use case com dependências.
        
        Args:
            scrapers: Lista de scrapers disponíveis
            repository: Repositório para persistir documentos
        """
        self.scrapers = scrapers
        self.repository = repository
    
    async def execute(
        self,
        urls: List[str],
        save_to_repository: bool = True,
        max_concurrent: int = 5,
    ) -> ScrapingResult:
        """
        Executa scraping de múltiplas URLs.
        
        Args:
            urls: Lista de URLs para scraping
            save_to_repository: Se True, salva documentos no repositório
            max_concurrent: Número máximo de scrapes simultâneos
        
        Returns:
            ScrapingResult: Resultado do scraping com todos os documentos
        """
        started_at = datetime.now()
        documents: List[Document] = []
        errors: List[str] = []
        warnings: List[str] = []
        successful = 0
        failed = 0
        skipped = 0
        
        # Agrupar URLs por scraper
        urls_by_scraper = self._group_urls_by_scraper(urls)
        
        # Processar cada grupo com seu scraper apropriado
        for scraper, scraper_urls in urls_by_scraper.items():
            if scraper is None:
                skipped += len(scraper_urls)
                warnings.extend([
                    f"No scraper supports URL: {url}" for url in scraper_urls
                ])
                continue
            
            # Scraping com concorrência limitada
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def scrape_with_limit(url: str) -> Optional[Document]:
                async with semaphore:
                    return await self._scrape_single(scraper, url, errors)
            
            tasks = [scrape_with_limit(url) for url in scraper_urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Processar resultados
            for result in results:
                if isinstance(result, Exception):
                    failed += 1
                    errors.append(str(result))
                elif result is not None:
                    documents.append(result)
                    successful += 1
                else:
                    failed += 1
        
        # Salvar documentos se solicitado
        if save_to_repository and documents:
            try:
                await self.repository.save_many(documents)
            except Exception as e:
                errors.append(f"Failed to save documents: {str(e)}")
        
        finished_at = datetime.now()
        
        # Criar resultado
        result = ScrapingResult(
            documents=tuple(documents),
            total_documents=len(documents),
            successful_scrapes=successful,
            failed_scrapes=failed,
            skipped_urls=skipped,
            started_at=started_at,
            finished_at=finished_at,
            source_urls=tuple(urls),
            errors=tuple(errors),
            warnings=tuple(warnings),
        )
        
        return result
    
    async def execute_full_site(
        self,
        base_url: str,
        save_to_repository: bool = True,
    ) -> ScrapingResult:
        """
        Executa scraping completo de um site a partir de URL base.
        
        O scraper descobrirá automaticamente todas as páginas.
        
        Args:
            base_url: URL base do site
            save_to_repository: Se True, salva documentos
        
        Returns:
            ScrapingResult: Resultado completo do scraping
        """
        started_at = datetime.now()
        
        # Encontrar scraper apropriado
        scraper = self._find_scraper_for_url(base_url)
        
        if scraper is None:
            return ScrapingResult(
                documents=tuple(),
                total_documents=0,
                successful_scrapes=0,
                failed_scrapes=0,
                skipped_urls=1,
                started_at=started_at,
                finished_at=datetime.now(),
                source_urls=(base_url,),
                errors=(f"No scraper supports URL: {base_url}",),
                warnings=tuple(),
            )
        
        # Executar scraping completo
        try:
            result = await scraper.scrape_all(base_url)
            
            # Salvar documentos
            if save_to_repository and result.documents:
                await self.repository.save_many(list(result.documents))
            
            return result
            
        except Exception as e:
            return ScrapingResult(
                documents=tuple(),
                total_documents=0,
                successful_scrapes=0,
                failed_scrapes=1,
                skipped_urls=0,
                started_at=started_at,
                finished_at=datetime.now(),
                source_urls=(base_url,),
                errors=(str(e),),
                warnings=tuple(),
            )
    
    async def validate_urls(self, urls: List[str]) -> Dict[str, bool]:
        """
        Valida lista de URLs antes de scraping.
        
        Args:
            urls: Lista de URLs para validar
        
        Returns:
            Dict[str, bool]: Mapa de URL -> válida (True/False)
        """
        results = {}
        
        for url in urls:
            scraper = self._find_scraper_for_url(url)
            if scraper is None:
                results[url] = False
            else:
                try:
                    results[url] = await scraper.validate_url(url)
                except:
                    results[url] = False
        
        return results
    
    async def estimate_total_documents(self, urls: List[str]) -> int:
        """
        Estima total de documentos que serão extraídos.
        
        Args:
            urls: Lista de URLs
        
        Returns:
            int: Estimativa total
        """
        total = 0
        
        for url in urls:
            scraper = self._find_scraper_for_url(url)
            if scraper:
                try:
                    estimate = await scraper.estimate_documents(url)
                    total += estimate
                except:
                    pass
        
        return total
    
    def _find_scraper_for_url(self, url: str) -> Optional[IDocumentScraper]:
        """Encontra scraper que suporta a URL"""
        for scraper in self.scrapers:
            if scraper.supports_url(url):
                return scraper
        return None
    
    def _group_urls_by_scraper(self, urls: List[str]) -> Dict[Optional[IDocumentScraper], List[str]]:
        """Agrupa URLs por scraper apropriado"""
        groups: Dict[Optional[IDocumentScraper], List[str]] = {}
        
        for url in urls:
            scraper = self._find_scraper_for_url(url)
            if scraper not in groups:
                groups[scraper] = []
            groups[scraper].append(url)
        
        return groups
    
    async def _scrape_single(
        self,
        scraper: IDocumentScraper,
        url: str,
        errors: List[str],
    ) -> Optional[Document]:
        """Scrape uma única URL com tratamento de erros"""
        try:
            return await scraper.scrape(url)
        except Exception as e:
            errors.append(f"Failed to scrape {url}: {str(e)}")
            return None
    
    async def close(self) -> None:
        """Fecha todos os scrapers e libera recursos"""
        for scraper in self.scrapers:
            try:
                await scraper.close()
            except:
                pass
