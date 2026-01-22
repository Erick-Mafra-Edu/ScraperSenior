#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE COMPLETO: Docker + Scraper + MCP Server
Verifica funcionamento do stack Docker Compose
"""

import requests
import json
import subprocess
import time
from pathlib import Path

class DockerTestSuite:
    """Suite de testes para Docker Compose"""
    
    def __init__(self):
        self.results = []
        self.base_url = "http://localhost:8000"
        self.meilisearch_url = "http://localhost:7700"
    
    def test_health_check(self):
        """Testa health check do MCP Server"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.results.append({
                    'test': 'Health Check',
                    'status': '✓ PASS',
                    'details': f"Status: {data.get('status')}, Service: {data.get('service')}"
                })
                return True
            else:
                self.results.append({
                    'test': 'Health Check',
                    'status': '✗ FAIL',
                    'details': f"HTTP {response.status_code}"
                })
                return False
        except Exception as e:
            self.results.append({
                'test': 'Health Check',
                'status': '✗ FAIL',
                'details': str(e)
            })
            return False
    
    def test_stats(self):
        """Testa endpoint de estatísticas"""
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=5)
            if response.status_code == 200:
                data = response.json()
                stats = data.get('stats', {})
                self.results.append({
                    'test': 'Statistics',
                    'status': '✓ PASS',
                    'details': f"Documents: {stats.get('total_documents')}, Modules: {stats.get('modules')}, Source: {stats.get('source')}"
                })
                return True
            else:
                self.results.append({
                    'test': 'Statistics',
                    'status': '✗ FAIL',
                    'details': f"HTTP {response.status_code}"
                })
                return False
        except Exception as e:
            self.results.append({
                'test': 'Statistics',
                'status': '✗ FAIL',
                'details': str(e)
            })
            return False
    
    def test_docker_containers(self):
        """Verifica se containers estão rodando"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=senior-docs", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            containers = result.stdout.strip().split('\n')
            mcp_running = any('mcp' in c for c in containers)
            meilisearch_running = any('meilisearch' in c for c in containers)
            
            if mcp_running and meilisearch_running:
                self.results.append({
                    'test': 'Docker Containers',
                    'status': '✓ PASS',
                    'details': f"Containers: {', '.join(filter(None, containers))}"
                })
                return True
            else:
                self.results.append({
                    'test': 'Docker Containers',
                    'status': '✗ FAIL',
                    'details': f"MCP: {mcp_running}, Meilisearch: {meilisearch_running}"
                })
                return False
        except Exception as e:
            self.results.append({
                'test': 'Docker Containers',
                'status': '✗ FAIL',
                'details': str(e)
            })
            return False
    
    def test_index_files(self):
        """Verifica se arquivos de índice existem"""
        try:
            index_file = Path("docs_indexacao_detailed.jsonl")
            if index_file.exists():
                size_mb = index_file.stat().st_size / (1024 * 1024)
                self.results.append({
                    'test': 'Index Files',
                    'status': '✓ PASS',
                    'details': f"Found docs_indexacao_detailed.jsonl ({size_mb:.1f} MB)"
                })
                return True
            else:
                self.results.append({
                    'test': 'Index Files',
                    'status': '✗ FAIL',
                    'details': "docs_indexacao_detailed.jsonl not found"
                })
                return False
        except Exception as e:
            self.results.append({
                'test': 'Index Files',
                'status': '✗ FAIL',
                'details': str(e)
            })
            return False
    
    def test_docker_image(self):
        """Verifica se imagem Docker foi construída"""
        try:
            result = subprocess.run(
                ["docker", "images", "senior-docs-mcp", "--format", "{{.Size}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.stdout.strip():
                size = result.stdout.strip()
                self.results.append({
                    'test': 'Docker Image',
                    'status': '✓ PASS',
                    'details': f"Image size: {size}"
                })
                return True
            else:
                self.results.append({
                    'test': 'Docker Image',
                    'status': '✗ FAIL',
                    'details': "senior-docs-mcp image not found"
                })
                return False
        except Exception as e:
            self.results.append({
                'test': 'Docker Image',
                'status': '✗ FAIL',
                'details': str(e)
            })
            return False
    
    def test_mcp_ready(self):
        """Testa readiness probe"""
        try:
            response = requests.get(f"{self.base_url}/ready", timeout=5)
            if response.status_code == 200:
                self.results.append({
                    'test': 'MCP Ready Probe',
                    'status': '✓ PASS',
                    'details': "Server is ready"
                })
                return True
            else:
                self.results.append({
                    'test': 'MCP Ready Probe',
                    'status': '✗ FAIL',
                    'details': f"HTTP {response.status_code}"
                })
                return False
        except Exception as e:
            self.results.append({
                'test': 'MCP Ready Probe',
                'status': '✗ FAIL',
                'details': str(e)
            })
            return False
    
    def run_all(self):
        """Executa todos os testes"""
        print("\n" + "="*80)
        print("[TESTE COMPLETO] Docker + Scraper + MCP Server")
        print("="*80 + "\n")
        
        tests = [
            ("Docker Image", self.test_docker_image),
            ("Docker Containers", self.test_docker_containers),
            ("Index Files", self.test_index_files),
            ("Health Check", self.test_health_check),
            ("Ready Probe", self.test_mcp_ready),
            ("Statistics", self.test_stats),
        ]
        
        for test_name, test_func in tests:
            print(f"[EXECUTANDO] {test_name}...")
            try:
                test_func()
            except Exception as e:
                print(f"  [ERRO] {e}")
            time.sleep(0.5)
        
        # Exibir resultados
        print("\n" + "="*80)
        print("[RESULTADOS]")
        print("="*80 + "\n")
        
        passed = 0
        failed = 0
        
        for result in self.results:
            status_symbol = "✓" if "PASS" in result['status'] else "✗"
            print(f"{status_symbol} {result['test']:<25} {result['status']:<12} {result['details']}")
            
            if "PASS" in result['status']:
                passed += 1
            else:
                failed += 1
        
        print("\n" + "-"*80)
        print(f"[SUMMARY] {passed} passed, {failed} failed out of {len(self.results)} tests")
        print("="*80 + "\n")
        
        return failed == 0


if __name__ == "__main__":
    suite = DockerTestSuite()
    success = suite.run_all()
    exit(0 if success else 1)
