#!/usr/bin/env python3
"""
Script de limpeza e manutenção do projeto
"""

import shutil
from pathlib import Path
import sys


def cleanup():
    """Remove dados gerados e cache"""
    
    print("\n" + "="*60)
    print("[LIMPEZA] Senior Docs Scraper")
    print("="*60 + "\n")
    
    # Diretórios a remover
    dirs_to_remove = [
        "docs_estruturado",
        "__pycache__",
        ".pytest_cache",
        ".playwright",
    ]
    
    # Arquivos a remover
    files_to_remove = [
        "docs_indexacao.jsonl",
        "docs_metadata.json",
        "*.db",
    ]
    
    removed = 0
    
    # Remover diretórios
    for dir_path in dirs_to_remove:
        p = Path(dir_path)
        if p.exists():
            try:
                shutil.rmtree(p)
                print(f"✅ Removido: {dir_path}/")
                removed += 1
            except Exception as e:
                print(f"❌ Erro ao remover {dir_path}: {e}")
    
    # Remover arquivos
    for pattern in files_to_remove:
        for file_path in Path(".").glob(pattern):
            try:
                file_path.unlink()
                print(f"✅ Removido: {file_path}")
                removed += 1
            except Exception as e:
                print(f"❌ Erro ao remover {file_path}: {e}")
    
    print(f"\n✅ {removed} item(ns) removido(s)")
    print("="*60 + "\n")


def install_deps():
    """Instala dependências"""
    
    print("\n[INSTALAÇÃO] Dependências")
    import subprocess
    
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"])
    print("✅ Dependências instaladas\n")


def setup_playwright():
    """Setup Playwright"""
    
    print("\n[SETUP] Playwright")
    import subprocess
    
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
    print("✅ Playwright configurado\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "clean":
            cleanup()
        elif cmd == "install":
            install_deps()
        elif cmd == "playwright":
            setup_playwright()
        else:
            print(f"Comando desconhecido: {cmd}")
            print("\nUso: python tools/maintenance.py [clean|install|playwright]")
    else:
        print("\nUso: python tools/maintenance.py [comando]")
        print("\nComandos:")
        print("  clean      - Remove dados gerados e cache")
        print("  install    - Instala dependências")
        print("  playwright - Setup Playwright")
