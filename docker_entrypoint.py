#!/usr/bin/env python3
"""
Entrypoint Docker para pipeline unificado
Orquestra:
1. Espera Meilisearch ficar disponivel
2. Executa scraper + indexador
3. Mantem container rodando
"""

import sys
import time
import asyncio
import subprocess
from pathlib import Path


def wait_for_meilisearch(max_retries=60, timeout=5):
    """Aguarda Meilisearch ficar disponivel"""
    import requests
    
    url = "http://meilisearch:7700/health"
    print(f"[*] Aguardando Meilisearch ({url})...")
    
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, timeout=timeout)
            if resp.status_code == 200:
                print(f"[OK] Meilisearch disponivel")
                return True
        except:
            pass
        
        wait_time = min(2 ** attempt, 30)
        print(f"[*] Tentativa {attempt+1}/{max_retries}... (aguardando {wait_time}s)")
        time.sleep(wait_time)
    
    print(f"[ERROR] Timeout: Meilisearch nao respondeu")
    return False


async def run_scraper_and_indexer():
    """Executa o scraper + indexador"""
    print(f"\n{'='*80}")
    print("INICIANDO SCRAPER + INDEXADOR UNIFICADO")
    print(f"{'='*80}\n")
    
    # Importa e executa
    from scrape_and_index_all import UnifiedIndexer
    
    indexer = UnifiedIndexer(
        meilisearch_url="http://meilisearch:7700",
        meilisearch_key=os.getenv("MEILISEARCH_KEY", "5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa")
    )
    
    success = await indexer.run()
    return success


def main():
    """Funcao principal"""
    print(f"{'='*80}")
    print("DOCKER ENTRYPOINT - PIPELINE UNIFICADO")
    print(f"{'='*80}\n")
    
    # 1. Aguarda Meilisearch
    if not wait_for_meilisearch():
        print(f"[ERROR] Nao conseguiu conectar ao Meilisearch")
        sys.exit(1)
    
    # 2. Executa scraper + indexador
    try:
        success = asyncio.run(run_scraper_and_indexer())
        
        if success:
            print(f"\n[OK] Pipeline concluido com sucesso")
            
            # 3. Executa post-scraping indexation
            print(f"\n{'='*80}")
            print("INICIANDO POS-SCRAPING INDEXAÇÃO")
            print(f"{'='*80}\n")
            
            try:
                result = subprocess.run(
                    [sys.executable, "post_scraping_indexation.py"],
                    cwd="/app",
                    capture_output=False
                )
                
                if result.returncode == 0:
                    print(f"\n[OK] Post-scraping indexation concluida")
                else:
                    print(f"\n[WARNING] Post-scraping indexation teve problemas")
            except Exception as idx_err:
                print(f"\n[WARNING] Erro ao executar post-scraping indexation: {idx_err}")
            
            print(f"[*] Container continuara rodando...")
            
            # Mantem container rodando
            try:
                while True:
                    time.sleep(3600)  # Dorme 1 hora
            except KeyboardInterrupt:
                print(f"\n[*] Container finalizado")
                sys.exit(0)
        else:
            print(f"[ERROR] Pipeline falhou")
            sys.exit(1)
    
    except Exception as e:
        print(f"[ERROR] Erro durante pipeline: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
