"""
Testes unitários para PlaywrightWorkerPool
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from libs.scrapers.adapters.playwright_worker_pool import (
    PlaywrightWorkerPool,
    WorkerResult,
)


@pytest.mark.asyncio
async def test_worker_pool_initialization():
    """Testa inicialização básica do worker pool"""
    pool = PlaywrightWorkerPool(headless=True)
    
    assert pool.num_workers == 0
    assert pool.pages == []
    assert pool.semaphore is None
    
    # Não inicializa de verdade (evita dep. do Playwright em CI)
    # Apenas testa estrutura


@pytest.mark.asyncio
async def test_worker_result_dataclass():
    """Testa estrutura de WorkerResult"""
    result = WorkerResult(
        url="https://example.com",
        success=True,
        result="success_data",
        worker_id=0,
        duration_seconds=1.5
    )
    
    assert result.url == "https://example.com"
    assert result.success is True
    assert result.result == "success_data"
    assert result.worker_id == 0
    assert result.duration_seconds == 1.5
    assert result.error is None


@pytest.mark.asyncio
async def test_worker_result_with_error():
    """Testa WorkerResult com erro"""
    result = WorkerResult(
        url="https://example.com",
        success=False,
        error="Timeout",
        worker_id=1,
        duration_seconds=5.0
    )
    
    assert result.success is False
    assert result.error == "Timeout"
    assert result.result is None


@pytest.mark.asyncio
async def test_pool_configuration():
    """Testa configurações do pool"""
    pool = PlaywrightWorkerPool(
        headless=True,
        timeout=60000
    )
    
    assert pool.headless is True
    assert pool.timeout == 60000


@pytest.mark.asyncio
async def test_get_methods_before_init():
    """Testa métodos getter antes de inicializar"""
    pool = PlaywrightWorkerPool()
    
    assert pool.get_num_workers() == 0
    assert pool.get_queue_size() == 0


@pytest.mark.asyncio
async def test_worker_result_batch_processing():
    """Testa processamento em lote de resultados"""
    r1 = WorkerResult("url1", True, "result1", 0, 1.0)
    r2 = WorkerResult("url2", False, error="Error", worker_id=1, duration_seconds=0.5)
    r3 = WorkerResult("url3", True, "result3", 1, 1.5)
    
    results = [r1, r2, r3]
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    assert len(successful) == 2
    assert len(failed) == 1
    assert len(results) == 3


@pytest.mark.asyncio
async def test_worker_result_statistics():
    """Testa estatísticas de WorkerResult"""
    results = [
        WorkerResult("url1", True, "result1", 0, 2.0),
        WorkerResult("url2", True, "result2", 1, 1.5),
        WorkerResult("url3", False, error="Error", worker_id=1, duration_seconds=5.0),
        WorkerResult("url4", True, "result4", 0, 0.8),
    ]
    
    success_count = sum(1 for r in results if r.success)
    total_count = len(results)
    success_rate = success_count / total_count
    
    assert success_rate == 0.75
    assert success_count == 3
    assert total_count == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
