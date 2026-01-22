#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do MCP Server - Valida busca por notas de versão e títulos
"""

import json
import requests
from pathlib import Path


def test_mcp_search():
    """Testa o MCP server com buscas"""
    
    print("\n" + "="*80)
    print("🔍 TESTE DO MCP SERVER - Busca de Notas de Versão")
    print("="*80 + "\n")
    
    # Verificar se MCP está rodando
    mcp_url = "http://localhost:8000"
    
    print(f"1️⃣  Verificando se MCP está rodando em {mcp_url}\n")
    
    try:
        response = requests.get(f"{mcp_url}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"   ✓ MCP Server está ONLINE")
            print(f"   Status: {health.get('status')}")
            print(f"   Service: {health.get('service')}\n")
        else:
            print(f"   ✗ MCP retornou status {response.status_code}")
            print(f"   Instruções: docker-compose up -d\n")
            return
    except Exception as e:
        print(f"   ✗ Erro ao conectar: {e}")
        print(f"   Instruções: docker-compose up -d\n")
        return
    
    # TESTE 1: Buscar por "notas de versão"
    print(f"2️⃣  Testando busca por 'notas de versão'\n")
    
    try:
        response = requests.get(
            f"{mcp_url}/search",
            params={"q": "notas de versão"},
            timeout=5
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"   ✓ Busca retornou {len(results)} resultado(s)")
            
            if results:
                for i, result in enumerate(results[:3], 1):
                    print(f"\n   Resultado {i}:")
                    print(f"      Título: {result.get('title', 'N/A')[:60]}")
                    print(f"      URL: {result.get('url', 'N/A')[:70]}")
                    print(f"      Score: {result.get('_rankingScore', 'N/A')}")
            else:
                print(f"   ℹ️  Nenhum resultado encontrado")
        else:
            print(f"   ✗ Erro: {response.status_code}")
            print(f"   {response.text}")
    
    except Exception as e:
        print(f"   ✗ Erro: {e}")
    
    # TESTE 2: Buscar por "versão"
    print(f"\n3️⃣  Testando busca por 'versão'\n")
    
    try:
        response = requests.get(
            f"{mcp_url}/search",
            params={"q": "versão"},
            timeout=5
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"   ✓ Busca retornou {len(results)} resultado(s)")
            
            if results:
                for i, result in enumerate(results[:3], 1):
                    print(f"\n   Resultado {i}:")
                    print(f"      Título: {result.get('title', 'N/A')[:60]}")
        else:
            print(f"   ✗ Erro: {response.status_code}")
    
    except Exception as e:
        print(f"   ✗ Erro: {e}")
    
    # TESTE 3: Listar módulos
    print(f"\n4️⃣  Listando módulos indexados\n")
    
    try:
        response = requests.get(f"{mcp_url}/list_modules", timeout=5)
        
        if response.status_code == 200:
            modules = response.json()
            print(f"   ✓ {len(modules)} módulos encontrados:")
            
            for module in modules[:5]:
                print(f"      • {module}")
        else:
            print(f"   ✗ Erro: {response.status_code}")
    
    except Exception as e:
        print(f"   ✗ Erro: {e}")
    
    # TESTE 4: Estatísticas
    print(f"\n5️⃣  Verificando estatísticas\n")
    
    try:
        response = requests.get(f"{mcp_url}/stats", timeout=5)
        
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✓ Estatísticas do índice:")
            print(f"      • Total de documentos: {stats.get('total_documents', 0)}")
            print(f"      • Módulos: {stats.get('modules', 0)}")
            print(f"      • Fonte: {stats.get('source', 'N/A')}")
        else:
            print(f"   ✗ Erro: {response.status_code}")
    
    except Exception as e:
        print(f"   ✗ Erro: {e}")
    
    print("\n" + "="*80)
    print("✅ TESTES DO MCP CONCLUÍDOS")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_mcp_search()
