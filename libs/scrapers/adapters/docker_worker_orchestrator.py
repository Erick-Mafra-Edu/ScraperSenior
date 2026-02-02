"""
Docker Multi-Worker Orchestrator

Gerencia múltiplos containers de workers e distribui URLs entre eles.
Permite escalar scraping horizontalmente com containers Docker.
"""

import asyncio
import json
import logging
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import docker
from docker.models.containers import Container

logger = logging.getLogger(__name__)


@dataclass
class WorkerContainer:
    """Representação de um container worker"""
    container_id: str
    container_name: str
    status: str  # running, stopped, created
    urls_processed: int = 0
    success_count: int = 0
    error_count: int = 0
    last_heartbeat: Optional[datetime] = None
    avg_duration_seconds: float = 0.0


class DockerWorkerOrchestrator:
    """
    Orchestrador de workers via Docker.
    
    Permite:
    - Criar e gerenciar múltiplos containers workers
    - Distribuir URLs entre workers
    - Monitorar saúde dos workers
    - Escalar dinamicamente
    - Coletar resultados
    """
    
    def __init__(self, image_name: str = "senior-docs-scraper:latest", network_name: str = "senior-docs"):
        self.image_name = image_name
        self.network_name = network_name
        
        self.client = docker.from_env()
        self.workers: Dict[str, WorkerContainer] = {}
        self.queue: asyncio.Queue = asyncio.Queue()
        
        self.logger = logging.getLogger(__name__)
    
    async def scale_workers(self, num_workers: int) -> List[WorkerContainer]:
        """
        Escala para número especificado de workers.
        
        Cria novos containers se necessário, para ou remove containers extras.
        """
        current_count = len(self.workers)
        
        if num_workers == current_count:
            self.logger.info(f"✅ Already running {num_workers} workers")
            return list(self.workers.values())
        
        if num_workers > current_count:
            # Criar novos workers
            diff = num_workers - current_count
            self.logger.info(f"📈 Scaling up: creating {diff} new workers")
            
            for i in range(diff):
                worker = await self._create_worker(current_count + i)
                self.workers[worker.container_id] = worker
        
        else:
            # Remover workers extras
            diff = current_count - num_workers
            self.logger.info(f"📉 Scaling down: removing {diff} workers")
            
            workers_list = list(self.workers.items())
            for i in range(diff):
                container_id, worker = workers_list[-(i+1)]
                await self._remove_worker(container_id)
        
        return list(self.workers.values())
    
    async def _create_worker(self, worker_id: int) -> WorkerContainer:
        """Cria um novo container worker"""
        try:
            container_name = f"senior-docs-worker-{worker_id:03d}"
            
            self.logger.info(f"🚀 Creating worker {worker_id}: {container_name}")
            
            container = self.client.containers.run(
                self.image_name,
                name=container_name,
                environment={
                    "PYTHONUNBUFFERED": "1",
                    "SCRAPER_MODE": "worker",
                    "WORKER_ID": str(worker_id),
                    "WORKER_QUEUE_HOST": "scraper-orchestrator",
                    "WORKER_QUEUE_PORT": "8001",
                    "LOG_LEVEL": "info",
                },
                network=self.network_name,
                detach=True,
                restart_policy={"Name": "on-failure", "MaximumRetryCount": 3},
                healthcheck={
                    "Test": ["CMD", "curl", "-f", "http://localhost:8001/health"],
                    "Interval": 10000000000,  # 10s em nanosegundos
                    "Timeout": 5000000000,    # 5s em nanosegundos
                    "Retries": 3,
                    "StartPeriod": 5000000000,
                },
            )
            
            worker = WorkerContainer(
                container_id=container.id[:12],
                container_name=container_name,
                status="running"
            )
            
            self.logger.info(f"✅ Worker {worker_id} created: {container.id[:12]}")
            return worker
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create worker {worker_id}: {e}")
            raise
    
    async def _remove_worker(self, container_id: str) -> None:
        """Remove um container worker"""
        try:
            worker = self.workers.get(container_id)
            if not worker:
                return
            
            self.logger.info(f"🛑 Stopping worker: {worker.container_name}")
            
            container = self.client.containers.get(container_id)
            container.stop(timeout=10)
            container.remove()
            
            del self.workers[container_id]
            self.logger.info(f"✅ Worker {worker.container_name} removed")
            
        except Exception as e:
            self.logger.error(f"⚠️ Error removing worker {container_id}: {e}")
    
    async def distribute_urls(self, urls: List[str], batch_size: int = 10) -> None:
        """
        Distribui URLs entre workers.
        
        Args:
            urls: Lista de URLs para processar
            batch_size: URLs por batch distribuído
        """
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i+batch_size]
            
            # Distribuir para próximo worker disponível
            for url in batch:
                await self.queue.put(url)
        
        self.logger.info(f"📤 Distributed {len(urls)} URLs to workers")
    
    async def monitor_workers(self, interval: int = 10) -> None:
        """
        Monitora saúde dos workers continuamente.
        
        Args:
            interval: Intervalo de check em segundos
        """
        while True:
            try:
                for container_id, worker in self.workers.items():
                    try:
                        container = self.client.containers.get(container_id)
                        
                        # Atualizar status
                        worker.status = container.status
                        
                        # Verificar saúde
                        if container.status != "running":
                            self.logger.warning(
                                f"⚠️ Worker {worker.container_name} is {container.status}"
                            )
                        
                    except docker.errors.NotFound:
                        worker.status = "not_found"
                        self.logger.error(
                            f"❌ Worker {worker.container_name} not found (container removed?)"
                        )
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"❌ Error monitoring workers: {e}")
                await asyncio.sleep(interval)
    
    async def get_worker_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos workers"""
        total_urls = sum(w.urls_processed for w in self.workers.values())
        total_success = sum(w.success_count for w in self.workers.values())
        total_errors = sum(w.error_count for w in self.workers.values())
        
        return {
            "total_workers": len(self.workers),
            "total_urls_processed": total_urls,
            "total_success": total_success,
            "total_errors": total_errors,
            "success_rate": total_success / total_urls * 100 if total_urls > 0 else 0,
            "workers": {
                name: asdict(worker)
                for name, worker in self.workers.items()
            }
        }
    
    async def cleanup(self) -> None:
        """Limpa todos os workers"""
        self.logger.info("🧹 Cleaning up workers...")
        
        container_ids = list(self.workers.keys())
        for container_id in container_ids:
            await self._remove_worker(container_id)
        
        self.logger.info("✅ All workers cleaned up")


async def example_orchestrator():
    """Exemplo de uso do orchestrador"""
    
    logging.basicConfig(level=logging.INFO)
    
    orchestrator = DockerWorkerOrchestrator()
    
    try:
        # Escalar para 3 workers
        workers = await orchestrator.scale_workers(3)
        print(f"✅ Scaled to {len(workers)} workers")
        
        # Distribuir URLs
        urls = [f"https://example.com/page{i}" for i in range(1, 21)]
        await orchestrator.distribute_urls(urls, batch_size=10)
        
        # Monitorar por 30s
        monitor_task = asyncio.create_task(orchestrator.monitor_workers(interval=5))
        await asyncio.sleep(30)
        monitor_task.cancel()
        
        # Estatísticas
        stats = await orchestrator.get_worker_stats()
        print(json.dumps(stats, indent=2, default=str))
        
    finally:
        await orchestrator.cleanup()


if __name__ == "__main__":
    # asyncio.run(example_orchestrator())
    print("✅ Docker orchestrator loaded")
