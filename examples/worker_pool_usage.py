"""
Exemplo de uso do PlaywrightWorkerPool com scraper

Este arquivo demonstra como usar o worker pool para processar URLs em paralelo.
"""

import asyncio
import logging
from typing import List

from libs.scrapers.adapters.playwright_worker_pool import PlaywrightWorkerPool
from libs.scrapers.domain import Document, DocumentSource, DocumentType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def scrape_url_with_worker(url: str, worker_id: int, pool: PlaywrightWorkerPool) -> Document:
    """
    Função worker que scrapa uma URL e retorna um Document.
    
    Esta função é executada dentro de um worker do pool.
    """
    page = pool.pages[worker_id]
    
    try:
        # Navegar para a URL
        await page.goto(url, wait_until="networkidle", timeout=30000)
        
        # Extrair título
        title = await page.title() or "Untitled"
        
        # Extrair conteúdo
        content = await page.text_content() or ""
        
        # Criar documento
        doc = Document(
            id=url,
            url=url,
            title=title,
            content=content,
            module="scraped",
            doc_type=DocumentType.TECHNICAL_DOC,
            source=DocumentSource.UNKNOWN,
            processed_by_worker=worker_id
        )
        
        return doc
        
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        raise


async def main_example_basic():
    """Exemplo básico: Processar URLs com 3 workers"""
    
    pool = PlaywrightWorkerPool(headless=True, timeout=30000)
    
    try:
        # Inicializar pool com 3 workers
        await pool.initialize(num_workers=3)
        
        # URLs para processar
        urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3",
            "https://example.com/page4",
            "https://example.com/page5",
        ]
        
        # Processar URLs em paralelo
        results = await pool.process_urls(
            urls,
            worker_func=lambda url, worker_id: scrape_url_with_worker(url, worker_id, pool),
            show_progress=True
        )
        
        # Analisar resultados
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        logger.info(f"✅ Sucesso: {len(successful)}/{len(results)}")
        logger.info(f"❌ Falhas: {len(failed)}/{len(results)}")
        
        for result in results:
            if result.success:
                doc = result.result
                logger.info(f"  ✓ {doc.title} ({result.duration_seconds:.2f}s)")
            else:
                logger.info(f"  ✗ {result.url} - {result.error}")
        
    finally:
        await pool.close()


async def main_example_with_retry():
    """Exemplo com retry automático"""
    
    pool = PlaywrightWorkerPool(headless=True)
    
    try:
        await pool.initialize(num_workers=2)
        
        urls = [
            "https://example.com/unreliable1",
            "https://example.com/unreliable2",
        ]
        
        # Processar com até 3 tentativas
        results = await pool.process_urls_with_retry(
            urls,
            worker_func=lambda url, worker_id: scrape_url_with_worker(url, worker_id, pool),
            max_retries=3,
            show_progress=True
        )
        
        logger.info(f"Final results: {len([r for r in results if r.success])} successful")
        
    finally:
        await pool.close()


async def main_example_monitoring():
    """Exemplo com monitoramento de progresso"""
    
    pool = PlaywrightWorkerPool(headless=True)
    
    try:
        num_workers = 3
        await pool.initialize(num_workers=num_workers)
        
        urls = [f"https://example.com/page{i}" for i in range(1, 21)]
        
        logger.info(f"Processing {len(urls)} URLs with {num_workers} workers")
        
        results = await pool.process_urls(
            urls,
            worker_func=lambda url, worker_id: scrape_url_with_worker(url, worker_id, pool),
            show_progress=True
        )
        
        # Estatísticas
        total_time = sum(r.duration_seconds for r in results)
        avg_time = total_time / len(results)
        success_rate = sum(1 for r in results if r.success) / len(results) * 100
        
        logger.info(f"\n📊 Estatísticas:")
        logger.info(f"  Total URLs: {len(results)}")
        logger.info(f"  Successful: {sum(1 for r in results if r.success)}")
        logger.info(f"  Failed: {sum(1 for r in results if not r.success)}")
        logger.info(f"  Success Rate: {success_rate:.1f}%")
        logger.info(f"  Total Time: {total_time:.2f}s")
        logger.info(f"  Avg Time/URL: {avg_time:.2f}s")
        logger.info(f"  Throughput: {len(results) / total_time:.2f} URLs/s")
        
    finally:
        await pool.close()


if __name__ == "__main__":
    # Descomentar para rodar exemplos
    # asyncio.run(main_example_basic())
    # asyncio.run(main_example_with_retry())
    # asyncio.run(main_example_monitoring())
    
    print("✅ Worker pool examples loaded. Uncomment to run.")
