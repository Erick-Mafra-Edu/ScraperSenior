#!/usr/bin/env python3
"""
MCP Client Test - Como VSCode/Claude usa o MCP
===============================================

Testa a comunicação JSON-RPC com o MCP Server
Simula como VSCode/Copilot Desktop se conecta
"""

import requests
import json
import sys


def make_jsonrpc_call(method, params=None, request_id=1):
    """Fazer chamada JSON-RPC 2.0 para o MCP Server"""
    
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": request_id
    }
    
    if params:
        payload["params"] = params
    
    print(f"\n→ JSON-RPC Call:")
    print(f"  Method: {method}")
    if params:
        print(f"  Params: {params}")
    print(f"  Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n← Response ({response.status_code}):")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  {json.dumps(data, indent=2, ensure_ascii=False)}")
            return data
        else:
            print(f"  Error: {response.text}")
            return None
    
    except Exception as e:
        print(f"  Error: {e}")
        return None


def test_mcp_protocol():
    """Testa o protocolo MCP como VSCode faria"""
    
    print("="*70)
    print("MCP PROTOCOL TESTING - Como VSCode/Copilot Desktop usa")
    print("="*70)
    
    # 1. Inicializar
    print("\n[1] Initialize - Primeira chamada do cliente MCP")
    init_result = make_jsonrpc_call("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "VSCode",
            "version": "1.0.0"
        }
    }, request_id=1)
    
    if not init_result or "error" in init_result:
        print("\n[ERROR] Initialize failed!")
        return False
    
    # 2. Listar ferramentas
    print("\n" + "="*70)
    print("[2] Tools/List - Descobrir ferramentas disponíveis")
    tools_result = make_jsonrpc_call("tools/list", {}, request_id=2)
    
    if tools_result and "result" in tools_result:
        tools = tools_result["result"].get("tools", [])
        print(f"\n✓ Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.get('name')}: {tool.get('description', 'N/A')}")
    
    # 3. Chamar ferramenta: search_docs
    print("\n" + "="*70)
    print("[3] Tools/Call - Buscar documentos (como Claude faria)")
    search_result = make_jsonrpc_call("tools/call", {
        "name": "search_docs",
        "arguments": {
            "query": "BI"
        }
    }, request_id=3)
    
    if search_result and "result" in search_result:
        result = search_result["result"]
        if isinstance(result, dict) and "content" in result:
            content = result["content"]
            if isinstance(content, list) and len(content) > 0:
                text = content[0].get("text", "")
                try:
                    data = json.loads(text)
                    hits = data.get("hits", [])
                    print(f"\n✓ Search returned {len(hits)} results:")
                    for i, hit in enumerate(hits[:3], 1):
                        print(f"  {i}. {hit.get('title', 'N/A')} (ID: {hit.get('id')})")
                except:
                    print(f"\n✓ Search returned results")
    
    # 4. Chamar ferramenta: list_modules
    print("\n" + "="*70)
    print("[4] Tools/Call - Listar módulos")
    modules_result = make_jsonrpc_call("tools/call", {
        "name": "list_modules",
        "arguments": {}
    }, request_id=4)
    
    if modules_result and "result" in modules_result:
        result = modules_result["result"]
        if isinstance(result, dict) and "content" in result:
            content = result["content"]
            if isinstance(content, list) and len(content) > 0:
                text = content[0].get("text", "")
                try:
                    data = json.loads(text)
                    modules = data.get("modules", [])
                    print(f"\n✓ Found {len(modules)} modules:")
                    for module in modules[:5]:
                        print(f"  - {module}")
                except:
                    print(f"\n✓ Modules listed")
    
    # 5. Chamar ferramenta: get_stats
    print("\n" + "="*70)
    print("[5] Tools/Call - Obter estatísticas")
    stats_result = make_jsonrpc_call("tools/call", {
        "name": "get_stats",
        "arguments": {}
    }, request_id=5)
    
    print("\n" + "="*70)
    print("MCP PROTOCOL TEST COMPLETE")
    print("="*70)
    
    return True


def test_rest_endpoints():
    """Testa endpoints REST (alternativa para testes simples)"""
    
    print("\n" + "="*70)
    print("REST ENDPOINTS (Alternative - Not used by VSCode)")
    print("="*70)
    
    print("\n[REST] GET /health")
    resp = requests.get("http://localhost:8000/health")
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
    
    print("\n[REST] POST /search")
    resp = requests.post(
        "http://localhost:8000/search",
        json={"query": "BI"},
        headers={"Content-Type": "application/json"}
    )
    print(f"  Status: {resp.status_code}")
    data = resp.json()
    if "results" in data:
        print(f"  Results: {len(data['results'])} documentos encontrados")


def main():
    print("\n" + "="*70)
    print("COMO VSCODE/COPILOT DESKTOP USA O MCP SERVER")
    print("="*70)
    print("""
Este teste mostra como VSCode/Copilot Desktop se comunica com o MCP Server:

1. VSCode envia uma requisição HTTP POST para http://localhost:8000/
2. No corpo, envia JSON-RPC 2.0 com o método desejado
3. O MCP Server processa e retorna o resultado no protocolo JSON-RPC

Protocolo JSON-RPC 2.0:
{
  "jsonrpc": "2.0",
  "method": "tools/list",      ← Método MCP
  "params": { ... },           ← Parâmetros opcionais
  "id": 1                       ← ID da requisição
}

Isto é diferente dos testes REST que fazíamos antes!
    """)
    
    # Testar JSON-RPC (o que VSCode usa)
    success = test_mcp_protocol()
    
    # Testar REST como alternativa
    print("\n" + "="*70)
    test_rest_endpoints()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
✓ VSCode/Copilot Desktop usa JSON-RPC 2.0 para se comunicar
✓ Primeira chamada é 'initialize' para descobrir capacidades
✓ Depois usa 'tools/list' para ver ferramentas disponíveis
✓ Depois chama 'tools/call' com o nome da ferramenta

Para integrar com VSCode:
1. Configure em ~/.copilot/claude_desktop_config.json:
   {
     "mcpServers": {
       "senior-docs": {
         "command": "python",
         "args": ["src/mcp_server_docker.py"]
       }
     }
   }

2. VSCode vai conectar usando SSE ou stdio
3. Comunicação será feita via JSON-RPC 2.0
    """)


if __name__ == "__main__":
    main()
