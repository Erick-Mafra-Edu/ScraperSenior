#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Prático de Integração: MCP + Meilisearch
===============================================

Este script testa:
1. Carregamento do MCP Server
2. Leitura dos índices JSONL
3. Simula buscas como se viessem do MCP protocol
4. Valida estrutura de resposta
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

# Adicionar libs ao path
sys.path.insert(0, str(Path(__file__).parent))

def print_section(title: str):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def print_success(msg: str):
    print(f"✓ {msg}")

def print_error(msg: str):
    print(f"✗ {msg}")

def print_warning(msg: str):
    print(f"⚠ {msg}")

def print_info(msg: str):
    print(f"ℹ {msg}")

def test_mcp_server_initialization():
    """Testa inicialização do MCP Server"""
    print_section("TEST 1: Inicialização do MCP Server")
    
    try:
        # Adicionar o diretório ao path
        import sys
        sys.path.insert(0, str(Path("apps/mcp-server")))
        
        from mcp_server import MCPServer, SeniorDocumentationMCP
        print_success("Importação do MCP Server bem-sucedida")
        
        # Criar instância
        server = MCPServer()
        print_success("MCPServer instanciado")
        
        # Verificar ferramentas
        tools = list(server.tools.keys())
        print_success(f"Ferramentas carregadas: {', '.join(tools)}")
        
        # Verificar configuração
        doc_search = server.doc_search
        print_success(f"SeniorDocumentationMCP inicializado")
        print_info(f"  - Usando local: {doc_search.use_local}")
        print_info(f"  - URL Meilisearch: {doc_search.meilisearch_url}")
        
        return server
    
    except Exception as e:
        print_error(f"Erro ao inicializar MCP Server: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_load_index_files():
    """Testa carregamento dos arquivos JSONL"""
    print_section("TEST 2: Carregamento de Índices JSONL")
    
    try:
        index_dir = Path("data/indexes")
        
        if not index_dir.exists():
            print_error(f"Diretório não encontrado: {index_dir}")
            return None
        
        # Testar arquivo principal
        main_index = index_dir / "docs_indexacao_detailed.jsonl"
        
        if not main_index.exists():
            print_error(f"Índice principal não encontrado: {main_index}")
            return None
        
        print_success(f"Arquivo encontrado: {main_index.name}")
        
        # Carregar primeiros documentos
        documents = []
        with open(main_index, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 5:  # Primeiros 5
                    break
                try:
                    doc = json.loads(line)
                    documents.append(doc)
                except json.JSONDecodeError as e:
                    print_warning(f"Erro ao parsear linha {i+1}: {e}")
        
        print_success(f"Carregados {len(documents)} documentos de teste")
        
        # Mostrar primeiro documento
        if documents:
            doc = documents[0]
            print_info(f"Primeiro documento:")
            print_info(f"  - ID: {doc.get('id', 'N/A')}")
            print_info(f"  - Título: {doc.get('title', 'N/A')[:60]}...")
            print_info(f"  - Módulo: {doc.get('module', 'N/A')}")
            print_info(f"  - Conteúdo: {len(doc.get('content', ''))} caracteres")
        
        return documents
    
    except Exception as e:
        print_error(f"Erro ao carregar índices: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_search_operations(server):
    """Testa operações de busca"""
    print_section("TEST 3: Operações de Busca")
    
    if not server:
        print_error("Servidor não disponível")
        return False
    
    try:
        # Test 1: Lista de módulos
        print("→ Testando list_modules...")
        modules = server.doc_search.get_modules()
        print_success(f"Módulos encontrados: {len(modules)}")
        if modules:
            print_info(f"  Primeiros 5: {', '.join(modules[:5])}")
        
        # Test 2: Busca simples
        print("\n→ Testando search (query='CRM')...")
        results = server.doc_search.search("CRM", limit=3)
        print_success(f"Resultados encontrados: {len(results)}")
        for i, result in enumerate(results, 1):
            print_info(f"  {i}. {result.get('title', 'N/A')[:60]}")
        
        # Test 3: Busca com filtro de módulo
        if modules:
            module = modules[0]
            print(f"\n→ Testando search com módulo='{module}'...")
            results = server.doc_search.search("", module=module, limit=3)
            print_success(f"Resultados encontrados: {len(results)}")
            for i, result in enumerate(results, 1):
                print_info(f"  {i}. {result.get('title', 'N/A')[:60]}")
        
        # Test 4: Estatísticas
        print("\n→ Testando get_stats...")
        stats = server.doc_search.get_stats()
        print_success("Estatísticas obtidas:")
        print_info(f"  - Total de documentos: {stats.get('total_documents', 'N/A')}")
        print_info(f"  - Módulos: {stats.get('modules', 'N/A')}")
        print_info(f"  - Com HTML: {stats.get('has_html', 'N/A')}")
        print_info(f"  - Fonte: {stats.get('source', 'N/A')}")
        
        return True
    
    except Exception as e:
        print_error(f"Erro durante buscas: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_call_interface(server):
    """Testa interface de chamada de ferramentas (como MCP faria)"""
    print_section("TEST 4: Interface de Chamada de Ferramentas (MCP)")
    
    if not server:
        print_error("Servidor não disponível")
        return False
    
    try:
        # Test 1: search_docs
        print("→ Chamando ferramenta 'search_docs'...")
        result = server.handle_tool_call("search_docs", {
            "query": "configurar",
            "limit": 3
        })
        result_obj = json.loads(result)
        
        if "results" in result_obj:
            print_success(f"Resultados: {result_obj['count']} documentos encontrados")
            print_info(f"  Query: {result_obj.get('query')}")
        elif "error" in result_obj:
            print_warning(f"Resposta com erro: {result_obj['error']}")
        else:
            print_warning(f"Resposta inesperada: {result_obj}")
        
        # Test 2: list_modules
        print("\n→ Chamando ferramenta 'list_modules'...")
        result = server.handle_tool_call("list_modules", {})
        result_obj = json.loads(result)
        
        print_success(f"Módulos: {result_obj.get('total_modules', 0)}")
        
        # Test 3: get_stats
        print("\n→ Chamando ferramenta 'get_stats'...")
        result = server.handle_tool_call("get_stats", {})
        result_obj = json.loads(result)
        
        print_success(f"Estatísticas obtidas:")
        print_info(f"  - Documentos: {result_obj.get('total_documents', 'N/A')}")
        print_info(f"  - Fonte: {result_obj.get('source', 'N/A')}")
        
        return True
    
    except Exception as e:
        print_error(f"Erro ao testar ferramentas: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_protocol_simulation():
    """Simula requisição MCP 2.0 JSON-RPC"""
    print_section("TEST 5: Simulação de Protocolo MCP 2.0")
    
    try:
        import sys
        sys.path.insert(0, str(Path("apps/mcp-server")))
        
        from mcp_server import MCPServer
        
        server = MCPServer()
        
        # Simular requisição JSON-RPC
        print("→ Simulando requisição JSON-RPC 2.0...")
        
        jsonrpc_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "search_docs",
                "arguments": {
                    "query": "vendas",
                    "limit": 5
                }
            }
        }
        
        print_info(f"Requisição:")
        print(json.dumps(jsonrpc_request, indent=2, ensure_ascii=False))
        
        # Processar
        tool_name = jsonrpc_request["params"]["name"]
        tool_args = jsonrpc_request["params"]["arguments"]
        
        result = server.handle_tool_call(tool_name, tool_args)
        result_obj = json.loads(result)
        
        # Simular resposta JSON-RPC
        jsonrpc_response = {
            "jsonrpc": "2.0",
            "id": jsonrpc_request["id"],
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result_obj, ensure_ascii=False)
                    }
                ]
            }
        }
        
        print_success(f"Resposta gerada:")
        print(json.dumps(jsonrpc_response, indent=2, ensure_ascii=False)[:500] + "...")
        
        return True
    
    except Exception as e:
        print_error(f"Erro na simulação MCP: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_behavior():
    """Testa comportamento de fallback (sem Meilisearch)"""
    print_section("TEST 6: Comportamento de Fallback")
    
    try:
        import sys
        sys.path.insert(0, str(Path("apps/mcp-server")))
        
        from mcp_server import SeniorDocumentationMCP
        
        # Criar instância que forçará uso local
        doc_search = SeniorDocumentationMCP(
            meilisearch_url="http://localhost:9999"  # Port inválido
        )
        
        print_info(f"Usando fallback local: {doc_search.use_local}")
        
        if doc_search.use_local:
            print_success("Fallback ativado corretamente")
            
            # Testar busca local
            results = doc_search.search("teste", limit=3)
            print_success(f"Busca local retornou: {len(results)} resultados")
        else:
            print_warning("Fallback não foi ativado (Meilisearch disponível?)")
        
        return True
    
    except Exception as e:
        print_error(f"Erro ao testar fallback: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "="*80)
    print("  TESTE PRÁTICO DE INTEGRAÇÃO: MCP + Meilisearch")
    print("="*80)
    
    results = []
    
    # Test 1
    server = test_mcp_server_initialization()
    results.append(("Inicialização MCP", server is not None))
    
    # Test 2
    documents = test_load_index_files()
    results.append(("Carregamento JSONL", documents is not None))
    
    # Test 3
    if server:
        search_ok = test_search_operations(server)
        results.append(("Operações de Busca", search_ok))
    
    # Test 4
    if server:
        tools_ok = test_tool_call_interface(server)
        results.append(("Interface de Ferramentas", tools_ok))
    
    # Test 5
    proto_ok = test_mcp_protocol_simulation()
    results.append(("Simulação MCP 2.0", proto_ok))
    
    # Test 6
    fallback_ok = test_fallback_behavior()
    results.append(("Fallback Behavior", fallback_ok))
    
    # Print summary
    print_section("RESUMO DOS TESTES")
    
    passed = 0
    for test_name, result in results:
        if result:
            print_success(test_name)
            passed += 1
        else:
            print_error(test_name)
    
    print(f"\n{'='*80}")
    print(f"  Total: {passed}/{len(results)} testes passaram")
    print(f"{'='*80}\n")
    
    return passed == len(results)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
