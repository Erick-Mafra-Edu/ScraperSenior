#!/usr/bin/env python3
"""
Script para sincronizar arquivos com o servidor e reconstruir a imagem Docker
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Executa um comando e mostra o resultado"""
    print(f"\n[*] {description}...")
    print(f"    Comando: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"    ❌ Erro: {result.stderr}")
            return False
        else:
            print(f"    ✅ Sucesso")
            if result.stdout:
                print(f"    Output: {result.stdout[:200]}")
            return True
    except Exception as e:
        print(f"    ❌ Exceção: {e}")
        return False

def main():
    """Sincroniza e reconstrói"""
    
    # Caminhos
    local_file = r"c:\Users\Digisys\scrapyTest\scrape_and_index_all.py"
    server_path = "/home/administrator/scraping/ScraperSenior"
    
    # 1. Sincronizar arquivo
    print("\n" + "="*70)
    print("SINCRONIZANDO ARQUIVOS")
    print("="*70)
    
    # Copiar via PowerShell/SCP
    cmd_sync = f'scp "{local_file}" administrator@192.168.1.100:{server_path}/'
    if run_command(cmd_sync, "Sincronizando scrape_and_index_all.py com servidor"):
        print("✅ Arquivo sincronizado com sucesso")
    else:
        print("⚠️  Tentativa de cópia via SCP falhou, pulando...")
    
    # 2. Reconstruir imagem Docker
    print("\n" + "="*70)
    print("RECONSTRUINDO IMAGEM DOCKER")
    print("="*70)
    
    cmd_build = "docker build -t senior-docs-scraper:latest -f infra/docker/Dockerfile ."
    if run_command(cmd_build, "Reconstruindo imagem Docker"):
        print("✅ Imagem Docker reconstruída com sucesso")
    else:
        print("❌ Erro ao reconstruir imagem")
        return False
    
    # 3. Parar contêineres
    print("\n" + "="*70)
    print("PARANDO CONTÊINERES")
    print("="*70)
    
    cmd_down = "docker-compose down"
    if run_command(cmd_down, "Parando contêineres"):
        print("✅ Contêineres parados com sucesso")
    else:
        print("⚠️  Erro ao parar contêineres")
    
    # 4. Iniciar contêineres
    print("\n" + "="*70)
    print("INICIANDO CONTÊINERES")
    print("="*70)
    
    cmd_up = "docker-compose up -d"
    if run_command(cmd_up, "Iniciando contêineres"):
        print("✅ Contêineres iniciados com sucesso")
    else:
        print("❌ Erro ao iniciar contêineres")
        return False
    
    print("\n" + "="*70)
    print("✅ SINCRONIZAÇÃO E REBUILD COMPLETOS")
    print("="*70)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
