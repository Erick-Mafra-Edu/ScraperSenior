# ✅ Arquitetura Corrigida - MCP Server Python

## 🎯 Decisão: Remover mcp-openapi-server

### ❌ Por que NÃO usar mcp-openapi-server:

1. **Meilisearch não é uma API preparada**
   - Meilisearch é um serviço interno
   - Expor seu OpenAPI spec como ferramentas MCP não faz sentido
   - As queries precisam de lógica customizada

2. **Duplicação de funcionalidade**
   - `mcp-server` Python já existe e faz busca corretamente
   - `mcp-openapi-server` só repetiria a mesma coisa

3. **Sem valor agregado**
   - `mcp-openapi-server` é para APIs REST prontas com OpenAPI spec
   - Neste projeto, temos lógica customizada no Python

---

## ✅ Arquitetura Correta:

```
┌─────────────────────────────────────────────────────────┐
│              Claude Desktop / Cursor IDE                │
└────────────────────────┬────────────────────────────────┘
                         │
                    MCP Protocol (stdio)
                         │
                         ↓
      ┌──────────────────────────────────────┐
      │      mcp-server (Python)             │
      │  apps/mcp-server/mcp_server.py       │
      │  - search_docs()                     │
      │  - list_modules()                    │
      │  - get_module_docs()                 │
      │  - get_stats()                       │
      └────────────┬─────────────────────────┘
                   │
                   ↓
         ┌─────────────────────┐
         │   Meilisearch       │
         │   (Busca/Index)     │
         └─────────────────────┘
```

---

## 📦 Serviços no Docker Compose:

1. **meilisearch** - Search engine (port 7700)
2. **mcp-server** - Python MCP Server (stdio para IDE)
3. **scraper** - Indexador Python

---

## 🔧 Se precisar de HTTP REST:

**Opção**: Criar wrapper REST simples sobre `mcp-server` Python

Exemplo:
```python
# apps/mcp-server/http_server.py
from fastapi import FastAPI
from mcp_server import MCPServer

app = FastAPI()
mcp = MCPServer()

@app.post("/search")
def search(query: str, module: str = None):
    result = mcp.handle_tool_call("search_docs", {
        "query": query,
        "module": module
    })
    return json.loads(result)
```

Mas por enquanto, **MCP via stdio é suficiente** para Claude Desktop.

---

## ✅ Próximos Passos:

1. Docker compose atualizado (sem mcp-openapi-server)
2. Dockerfile simplificado (sem Node.js)
3. Usar `mcp-server` Python existente

**Status**: ✅ Pronto para usar!

```bash
# Apenas MCP (para Claude Desktop/Cursor)
docker-compose up -d meilisearch mcp-server scraper
```

---

## 📚 Referências:

- `apps/mcp-server/mcp_server.py` - Implementação MCP
- `docs/guides/DUAL_MCP_OPENAPI_GUIDE.md` - Será atualizado
- `docker-compose.yml` - Serviços simplificados
