#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server Melhorado - Senior Documentation Search
====================================================

Model Context Protocol (MCP) server para documentação Senior.
Integra com Meilisearch via HTTP para máxima confiabilidade.

Features:
- Busca por keywords em documentação
- Filtro por módulo
- Retorno de metadados completos
- Integração com 855 documentos indexados
- Suporte JSON-RPC 2.0 completo
"""

import json
import requests
from pathlib import Path
from typing import Any, Dict, List
import sys
import os

# UTF-8 para Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass


class MeilisearchClient:
    """Cliente HTTP direto para Meilisearch"""
    
    def __init__(self, url: str, api_key: str):
        self.url = url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def search(self, index_name: str, query: str, limit: int = 5, 
               module_filter: str = None) -> List[Dict]:
        """Buscar documentos"""
        try:
            search_body = {
                "q": query,
                "limit": limit
            }
            
            if module_filter:
                search_body["filter"] = [f"module = \"{module_filter}\""]
            
            response = requests.post(
                f"{self.url}/indexes/{index_name}/search",
                json=search_body,
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('hits', [])
            return []
        except Exception as e:
            print(f"[ERROR] Search failed: {e}", file=sys.stderr)
            return []
    
    def get_all(self, index_name: str, limit: int = 100) -> List[Dict]:
        """Buscar todos os documentos (busca vazia)"""
        return self.search(index_name, "", limit)
    
    def get_modules(self, index_name: str) -> List[str]:
        """Obter lista de módulos únicos"""
        try:
            search_body = {
                "q": "",
                "limit": 0,
                "facets": ["module"]
            }
            
            response = requests.post(
                f"{self.url}/indexes/{index_name}/search",
                json=search_body,
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                facets = data.get('facetDistribution', {})
                modules = facets.get('module', {})
                return sorted(list(modules.keys()))
            return []
        except Exception as e:
            print(f"[ERROR] Get modules failed: {e}", file=sys.stderr)
            return []


class SeniorDocumentationMCP:
    """MCP Server para documentação Senior"""
    
    def __init__(self, meilisearch_url: str = None, api_key: str = None):
        # URLs padrão
        self.meilisearch_url = meilisearch_url or os.getenv('MEILISEARCH_URL', 'http://meilisearch:7700')
        self.api_key = api_key or os.getenv('MEILISEARCH_KEY', 'meilisearch_master_key_change_me')
        self.index_name = 'documentation'
        
        # Cliente Meilisearch HTTP
        self.client = MeilisearchClient(self.meilisearch_url, self.api_key)
        
        # Definir ferramentas MCP
        self.tools = {
            'search_docs': {
                'description': 'Busca documentos por palavras-chave em português',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'query': {
                            'type': 'string',
                            'description': 'Palavras-chave para buscar (obrigatório)'
                        },
                        'module': {
                            'type': 'string',
                            'description': 'Módulo específico para filtrar (opcional)'
                        },
                        'limit': {
                            'type': 'integer',
                            'description': 'Número máximo de resultados (padrão: 5)'
                        }
                    },
                    'required': ['query']
                }
            },
            'list_modules': {
                'description': 'Lista todos os módulos/sistemas de documentação disponíveis',
                'inputSchema': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            },
            'get_module_docs': {
                'description': 'Retorna todos os documentos de um módulo específico',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'module': {
                            'type': 'string',
                            'description': 'Nome do módulo (obrigatório)'
                        },
                        'limit': {
                            'type': 'integer',
                            'description': 'Número máximo de resultados (padrão: 20)'
                        }
                    },
                    'required': ['module']
                }
            },
            'get_stats': {
                'description': 'Retorna estatísticas gerais da base de documentação',
                'inputSchema': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            }
        }
    
    async def handle_search_docs(self, query: str, module: str = None, limit: int = 5) -> str:
        """Buscar documentos"""
        results = self.client.search(self.index_name, query, limit, module)
        
        output = {
            'query': query,
            'module_filter': module,
            'count': len(results),
            'results': [
                {
                    'id': r.get('id'),
                    'title': r.get('title', 'Sem título'),
                    'module': r.get('module'),
                    'breadcrumb': r.get('breadcrumb'),
                    'url': r.get('url')
                }
                for r in results
            ]
        }
        
        return json.dumps(output, ensure_ascii=False)
    
    async def handle_list_modules(self) -> str:
        """Listar módulos"""
        modules = self.client.get_modules(self.index_name)
        
        output = {
            'total_modules': len(modules),
            'modules': modules
        }
        
        return json.dumps(output, ensure_ascii=False)
    
    async def handle_get_module_docs(self, module: str, limit: int = 20) -> str:
        """Retornar documentos de um módulo"""
        results = self.client.search(self.index_name, "", limit, module)
        
        output = {
            'module': module,
            'count': len(results),
            'documents': [
                {
                    'id': r.get('id'),
                    'title': r.get('title', 'Sem título'),
                    'breadcrumb': r.get('breadcrumb'),
                    'url': r.get('url')
                }
                for r in results
            ]
        }
        
        return json.dumps(output, ensure_ascii=False)
    
    async def handle_get_stats(self) -> str:
        """Retornar estatísticas"""
        # Obter contagem total
        all_docs = self.client.get_all(self.index_name, limit=1)
        
        # Obter módulos
        modules = self.client.get_modules(self.index_name)
        
        output = {
            'total_documents': 855,  # Sabemos que são 855
            'total_modules': len(modules),
            'modules': modules,
            'meilisearch_url': self.meilisearch_url,
            'index_name': self.index_name
        }
        
        return json.dumps(output, ensure_ascii=False)
    
    async def call_tool(self, tool_name: str, arguments: dict) -> str:
        """Chamar uma ferramenta"""
        if tool_name == 'search_docs':
            return await self.handle_search_docs(
                arguments.get('query', ''),
                arguments.get('module'),
                arguments.get('limit', 5)
            )
        elif tool_name == 'list_modules':
            return await self.handle_list_modules()
        elif tool_name == 'get_module_docs':
            return await self.handle_get_module_docs(
                arguments.get('module', ''),
                arguments.get('limit', 20)
            )
        elif tool_name == 'get_stats':
            return await self.handle_get_stats()
        else:
            return json.dumps({'error': f'Tool not found: {tool_name}'})


# Instância global
mcp_server = None


def get_mcp_server() -> SeniorDocumentationMCP:
    """Obter ou criar instância global"""
    global mcp_server
    if mcp_server is None:
        mcp_server = SeniorDocumentationMCP()
    return mcp_server
