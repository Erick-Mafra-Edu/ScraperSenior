# MCP Server - Três Formas de Comunicação

## Resumo

Agora temos 3 formas de executar o MCP Server:

### 1. **MCP STDIO** (Melhor para VS Code)
- Arquivo: `mcp_server.py`
- Protocolo: JSON-RPC via stdin/stdout
- Comunicação: Baseada em linhas, sem buffering
- Melhor para: IDE (VS Code, Cursor)
- Config:
  ```json
  {
    "type": "stdio",
    "command": "python",
    "args": ["apps/mcp-server/mcp_server.py"]
  }
  ```

### 2. **MCP HTTP** (Novo! Conforme spec oficial)
- Arquivo: `mcp_server_http.py`
- Protocolo: Streamable HTTP Transport (MCP 2025-06-18)
- Comunicação: HTTP POST/GET com SSE
- Session Management com `Mcp-Session-Id`
- Melhor para: Aplicações web, APIs remotas
- Config:
  ```json
  {
    "type": "http",
    "url": "http://localhost:8000/mcp"
  }
  ```

### 3. **OpenAPI + MCP Dual-Mode** (Docker)
- Arquivo: `mcp_entrypoint_dual.py`
- Detecta automaticamente o modo
- MCP stdio funciona sempre
- OpenAPI HTTP opcional
- Melhor para: Docker containers

---

## Diferenças Técnicas

| Aspecto | STDIO | HTTP | Dual |
|---------|-------|------|------|
| **Inicialização** | Muito rápida | Requer HTTP server | Detecta ambiente |
| **Overhead** | Mínimo | Overhead HTTP | Varia |
| **Session** | Uma por processo | Múltiplas via Mcp-Session-Id | Uma por modo |
| **Streaming** | Linhas simples | SSE (Server-Sent Events) | Suporta ambos |
| **IDE Support** | ✅ Excelente | ✅ Excelente | ✅ Ambos |
| **Remoto** | ❌ Não | ✅ Sim | ✅ Sim (HTTP) |

---

## Implementação JSON-RPC

### STDIO (mcp_server.py)
```python
# Loop principal - lê linhas de stdin
while True:
    line = sys.stdin.readline()
    message = json.loads(line)
    
    # Processa método
    if method == "initialize":
        response = {...}
    elif method == "tools/list":
        response = {...}
    elif method == "tools/call":
        response = {...}
    
    # Envia resposta em uma linha
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()
```

### HTTP (mcp_server_http.py)
```python
# Endpoints HTTP conforme spec oficial
@app.post("/mcp")
async def mcp_post(request: Request) -> Response:
    # Valida headers: Accept, Mcp-Session-Id, MCP-Protocol-Version
    # Parse JSON-RPC do body
    # Retorna JSON ou SSE stream
    
    if method == "initialize":
        # Cria sessão
        session_id = uuid.uuid4()
        return Response(..., headers={"Mcp-Session-Id": session_id})

@app.get("/mcp")
async def mcp_get():
    # SSE stream para notificações do servidor
    # Retorna 405 se não implementado

@app.delete("/mcp")
async def mcp_delete():
    # Termina sessão
```

---

## Configuração no VS Code (mcp.json)

```json
{
  "servers": {
    "senior-docs-http": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    },
    "senior-docs-stdio": {
      "type": "stdio",
      "command": "python",
      "args": ["C:\\Users\\Digisys\\scrapyTest\\apps\\mcp-server\\mcp_server.py"]
    }
  }
}
```

---

## Como Usar

### Opção 1: HTTP Server Local
```bash
# Terminal 1: Iniciar HTTP server
python apps/mcp-server/mcp_server_http.py
# Listening on http://127.0.0.1:8000

# Terminal 2: Usar no VS Code
# Configure mcp.json para usar http://localhost:8000/mcp
```

### Opção 2: STDIO Direct
```bash
# Configure mcp.json para usar mcp_server.py direto
# VS Code iniciará o processo automaticamente
```

### Opção 3: Docker Dual-Mode
```bash
docker-compose up mcp-server
# Ambos MCP e HTTP rodam
```

---

## Testes

### Testar STDIO
```bash
# Simular comunicação JSON-RPC
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python apps/mcp-server/mcp_server.py
```

### Testar HTTP
```bash
# Iniciar server em outro terminal
python apps/mcp-server/mcp_server_http.py

# Em outro terminal:
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
```

---

## Recomendações

- **Para desenvolvimento local**: Use **STDIO** (mais simples)
- **Para produção/remoto**: Use **HTTP** (conforme spec, seguro com session management)
- **Para Docker**: Use **Dual-Mode** (detecta automaticamente)

Todos implementam o protocolo JSON-RPC MCP conforme especificação oficial!
