"""
Testes de integração para Docker Multi-Worker Orchestrator
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

from libs.scrapers.adapters.docker_worker_orchestrator import (
    DockerWorkerOrchestrator,
    WorkerContainer,
)


@pytest.mark.asyncio
async def test_worker_container_dataclass():
    """Testa estrutura de WorkerContainer"""
    worker = WorkerContainer(
        container_id="abc123",
        container_name="senior-docs-worker-001",
        status="running",
        urls_processed=10,
        success_count=9,
        error_count=1,
        avg_duration_seconds=1.5
    )
    
    assert worker.container_id == "abc123"
    assert worker.container_name == "senior-docs-worker-001"
    assert worker.status == "running"
    assert worker.urls_processed == 10
    assert worker.success_count == 9
    assert worker.error_count == 1


@pytest.mark.asyncio
async def test_worker_container_success_rate():
    """Testa cálculo de taxa de sucesso"""
    worker = WorkerContainer(
        container_id="abc123",
        container_name="test",
        status="running",
        urls_processed=100,
        success_count=95,
        error_count=5,
    )
    
    success_rate = worker.success_count / worker.urls_processed
    assert success_rate == 0.95


@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """Testa inicialização do orchestrador"""
    orchestrator = DockerWorkerOrchestrator(
        image_name="custom-image:latest",
        network_name="custom-network"
    )
    
    assert orchestrator.image_name == "custom-image:latest"
    assert orchestrator.network_name == "custom-network"
    assert len(orchestrator.workers) == 0


@pytest.mark.asyncio
async def test_orchestrator_queue():
    """Testa fila do orchestrador"""
    orchestrator = DockerWorkerOrchestrator()
    
    # Adicionar URLs à fila
    urls = [
        "https://example.com/1",
        "https://example.com/2",
        "https://example.com/3",
    ]
    
    await orchestrator.distribute_urls(urls, batch_size=2)
    
    assert orchestrator.queue.qsize() == 3


@pytest.mark.asyncio
async def test_orchestrator_stats_empty():
    """Testa estatísticas com zero workers"""
    orchestrator = DockerWorkerOrchestrator()
    
    stats = await orchestrator.get_worker_stats()
    
    assert stats["total_workers"] == 0
    assert stats["total_urls_processed"] == 0
    assert stats["total_success"] == 0
    assert stats["total_errors"] == 0


@pytest.mark.asyncio
async def test_orchestrator_stats_with_workers():
    """Testa estatísticas com múltiplos workers"""
    orchestrator = DockerWorkerOrchestrator()
    
    # Simular workers com estatísticas
    worker1 = WorkerContainer(
        container_id="abc123",
        container_name="worker-1",
        status="running",
        urls_processed=50,
        success_count=48,
        error_count=2,
    )
    
    worker2 = WorkerContainer(
        container_id="def456",
        container_name="worker-2",
        status="running",
        urls_processed=50,
        success_count=50,
        error_count=0,
    )
    
    orchestrator.workers[worker1.container_id] = worker1
    orchestrator.workers[worker2.container_id] = worker2
    
    stats = await orchestrator.get_worker_stats()
    
    assert stats["total_workers"] == 2
    assert stats["total_urls_processed"] == 100
    assert stats["total_success"] == 98
    assert stats["total_errors"] == 2
    assert abs(stats["success_rate"] - 98.0) < 0.1


@pytest.mark.asyncio
async def test_worker_container_batch_processing():
    """Testa processamento em lote de containers"""
    workers = [
        WorkerContainer(f"id{i}", f"worker-{i}", "running", urls_processed=10+i)
        for i in range(3)
    ]
    
    total_processed = sum(w.urls_processed for w in workers)
    assert total_processed == 33  # 10 + 11 + 12


@pytest.mark.asyncio
async def test_orchestrator_json_serialization():
    """Testa serialização JSON de estatísticas"""
    orchestrator = DockerWorkerOrchestrator()
    
    worker = WorkerContainer(
        container_id="abc123",
        container_name="worker-1",
        status="running",
        urls_processed=10,
        success_count=9,
        error_count=1,
    )
    
    orchestrator.workers[worker.container_id] = worker
    
    stats = await orchestrator.get_worker_stats()
    
    # Deve ser serializável em JSON
    json_str = json.dumps(stats, default=str)
    assert len(json_str) > 0
    
    # Desserializar para validar
    parsed = json.loads(json_str)
    assert parsed["total_workers"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
