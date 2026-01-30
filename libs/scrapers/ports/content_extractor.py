"""
Port - Content Extractor Interface

Define o contrato para extração de conteúdo de páginas web.
Abstrai detalhes de Playwright, Selenium, ou outras ferramentas.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from playwright.async_api import Page


class IContentExtractor(ABC):
    """
    Port (Interface) para extratores de conteúdo web.
    
    Abstrai a ferramenta de scraping (Playwright, Selenium, etc.)
    permitindo que o core trabalhe com qualquer implementação.
    """
    
    @abstractmethod
    async def navigate(self, url: str, timeout: int = 30000) -> Page:
        """
        Navega para uma URL e retorna a página.
        
        Args:
            url: URL de destino
            timeout: Timeout em milissegundos
        
        Returns:
            Page: Página carregada (abstração)
        
        Raises:
            NavigationError: Se falhar ao navegar
        """
        pass
    
    @abstractmethod
    async def extract_text(self, page: Page, selector: str) -> str:
        """
        Extrai texto de um elemento.
        
        Args:
            page: Página
            selector: Seletor CSS
        
        Returns:
            str: Texto extraído (vazio se não encontrado)
        """
        pass
    
    @abstractmethod
    async def extract_texts(self, page: Page, selector: str) -> List[str]:
        """
        Extrai texto de múltiplos elementos.
        
        Args:
            page: Página
            selector: Seletor CSS
        
        Returns:
            List[str]: Lista de textos extraídos
        """
        pass
    
    @abstractmethod
    async def extract_attribute(self, page: Page, selector: str, attribute: str) -> Optional[str]:
        """
        Extrai atributo de um elemento.
        
        Args:
            page: Página
            selector: Seletor CSS
            attribute: Nome do atributo (ex: "href", "src")
        
        Returns:
            Optional[str]: Valor do atributo ou None
        """
        pass
    
    @abstractmethod
    async def extract_links(self, page: Page, selector: str) -> List[str]:
        """
        Extrai todos os links (href) de elementos.
        
        Args:
            page: Página
            selector: Seletor CSS (ex: "a", "nav a")
        
        Returns:
            List[str]: Lista de URLs
        """
        pass
    
    @abstractmethod
    async def wait_for_element(self, page: Page, selector: str, timeout: int = 30000) -> bool:
        """
        Aguarda elemento aparecer na página.
        
        Args:
            page: Página
            selector: Seletor CSS
            timeout: Timeout em milissegundos
        
        Returns:
            bool: True se elemento apareceu, False se timeout
        """
        pass
    
    @abstractmethod
    async def click(self, page: Page, selector: str) -> None:
        """
        Clica em um elemento.
        
        Args:
            page: Página
            selector: Seletor CSS
        
        Raises:
            InteractionError: Se falhar ao clicar
        """
        pass
    
    @abstractmethod
    async def execute_script(self, page: Page, script: str) -> Any:
        """
        Executa JavaScript na página.
        
        Args:
            page: Página
            script: Código JavaScript
        
        Returns:
            Any: Resultado da execução
        """
        pass
    
    @abstractmethod
    async def get_page_html(self, page: Page) -> str:
        """
        Retorna HTML completo da página.
        
        Args:
            page: Página
        
        Returns:
            str: HTML da página
        """
        pass
    
    @abstractmethod
    async def screenshot(self, page: Page, filepath: str) -> None:
        """
        Tira screenshot da página.
        
        Args:
            page: Página
            filepath: Caminho para salvar imagem
        """
        pass
    
    @abstractmethod
    async def close_page(self, page: Page) -> None:
        """
        Fecha uma página.
        
        Args:
            page: Página a ser fechada
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """
        Fecha o extrator e limpa recursos (browser, etc.).
        """
        pass
