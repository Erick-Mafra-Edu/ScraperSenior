#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite para Meilisearch
Valida: Indexação, Documentos, Busca
"""

import requests
import json
import sys
from time import sleep


class MeilisearchTests:
    def __init__(self, base_url="http://localhost:7700", api_key="meilisearch_master_key_change_me"):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def test_connection(self):
        """Testa conexão com Meilisearch"""
        print("\n" + "="*80)
        print("🧪 TEST: Meilisearch Connection")
        print("="*80)
        
        try:
            r = requests.get(f"{self.base_url}/health", timeout=5)
            
            if r.status_code != 200:
                print(f"❌ FAIL: Status {r.status_code}")
                return False
            
            print(f"✅ PASS: Meilisearch conectado")
            return True
            
        except Exception as e:
            print(f"❌ FAIL: Não conseguiu conectar: {e}")
            return False
    
    def test_index_exists(self):
        """Testa se índice existe"""
        print("\n" + "="*80)
        print("🧪 TEST: Index Existence")
        print("="*80)
        
        try:
            r = requests.get(f"{self.base_url}/indexes", headers=self.headers, timeout=5)
            
            if r.status_code != 200:
                print(f"❌ FAIL: Status {r.status_code}")
                return False
            
            indexes = r.json()
            index_names = [idx.get('uid') for idx in indexes.get('results', [])]
            
            print(f"✓ Índices encontrados: {index_names}")
            
            if 'senior_docs' in index_names:
                print(f"✅ PASS: Índice 'senior_docs' existe")
                return True
            else:
                print(f"❌ FAIL: Índice 'senior_docs' não encontrado")
                return False
                
        except Exception as e:
            print(f"❌ FAIL: {e}")
            return False
    
    def test_document_count(self):
        """Testa contagem de documentos"""
        print("\n" + "="*80)
        print("🧪 TEST: Document Count")
        print("="*80)
        
        try:
            r = requests.get(
                f"{self.base_url}/indexes/senior_docs/stats",
                headers=self.headers,
                timeout=5
            )
            
            if r.status_code != 200:
                print(f"❌ FAIL: Status {r.status_code}")
                return False
            
            data = r.json()
            doc_count = data.get('numberOfDocuments', 0)
            
            print(f"✓ Documentos indexados: {doc_count}")
            
            if doc_count > 0:
                print(f"✅ PASS: {doc_count} documentos encontrados")
                return True
            else:
                print(f"❌ FAIL: Nenhum documento indexado")
                return False
                
        except Exception as e:
            print(f"❌ FAIL: {e}")
            return False
    
    def test_search_functionality(self):
        """Testa funcionalidade de busca"""
        print("\n" + "="*80)
        print("🧪 TEST: Search Functionality")
        print("="*80)
        
        try:
            payload = {"q": "Gestão"}
            r = requests.post(
                f"{self.base_url}/indexes/senior_docs/search",
                headers=self.headers,
                json=payload,
                timeout=5
            )
            
            if r.status_code != 200:
                print(f"❌ FAIL: Status {r.status_code}")
                return False
            
            data = r.json()
            hits = data.get('hits', [])
            
            print(f"✓ Resultados encontrados: {len(hits)}")
            for hit in hits[:3]:
                print(f"  • {hit.get('title', 'N/A')[:60]}...")
            
            if len(hits) > 0:
                print(f"✅ PASS: Busca funcionando ({len(hits)} resultados)")
                return True
            else:
                print(f"⚠️ WARNING: Nenhum resultado para 'Gestão'")
                return False
                
        except Exception as e:
            print(f"❌ FAIL: {e}")
            return False
    
    def test_document_fields(self):
        """Testa campos dos documentos"""
        print("\n" + "="*80)
        print("🧪 TEST: Document Fields")
        print("="*80)
        
        required_fields = ['id', 'title', 'url', 'module']
        
        try:
            # Pegar um documento
            r = requests.post(
                f"{self.base_url}/indexes/senior_docs/search",
                headers=self.headers,
                json={"q": "*", "limit": 1},
                timeout=5
            )
            
            if r.status_code != 200:
                print(f"❌ FAIL: Status {r.status_code}")
                return False
            
            data = r.json()
            hits = data.get('hits', [])
            
            if len(hits) == 0:
                print(f"⚠️ WARNING: Nenhum documento para validar campos")
                return False
            
            doc = hits[0]
            missing = [f for f in required_fields if f not in doc]
            
            if missing:
                print(f"❌ FAIL: Campos ausentes: {missing}")
                return False
            
            print(f"✓ Documento exemplo:")
            for field in required_fields:
                value = str(doc[field])[:60]
                print(f"  • {field}: {value}")
            
            print(f"✅ PASS: Todos os campos requeridos presentes")
            return True
                
        except Exception as e:
            print(f"❌ FAIL: {e}")
            return False
    
    def test_search_by_module(self):
        """Testa busca por módulo"""
        print("\n" + "="*80)
        print("🧪 TEST: Search by Module")
        print("="*80)
        
        try:
            # Fazer busca com filtro por módulo
            payload = {
                "q": "",
                "filter": "module = 'GESTAO DE PESSOAS HCM'"
            }
            r = requests.post(
                f"{self.base_url}/indexes/senior_docs/search",
                headers=self.headers,
                json=payload,
                timeout=5
            )
            
            if r.status_code != 200:
                print(f"❌ FAIL: Status {r.status_code}")
                return False
            
            data = r.json()
            hits = data.get('hits', [])
            
            print(f"✓ Documentos do módulo 'GESTAO DE PESSOAS HCM': {len(hits)}")
            
            if len(hits) > 0:
                print(f"✅ PASS: Filtro por módulo funcionando")
                return True
            else:
                print(f"⚠️ WARNING: Nenhum documento encontrado com filtro")
                return False
                
        except Exception as e:
            print(f"❌ FAIL: {e}")
            return False
    
    def run_all(self):
        """Executa todos os testes"""
        print("\n" + "="*80)
        print("🚀 INICIANDO SUITE DE TESTES - MEILISEARCH")
        print("="*80)
        
        # Aguardar Meilisearch ficar pronto
        print("\n⏳ Aguardando Meilisearch ficar pronto...")
        for i in range(10):
            try:
                r = requests.get(f"{self.base_url}/health", timeout=2)
                if r.status_code == 200:
                    print("✅ Meilisearch pronto!\n")
                    break
            except:
                pass
            
            if i < 9:
                sleep(1)
        
        tests = [
            ("Meilisearch Connection", self.test_connection),
            ("Index Existence", self.test_index_exists),
            ("Document Count", self.test_document_count),
            ("Search Functionality", self.test_search_functionality),
            ("Document Fields", self.test_document_fields),
            ("Search by Module", self.test_search_by_module),
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
        print("📊 RESUMO DOS TESTES MEILISEARCH")
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
    tester = MeilisearchTests()
    success = tester.run_all()
    sys.exit(0 if success else 1)
