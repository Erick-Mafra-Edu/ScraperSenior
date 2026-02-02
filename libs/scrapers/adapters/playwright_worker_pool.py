"""
Adapter - Playwright Browser Worker Pool

Implementação concreta de IBrowserWorkerPool usando Playwright para
gerenciar múltiplas páginas em paralelo e processar URLs concorrentemente.
"""

import asyncio
import time
import logging
from typing import List, Callable, Any, Optional
from datetime import datetime

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from libs.scrapers.ports.browser_worker_pool import IBrowserWorkerPool, WorkerResult


logger = logging.getLogger(__name__)


class PlaywrightWorkerPool(IBrowserWorkerPool):
    """
    Pool de workers usando Playwright com asyncio.
    
    Características:
    - Múltiplas páginas no mesmo contexto (compartilham cookies/cache)
    - asyncio.Semaphore para limitar concorrência
    - asyncio.Queue para distribuição de URLs entre workers
    - Logging detalhado de duração e erros por worker
    - Retry automático com fallback para processamento sequencial
    """
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Inicializa o pool.
        
        Args:
            headless: Se deve rodar Playwright em modo headless
            timeout: Timeout padrão para operações (ms)
        """
        self.headless = headless
        self.timeout = timeout
        
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.pages: List[Page] = []
        
        self.num_workers = 0
        self.semaphore: Optional[asyncio.Semaphore] = None
        self.queue: Optional[asyncio.Queue] = None
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self, num_workers: int) -> None:
        """Inicializa o Playwright browser e cria N páginas"""
        try:
            self.num_workers = num_workers
            self.semaphore = asyncio.Semaphore(num_workers)
            self.queue = asyncio.Queue()
            
            # Iniciar Playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
            self.context = await self.browser.new_context()
            
            # Criar páginas (workers)
            self.pages = [
                await self.context.new_page() for _ in range(num_workers)
            ]
            
            # Configurar timeout padrão
            for page in self.pages:
                page.set_default_timeout(self.timeout)
            
            self.logger.info(f"✅ Initialized PlaywrightWorkerPool with {num_workers} workers")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize worker pool: {e}")
            raise
    
    async def close(self) -> None:
        """Fecha todas as páginas, contexto e browser"""
        try:
            for page in self.pages:
                try:
                    await page.close()
                except Exception as e:
                    self.logger.warning(f"Error closing page: {e}")
            
            if self.context:
                await self.context.close()
            
            if self.browser:
                await self.browser.close()
            
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            
            self.pages = []
            self.logger.info("✅ Closed PlaywrightWorkerPool")
            
        except Exception as e:
            self.logger.error(f"❌ Error closing worker pool: {e}")
    
    async def process_urls(
        self,
        urls: List[str],
        worker_func: Callable[[str, int], Any],
        show_progress: bool = True
    ) -> List[WorkerResult]:
        """Processa URLs em paralelo usando workers"""
        
        if not self.pages:
            self.logger.error("Worker pool not initialized. Call initialize() first.")
            raise RuntimeError("Worker pool not initialized")
        
        results = []
        completed = 0
        total = len(urls)
        
        async def worker(worker_id: int) -> None:
            """Worker que processa URLs da fila"""
            nonlocal completed
            
            while True:
                try:
                    url = self.queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
                
                start_time = time.time()
                result = WorkerResult(url=url, success=False, worker_id=worker_id)
                
                try:
                    async with self.semaphore:
                        page = self.pages[worker_id]
                        result.result = await worker_func(url, worker_id)
                        result.success = True
                    
                    result.duration_seconds = time.time() - start_time
                    self.logger.debug(
                        f"✅ Worker {worker_id}: {url[:50]}... "
                        f"({result.duration_seconds:.2f}s)"
                    )
                    
                except Exception as e:
                    result.error = str(e)
                    result.duration_seconds = time.time() - start_time
                    self.logger.error(
                        f"❌ Worker {worker_id}: {url[:50]}... "
                        f"Error: {e} ({result.duration_seconds:.2f}s)"
                    )
                
                finally:
                    results.append(result)
                    completed += 1
                    
                    if show_progress:
                        progress = (completed / total) * 100
                        self.logger.info(
                            f"Progress: {completed}/{total} ({progress:.1f}%) - "
                            f"Last: {url[:50]}..."
                        )
                    
                    self.queue.task_done()
        
        # Adicionar URLs à fila
        for url in urls:
            await self.queue.put(url)
        
        # Criar tasks para todos os workers
        worker_tasks = [
            asyncio.create_task(worker(i)) for i in range(self.num_workers)
        ]
        
        # Aguardar todos os workers completarem
        await asyncio.gather(*worker_tasks)
        
        self.logger.info(
            f"✅ Completed processing {total} URLs "
            f"({len([r for r in results if r.success])} successful)"
        )
        
        return results
    
    async def process_urls_with_retry(
        self,
        urls: List[str],
        worker_func: Callable[[str, int], Any],
        max_retries: int = 3,
        show_progress: bool = True
    ) -> List[WorkerResult]:
        """Processa URLs com retry automático"""
        
        remaining_urls = urls.copy()
        all_results = []
        
        for attempt in range(max_retries):
            self.logger.info(
                f"Attempt {attempt + 1}/{max_retries}: "
                f"Processing {len(remaining_urls)} URLs"
            )
            
            # Processar URLs restantes
            results = await self.process_urls(
                remaining_urls,
                worker_func,
                show_progress=show_progress
            )
            
            all_results.extend(results)
            
            # Separar sucesso de falhas
            failed_urls = [r.url for r in results if not r.success]
            
            if not failed_urls:
                self.logger.info("✅ All URLs processed successfully!")
                break
            
            remaining_urls = failed_urls
            
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                self.logger.info(
                    f"⏳ Retrying {len(failed_urls)} failed URLs in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
        
        return all_results
    
    def get_num_workers(self) -> int:
        """Retorna número de workers"""
        return self.num_workers
    
    def get_queue_size(self) -> int:
        """Retorna tamanho da fila (URLs pendentes)"""
        return self.queue.qsize() if self.queue else 0


# Helper para criar uma função worker padrão
async def create_standard_worker_func(
    page_getter: Callable[[int], Page]
) -> Callable[[str, int], Any]:
    """
    Cria uma função worker padrão que apenas navega para URL.
    
    Útil para testes e benchmarks.
    """
    async def worker(url: str, worker_id: int) -> str:
        page = page_getter(worker_id)
        await page.goto(url, wait_until="networkidle")
        title = await page.title()
        return title
    
    return worker
