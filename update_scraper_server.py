#!/usr/bin/env python3
"""
Atualiza o arquivo scrape_and_index_all.py no servidor via SSH
Muda o cliente Meilisearch para HTTP direto
"""

import requests
import json
import subprocess
import time
import os

def update_file_via_ssh():
    """Atualiza o arquivo scrape_and_index_all.py no servidor"""
    
    # Conectar ao servidor e atualizar o arquivo
    # Este script deve ser executado no servidor via: python update_scraper.py
    
    file_path = "/home/administrator/scraping/ScraperSenior/scrape_and_index_all.py"
    
    print("[*] Verificando se o arquivo existe...")
    
    # 1. Substituir import
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 2. Substituir import meilisearch por requests
    old_import = """# Tenta importar meilisearch
try:
    import meilisearch
except ImportError:
    print("[!] meilisearch nao instalado. Instalando...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "meilisearch"])
    import meilisearch"""
    
    new_import = """# Importar requests para cliente HTTP direto
try:
    import requests
except ImportError:
    print("[!] requests nao instalado. Instalando...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests"""
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        print("[✓] Import atualizado")
    
    # 3. Atualizar chave
    old_key = "'e3afed0047b08059d0fada10f400c1e5'"
    new_key = "'2cdc242bdaba66aede1da77794106635cfd7d57524dbc61b4bd6a7c2af39097f'"
    
    if old_key in content:
        content = content.replace(old_key, new_key)
        print("[✓] Chave de API atualizada")
    
    # 4. Salvar arquivo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[✓] Arquivo atualizado com sucesso")
    print("\n[*] Próximos passos:")
    print("    1. Reconstruir imagem Docker:")
    print("       docker-compose down -v")
    print("       docker build -t senior-docs-scraper:latest -f infra/docker/Dockerfile .")
    print("       docker-compose up -d")
    print("    2. Verificar logs:")
    print("       docker logs -f senior-docs-scraper")

if __name__ == "__main__":
    update_file_via_ssh()
