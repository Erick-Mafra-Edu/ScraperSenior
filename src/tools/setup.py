#!/usr/bin/env python3
"""
Setup rápido do projeto
"""

import subprocess
import sys
from pathlib import Path


def run(cmd, description):
    """Executa comando com feedback"""
    print(f"\n[→] {description}...")
    try:
        subprocess.run(cmd, shell=False, check=True, capture_output=True)
        print(f"   ✅ OK")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Erro: {e}")
        return False


def main():
    print("\n" + "="*60)
    print("[SETUP] Senior Documentation Scraper")
    print("="*60)
    
    # 1. Criar .env
    if not Path(".env").exists():
        print("\n[1] Criando arquivo .env...")
        with open(".env", "w") as f:
            f.write(open(".env.example").read())
        print("    ✅ .env criado (copiar de .env.example)")
    
    # 2. Instalar dependências
    print("\n[2] Instalando dependências...")
    run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"], 
        "pip install")
    
    # 3. Setup Playwright
    print("\n[3] Setup Playwright...")
    run([sys.executable, "-m", "playwright", "install", "chromium"], 
        "playwright install")
    
    # 4. Criar diretórios se não existem
    print("\n[4] Criando diretórios...")
    for dir_path in ["docs_estruturado", "tools"]:
        Path(dir_path).mkdir(exist_ok=True)
    print("    ✅ Diretórios OK")
    
    print("\n" + "="*60)
    print("✅ Setup completo!")
    print("\nPróximo passo:")
    print("  python src/scraper_unificado.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
