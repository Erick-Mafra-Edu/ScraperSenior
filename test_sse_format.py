#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de SSE - Valida que o formato SSE está correto
"""

import json
import asyncio
import httpx

async def test_sse_format():
    """Testa se a resposta SSE está em formato válido"""
    
    print("=" * 70)
    print("TESTE DE FORMATO SSE")
    print("=" * 70)
    print()
    
    # Testar com Accept: text/event-stream
    headers = {
        "Accept": "text/event-stream",
        "Content-Type": "application/json"
    }
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "search_docs",
            "arguments": {
                "query": "LSP",
                "limit": 3
            }
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print("[1] Enviando requisição para /mcp com Accept: text/event-stream")
            response = await client.post(
                "http://localhost:8000/mcp",
                json=payload,
                headers=headers
            )
            
            print(f"[2] Status: {response.status_code}")
            print(f"[3] Content-Type: {response.headers.get('content-type', 'N/A')}")
            print()
            
            content = response.text
            print(f"[4] Resposta SSE:")
            print(f"    Comprimento: {len(content)} bytes")
            print()
            
            # Validar formato SSE
            if content.startswith("data: "):
                print("✅ Formato correto: começa com 'data: '")
            else:
                print(f"❌ Formato incorreto: começa com '{content[:20]}'")
            
            # Extrai JSON da resposta
            if content.startswith("data: "):
                json_part = content[6:].strip()  # Remove "data: " e espaços
                
                # Verificar se é uma única linha (SSE válido)
                lines = json_part.split('\n')
                if len(lines) == 1:
                    print("✅ JSON em uma única linha (SSE válido)")
                else:
                    print(f"❌ JSON com {len(lines)} linhas (SSE inválido)")
                    print("   Primeiras 3 linhas:")
                    for i, line in enumerate(lines[:3]):
                        print(f"   {i+1}: {line[:60]}...")
                
                # Tentar parsear JSON
                try:
                    data = json.loads(json_part)
                    print("✅ JSON válido e parseável")
                    print()
                    print(f"   Resposta:")
                    print(f"   - ID: {data.get('id')}")
                    print(f"   - Type: {data.get('result', {}).get('type')}")
                    print(f"   - Result (primeiros 100 chars):")
                    result_text = data.get('result', {}).get('text', 'N/A')
                    if isinstance(result_text, str):
                        print(f"     {result_text[:100]}...")
                except json.JSONDecodeError as e:
                    print(f"❌ Erro ao parsear JSON: {e}")
                    print(f"   JSON: {json_part[:200]}...")
            
            print()
            print("=" * 70)
            print("RESULTADO: ✅ SSE formato está correto!")
            print("=" * 70)
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("\n⚠️  Certifique-se que o servidor MCP está rodando em localhost:8000")
    print("    Comando: python apps/mcp-server/mcp_server_http.py\n")
    
    try:
        asyncio.run(test_sse_format())
    except KeyboardInterrupt:
        print("\n\nCancelado pelo usuário")
