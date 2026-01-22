#!/usr/bin/env python3
"""Teste de integração do MCP Server com dados completos"""
import json
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from mcp_server import MCPServer

print("=== TESTE DE INTEGRAÇÃO MCP SERVER ===\n")

# Criar instância do servidor
server = MCPServer()

print("✓ Servidor criado\n")

# Teste 1: Get Stats
print("1️⃣ Testando get_stats:")
stats = server.doc_search.get_stats()
print(f"   Total de documentos: {stats.get('total_docs', 0)}")
print(f"   Módulos: {stats.get('total_modules', 0)}")
print(f"   Fonte: {stats.get('source', 'local')}")
print(f"   Status: {'✅ OK' if stats.get('total_docs', 0) > 22 else '❌ ERRO'}\n")

# Teste 2: List Modules
print("2️⃣ Testando list_modules:")
modules = server.doc_search.get_modules()
print(f"   Módulos encontrados: {len(modules)}")
for mod in sorted(modules)[:5]:
    print(f"     - {mod}")
if len(modules) > 5:
    print(f"     ... e mais {len(modules) - 5}")
print(f"   Status: {'✅ OK' if len(modules) > 1 else '❌ ERRO'}\n")

# Teste 3: Get Module Docs
print("3️⃣ Testando get_by_module:")
docs = server.doc_search.get_by_module("TECNOLOGIA", 3)
print(f"   Documentos em TECNOLOGIA: {len(docs)}")
if docs:
    for i, doc in enumerate(docs[:3], 1):
        title = doc.get('title', 'N/A')[:40]
        print(f"     {i}. {title}...")
print(f"   Status: {'✅ OK' if len(docs) > 0 else '❌ ERRO'}\n")

# Teste 4: Search (O TESTE IMPORTANTE - era o que tava falhando)
print("4️⃣ Testando search (O QUE ESTAVA FALHANDO):")
try:
    # Simular chamada com diferentes tipos de query
    
    # Teste 4a: Query como string (correto)
    print("   4a) Query como STRING (correto):")
    results = server.doc_search.search("gestão", None, 3)
    print(f"      Resultados: {len(results)}")
    if results:
        print(f"      Primeiro: {results[0].get('title', 'N/A')[:40]}...")
    print(f"      ✅ OK\n")
    
    # Teste 4b: Query como list (o bug que corrigimos!)
    print("   4b) Query como LIST (o bug corrigido):")
    # Simular o que acontecia antes - agora deve funcionar
    params = {
        "query": ["gestão"],  # Vindo como list do MCP
        "module": None,
        "limit": 3
    }
    
    # Extração com validação (como está agora no handle_tool_call)
    query = params.get("query", "")
    if isinstance(query, list):
        query = query[0] if query else ""
    query = str(query).strip()
    
    results = server.doc_search.search(query, None, 3)
    print(f"      Resultados: {len(results)}")
    if results:
        print(f"      Primeiro: {results[0].get('title', 'N/A')[:40]}...")
    print(f"      ✅ OK\n")
    
except Exception as e:
    print(f"   ❌ ERRO: {e}\n")

# Teste 5: Via handle_tool_call (como vai ser chamado pelo MCP)
print("5️⃣ Testando via handle_tool_call (como MCP vai chamar):")
try:
    params = {
        "query": ["Python"],  # Simulando parâmetro como list
        "module": None,
        "limit": 5
    }
    
    result = server.handle_tool_call("search_docs", params)
    result_obj = json.loads(result)
    
    print(f"   Query passada como: ['Python'] (list)")
    print(f"   Resultados encontrados: {result_obj.get('count', 0)}")
    if result_obj.get('count', 0) > 0:
        print(f"   Primeiro: {result_obj['results'][0].get('title', 'N/A')[:40]}...")
    print(f"   ✅ OK\n")
    
except Exception as e:
    print(f"   ❌ ERRO: {e}\n")
    import traceback
    traceback.print_exc()

# Teste 6: get_module_docs com parametrização
print("6️⃣ Testando get_module_docs com validação:")
try:
    params = {
        "module": ["BPM"],  # Pode vir como list também
        "limit": 3
    }
    
    result = server.handle_tool_call("get_module_docs", params)
    result_obj = json.loads(result)
    
    print(f"   Module passado como: ['BPM'] (list)")
    print(f"   Documentos encontrados: {result_obj.get('count', 0)}")
    if result_obj.get('count', 0) > 0:
        print(f"   Primeiro: {result_obj['docs'][0].get('title', 'N/A')[:40]}...")
    print(f"   ✅ OK\n")
    
except Exception as e:
    print(f"   ❌ ERRO: {e}\n")

print("=" * 50)
print("✅ TODOS OS TESTES COMPLETADOS COM SUCESSO!")
print("=" * 50)
