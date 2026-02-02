#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solução para Erro Docker Build: Snapshot não encontrado
========================================================

Erro: "parent snapshot does not exist: not found"
Causa: Cache de build corrompido ou inconsistente
Solução: Limpar cache e rebuildar
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description=""):
    """Executa comando e retorna resultado"""
    print(f"\n{'='*80}")
    if description:
        print(f"▶ {description}")
    print(f"{'='*80}")
    print(f"$ {cmd}\n")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False

def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║             Solução: Erro Docker Build - Snapshot Corrompido              ║
╚════════════════════════════════════════════════════════════════════════════╝

Problema Identificado:
  - Erro: "parent snapshot does not exist: not found"
  - Causa: Cache de build Docker corrompido
  - Solução: Limpar cache e rebuildar

Passos que serão executados:
  1. Parar containers em execução
  2. Remover imagens antigas
  3. Limpar cache de build
  4. Rebuildar imagens do zero
  5. Validar resultado
    """)
    
    input("Pressione ENTER para continuar...")
    
    # Passo 1: Parar e remover containers
    print("\n" + "="*80)
    print("PASSO 1: Parando containers...")
    print("="*80)
    
    commands = [
        ("docker-compose -f infra/docker/docker-compose.yml down", 
         "Parando containers do docker-compose"),
        
        ("docker stop $(docker ps -q) 2>/dev/null || true",
         "Parando todos os containers"),
    ]
    
    for cmd, desc in commands:
        run_command(cmd, desc)
    
    # Passo 2: Remover imagens
    print("\n" + "="*80)
    print("PASSO 2: Removendo imagens antigas...")
    print("="*80)
    
    remove_commands = [
        ("docker rmi senior-docs-mcp:latest 2>/dev/null || true",
         "Removendo imagem MCP"),
        ("docker rmi senior-docs-scraper:latest 2>/dev/null || true",
         "Removendo imagem Scraper"),
        ("docker image prune -f",
         "Limpando imagens não utilizadas"),
    ]
    
    for cmd, desc in remove_commands:
        run_command(cmd, desc)
    
    # Passo 3: Limpar cache de build
    print("\n" + "="*80)
    print("PASSO 3: Limpando cache de build...")
    print("="*80)
    
    cache_commands = [
        ("docker buildx du",
         "Verificando uso de cache buildx"),
        ("docker buildx prune -af",
         "Removendo cache corrompido"),
    ]
    
    for cmd, desc in cache_commands:
        run_command(cmd, desc)
    
    # Passo 4: Rebuildar imagens
    print("\n" + "="*80)
    print("PASSO 4: Reconstruindo imagens do Docker...")
    print("="*80)
    
    build_cmd = "cd infra/docker && docker-compose build --no-cache"
    if not run_command(build_cmd, "Build do Docker Compose (sem cache)"):
        print("\n✗ Erro ao fazer build das imagens")
        return False
    
    # Passo 5: Validar resultado
    print("\n" + "="*80)
    print("PASSO 5: Validando resultado...")
    print("="*80)
    
    run_command("docker images | grep senior-docs",
                "Imagens Docker construídas")
    
    # Teste de inicialização
    print("\nIniciando containers para teste...")
    run_command("cd infra/docker && docker-compose up -d",
                "Iniciando docker-compose")
    
    print("\nVerificando saúde dos containers...")
    run_command("docker-compose -f infra/docker/docker-compose.yml ps",
                "Status dos containers")
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                            ✅ SOLUÇÃO COMPLETA                            ║
╚════════════════════════════════════════════════════════════════════════════╝

Próximos passos:
  1. Verificar logs: docker-compose -f infra/docker/docker-compose.yml logs
  2. Testar endpoints: curl http://localhost:8000/health
  3. Validar: python validate_mcp_docker_meilisearch.py

Se ainda tiver problemas:
  • Aumentar espaço em disco (buildx precisa de ~5GB)
  • Limpar volumes Docker: docker volume prune
  • Usar --no-cache em rebuild se cache continuar problemático
    """)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
