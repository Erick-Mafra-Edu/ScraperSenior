#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite para MCP Server
Valida: Endpoints, Dados, Conexão com Meilisearch
"""

import requests
import json
import sys
from pathlib import Path
from time import sleep


class MCPTests:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
    
    def test_health(self):
        """Testa se servidor está saudável"""
        print("\n" + "="*80)
        print("🧪 TEST: MCP Server Health")
        print("="*80)
        
        try:
            r = requests.get(f"{self.base_url}/health", timeout=5)
            
            if r.status_code != 200:
                print(f"❌ FAIL: Status {r.status_code}")
                return False
            
            data = r.json()
            if data.get('status') != 'healthy':
                print(f"❌ FAIL: Status não é 'healthy': {data}")
                return False
            
            print(f"✅ PASS: Server is healthy")
            return True
            
        except requests.exceptions.ConnectionError:
            print(f"❌ FAIL: Não conseguiu conectar em {self.base_url}")
            return False
        except Exception as e:
            print(f"❌ FAIL: {e}")
            return False
    
    def test_stats(self):
        """Testa endpoint de estatísticas"""
        print("\n" + "="*80)
        print("🧪 TEST: MCP Stats Endpoint")
        print("="*80)
        
        try:
            r = requests.get(f"{self.base_url}/stats", timeout=5)
            
            if r.status_code != 200:
                print(f"❌ FAIL: Status {r.status_code}")
                return False
            
            data = r.json()
            
            # Verify fields
            required_fields = ['total_documents', 'modules', 'meilisearch_status']
            missing = [f for f in required_fields if f not in data]
            
            if missing:
                print(f"❌ FAIL: Campos ausentes: {missing}")
                return False
            
            print(f"✓ Total de documentos: {data.get('total_documents')}")
            print(f"✓ Módulos: {len(data.get('modules', []))}")
            print(f"✓ Status Meilisearch: {data.get('meilisearch_status')}")
            
            if data.get('total_documents', 0) > 0:
                print(f"✅ PASS: {data['total_documents']} documentos encontrados")
                return True
            else:
                print(f"⚠️ WARNING: Nenhum documento carregado")
                return False
                
        except Exception as e:
            print(f"❌ FAIL: {e}")
            return False
    
    def test_tools(self):
        """Testa endpoint de ferramentas"""
        print("\n" + "="*80)
        print("🧪 TEST: MCP Tools Endpoint")
        print("="*80)
        
        try:
            r = requests.get(f"{self.base_url}/tools", timeout=5)
            
            if r.status_code != 200:
                print(f"❌ FAIL: Status {r.status_code}")
                return False
            
            tools = r.json()
            
            if not isinstance(tools, list) or len(tools) == 0:
                print(f"❌ FAIL: Tools deve ser lista não vazia")
                return False
            
            print(f"✓ Ferramentas disponíveis: {len(tools)}")
            for tool in tools:
                print(f"  • {tool.get('name', 'N/A')}")
            
            print(f"✅ PASS: {len(tools)} ferramentas disponíveis")
            return True
            
        except Exception as e:
            print(f"❌ FAIL: {e}")
            return False
    
    def test_search_endpoint(self):
        """Testa endpoint de busca POST"""
        print("\n" + "="*80)
        print("🧪 TEST: MCP Search Endpoint (POST)")
        print("="*80)
        
        try:
            payload = {"query": "Gestão"}
            r = requests.post(f"{self.base_url}/search", json=payload, timeout=5)
            
            if r.status_code != 200:
                print(f"❌ FAIL: Status {r.status_code} - {r.text}")
                return False
            
            data = r.json()
            
            if not isinstance(data, (dict, list)):
                print(f"❌ FAIL: Resposta deve ser dict ou list")
                return False
            
            # Se for dict, pode ter 'results'
            if isinstance(data, dict):
                results = data.get('results', [])
            else:
                results = data
            
            if isinstance(results, list) and len(results) > 0:
                print(f"✓ Resultados encontrados: {len(results)}")
                for res in results[:3]:
                    print(f"  • {res.get('title', 'N/A')[:60]}...")
                print(f"✅ PASS: Busca retornou resultados")
                return True
            else:
                print(f"⚠️ WARNING: Nenhum resultado para 'Gestão'")
                return False
                
        except Exception as e:
            print(f"❌ FAIL: {e}")
            return False
    
    def test_call_tool(self):
        """Testa chamada de ferramenta via POST /call"""
        print("\n" + "="*80)
        print("🧪 TEST: MCP Call Tool Endpoint")
        print("="*80)
        
        try:
            payload = {
                "tool": "search_senior_docs",
                "arguments": {"query": "Gestão"}
            }
            r = requests.post(f"{self.base_url}/call", json=payload, timeout=5)
            
            if r.status_code != 200:
                print(f"❌ FAIL: Status {r.status_code}")
                return False
            
            data = r.json()
            
            if not isinstance(data, dict):
                print(f"❌ FAIL: Resposta deve ser dict")
                return False
            
            print(f"✓ Resposta recebida")
            if 'results' in data and len(data['results']) > 0:
                print(f"✓ Resultados: {len(data['results'])}")
                print(f"✅ PASS: Ferramenta executada com sucesso")
                return True
            else:
                print(f"⚠️ WARNING: Nenhum resultado")
                return False
                
        except Exception as e:
            print(f"❌ FAIL: {e}")
            return False
    
    def test_meilisearch_connection(self):
        """Testa conexão com Meilisearch"""
        print("\n" + "="*80)
        print("🧪 TEST: Meilisearch Connection")
        print("="*80)
        
        try:
            # Tenta via MCP stats
            r = requests.get(f"{self.base_url}/stats", timeout=5)
            
            if r.status_code != 200:
                print(f"❌ FAIL: Não conseguiu acessar stats")
                return False
            
            data = r.json()
            meilisearch_status = data.get('meilisearch_status')
            
            print(f"✓ Status Meilisearch: {meilisearch_status}")
            
            if meilisearch_status in ['connected', 'healthy', 'online']:
                print(f"✅ PASS: Meilisearch conectado")
                return True
            else:
                print(f"⚠️ WARNING: Meilisearch status: {meilisearch_status}")
                return False
                
        except Exception as e:
            print(f"❌ FAIL: {e}")
            return False
    
    def run_all(self):
        """Executa todos os testes"""
        print("\n" + "="*80)
        print("🚀 INICIANDO SUITE DE TESTES - MCP SERVER")
        print("="*80)
        
        # Aguardar servidor ficar pronto
        print("\n⏳ Aguardando MCP Server ficar pronto...")
        for i in range(10):
            try:
                r = requests.get(f"{self.base_url}/health", timeout=2)
                if r.status_code == 200:
                    print("✅ MCP Server pronto!\n")
                    break
            except:
                pass
            
            if i < 9:
                sleep(1)
        
        tests = [
            ("MCP Health", self.test_health),
            ("MCP Stats", self.test_stats),
            ("MCP Tools", self.test_tools),
            ("Meilisearch Connection", self.test_meilisearch_connection),
            ("Search Endpoint", self.test_search_endpoint),
            ("Call Tool Endpoint", self.test_call_tool),
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"\n❌ ERRO ao executar {test_name}: {e}")
                results[test_name] = False
        
        # Summary
        print("\n" + "="*80)
        print("📊 RESUMO DOS TESTES MCP")
        print("="*80)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print("\n" + "-"*80)
        print(f"Total: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
        print("="*80 + "\n")
        
        return passed == total


if __name__ == "__main__":
    tester = MCPTests()
    success = tester.run_all()
    sys.exit(0 if success else 1)
