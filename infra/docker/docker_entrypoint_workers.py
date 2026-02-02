#!/usr/bin/env python3
"""
Multi-Worker Docker Entrypoint

Suporta dois modos:
1. ORCHESTRATOR: Gerencia múltiplos workers via Docker API
2. WORKER: Processa URLs da fila do orchestrator
3. LEGACY (default): Scraper único (compatível com versão anterior)
"""

import sys
import os
import time
import asyncio
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def wait_for_meilisearch(max_retries=60, timeout=5):
    """Aguarda Meilisearch ficar disponível"""
    import requests
    
    url = os.getenv("MEILISEARCH_URL", "http://meilisearch:7700")
    logger.info(f"Aguardando Meilisearch ({url})...")
    
    for attempt in range(max_retries):
        try:
            resp = requests.get(f"{url}/health", timeout=timeout)
            if resp.status_code == 200:
                logger.info("✅ Meilisearch disponível")
                return True
        except Exception as e:
            pass
        
        wait_time = min(2 ** attempt, 30)
        logger.info(f"Tentativa {attempt+1}/{max_retries}... (aguardando {wait_time}s)")
        time.sleep(wait_time)
    
    logger.error("❌ Timeout: Meilisearch não respondeu")
    return False


async def run_orchestrator():
    """Executa modo ORCHESTRATOR - gerencia múltiplos workers"""
    logger.info("🎭 Iniciando ORCHESTRATOR mode")
    
    try:
        from libs.scrapers.adapters.docker_worker_orchestrator import DockerWorkerOrchestrator
        from apps.scraper.scraper_unificado import ScraperUnificado
        import json
        
        num_workers = int(os.getenv("NUM_WORKERS", "3"))
        
        logger.info(f"Iniciando orchestrator com {num_workers} workers")
        
        orchestrator = DockerWorkerOrchestrator()
        
        # Escalar workers
        workers = await orchestrator.scale_workers(num_workers)
        logger.info(f"✅ {len(workers)} workers escalados")
        
        # Executar scraper e distribuir URLs
        logger.info("Iniciando scraper para distribuir URLs...")
        
        scraper = ScraperUnificado(config_path="apps/scraper/config/scraper_config.json")
        
        # Aguardar workers processarem
        logger.info("⏳ Aguardando processamento dos workers...")
        await asyncio.sleep(300)  # 5 minutos
        
        # Coletar estatísticas
        stats = await orchestrator.get_worker_stats()
        logger.info(f"📊 Estatísticas: {json.dumps(stats, indent=2, default=str)}")
        
        # Cleanup
        await orchestrator.cleanup()
        
        logger.info("✅ ORCHESTRATOR completado com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro no ORCHESTRATOR: {e}", exc_info=True)
        sys.exit(1)


async def run_worker():
    """Executa modo WORKER - processa URLs da fila"""
    logger.info("👷 Iniciando WORKER mode")
    
    try:
        worker_id = int(os.getenv("WORKER_ID", "0"))
        queue_host = os.getenv("WORKER_QUEUE_HOST", "localhost")
        queue_port = int(os.getenv("WORKER_QUEUE_PORT", "8001"))
        
        logger.info(f"Worker {worker_id} conectando a {queue_host}:{queue_port}")
        
        # Aguardar orchestrator
        for attempt in range(30):
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    resp = await client.get(f"http://{queue_host}:{queue_port}/health", timeout=5)
                    if resp.status_code == 200:
                        logger.info("✅ Orchestrator disponível")
                        break
            except Exception:
                pass
            
            wait_time = min(2 ** attempt, 10)
            logger.info(f"Aguardando orchestrator... (tentativa {attempt+1}/30)")
            await asyncio.sleep(wait_time)
        
        # Processar URLs da fila
        logger.info(f"Worker {worker_id} aguardando URLs da fila...")
        
        # TODO: Implementar polling de URLs do orchestrator
        # Por enquanto, apenas aguarda (será implementado com API REST)
        await asyncio.sleep(float('inf'))
        
        logger.info("✅ WORKER completado")
        
    except Exception as e:
        logger.error(f"❌ Erro no WORKER: {e}", exc_info=True)
        sys.exit(1)


async def run_legacy_scraper():
    """Executa modo LEGACY - scraper único (compatível com v1.x)"""
    logger.info("📜 Iniciando modo LEGACY (scraper único)")
    
    try:
        from scrape_and_index_all import UnifiedIndexer
        
        logger.info("Executando UnifiedIndexer...")
        
        indexer = UnifiedIndexer(
            scraper_config="apps/scraper/config/scraper_config.json",
            output_dir="data/indexes",
            meilisearch_url=os.getenv("MEILISEARCH_URL", "http://localhost:7700"),
            meilisearch_key=os.getenv("MEILISEARCH_KEY", "changeme"),
        )
        
        result = await indexer.run()
        
        logger.info(f"✅ Scraper completado: {result}")
        
    except Exception as e:
        logger.error(f"❌ Erro no scraper: {e}", exc_info=True)
        sys.exit(1)


async def main():
    """Entrypoint principal"""
    
    # Aguardar Meilisearch
    if not wait_for_meilisearch():
        logger.error("Meilisearch não ficou disponível")
        sys.exit(1)
    
    # Determinar modo de execução
    mode = os.getenv("SCRAPER_MODE", "legacy").lower()
    
    logger.info(f"🚀 Modo de execução: {mode.upper()}")
    
    if mode == "orchestrator":
        await run_orchestrator()
    elif mode == "worker":
        await run_worker()
    else:
        await run_legacy_scraper()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⏹️  Interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}", exc_info=True)
        sys.exit(1)
