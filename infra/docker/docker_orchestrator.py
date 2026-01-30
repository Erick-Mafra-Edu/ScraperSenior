#!/usr/bin/env python3
"""
Orchestrador Docker para Scraper + Meilisearch
==============================================

Gerencia:
1. Inicialização do Meilisearch
2. Execução dos scrapers (website + Zendesk)
3. Indexação unificada

Uso:
    python docker_orchestrator.py [--action setup|scrape|index|cleanup|all]
"""

import subprocess
import sys
import time
import json
from pathlib import Path
from typing import List


class DockerOrchestrator:
    """Orquestra serviços Docker e scrapers"""
    
    def __init__(self):
        self.docker_compose_file = Path("docker-compose.yml")
        self.meilisearch_url = "http://localhost:7700"
        self.api_key = "meilisearch_master_key"
        self.max_retries = 10
    
    def run_command(self, command: str, shell: bool = True) -> bool:
        """Executa comando e retorna sucesso"""
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0
        except Exception as e:
            print(f"   ❌ Erro ao executar comando: {e}")
            return False
    
    def docker_compose_up(self) -> bool:
        """Inicia serviços Docker"""
        print(f"\n🐳 Iniciando serviços Docker...")
        
        if not self.docker_compose_file.exists():
            print(f"   ⚠️  docker-compose.yml não encontrado")
            return False
        
        if self.run_command("docker-compose up -d"):
            print(f"   ✅ Serviços iniciados")
            return self.wait_meilisearch()
        else:
            print(f"   ❌ Erro ao iniciar serviços")
            return False
    
    def docker_compose_down(self) -> bool:
        """Para serviços Docker"""
        print(f"\n🛑 Parando serviços Docker...")
        
        if self.run_command("docker-compose down"):
            print(f"   ✅ Serviços parados")
            return True
        else:
            print(f"   ⚠️  Erro ao parar serviços")
            return False
    
    def wait_meilisearch(self) -> bool:
        """Aguarda Meilisearch ficar disponível"""
        print(f"\n⏳ Aguardando Meilisearch...")
        
        import requests
        
        for attempt in range(self.max_retries):
            try:
                resp = requests.get(f"{self.meilisearch_url}/health", timeout=5)
                if resp.status_code == 200:
                    print(f"   ✅ Meilisearch pronto")
                    return True
            except:
                pass
            
            wait_time = 2 ** attempt  # Backoff exponencial
            print(f"   ⏳ Tentativa {attempt+1}/{self.max_retries}... (aguardando {wait_time}s)")
            time.sleep(wait_time)
        
        print(f"   ❌ Timeout: Meilisearch não respondeu")
        return False
    
    def run_scraper_and_indexer(self) -> bool:
        """Executa scraper + indexador unificado"""
        print(f"\n🚀 Executando scraper + indexador unificado...")
        
        command = f"python scrape_and_index_all.py --url {self.meilisearch_url} --api-key {self.api_key}"
        
        if self.run_command(command):
            print(f"   ✅ Scraper e indexador concluídos")
            return True
        else:
            print(f"   ❌ Erro ao executar scraper/indexador")
            return False
    
    def verify_index(self) -> bool:
        """Verifica se documentos foram indexados"""
        print(f"\n🔍 Verificando índice...")
        
        try:
            import requests
            
            resp = requests.get(
                f"{self.meilisearch_url}/indexes/documentation/stats",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5
            )
            
            if resp.status_code == 200:
                stats = resp.json()
                doc_count = stats.get('numberOfDocuments', 0)
                print(f"   ✅ Documentos indexados: {doc_count}")
                return doc_count > 0
            else:
                print(f"   ⚠️  Índice não encontrado (normal na primeira execução)")
                return True
        
        except Exception as e:
            print(f"   ⚠️  Erro ao verificar: {e}")
            return True
    
    def run_all(self) -> bool:
        """Executa pipeline completo"""
        print(f"\n{'='*80}")
        print("🎯 PIPELINE COMPLETO - SCRAPER + MEILISEARCH")
        print(f"{'='*80}")
        
        # 1. Inicia Docker
        if not self.docker_compose_up():
            print(f"\n❌ Falha ao iniciar Docker")
            return False
        
        # 2. Executa scraper + indexador
        if not self.run_scraper_and_indexer():
            print(f"\n❌ Falha ao executar scraper/indexador")
            self.docker_compose_down()
            return False
        
        # 3. Verifica índice
        if not self.verify_index():
            print(f"\n⚠️  Índice pode estar vazio")
        
        print(f"\n{'='*80}")
        print("✅ PIPELINE CONCLUÍDO COM SUCESSO")
        print(f"{'='*80}")
        print(f"\n📊 Acessar Meilisearch em: http://localhost:7700")
        print(f"📄 Documentos em: docs_unified/")
        print(f"{'='*80}\n")
        
        return True


def main():
    """Função principal"""
    action = "all"
    
    if len(sys.argv) > 1:
        action = sys.argv[1].replace("--action", "").strip()
    
    orchestrator = DockerOrchestrator()
    
    try:
        if action == "setup":
            success = orchestrator.docker_compose_up()
        elif action == "scrape":
            success = orchestrator.run_scraper_and_indexer()
        elif action == "index":
            success = orchestrator.verify_index()
        elif action == "cleanup":
            success = orchestrator.docker_compose_down()
        elif action == "all":
            success = orchestrator.run_all()
        else:
            print(f"Ação desconhecida: {action}")
            print(f"Use: setup|scrape|index|cleanup|all")
            return False
        
        return success
    
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Operação cancelada pelo usuário")
        orchestrator.docker_compose_down()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
