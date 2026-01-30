"""
Script de Teste de Deployment Docker

Testa a implantação Docker e valida se os documentos foram indexados.
Verifica:
1. Docker build completo
2. Containers rodando corretamente
3. Meilisearch acessível
4. Documentos indexados
5. API respondendo
"""

import asyncio
import json
import subprocess
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
import urllib3

# Desabilita warnings de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DockerDeploymentTest:
    """Testa deployment Docker e indexação"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "status": "pending"
            }
        }
        self.meilisearch_url = "http://localhost:7700"
        self.meilisearch_key = "meilisearch_master_key_change_me"
    
    def run_command(self, command: str, description: str = "") -> Dict[str, Any]:
        """Executa comando e retorna resultado"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Timeout",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def add_test_result(self, test_name: str, passed: bool, details: Dict[str, Any]):
        """Adiciona resultado de teste"""
        self.results["tests"].append({
            "name": test_name,
            "passed": passed,
            "timestamp": datetime.now().isoformat(),
            "details": details
        })
        
        if passed:
            self.results["summary"]["passed"] += 1
        else:
            self.results["summary"]["failed"] += 1
        
        self.results["summary"]["total"] += 1
    
    async def test_docker_build(self) -> bool:
        """Testa docker build"""
        print("\n[1/8] Testando Docker build...")
        
        result = self.run_command("docker-compose -f docker-compose.yml build --no-cache")
        
        if result["success"]:
            self.add_test_result(
                "Docker build",
                True,
                {"message": "Build completed successfully"}
            )
            print("  ✓ Docker build completado com sucesso")
            return True
        else:
            self.add_test_result(
                "Docker build",
                False,
                {"error": result["stderr"]}
            )
            print(f"  ✗ Erro no build: {result['stderr'][:100]}")
            return False
    
    async def test_docker_up(self) -> bool:
        """Testa docker-compose up"""
        print("[2/8] Iniciando containers Docker...")
        
        result = self.run_command("docker-compose -f docker-compose.yml up -d")
        
        if result["success"]:
            self.add_test_result(
                "Docker compose up",
                True,
                {"message": "Containers started"}
            )
            print("  ✓ Containers iniciados")
            time.sleep(5)  # Aguardar inicialização
            return True
        else:
            self.add_test_result(
                "Docker compose up",
                False,
                {"error": result["stderr"]}
            )
            print(f"  ✗ Erro ao iniciar: {result['stderr'][:100]}")
            return False
    
    async def test_meilisearch_health(self) -> bool:
        """Testa saúde do Meilisearch"""
        print("[3/8] Verificando Meilisearch health...")
        
        try:
            response = requests.get(f"{self.meilisearch_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.add_test_result(
                    "Meilisearch health",
                    True,
                    {"status": data.get("status", "ok")}
                )
                print(f"  ✓ Meilisearch healthy: {data.get('status', 'ok')}")
                return True
            else:
                self.add_test_result(
                    "Meilisearch health",
                    False,
                    {"status": response.status_code}
                )
                print(f"  ✗ Meilisearch retornou: {response.status_code}")
                return False
        
        except Exception as e:
            self.add_test_result(
                "Meilisearch health",
                False,
                {"error": str(e)}
            )
            print(f"  ✗ Erro: {str(e)}")
            return False
    
    async def test_indexes_list(self) -> bool:
        """Lista todos os índices"""
        print("[4/8] Listando índices Meilisearch...")
        
        try:
            headers = {"Authorization": f"Bearer {self.meilisearch_key}"}
            response = requests.get(f"{self.meilisearch_url}/indexes", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                indexes = data.get("results", [])
                
                self.add_test_result(
                    "List indexes",
                    True,
                    {
                        "count": len(indexes),
                        "indexes": [idx.get("uid") for idx in indexes]
                    }
                )
                
                index_names = [idx.get("uid") for idx in indexes]
                print(f"  ✓ Índices encontrados: {len(indexes)}")
                for idx_name in index_names:
                    print(f"    • {idx_name}")
                
                return len(indexes) > 0
            else:
                self.add_test_result(
                    "List indexes",
                    False,
                    {"status": response.status_code}
                )
                print(f"  ✗ Erro ao listar: {response.status_code}")
                return False
        
        except Exception as e:
            self.add_test_result(
                "List indexes",
                False,
                {"error": str(e)}
            )
            print(f"  ✗ Erro: {str(e)}")
            return False
    
    async def test_documentation_index(self) -> bool:
        """Testa índice de documentação"""
        print("[5/8] Verificando índice 'documentation'...")
        
        try:
            headers = {"Authorization": f"Bearer {self.meilisearch_key}"}
            response = requests.get(
                f"{self.meilisearch_url}/indexes/documentation",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                doc_count = data.get("numberOfDocuments", 0)
                
                self.add_test_result(
                    "Documentation index",
                    True,
                    {
                        "documents": doc_count,
                        "fields_distribution": data.get("fieldsDistribution", {})
                    }
                )
                
                print(f"  ✓ Índice 'documentation' encontrado")
                print(f"    • Documentos: {doc_count}")
                print(f"    • Campos: {list(data.get('fieldsDistribution', {}).keys())}")
                
                return doc_count > 0
            else:
                self.add_test_result(
                    "Documentation index",
                    False,
                    {"status": response.status_code}
                )
                print(f"  ✗ Índice não encontrado: {response.status_code}")
                return False
        
        except Exception as e:
            self.add_test_result(
                "Documentation index",
                False,
                {"error": str(e)}
            )
            print(f"  ✗ Erro: {str(e)}")
            return False
    
    async def test_search_query(self) -> bool:
        """Testa busca no índice"""
        print("[6/8] Testando busca...")
        
        try:
            headers = {"Authorization": f"Bearer {self.meilisearch_key}"}
            
            # Fazer busca genérica
            query = {
                "q": "documento",
                "limit": 10
            }
            
            response = requests.post(
                f"{self.meilisearch_url}/indexes/documentation/search",
                json=query,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("hits", [])
                
                self.add_test_result(
                    "Search query",
                    True,
                    {
                        "query": "documento",
                        "results_found": len(results),
                        "processing_time_ms": data.get("processingTimeMs", 0)
                    }
                )
                
                print(f"  ✓ Busca executada com sucesso")
                print(f"    • Query: 'documento'")
                print(f"    • Resultados: {len(results)}")
                print(f"    • Tempo: {data.get('processingTimeMs', 0)}ms")
                
                if len(results) > 0:
                    print(f"    • Primeiro resultado: {results[0].get('title', 'N/A')[:50]}")
                
                return True
            else:
                self.add_test_result(
                    "Search query",
                    False,
                    {"status": response.status_code}
                )
                print(f"  ✗ Erro na busca: {response.status_code}")
                return False
        
        except Exception as e:
            self.add_test_result(
                "Search query",
                False,
                {"error": str(e)}
            )
            print(f"  ✗ Erro: {str(e)}")
            return False
    
    async def test_containers_running(self) -> bool:
        """Verifica se containers estão rodando"""
        print("[7/8] Verificando containers...")
        
        result = self.run_command("docker-compose -f docker-compose.yml ps")
        
        if result["success"]:
            # Contar containers rodando
            lines = result["stdout"].split("\n")
            running_count = sum(1 for line in lines if "Up" in line)
            
            self.add_test_result(
                "Containers running",
                running_count >= 1,
                {
                    "output": result["stdout"],
                    "running": running_count
                }
            )
            
            print(f"  ✓ Containers rodando: {running_count}")
            print(result["stdout"])
            
            return running_count >= 1
        else:
            self.add_test_result(
                "Containers running",
                False,
                {"error": result["stderr"]}
            )
            print(f"  ✗ Erro: {result['stderr'][:100]}")
            return False
    
    async def test_logs(self) -> bool:
        """Coleta logs dos containers"""
        print("[8/8] Coletando logs...")
        
        result = self.run_command("docker-compose -f docker-compose.yml logs --tail 50")
        
        if result["success"]:
            # Verificar por erros nos logs
            stdout = result["stdout"]
            has_errors = "error" in stdout.lower() or "failed" in stdout.lower()
            
            self.add_test_result(
                "Container logs",
                not has_errors,
                {
                    "log_lines": len(stdout.split("\n")),
                    "has_errors": has_errors,
                    "logs_snippet": stdout[:500]
                }
            )
            
            print(f"  ✓ Logs coletados ({len(stdout.split(chr(10)))} linhas)")
            
            return True
        else:
            self.add_test_result(
                "Container logs",
                False,
                {"error": result["stderr"]}
            )
            print(f"  ✗ Erro: {result['stderr'][:100]}")
            return False
    
    async def cleanup(self):
        """Limpa containers"""
        print("\n[CLEANUP] Encerrando containers...")
        
        result = self.run_command("docker-compose -f docker-compose.yml down")
        
        if result["success"]:
            print("  ✓ Containers encerrados")
        else:
            print(f"  ✗ Erro ao encerrar: {result['stderr'][:100]}")
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes"""
        print("\n" + "="*70)
        print("TESTE DE DEPLOYMENT DOCKER")
        print("="*70)
        
        try:
            # Executar testes sequencialmente
            tests = [
                self.test_docker_build,
                self.test_docker_up,
                self.test_meilisearch_health,
                self.test_indexes_list,
                self.test_documentation_index,
                self.test_search_query,
                self.test_containers_running,
                self.test_logs,
            ]
            
            for test in tests:
                try:
                    await test()
                except Exception as e:
                    print(f"  ✗ Erro em {test.__name__}: {str(e)}")
        
        finally:
            await self.cleanup()
        
        # Atualizar summary
        self.results["summary"]["status"] = "completed"
        
        return self.results
    
    def save_report(self, filepath: str):
        """Salva relatório em JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\nRelatório salvo em: {filepath}")
    
    def print_summary(self):
        """Imprime resumo dos testes"""
        print("\n" + "="*70)
        print("RESUMO DOS TESTES")
        print("="*70)
        
        summary = self.results["summary"]
        
        print(f"\nTotal de testes: {summary['total']}")
        print(f"Sucessos: {summary['passed']}")
        print(f"Falhas: {summary['failed']}")
        print(f"Taxa de sucesso: {(summary['passed']/summary['total']*100):.1f}%" if summary['total'] > 0 else "N/A")
        
        print("\nDetalhes dos testes:")
        for test in self.results["tests"]:
            status = "[OK]" if test["passed"] else "[FALHA]"
            print(f"  {status} {test['name']}")
            
            if not test["passed"] and "error" in test["details"]:
                print(f"       Erro: {test['details']['error'][:100]}")


async def main():
    """Main"""
    tester = DockerDeploymentTest()
    
    results = await tester.run_all_tests()
    
    # Salvar relatório
    tester.save_report("docker_deployment_test.json")
    
    # Imprimir resumo
    tester.print_summary()
    
    print("\n" + "="*70)
    if results["summary"]["passed"] == results["summary"]["total"]:
        print("✅ TODOS OS TESTES PASSARAM!")
    else:
        print(f"⚠ {results['summary']['failed']} teste(s) falharam")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
