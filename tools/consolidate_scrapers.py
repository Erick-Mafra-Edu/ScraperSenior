#!/usr/bin/env python3
"""
Script de Consolidação - Remove Scrapers Redundantes
Mantém apenas o scraper modular como source of truth
"""

import os
from pathlib import Path
import shutil
from datetime import datetime


def safe_delete(filepath, dry_run=True):
    """Deleta arquivo com segurança"""
    try:
        p = Path(filepath)
        if p.exists():
            size = p.stat().st_size
            action = "WOULD DELETE" if dry_run else "DELETING"
            print(f"  {action}: {filepath} ({size:,} bytes)")
            
            if not dry_run:
                if p.is_file():
                    p.unlink()
                elif p.is_dir():
                    shutil.rmtree(p)
            return True
    except Exception as e:
        print(f"  ❌ Erro ao deletar {filepath}: {e}")
    return False


def backup_file(filepath, backup_dir="backups/scrapers"):
    """Faz backup de arquivo antes de deletar"""
    try:
        p = Path(filepath)
        if p.exists():
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dest = backup_path / f"{p.stem}_{timestamp}{p.suffix}"
            
            if p.is_file():
                shutil.copy2(p, backup_dest)
            else:
                shutil.copytree(p, backup_dest)
            
            print(f"  ✅ Backup: {backup_dest}")
            return True
    except Exception as e:
        print(f"  ❌ Erro ao fazer backup: {e}")
    return False


def consolidate_scrapers(dry_run=True, backup=True):
    """Consolidação principal"""
    
    print("\n" + "="*80)
    print("CONSOLIDAÇÃO DE SCRAPERS - Remover Redundância")
    print("="*80)
    
    if dry_run:
        print("⚠️  Modo DRY-RUN (sem deletar arquivos)")
    print()
    
    # Arquivos redundantes
    redundant_files = [
        "src/scrapers/scraper_complete.py",        # 287 linhas
        "src/scrapers/scraper_senior_advanced.py", # 227 linhas
        "src/scrapers/scraper_js.py",              # 353 linhas
        "src/scrapers/scraper_senior_js.py",       # 210 linhas
        "src/scrapers/simple_scraper.py",          # 103 linhas
        "src/scrapers/pipeline_complete.py",       # 99 linhas
    ]
    
    # Arquivos a manter
    keep_files = [
        "src/scraper_unificado.py",        # Referência de detecção de tipo
        "src/scrapers/scrape_senior_docs.py",  # Utilitários de parsing
        "src/scraper_modular.py",          # Novo padrão
    ]
    
    print("📋 Arquivos REDUNDANTES a Remover:")
    print("─" * 80)
    
    total_bytes = 0
    for filepath in redundant_files:
        try:
            p = Path(filepath)
            if p.exists():
                size = p.stat().st_size
                total_bytes += size
                print(f"  ❌ {filepath:50} ({size:>8,} bytes)")
        except:
            pass
    
    print(f"\n  Total a remover: {total_bytes:,} bytes (~{total_bytes/1024:.1f} KB)")
    
    print("\n✅ Arquivos a MANTER:")
    print("─" * 80)
    for filepath in keep_files:
        p = Path(filepath)
        if p.exists():
            size = p.stat().st_size
            print(f"  ✅ {filepath:50} ({size:>8,} bytes)")
    
    print("\n" + "="*80)
    print("AÇÕES")
    print("="*80 + "\n")
    
    # Backup
    if backup:
        print("1️⃣  Fazendo backup dos arquivos...")
        for filepath in redundant_files:
            if Path(filepath).exists():
                backup_file(filepath)
    
    # Deletar
    print("\n2️⃣  Removendo arquivos redundantes...")
    deleted_count = 0
    for filepath in redundant_files:
        if safe_delete(filepath, dry_run=dry_run):
            deleted_count += 1
    
    # Relatório
    print("\n" + "="*80)
    print("RELATÓRIO")
    print("="*80)
    print(f"\nArquivos processados: {len(redundant_files)}")
    print(f"Arquivos deletados: {deleted_count}")
    print(f"Bytes recuperados: ~{total_bytes:,}")
    
    print("\n✅ CONSOLIDAÇÃO COMPLETA!")
    print("\nProximas ações:")
    print("  1. Reconstruir Docker: docker-compose build --no-cache")
    print("  2. Testar scraper: python exemplo_scraper_modular.py")
    print("  3. Executar testes: python test_scraper_modular.py")
    print("  4. Commit: git add -A && git commit -m 'Consolidar scrapers'")
    
    print("\n" + "="*80 + "\n")


def verify_consolidation():
    """Verifica estado após consolidação"""
    print("\n" + "="*80)
    print("VERIFICAÇÃO DE CONSOLIDAÇÃO")
    print("="*80 + "\n")
    
    scrapers_dir = Path("src/scrapers")
    if not scrapers_dir.exists():
        print("❌ Diretório src/scrapers não encontrado")
        return False
    
    files = list(scrapers_dir.glob("*.py"))
    
    print(f"Arquivos em src/scrapers/: {len(files)}")
    for f in sorted(files):
        size = f.stat().st_size
        print(f"  • {f.name:40} ({size:>8,} bytes)")
    
    # Verifica se modular existe
    modular = Path("src/scraper_modular.py")
    if modular.exists():
        print(f"\n✅ Scraper modular encontrado: {modular.stat().st_size:,} bytes")
    else:
        print(f"\n❌ Scraper modular NÃO encontrado!")
        return False
    
    print("\n" + "="*80 + "\n")
    return True


def main():
    """Função principal"""
    import sys
    
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  CONSOLIDAÇÃO DE SCRAPERS - Senior Documentation".center(78) + "║")
    print("║" + "  Remove scrapers redundantes, mantém apenas o modular".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # Parse argumentos
    dry_run = "--execute" not in sys.argv
    backup = "--no-backup" not in sys.argv
    
    if dry_run:
        print("\n⚠️  Execute com --execute para realmente deletar arquivos")
        print("   Exemplo: python tools/consolidate_scrapers.py --execute")
    
    print()
    
    # Executa
    consolidate_scrapers(dry_run=dry_run, backup=backup)
    
    # Verifica
    verify_consolidation()


if __name__ == "__main__":
    main()
