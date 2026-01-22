#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server - Senior Documentation Search
========================================

Model Context Protocol (MCP) server para busca em documentação Senior.
Integra com Meilisearch para busca rápida e relevante.

Recursos:
- Busca por keywords em toda documentação
- Filtro por módulo
- Busca por breadcrumb/hierarquia
- Retorno de metadados completos
- Suporte a HTML original

Instalação:
    pip install mcp
    
Uso:
    python src/mcp_server.py [--meilisearch-url http://localhost:7700]
"""

import json
import asyncio
from pathlib import Path
from typing import Any, Dict, List
import sys
import os

# Forçar UTF-8 para evitar problemas de encoding no Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

try:
    import meilisearch
    MEILISEARCH_AVAILABLE = True
except ImportError:
    MEILISEARCH_AVAILABLE = False
    # Comentado para não interferir com protocolo MCP quando rodando em VS Code
    # print("[!] Meilisearch client não disponível. Usando modo local.")


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Carrega a configuração do arquivo mcp_config.json
    
    Args:
        config_path: Caminho para o arquivo de configuração (opcional)
    
    Returns:
        Dicionário com as configurações
    """
    if config_path is None:
        # Tentar encontrar mcp_config.json no diretório raiz do projeto
        script_dir = Path(__file__).parent.parent  # Sobe um nível de src/
        config_path = script_dir / "mcp_config.json"
    else:
        config_path = Path(config_path)
    
    # Configurações padrão
    default_config = {
        "meilisearch": {
            "url": "http://localhost:7700",
            "apiKey": "meilisearch_master_key"
        },
        "settings": {
            "indexName": "senior_docs",
            "maxResults": 10,
            "timeout": 5000
        }
    }
    
    # Tentar carregar o arquivo de configuração
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                # Comentado para não interferir com protocolo MCP
                # print(f"✓ Configuração carregada de: {config_path}")
                # Mesclar com padrões se algo estiver faltando
                default_config.update(config)
                return default_config
        except Exception as e:
            # Comentado para não interferir com protocolo MCP
            # print(f"[!] Erro ao carregar configuração: {e}")
            # print(f"[!] Usando configurações padrão")
            return default_config
    else:
        # Comentado para não interferir com protocolo MCP
        # print(f"[!] Arquivo de configuração não encontrado: {config_path}")
        # print(f"[!] Usando configurações padrão")
        return default_config


class SeniorDocumentationMCP:
    """MCP Server para documentação Senior"""
    
    def __init__(self, meilisearch_url: str = None, api_key: str = None, config_path: str = None):
        # Carregar configuração
        self.config = load_config(config_path)
        
        # Usar valores fornecidos ou da configuração
        self.meilisearch_url = meilisearch_url or self.config["meilisearch"]["url"]
        self.api_key = api_key or self.config["meilisearch"]["apiKey"]
        self.index_name = self.config["settings"].get("indexName", "senior_docs")
        self.max_results = self.config["settings"].get("maxResults", 10)
        
        self.client = None
        self.local_documents = []
        self.use_local = not MEILISEARCH_AVAILABLE
        
        if MEILISEARCH_AVAILABLE:
            try:
                self.client = meilisearch.Client(self.meilisearch_url, self.api_key)
                # Testar conexão
                self.client.health()
                # Comentado para não interferir com protocolo MCP
                # print(f"[✓] Conectado ao Meilisearch: {self.meilisearch_url}")
                self.use_local = False
            except:
                # Comentado para não interferir com protocolo MCP
                # print("[!] Não conseguiu conectar ao Meilisearch. Usando modo local.")
                self.use_local = True
                self._load_local_documents()
        else:
            self._load_local_documents()
    
    def _load_local_documents(self):
        """Carrega documentos do arquivo JSONL local"""
        index_file = Path("docs_indexacao_detailed.jsonl")
        if not index_file.exists():
            # Comentado para não interferir com protocolo MCP
            # print(f"[!] Arquivo não encontrado: {index_file}")
            return
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.local_documents.append(json.loads(line))
            # Comentado para não interferir com protocolo MCP
            # print(f"[✓] Carregados {len(self.local_documents)} documentos localmente")
        except Exception as e:
            # Comentado para não interferir com protocolo MCP
            # print(f"[✗] Erro ao carregar documentos: {e}")
            pass
    
    def search(self, query: str, module: str = None, limit: int = 5) -> List[Dict]:
        """
        Busca documentos no Meilisearch ou localmente
        
        Args:
            query: String de busca
            module: Filtro por módulo (opcional)
            limit: Número máximo de resultados
            
        Returns:
            Lista de documentos encontrados
        """
        if self.use_local:
            return self._search_local(query, module, limit)
        
        try:
            if not self.client:
                return []
            
            index = self.client.index(self.index_name)
            
            search_params = {
                "limit": limit,
                "attributesToRetrieve": [
                    "id", "title", "url", "module", "breadcrumb",
                    "headers_count", "content_length", "has_html"
                ]
            }
            
            if module:
                search_params["filter"] = f'module = "{module}"'
            
            results = index.search(query, search_params)
            return results.get("hits", [])
        except Exception as e:
            # Silenciar para não interferir no protocolo MCP stdio
            return []
    
    def _search_local(self, query: str, module: str = None, limit: int = 5) -> List[Dict]:
        """Busca local simples em documentos"""
        query_lower = query.lower()
        results = []
        
        for doc in self.local_documents:
            # Filtrar por módulo se especificado
            if module and doc['module'] != module:
                continue
            
            score = 0
            # Buscar em título (peso maior)
            if query_lower in doc['title'].lower():
                score += 3
            # Buscar em módulo
            if query_lower in doc['module'].lower():
                score += 2
            # Buscar em breadcrumb
            if query_lower in doc['breadcrumb'].lower():
                score += 1
            # Buscar em headers
            if any(query_lower in h.lower() for h in doc.get('headers', [])):
                score += 1
            # Buscar em conteúdo
            if query_lower in doc['content'].lower():
                score += 1
            
            if score > 0:
                results.append((score, doc))
        
        # Ordenar por score e retornar top N
        results.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in results[:limit]]
    
    def get_by_module(self, module: str, limit: int = 20) -> List[Dict]:
        """Retorna documentos de um módulo específico"""
        if self.use_local:
            return [d for d in self.local_documents if d['module'] == module][:limit]
        
        try:
            if not self.client:
                return []
            
            index = self.client.index(self.index_name)
            results = index.search(
                "",
                {
                    "filter": f'module = "{module}"',
                    "limit": limit,
                    "attributesToRetrieve": [
                        "id", "title", "url", "module", "breadcrumb",
                        "headers_count", "content_length", "has_html"
                    ]
                }
            )
            return results.get("hits", [])
        except Exception as e:
            # Silenciar para não interferir no protocolo MCP stdio
            return []
    
    def get_modules(self) -> List[str]:
        """Retorna lista de módulos disponíveis"""
        if self.use_local:
            modules = set(d['module'] for d in self.local_documents)
            return sorted(list(modules))
        
        try:
            if not self.client:
                return []
            
            index = self.client.index(self.index_name)
            # Busca vazia para pegar facets
            results = index.search("", {"facets": ["module"], "limit": 0})
            
            facets = results.get("facetDistribution", {})
            modules = facets.get("module", {})
            return sorted(list(modules.keys()))
        except Exception as e:
            # Silenciar para não interferir no protocolo MCP stdio
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do índice"""
        if self.use_local:
            stats = {
                'total_documents': len(self.local_documents),
                'modules': len(set(d['module'] for d in self.local_documents)),
                'has_html': sum(1 for d in self.local_documents if d.get('has_html')),
                'source': 'local'
            }
            return stats
        
        try:
            if not self.client:
                return {}
            
            index = self.client.index(self.index_name)
            stats = index.get_stats()
            stats['source'] = 'meilisearch'
            return stats
        except Exception as e:
            # Silenciar para não interferir no protocolo MCP stdio
            return {}


class MCPServer:
    """Servidor MCP simples para documentação Senior"""
    
    def __init__(self):
        self.doc_search = SeniorDocumentationMCP()
        self.tools = {
            "search_docs": {
                "description": "Busca documentos por palavras-chave",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Palavras-chave para busca (obrigatório)"
                        },
                        "module": {
                            "type": "string",
                            "description": "Módulo específico para filtrar (opcional)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Número máximo de resultados (padrão: 5)"
                        }
                    },
                    "required": ["query"]
                },
                "parameters": {
                    "query": {"type": "string", "description": "Palavras-chave para busca"},
                    "module": {"type": "string", "description": "Módulo específico (opcional)"},
                    "limit": {"type": "number", "description": "Número de resultados (padrão: 5)"}
                }
            },
            "list_modules": {
                "description": "Lista todos os módulos disponíveis com contagem de documentos",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "parameters": {}
            },
            "get_module_docs": {
                "description": "Retorna todos os documentos de um módulo específico",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "module": {
                            "type": "string",
                            "description": "Nome do módulo (obrigatório)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Número máximo de resultados (padrão: 20)"
                        }
                    },
                    "required": ["module"]
                },
                "parameters": {
                    "module": {"type": "string", "description": "Nome do módulo"},
                    "limit": {"type": "number", "description": "Número de resultados (padrão: 20)"}
                }
            },
            "get_stats": {
                "description": "Retorna estatísticas da base de documentação",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "parameters": {}
            }
        }
    
    def handle_tool_call(self, tool_name: str, params: Dict) -> str:
        """Processa chamada de ferramenta"""
        try:
            if tool_name == "search_docs":
                query = params.get("query", "")
                # Validação: garantir que query é string
                if isinstance(query, list):
                    query = query[0] if query else ""
                query = str(query).strip()
                
                module = params.get("module")
                if isinstance(module, list):
                    module = module[0] if module else None
                if module:
                    module = str(module).strip()
                
                limit = int(params.get("limit", 5))
                
                if not query:
                    return json.dumps({"error": "query é obrigatório"})
                
                results = self.doc_search.search(query, module, limit)
                return json.dumps({
                    "query": query,
                    "module_filter": module,
                    "count": len(results),
                    "results": results
                }, ensure_ascii=False, indent=2)
            
            elif tool_name == "list_modules":
                modules = self.doc_search.get_modules()
                return json.dumps({
                    "total_modules": len(modules),
                    "modules": modules
                }, ensure_ascii=False)
            
            elif tool_name == "get_module_docs":
                module = params.get("module")
                # Validação: garantir que module é string
                if isinstance(module, list):
                    module = module[0] if module else None
                if module:
                    module = str(module).strip()
                
                limit = int(params.get("limit", 20))
                
                if not module:
                    return json.dumps({"error": "module é obrigatório"})
                
                docs = self.doc_search.get_by_module(module, limit)
                return json.dumps({
                    "module": module,
                    "count": len(docs),
                    "docs": docs
                }, ensure_ascii=False, indent=2)
            
            elif tool_name == "get_stats":
                stats = self.doc_search.get_stats()
                return json.dumps(stats, ensure_ascii=False, indent=2)
            
            else:
                return json.dumps({"error": f"Ferramenta desconhecida: {tool_name}"})
        
        except Exception as e:
            return json.dumps({"error": str(e)})


def main():
    # Comentado para não interferir com protocolo MCP
    # Os prints são enviados via stderr, mas interferem no parsing do protocolo
    # print("\n" + "="*80)
    # print("[MCP SERVER] Senior Documentation Search")
    # print("="*80 + "\n")
    
    server = MCPServer()
    
    # Exibir ferramentas disponíveis
    # print("[FERRAMENTAS DISPONÍVEIS]\n")
    # for tool_name, tool_info in server.tools.items():
    #     print(f"  • {tool_name}")
    #     print(f"    {tool_info['description']}")
    
    # Exibir módulos
    # print("\n[MÓDULOS DISPONÍVEIS]\n")
    # modules = server.doc_search.get_modules()
    # for i, module in enumerate(modules, 1):
    #     print(f"  {i}. {module}")
    
    # Exibir estatísticas
    # print("\n[ESTATÍSTICAS]\n")
    # stats = server.doc_search.get_stats()
    # print(f"  Total de documentos: {stats.get('total_documents', 'N/A')}")
    # print(f"  Módulos: {stats.get('modules', 'N/A')}")
    # print(f"  Fonte: {stats.get('source', 'N/A')}")
    
    # Demo
    # print("\n[DEMO - Busca por 'CRM']\n")
    # result = server.handle_tool_call("search_docs", {"query": "CRM", "limit": 3})
    # result_obj = json.loads(result)
    # for doc in result_obj.get("results", [])[:3]:
    #     print(f"  • {doc['title']}")
    #     print(f"    Módulo: {doc['module']} | URL: {doc['url'][:80]}...")
    
    # print("\n" + "="*80 + "\n")
    # print("[✓] MCP Server pronto para integração!")
    # print("Ferramentas podem ser chamadas via MCP protocol.\n")


if __name__ == "__main__":
    main()
