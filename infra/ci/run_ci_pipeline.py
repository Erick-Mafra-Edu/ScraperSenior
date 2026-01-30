#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CI/CD Pipeline - Orquestrador de Testes
Executa todos os testes em sequência e gera relatório
"""

import subprocess
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Fix encoding para Windows
if sys.platform == 'win32':
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class CICDPipeline:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tests_dir = self.project_root / "tests"
        self.report_file = self.project_root / "test_report.json"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
    
    def run_test(self, test_name, test_script):
        """Executa um teste e retorna resultado"""
        print(f"\n{'='*80}")
        print(f"▶️  Executando: {test_name}")
        print(f"{'='*80}")
        
        script_path = self.tests_dir / test_script
        
        if not script_path.exists():
            print(f"❌ Arquivo não encontrado: {script_path}")
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Print output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            
            success = result.returncode == 0
            self.results["tests"][test_name] = {
                "passed": success,
                "returncode": result.returncode,
                "timestamp": datetime.now().isoformat()
            }
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"⏱️  TIMEOUT: Teste demorou mais de 60 segundos")
            self.results["tests"][test_name] = {
                "passed": False,
                "error": "timeout",
                "timestamp": datetime.now().isoformat()
            }
            return False
        except Exception as e:
            print(f"❌ ERRO ao executar: {e}")
            self.results["tests"][test_name] = {
                "passed": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            return False
    
    def validate_infrastructure(self):
        """Valida se infraestrutura está pronta"""
        print(f"\n{'='*80}")
        print("🔍 VALIDANDO INFRAESTRUTURA")
        print(f"{'='*80}")
        
        checks = {
            "Docker Compose": self.project_root / "docker-compose.yml",
            "JSONL Docs": self.project_root / "docs_indexacao_detailed.jsonl",
            "Scraper": self.project_root / "src" / "scraper_unificado.py",
            "MCP Server": self.project_root / "src" / "mcp_server.py",
        }
        
        all_ok = True
        for check_name, path in checks.items():
            if path.exists():
                print(f"✅ {check_name}: {path.name}")
            else:
                print(f"❌ {check_name}: NÃO ENCONTRADO ({path})")
                all_ok = False
        
        return all_ok
    
    def run_all(self):
        """Executa pipeline completo"""
        print("\n" + "="*80)
        print("[*] INICIANDO CI/CD PIPELINE - SENIOR DOCS")
        print("="*80)
        print(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Projeto: {self.project_root}")
        
        # 1. Validar infraestrutura
        infra_ok = self.validate_infrastructure()
        
        if not infra_ok:
            print("\n⚠️  Infraestrutura não completa, mas continuando com testes...")
        
        # 2. Executar testes em sequência
        test_suite = [
            ("Scraper Data Validation", "test_scraper.py"),
            ("Meilisearch Tests", "test_meilisearch.py"),
            ("MCP Server Tests", "test_mcp_server.py"),
        ]
        
        results = []
        for test_name, script in test_suite:
            success = self.run_test(test_name, script)
            results.append((test_name, success))
            time.sleep(1)  # Pequeno delay entre testes
        
        # 3. Gerar relatório
        self.generate_report(results)
        
        return all(success for _, success in results)
    
    def generate_report(self, results):
        """Gera relatório dos testes"""
        print(f"\n{'='*80}")
        print("[*] RELATORIO FINAL")
        print(f"{'='*80}")
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        # Summary stats
        self.results["summary"] = {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": f"{passed/total*100:.1f}%",
            "status": "SUCCESS ✅" if passed == total else "FAILED ❌"
        }
        
        # Print summary
        print(f"\nResultados dos Testes:")
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status}: {test_name}")
        
        print(f"\n{'-'*80}")
        print(f"Total: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
        print(f"Status: {self.results['summary']['status']}")
        
        # Save report
        try:
            with open(self.report_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n📁 Relatório salvo em: {self.report_file}")
        except Exception as e:
            print(f"\n⚠️  Erro ao salvar relatório: {e}")
        
        print("="*80 + "\n")
        
        return passed == total


def main():
    """Ponto de entrada principal"""
    pipeline = CICDPipeline()
    success = pipeline.run_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
