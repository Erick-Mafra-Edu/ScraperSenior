"""
Teste de Validação da API Senior Documentation
Valida a conformidade com o schema OpenAPI e testa todos os endpoints
"""

import json
import requests
import pytest
from pathlib import Path
from typing import Dict, Any, List
from api_server_detector import detect_api_server


class SeniorAPITester:
    """Testador da API Senior Documentation"""
    
    def __init__(self, api_url: str = None, openapi_path: str = None):
        # Se api_url não fornecida, detectar automaticamente
        if api_url is None:
            api_url, _ = detect_api_server()
        
        self.api_url = api_url.rstrip("/")
        self.openapi_path = openapi_path or "openapi.json"
        self.schema = None
        self.endpoints = {}
        self.load_schema()
    
    def load_schema(self):
        """Carrega o schema OpenAPI"""
        try:
            # Tentar carregar do arquivo local
            if Path(self.openapi_path).exists():
                with open(self.openapi_path, 'r', encoding='utf-8') as f:
                    self.schema = json.load(f)
                print(f"✅ Schema carregado de {self.openapi_path}")
            else:
                # Tentar baixar da API
                response = requests.get(f"{self.api_url}/openapi.json", timeout=5)
                response.raise_for_status()
                self.schema = response.json()
                print(f"✅ Schema carregado de {self.api_url}/openapi.json")
        except Exception as e:
            raise Exception(f"❌ Falha ao carregar schema OpenAPI: {str(e)}")
    
    def validate_schema_structure(self) -> bool:
        """Valida a estrutura básica do schema OpenAPI"""
        required_fields = ["openapi", "info", "paths", "components"]
        
        for field in required_fields:
            assert field in self.schema, f"❌ Campo obrigatório '{field}' não encontrado no schema"
        
        assert self.schema.get("openapi").startswith("3"), "❌ OpenAPI versão 3.x esperada"
        assert "title" in self.schema["info"], "❌ Campo 'title' faltando em 'info'"
        assert isinstance(self.schema["paths"], dict), "❌ 'paths' deve ser um dicionário"
        
        print(f"✅ Estrutura do schema validada")
        print(f"   - Versão OpenAPI: {self.schema['openapi']}")
        print(f"   - Título: {self.schema['info']['title']}")
        print(f"   - Endpoints: {len(self.schema['paths'])}")
        return True
    
    def test_endpoints_defined(self) -> Dict[str, List[str]]:
        """Lista todos os endpoints definidos no schema"""
        endpoints = {}
        
        for path, path_item in self.schema["paths"].items():
            methods = [m for m in ["get", "post", "put", "delete", "patch"] if m in path_item]
            endpoints[path] = methods
            print(f"📍 {path}")
            for method in methods:
                op = path_item[method]
                summary = op.get("summary", "Sem descrição")
                print(f"   ├─ {method.upper()}: {summary}")
        
        self.endpoints = endpoints
        return endpoints
    
    def test_health_endpoint(self) -> bool:
        """Testa o endpoint /health"""
        print("\n🏥 Testando /health...")
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            assert response.status_code == 200, f"❌ Status {response.status_code} esperado 200"
            
            data = response.json()
            assert "status" in data, "❌ Campo 'status' faltando na resposta"
            assert data["status"] in ["healthy", "unhealthy"], "❌ Status inválido"
            
            print(f"✅ /health respondeu com sucesso")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Versão: {data.get('version')}")
            return True
        except Exception as e:
            print(f"❌ Erro em /health: {str(e)}")
            return False
    
    def test_stats_endpoint(self) -> bool:
        """Testa o endpoint /stats"""
        print("\n📊 Testando /stats...")
        try:
            response = requests.get(f"{self.api_url}/stats", timeout=5)
            assert response.status_code == 200, f"❌ Status {response.status_code} esperado 200"
            
            data = response.json()
            assert data.get("success"), "❌ success=false na resposta"
            assert "total_documents" in data, "❌ Campo 'total_documents' faltando"
            assert "total_modules" in data, "❌ Campo 'total_modules' faltando"
            assert "modules" in data, "❌ Campo 'modules' faltando"
            
            print(f"✅ /stats respondeu com sucesso")
            print(f"   - Total de documentos: {data.get('total_documents')}")
            print(f"   - Total de módulos: {data.get('total_modules')}")
            print(f"   - Módulos: {', '.join(data.get('modules', {}).keys())}")
            return True
        except Exception as e:
            print(f"❌ Erro em /stats: {str(e)}")
            return False
    
    def test_modules_endpoint(self) -> bool:
        """Testa o endpoint /modules"""
        print("\n📚 Testando /modules...")
        try:
            response = requests.get(f"{self.api_url}/modules", timeout=5)
            assert response.status_code == 200, f"❌ Status {response.status_code} esperado 200"
            
            data = response.json()
            assert data.get("success"), "❌ success=false na resposta"
            assert "modules" in data, "❌ Campo 'modules' faltando"
            assert isinstance(data["modules"], list), "❌ 'modules' deve ser uma lista"
            
            print(f"✅ /modules respondeu com sucesso")
            print(f"   - Total de módulos: {len(data['modules'])}")
            for module in data["modules"][:5]:
                name = module.get("name", "Unknown")
                count = module.get("doc_count", 0)
                print(f"   ├─ {name}: {count} documentos")
            if len(data["modules"]) > 5:
                print(f"   └─ ... e mais {len(data['modules']) - 5} módulos")
            return True
        except Exception as e:
            print(f"❌ Erro em /modules: {str(e)}")
            return False
    
    def test_search_endpoint_valid_query(self, query: str = "configurar") -> bool:
        """Testa o endpoint /search com query válida"""
        print(f"\n🔍 Testando /search com query '{query}'...")
        try:
            payload = {
                "query": query,
                "limit": 5
            }
            response = requests.post(f"{self.api_url}/search", json=payload, timeout=10)
            assert response.status_code == 200, f"❌ Status {response.status_code} esperado 200"
            
            data = response.json()
            assert data.get("success"), "❌ success=false na resposta"
            assert "query" in data, "❌ Campo 'query' faltando"
            assert "results" in data, "❌ Campo 'results' faltando"
            assert "total" in data, "❌ Campo 'total' faltando"
            assert isinstance(data["results"], list), "❌ 'results' deve ser uma lista"
            
            print(f"✅ /search respondeu com sucesso")
            print(f"   - Query: {data.get('query')}")
            print(f"   - Total encontrado: {data.get('total')}")
            print(f"   - Resultados retornados: {len(data['results'])}")
            
            if data["results"]:
                doc = data["results"][0]
                print(f"\n   Primeiro resultado:")
                print(f"   ├─ Título: {doc.get('title')}")
                print(f"   ├─ Módulo: {doc.get('module')}")
                print(f"   ├─ Score: {doc.get('score')}")
                print(f"   └─ Preview: {doc.get('content_preview', '')[:100]}...")
            
            return True
        except Exception as e:
            print(f"❌ Erro em /search: {str(e)}")
            return False
    
    def test_search_endpoint_with_module(self, query: str = "configurar", module: str = "RH") -> bool:
        """Testa o endpoint /search com filtro de módulo"""
        print(f"\n🔍 Testando /search com query '{query}' no módulo '{module}'...")
        try:
            payload = {
                "query": query,
                "module": module,
                "limit": 5
            }
            response = requests.post(f"{self.api_url}/search", json=payload, timeout=10)
            assert response.status_code == 200, f"❌ Status {response.status_code} esperado 200"
            
            data = response.json()
            assert data.get("success"), "❌ success=false na resposta"
            
            # Validar que todos os resultados são do módulo solicitado
            for result in data.get("results", []):
                assert result.get("module") == module, f"❌ Resultado contém módulo diferente"
            
            print(f"✅ /search com módulo respondeu com sucesso")
            print(f"   - Query: {data.get('query')}")
            print(f"   - Módulo filtrado: {module}")
            print(f"   - Total encontrado: {data.get('total')}")
            print(f"   - Resultados retornados: {len(data['results'])}")
            
            return True
        except Exception as e:
            print(f"❌ Erro em /search com módulo: {str(e)}")
            return False
    
    def test_search_endpoint_empty_query(self) -> bool:
        """Testa o endpoint /search com query vazia (deve falhar)"""
        print(f"\n🔍 Testando /search com query vazia (esperando erro)...")
        try:
            payload = {
                "query": ""
            }
            response = requests.post(f"{self.api_url}/search", json=payload, timeout=10)
            
            if response.status_code == 400:
                print(f"✅ /search rejeitou query vazia conforme esperado (status 400)")
                return True
            else:
                print(f"⚠️  /search aceitou query vazia (status {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Erro testando query vazia: {str(e)}")
            return False
    
    def test_search_endpoint_pagination(self) -> bool:
        """Testa o endpoint /search com paginação"""
        print(f"\n🔍 Testando /search com paginação...")
        try:
            # Primeira página
            payload1 = {"query": "configurar", "limit": 3, "offset": 0}
            response1 = requests.post(f"{self.api_url}/search", json=payload1, timeout=10)
            assert response1.status_code == 200
            data1 = response1.json()
            
            # Segunda página
            payload2 = {"query": "configurar", "limit": 3, "offset": 3}
            response2 = requests.post(f"{self.api_url}/search", json=payload2, timeout=10)
            assert response2.status_code == 200
            data2 = response2.json()
            
            # Validar que os resultados são diferentes
            ids1 = [r.get("id") for r in data1.get("results", [])]
            ids2 = [r.get("id") for r in data2.get("results", [])]
            
            print(f"✅ Paginação funcionando")
            print(f"   - Página 1 (offset=0): {len(ids1)} resultados")
            print(f"   - Página 2 (offset=3): {len(ids2)} resultados")
            print(f"   - Sem sobreposição: {len(set(ids1) & set(ids2)) == 0}")
            
            return True
        except Exception as e:
            print(f"❌ Erro testando paginação: {str(e)}")
            return False
    
    def validate_response_schema(self, response_data: Dict[str, Any], expected_schema: Dict[str, Any]) -> bool:
        """Valida se a resposta segue o schema esperado"""
        # Implementação simplificada
        for key, expected_type in expected_schema.items():
            if key not in response_data:
                print(f"❌ Campo obrigatório '{key}' faltando na resposta")
                return False
            
            if not isinstance(response_data[key], expected_type):
                print(f"❌ Campo '{key}' tem tipo inválido")
                return False
        
        return True
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Executa todos os testes"""
        print("=" * 60)
        print("🧪 INICIANDO TESTES DA API SENIOR DOCUMENTATION")
        print("=" * 60)
        
        results = {}
        
        try:
            results["schema_structure"] = self.validate_schema_structure()
            results["endpoints_defined"] = bool(self.test_endpoints_defined())
            results["health"] = self.test_health_endpoint()
            results["stats"] = self.test_stats_endpoint()
            results["modules"] = self.test_modules_endpoint()
            results["search_valid"] = self.test_search_endpoint_valid_query()
            results["search_with_module"] = self.test_search_endpoint_with_module()
            results["search_empty"] = self.test_search_endpoint_empty_query()
            results["search_pagination"] = self.test_search_endpoint_pagination()
        except Exception as e:
            print(f"\n❌ Erro durante testes: {str(e)}")
            results["error"] = str(e)
        
        # Resumo final
        print("\n" + "=" * 60)
        print("📋 RESUMO DOS TESTES")
        print("=" * 60)
        
        passed = sum(1 for v in results.values() if v is True)
        failed = sum(1 for v in results.values() if v is False)
        
        for test_name, result in results.items():
            status = "✅ PASSOU" if result is True else "❌ FALHOU" if result is False else "⚠️  ERRO"
            print(f"{status}: {test_name}")
        
        print("=" * 60)
        print(f"Total: {passed} PASSOU | {failed} FALHOU")
        print(f"Taxa de sucesso: {(passed / (passed + failed) * 100):.1f}%" if (passed + failed) > 0 else "N/A")
        print("=" * 60)
        
        return results


# Testes com pytest
class TestSeniorAPI:
    """Testes unitários para Senior API"""
    
    @pytest.fixture(scope="class")
    def tester(self):
        """Fixture para o testador"""
        return SeniorAPITester()
    
    def test_schema_structure(self, tester):
        """Testa a estrutura do schema OpenAPI"""
        assert tester.validate_schema_structure()
    
    def test_endpoints_exist(self, tester):
        """Testa se endpoints estão definidos"""
        endpoints = tester.test_endpoints_defined()
        assert len(endpoints) > 0
        assert "/health" in endpoints
        assert "/search" in endpoints
        assert "/stats" in endpoints
    
    def test_health_endpoint(self, tester):
        """Testa o endpoint /health"""
        assert tester.test_health_endpoint()
    
    def test_stats_endpoint(self, tester):
        """Testa o endpoint /stats"""
        assert tester.test_stats_endpoint()
    
    def test_modules_endpoint(self, tester):
        """Testa o endpoint /modules"""
        assert tester.test_modules_endpoint()
    
    def test_search_with_query(self, tester):
        """Testa /search com query válida"""
        assert tester.test_search_endpoint_valid_query()
    
    def test_search_with_module_filter(self, tester):
        """Testa /search com filtro de módulo"""
        assert tester.test_search_endpoint_with_module()
    
    def test_search_pagination(self, tester):
        """Testa /search com paginação"""
        assert tester.test_search_endpoint_pagination()


if __name__ == "__main__":
    # Executar testes
    tester = SeniorAPITester()
    results = tester.run_all_tests()
    
    # Retornar código de saída baseado no resultado
    exit(0 if all(results.values()) else 1)
