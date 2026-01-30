#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar se a configuração do MCP Server está funcionando corretamente
"""

import sys
import json
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_server import load_config, SeniorDocumentationMCP

def test_config_loading():
    """Testa o carregamento da configuração"""
    print("=" * 60)
    print("TESTE 1: Carregamento de Configuração")
    print("=" * 60)
    
    try:
        config = load_config()
        print("[✓] Configuração carregada com sucesso!")
        print("\nConteúdo da configuração:")
        print(json.dumps(config, indent=2, ensure_ascii=False))
        return True
    except Exception as e:
        print(f"[✗] Erro ao carregar configuração: {e}")
        return False

def test_mcp_initialization():
    """Testa a inicialização do MCP Server"""
    print("\n" + "=" * 60)
    print("TESTE 2: Inicialização do MCP Server")
    print("=" * 60)
    
    try:
        mcp = SeniorDocumentationMCP()
        print("[✓] MCP Server inicializado com sucesso!")
        print(f"  - URL Meilisearch: {mcp.meilisearch_url}")
        print(f"  - Index Name: {mcp.index_name}")
        print(f"  - Modo Utilizado: {'Local (JSONL)' if mcp.use_local else 'Meilisearch'}")
        
        if mcp.use_local:
            print(f"  - Documentos Carregados: {len(mcp.local_documents)}")
        
        return True
    except Exception as e:
        print(f"[✗] Erro ao inicializar MCP Server: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_functionality():
    """Testa a funcionalidade de busca"""
    print("\n" + "=" * 60)
    print("TESTE 3: Funcionalidade de Busca")
    print("=" * 60)
    
    try:
        mcp = SeniorDocumentationMCP()
        
        # Realizar uma busca de teste
        results = mcp.search("CRM", limit=3)
        
        print(f"[✓] Busca realizada com sucesso!")
        print(f"  - Query: 'CRM'")
        print(f"  - Resultados encontrados: {len(results)}")
        
        if results:
            print("\n  Primeiros resultados:")
            for i, result in enumerate(results[:2], 1):
                print(f"    {i}. {result.get('titulo', 'N/A')} (Score: {result.get('score', 'N/A')})")
        
        return True
    except Exception as e:
        print(f"[✗] Erro durante a busca: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " TESTE COMPLETO - MCP SERVER CONFIGURATION ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    
    tests = [
        ("Carregamento de Configuração", test_config_loading),
        ("Inicialização do MCP Server", test_mcp_initialization),
        ("Funcionalidade de Busca", test_search_functionality),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[✓]" if result else "[✗]"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM! O MCP Server está pronto para usar.")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os erros acima.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
