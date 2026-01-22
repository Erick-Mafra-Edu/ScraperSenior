#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Watch Mode - Monitora arquivos e roda testes ao detectar mudanças
"""

import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime


class FileWatcher:
    def __init__(self, watch_paths=None, test_script="run_ci_pipeline.py"):
        self.watch_paths = watch_paths or [
            "src/",
            "docs_indexacao_detailed.jsonl",
        ]
        self.test_script = test_script
        self.file_times = {}
        self.project_root = Path(__file__).parent.parent
    
    def get_file_mtime(self, path):
        """Obtém tempo de modificação do arquivo"""
        try:
            return path.stat().st_mtime
        except OSError:
            return None
    
    def get_watched_files(self):
        """Retorna lista de arquivos monitorados"""
        files = []
        
        for watch_path in self.watch_paths:
            full_path = self.project_root / watch_path
            
            if full_path.is_file():
                files.append(full_path)
            elif full_path.is_dir():
                # Recursivamente adicionar arquivos .py
                files.extend(full_path.rglob("*.py"))
            else:
                # Arquivo específico (pode ser jsonl, etc)
                if full_path.exists():
                    files.append(full_path)
        
        return files
    
    def check_changes(self):
        """Verifica se há mudanças nos arquivos"""
        files = self.get_watched_files()
        
        for file_path in files:
            mtime = self.get_file_mtime(file_path)
            
            if mtime is None:
                continue
            
            if str(file_path) not in self.file_times:
                # Novo arquivo
                self.file_times[str(file_path)] = mtime
            elif self.file_times[str(file_path)] != mtime:
                # Arquivo modificado
                return True, str(file_path)
            
            self.file_times[str(file_path)] = mtime
        
        return False, None
    
    def run_tests(self):
        """Executa testes"""
        print(f"\n{'='*80}")
        print(f"🧪 EXECUTANDO TESTES - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}\n")
        
        result = subprocess.run(
            [sys.executable, str(self.project_root / self.test_script)],
            cwd=str(self.project_root)
        )
        
        return result.returncode == 0
    
    def start(self, interval=2):
        """Inicia monitoramento"""
        print(f"\n{'='*80}")
        print("👀 WATCH MODE - Monitorando mudanças")
        print(f"{'='*80}")
        print(f"Arquivos monitorados:")
        for path in self.watch_paths:
            print(f"  • {path}")
        print(f"\nIntervalo de verificação: {interval}s")
        print("Pressione Ctrl+C para parar\n")
        
        # Initialize file times
        for file_path in self.get_watched_files():
            self.file_times[str(file_path)] = self.get_file_mtime(file_path)
        
        try:
            while True:
                changed, file_path = self.check_changes()
                
                if changed:
                    print(f"\n📝 Mudança detectada: {file_path}")
                    success = self.run_tests()
                    
                    if success:
                        print(f"\n✅ Testes passaram!")
                    else:
                        print(f"\n❌ Testes falharam!")
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print(f"\n\n{'='*80}")
            print("⏹️  Watch mode encerrado")
            print(f"{'='*80}\n")


def main():
    watch_paths = [
        "src/",
        "tests/",
        "docs_indexacao_detailed.jsonl",
    ]
    
    watcher = FileWatcher(watch_paths=watch_paths)
    watcher.start(interval=2)


if __name__ == "__main__":
    main()
