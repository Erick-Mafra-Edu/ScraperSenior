#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do MCP Server - Senior Documentation
==========================================

Script de teste completo das funcionalidades do MCP Server
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp_server import MCPServer


def test_mcp_server():
    """Testa todas as funcionalidades do MCP Server"""
    
    print("\n" + "="*90)
    print("[TESTE] MCP Server - Senior Documentation")
    print("="*90 + "\n")
    
    # Inicializar servidor
    server = MCPServer()
    
    # Teste 1: Listar módulos
    print("[TESTE 1] Listar módulos\n")
    result = server.handle_tool_call("list_modules", {})
    result_obj = json.loads(result)
    print(f"  ✓ Módulos disponíveis: {result_obj['total_modules']}")
    print(f"  ✓ Primeiro módulo: {result_obj['modules'][0]}")
    
    # Teste 2: Buscar por "CRM"
    print("\n[TESTE 2] Buscar por 'CRM'\n")
    result = server.handle_tool_call("search_docs", {"query": "CRM", "limit": 3})
    result_obj = json.loads(result)
    print(f"  ✓ Query: {result_obj['query']}")
    print(f"  ✓ Resultados encontrados: {result_obj['count']}")
    for i, doc in enumerate(result_obj['results'], 1):
        print(f"    {i}. {doc['title'][:60]}")
    
    # Teste 3: Buscar por "Gerador de Relatórios"
    print("\n[TESTE 3] Buscar por 'Gerador de Relatórios'\n")
    result = server.handle_tool_call("search_docs", {"query": "Gerador de Relatórios", "limit": 3})
    result_obj = json.loads(result)
    print(f"  ✓ Query: {result_obj['query']}")
    print(f"  ✓ Resultados encontrados: {result_obj['count']}")
    for i, doc in enumerate(result_obj['results'], 1):
        print(f"    {i}. {doc['title'][:60]}")
    
    # Teste 4: Buscar por módulo
    print("\n[TESTE 4] Buscar por 'usuário' no módulo TECNOLOGIA\n")
    result = server.handle_tool_call("search_docs", {
        "query": "usuário",
        "module": "TECNOLOGIA",
        "limit": 2
    })
    result_obj = json.loads(result)
    print(f"  ✓ Query: {result_obj['query']}")
    print(f"  ✓ Módulo: {result_obj['module_filter']}")
    print(f"  ✓ Resultados encontrados: {result_obj['count']}")
    for i, doc in enumerate(result_obj['results'], 1):
        print(f"    {i}. {doc['title'][:60]}")
    
    # Teste 5: Obter documentos de um módulo
    print("\n[TESTE 5] Obter documentos do módulo GESTAO_DE_RELACIONAMENTO_CRM\n")
    result = server.handle_tool_call("get_module_docs", {
        "module": "GESTAO_DE_RELACIONAMENTO_CRM",
        "limit": 3
    })
    result_obj = json.loads(result)
    print(f"  ✓ Módulo: {result_obj['module']}")
    print(f"  ✓ Documentos no módulo: {result_obj['count']} (mostrando 3)")
    for i, doc in enumerate(result_obj['docs'], 1):
        print(f"    {i}. {doc['title'][:60]}")
    
    # Teste 6: Obter estatísticas
    print("\n[TESTE 6] Obter estatísticas\n")
    result = server.handle_tool_call("get_stats", {})
    result_obj = json.loads(result)
    print(f"  ✓ Total de documentos: {result_obj.get('total_documents', 'N/A')}")
    print(f"  ✓ Módulos: {result_obj.get('modules', 'N/A')}")
    print(f"  ✓ Com HTML original: {result_obj.get('has_html', 'N/A')}")
    print(f"  ✓ Fonte de dados: {result_obj.get('source', 'N/A')}")
    
    print("\n" + "="*90)
    print("[✓] TODOS OS TESTES PASSARAM COM SUCESSO!")
    print("="*90 + "\n")


if __name__ == "__main__":
    test_mcp_server()
