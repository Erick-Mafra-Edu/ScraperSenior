"""
Script para verificar módulos indexados no servidor Senior Documentation API
"""

import requests
import json
from typing import Dict, List
from api_server_detector import detect_api_server
from collections import defaultdict


class ModuleInspector:
    """Inspetor de módulos disponíveis na API"""
    
    def __init__(self, api_url: str = None):
        if api_url is None:
            api_url, _ = detect_api_server()
        self.api_url = api_url.rstrip("/")
        self.modules = {}
        self.documents_by_module = defaultdict(int)
    
    def get_modules_list(self) -> List[Dict]:
        """Obtém lista de módulos via /modules endpoint"""
        print("🔍 Buscando módulos via /modules endpoint...")
        try:
            response = requests.get(f"{self.api_url}/modules", timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                modules = data.get("modules", [])
                print(f"✅ {len(modules)} módulos encontrados via /modules\n")
                return modules
            else:
                print(f"❌ Erro: {data.get('detail', 'Desconhecido')}")
                return []
        except Exception as e:
            print(f"❌ Erro ao buscar módulos: {str(e)}\n")
            return []
    
    def get_stats(self) -> Dict:
        """Obtém estatísticas da API"""
        print("📊 Buscando estatísticas via /stats endpoint...")
        try:
            response = requests.get(f"{self.api_url}/stats", timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                print(f"✅ Estatísticas obtidas\n")
                return data
            else:
                print(f"❌ Erro: {data.get('detail', 'Desconhecido')}")
                return {}
        except Exception as e:
            print(f"❌ Erro ao buscar estatísticas: {str(e)}\n")
            return {}
    
    def search_by_module(self, module: str, query: str = "*") -> int:
        """Conta documentos em um módulo específico via busca"""
        try:
            payload = {"query": query, "module": module, "limit": 1}
            response = requests.post(f"{self.api_url}/search", json=payload, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("total", 0)
        except:
            pass
        
        return 0
    
    def discover_modules_via_search(self) -> Dict[str, int]:
        """Descobre módulos fazendo buscas com queries conhecidas"""
        print("🔎 Descobrindo módulos via buscas...")
        
        # Queries que devem retornar resultados de diferentes módulos
        test_queries = [
            "configurar",
            "como fazer",
            "backup",
            "ntlm",
            "procedimento",
            "guia",
            "erro",
            "solução",
            "implementação",
            "documentação"
        ]
        
        modules_found = {}
        
        for query in test_queries:
            try:
                payload = {"query": query, "limit": 20}
                response = requests.post(f"{self.api_url}/search", json=payload, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    for doc in data.get("results", []):
                        module = doc.get("module")
                        if module:
                            if module not in modules_found:
                                modules_found[module] = {"count": 0, "examples": []}
                            modules_found[module]["count"] += 1
                            
                            # Guardar exemplo
                            if len(modules_found[module]["examples"]) < 2:
                                modules_found[module]["examples"].append({
                                    "title": doc.get("title"),
                                    "query": query
                                })
            except:
                pass
        
        return modules_found
    
    def get_sample_documents_by_module(self) -> Dict[str, List[Dict]]:
        """Obtém documentos de amostra de cada módulo"""
        print("📄 Buscando documentos de amostra...")
        
        # Tentar obter documentação de cada módulo conhecido
        known_modules = [
            "RH", "FINANCEIRO", "TECNOLOGIA", "BPM", "FISCAL",
            "GESTAO", "VENDAS", "COMPRAS", "ESTOQUE", "QUALIDADE"
        ]
        
        modules_with_docs = {}
        
        for module in known_modules:
            try:
                payload = {"query": "procedimento", "module": module, "limit": 3}
                response = requests.post(f"{self.api_url}/search", json=payload, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    total = data.get("total", 0)
                    results = data.get("results", [])
                    
                    if total > 0:
                        modules_with_docs[module] = {
                            "total": total,
                            "samples": [
                                {
                                    "title": doc.get("title"),
                                    "score": doc.get("score")
                                }
                                for doc in results[:2]
                            ]
                        }
            except:
                pass
        
        return modules_with_docs
    
    def print_modules_table(self, modules: List[Dict]):
        """Imprime tabela formatada de módulos"""
        if not modules:
            print("❌ Nenhum módulo encontrado\n")
            return
        
        print("=" * 80)
        print("📚 MÓDULOS DESCOBERTOS")
        print("=" * 80)
        print(f"{'#':<3} {'Nome':<25} {'Documentos':<15} {'Status':<20}")
        print("-" * 80)
        
        for i, module in enumerate(modules, 1):
            name = module.get("name", "Unknown")
            doc_count = module.get("doc_count", 0)
            status = "✅ Ativo" if doc_count > 0 else "⚠️  Vazio"
            print(f"{i:<3} {name:<25} {doc_count:<15} {status:<20}")
        
        print("=" * 80)
        print()
    
    def print_stats(self, stats: Dict):
        """Imprime estatísticas formatadas"""
        if not stats:
            print("❌ Nenhuma estatística disponível\n")
            return
        
        print("=" * 80)
        print("📊 ESTATÍSTICAS DA API")
        print("=" * 80)
        print(f"Total de Documentos:  {stats.get('total_documents', 'N/A'):>15}")
        print(f"Total de Módulos:     {stats.get('total_modules', 'N/A'):>15}")
        print(f"Índice Meilisearch:   {stats.get('index_name', 'N/A'):>15}")
        
        if stats.get('modules'):
            print(f"\nMódulos com documentos:")
            for module, count in sorted(stats['modules'].items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    print(f"  ├─ {module}: {count} documentos")
        
        print("=" * 80)
        print()
    
    def print_discovered_modules(self, modules: Dict[str, int]):
        """Imprime módulos descobertos via busca"""
        if not modules:
            print("❌ Nenhum módulo descoberto via busca\n")
            return
        
        print("=" * 80)
        print("🔎 MÓDULOS DESCOBERTOS VIA BUSCA")
        print("=" * 80)
        print(f"{'Módulo':<25} {'Ocorrências':<15} {'Exemplos':<40}")
        print("-" * 80)
        
        for module in sorted(modules.keys()):
            count = modules[module]["count"]
            examples = modules[module]["examples"]
            example_text = ", ".join([e["title"][:30] for e in examples[:2]])
            print(f"{module:<25} {count:<15} {example_text:<40}")
        
        print("=" * 80)
        print()
    
    def print_sample_documents(self, modules_docs: Dict):
        """Imprime documentos de amostra"""
        if not modules_docs:
            print("❌ Nenhum documento encontrado\n")
            return
        
        print("=" * 80)
        print("📄 DOCUMENTOS DE AMOSTRA POR MÓDULO")
        print("=" * 80)
        
        for module in sorted(modules_docs.keys()):
            info = modules_docs[module]
            print(f"\n🔹 {module}")
            print(f"   Total: {info['total']} documentos")
            print(f"   Amostras:")
            for sample in info['samples']:
                print(f"   ├─ {sample['title']}")
        
        print("\n" + "=" * 80)
        print()
    
    def run_full_inspection(self):
        """Executa inspeção completa"""
        print("\n" + "=" * 80)
        print("🔍 INSPEÇÃO COMPLETA DE MÓDULOS - SENIOR DOCUMENTATION API")
        print("=" * 80)
        print(f"Servidor: {self.api_url}\n")
        
        # 1. Obter lista via /modules
        modules = self.get_modules_list()
        self.print_modules_table(modules)
        
        # 2. Obter estatísticas
        stats = self.get_stats()
        self.print_stats(stats)
        
        # 3. Descobrir módulos via busca
        discovered = self.discover_modules_via_search()
        print(f"✅ {len(discovered)} módulos descobertos via busca\n")
        self.print_discovered_modules(discovered)
        
        # 4. Obter amostras de documentos
        samples = self.get_sample_documents_by_module()
        self.print_sample_documents(samples)
        
        # 5. Resumo final
        print("=" * 80)
        print("📋 RESUMO")
        print("=" * 80)
        print(f"✅ Módulos via /modules:      {len(modules)}")
        print(f"✅ Módulos descobertos:       {len(discovered)}")
        print(f"✅ Módulos com documentos:    {len(samples)}")
        print(f"✅ Total de documentos:       {stats.get('total_documents', 'N/A')}")
        print("=" * 80)
        
        # 6. Gerar JSON com resultado
        result = {
            "server": self.api_url,
            "modules_from_endpoint": modules,
            "modules_discovered": discovered,
            "modules_with_samples": samples,
            "stats": stats
        }
        
        with open("modules_inspection_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print("\n✅ Resultado salvo em: modules_inspection_result.json\n")
        
        return result


if __name__ == "__main__":
    inspector = ModuleInspector()
    inspector.run_full_inspection()
