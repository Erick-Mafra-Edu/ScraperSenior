#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pre-commit Hook para Git
Executa validações antes de cada commit
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Executa comando e retorna sucesso/falha"""
    print(f"\n🔍 {description}...")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0


def main():
    print("\n" + "="*80)
    print("🔐 PRE-COMMIT VALIDATION")
    print("="*80)
    
    checks = [
        ("python -m py_compile src/*.py", "Validar sintaxe Python"),
        ("python tests/test_scraper.py", "Validar dados do scraper"),
    ]
    
    all_passed = True
    
    for cmd, desc in checks:
        if not run_command(cmd, desc):
            print(f"❌ {desc} FALHOU")
            all_passed = False
        else:
            print(f"✅ {desc} OK")
    
    print("\n" + "="*80)
    
    if all_passed:
        print("✅ Todos os checks passaram! Commit permitido.")
        print("="*80 + "\n")
        return 0
    else:
        print("❌ Alguns checks falharam. Commit bloqueado.")
        print("="*80 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
