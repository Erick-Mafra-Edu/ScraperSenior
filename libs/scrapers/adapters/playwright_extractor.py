"""
Adapter - Playwright Content Extractor

Implementação concreta de IContentExtractor usando Playwright.
Abstrai detalhes do Playwright para o resto da aplicação.
"""

from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from libs.scrapers.ports import IContentExtractor


class PlaywrightExtractor(IContentExtractor):
    """
    Adapter que implementa IContentExtractor usando Playwright.
    
    Encapsula toda a complexidade do Playwright, fornecendo
    uma interface simples para extração de conteúdo web.
    """
    
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
        user_agent: Optional[str] = None,
    ):
        """
        Inicializa extractor.
        
        Args:
            headless: Se True, roda browser em modo headless
            timeout: Timeout padrão em milissegundos
            user_agent: User agent customizado (opcional)
        """
        self.headless = headless
        self.timeout = timeout
        self.user_agent = user_agent
        
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
    
    async def _ensure_browser(self) -> Browser:
        """Garante que o browser está iniciado"""
        if self._browser is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless
            )
            
            # Criar contexto com configurações
            context_options = {
                "user_agent": self.user_agent,
            } if self.user_agent else {}
            
            self._context = await self._browser.new_context(**context_options)
        
        return self._browser
    
    async def navigate(self, url: str, timeout: int = 30000) -> Page:
        """
        Navega para uma URL e retorna a página.
        
        Args:
            url: URL de destino
            timeout: Timeout em milissegundos
        
        Returns:
            Page: Página carregada
        """
        await self._ensure_browser()
        
        page = await self._context.new_page()
        
        try:
            await page.goto(url, timeout=timeout, wait_until="networkidle")
            return page
        except Exception as e:
            await page.close()
            raise Exception(f"Failed to navigate to {url}: {str(e)}")
    
    async def extract_text(self, page: Page, selector: str) -> str:
        """
        Extrai texto de um elemento.
        
        Args:
            page: Página
            selector: Seletor CSS
        
        Returns:
            str: Texto extraído (vazio se não encontrado)
        """
        try:
            element = await page.query_selector(selector)
            if element:
                text = await element.inner_text()
                return text.strip()
            return ""
        except Exception:
            return ""
    
    async def extract_texts(self, page: Page, selector: str) -> List[str]:
        """
        Extrai texto de múltiplos elementos.
        
        Args:
            page: Página
            selector: Seletor CSS
        
        Returns:
            List[str]: Lista de textos extraídos
        """
        try:
            elements = await page.query_selector_all(selector)
            texts = []
            for element in elements:
                text = await element.inner_text()
                if text.strip():
                    texts.append(text.strip())
            return texts
        except Exception:
            return []
    
    async def extract_attribute(
        self,
        page: Page,
        selector: str,
        attribute: str
    ) -> Optional[str]:
        """
        Extrai atributo de um elemento.
        
        Args:
            page: Página
            selector: Seletor CSS
            attribute: Nome do atributo
        
        Returns:
            Optional[str]: Valor do atributo ou None
        """
        try:
            element = await page.query_selector(selector)
            if element:
                value = await element.get_attribute(attribute)
                return value
            return None
        except Exception:
            return None
    
    async def extract_links(self, page: Page, selector: str) -> List[str]:
        """
        Extrai todos os links (href) de elementos.
        
        Args:
            page: Página
            selector: Seletor CSS
        
        Returns:
            List[str]: Lista de URLs
        """
        try:
            elements = await page.query_selector_all(selector)
            links = []
            for element in elements:
                href = await element.get_attribute("href")
                if href:
                    links.append(href)
            return links
        except Exception:
            return []
    
    async def wait_for_element(
        self,
        page: Page,
        selector: str,
        timeout: int = 30000
    ) -> bool:
        """
        Aguarda elemento aparecer na página.
        
        Args:
            page: Página
            selector: Seletor CSS
            timeout: Timeout em milissegundos
        
        Returns:
            bool: True se elemento apareceu, False se timeout
        """
        try:
            await page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception:
            return False
    
    async def click(self, page: Page, selector: str) -> None:
        """
        Clica em um elemento.
        
        Args:
            page: Página
            selector: Seletor CSS
        
        Raises:
            Exception: Se falhar ao clicar
        """
        try:
            await page.click(selector)
        except Exception as e:
            raise Exception(f"Failed to click on {selector}: {str(e)}")
    
    async def execute_script(self, page: Page, script: str) -> Any:
        """
        Executa JavaScript na página.
        
        Args:
            page: Página
            script: Código JavaScript
        
        Returns:
            Any: Resultado da execução
        """
        try:
            return await page.evaluate(script)
        except Exception as e:
            raise Exception(f"Failed to execute script: {str(e)}")
    
    async def get_page_html(self, page: Page) -> str:
        """
        Retorna HTML completo da página.
        
        Args:
            page: Página
        
        Returns:
            str: HTML da página
        """
        try:
            return await page.content()
        except Exception:
            return ""
    
    async def screenshot(self, page: Page, filepath: str) -> None:
        """
        Tira screenshot da página.
        
        Args:
            page: Página
            filepath: Caminho para salvar imagem
        """
        try:
            await page.screenshot(path=filepath)
        except Exception as e:
            raise Exception(f"Failed to take screenshot: {str(e)}")
    
    async def close_page(self, page: Page) -> None:
        """
        Fecha uma página.
        
        Args:
            page: Página a ser fechada
        """
        try:
            await page.close()
        except Exception:
            pass
    
    async def close(self) -> None:
        """
        Fecha o extrator e limpa recursos.
        """
        if self._context:
            await self._context.close()
            self._context = None
        
        if self._browser:
            await self._browser.close()
            self._browser = None
        
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
