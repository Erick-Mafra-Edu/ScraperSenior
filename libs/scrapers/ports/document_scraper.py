"""
Port - Document Scraper Interface

Define o contrato para implementações de scrapers de documentação.
Qualquer fonte de dados (Senior Docs, Zendesk, etc.) deve implementar esta interface.
"""

from abc import ABC, abstractmethod
from typing import List, AsyncIterator, Optional
from libs.scrapers.domain import Document, ScrapingResult


class IDocumentScraper(ABC):
    """
    Port (Interface) para scrapers de documentação.
    
    Define o contrato que todos os adapters de scraping devem seguir.
    Permite que o core da aplicação trabalhe com qualquer implementação
    sem conhecer detalhes técnicos.
    """
    
    @abstractmethod
    async def scrape(self, url: str, **kwargs) -> Document:
        """
        Scrape uma única URL e retorna um Document.
        
        Args:
            url: URL do documento a ser extraído
            **kwargs: Argumentos adicionais específicos do adapter
        
        Returns:
            Document: Documento extraído
        
        Raises:
            ScrapingError: Se houver erro ao fazer scraping
        """
        pass
    
    @abstractmethod
    async def scrape_multiple(self, urls: List[str], **kwargs) -> AsyncIterator[Document]:
        """
        Scrape múltiplas URLs e retorna um iterator assíncrono de Documents.
        
        Args:
            urls: Lista de URLs a serem extraídas
            **kwargs: Argumentos adicionais específicos do adapter
        
        Yields:
            Document: Documentos extraídos um por vez
        """
        pass
    
    @abstractmethod
    async def scrape_all(self, base_url: str, **kwargs) -> ScrapingResult:
        """
        Scrape todas as páginas a partir de uma URL base.
        Descobre navegação automaticamente e extrai tudo.
        
        Args:
            base_url: URL base para começar o scraping
            **kwargs: Argumentos adicionais específicos do adapter
        
        Returns:
            ScrapingResult: Resultado completo do scraping com todos os documentos
        """
        pass
    
    @abstractmethod
    def supports_url(self, url: str) -> bool:
        """
        Verifica se este scraper suporta a URL fornecida.
        
        Permite que o sistema selecione automaticamente o adapter correto
        baseado na URL.
        
        Args:
            url: URL a ser verificada
        
        Returns:
            bool: True se o scraper suporta a URL, False caso contrário
        """
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """
        Retorna o nome da fonte de dados deste scraper.
        
        Returns:
            str: Nome da fonte (ex: "senior_madcap", "zendesk")
        """
        pass
    
    @abstractmethod
    async def validate_url(self, url: str) -> bool:
        """
        Valida se a URL é acessível e válida.
        
        Args:
            url: URL a ser validada
        
        Returns:
            bool: True se a URL é válida, False caso contrário
        """
        pass
    
    @abstractmethod
    async def estimate_documents(self, base_url: str) -> int:
        """
        Estima quantos documentos serão extraídos de uma URL base.
        
        Útil para mostrar progresso ao usuário.
        
        Args:
            base_url: URL base
        
        Returns:
            int: Estimativa de documentos (0 se impossível estimar)
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """
        Limpa recursos do scraper (fecha browsers, conexões, etc.).
        
        Deve ser chamado quando o scraper não for mais usado.
        """
        pass
