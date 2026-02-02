# OpenAPI Server - Guia de Implementação e Uso

## 📋 Visão Geral

O MCP Server Senior Documentation foi convertido para um servidor **Dual-Mode** que suporta tanto:

1. **MCP Mode (stdio)** - Para integração com IDEs (Claude Desktop, Cursor)
2. **OpenAPI Mode (HTTP REST)** - Para acesso via API com documentação Swagger automática
3. **Dual Mode** - Ambos os modos funcionando simultaneamente

---

## 🏗️ Arquitetura Implementada

### Arquivos Criados

```
apps/mcp-server/
├── mcp_server.py                # MCP Server original (stdio)
├── mcp_server_docker.py         # Variante HTTP
├── openapi_adapter.py           # ✨ NOVO: Adapter FastAPI/OpenAPI
├── mcp_entrypoint_dual.py       # ✨ NOVO: Entrypoint dual-mode
└── __init__.py

Dockerfile.mcp                    # Atualizado com FastAPI/Uvicorn
docker-compose.yml               # Atualizado com modo OpenAPI
```

### Stack Tecnológico

```
┌─────────────────────────────────────────────────────────────┐
│                      Clientes                                │
│  IDE (VS Code/Cursor)  │  REST API Clients  │  Browser       │
└────────────┬────────────────────┬──────────────────┬──────────┘
             │                    │                  │
             │ stdio (MCP)        │ HTTP             │ HTTP
             │                    │                  │
┌────────────▼────────────────────▼──────────────────▼──────────┐
│         MCP/OpenAPI Dual-Mode Server                          │
│                                                               │
│  ┌─────────────────┐      ┌────────────────────────────────┐  │
│  │   MCP Mode      │      │   OpenAPI Mode (FastAPI)       │  │
│  │  (stdio)        │      │                                │  │
│  │                 │      │  GET /health                   │  │
│  │ SeniorDocMCP    │      │  POST /search                  │  │
│  │ (json-rpc)      │      │  GET /modules                  │  │
│  │                 │      │  GET /modules/{name}           │  │
│  └────────┬────────┘      │  GET /stats                    │  │
│           │               │                                │  │
│           │   ┌───────────┤  /docs (Swagger UI)            │  │
│           │   │           │  /redoc (ReDoc UI)             │  │
│           │   │           │  /openapi.json (Schema)        │  │
│           └───┼───────────┘                                │  │
│               │                                             │  │
│  ┌────────────▼───────────────────────────────────────┐  │
│  │        Núcleo Compartilhado (SeniorDocMCP)         │  │
│  │                                                    │  │
│  │  - search(query, module, limit, offset)           │  │
│  │  - get_modules()                                  │  │
│  │  - get_module_docs(module)                        │  │
│  │  - get_stats()                                    │  │
│  │  - health_check()                                 │  │
│  └────────────┬───────────────────────────────────────┘  │
│               │                                           │
└───────────────┼───────────────────────────────────────────┘
                │
                ↓
         ┌──────────────┐
         │  Meilisearch │ (port 7700)
         │  (Search)    │
         └──────────────┘
```

---

## 🚀 Como Usar no Docker

### 1. **OpenAPI Mode (Padrão - Recomendado)**

Modo REST API com documentação Swagger automática.

```bash
# Iniciar container em modo OpenAPI
docker-compose up -d mcp-server

# Acessar a API
curl http://localhost:8000/health
curl http://localhost:8000/stats

# Documentação interativa
# Swagger UI:  http://localhost:8000/docs
# ReDoc:       http://localhost:8000/redoc
# Schema:      http://localhost:8000/openapi.json

# Ver logs
docker-compose logs -f mcp-server
```

### 2. **MCP Mode (Para IDE)**

Modo stdio para integração com Claude Desktop/Cursor.

```bash
# Iniciar em modo MCP
docker-compose up -d --build
docker exec senior-docs-mcp-server python apps/mcp-server/mcp_entrypoint_dual.py --mode mcp

# Ou via docker-compose com override
export MCP_MODE=mcp
docker-compose up -d mcp-server
```

### 3. **Dual Mode (Ambos Simultaneamente)**

MCP + OpenAPI rodando juntos.

```bash
# Iniciar em modo dual
export MCP_MODE=both
docker-compose up -d mcp-server

# Ambos funcionam:
# - MCP via stdio (connect com IDE)
# - OpenAPI em http://localhost:8000
```

### 4. **Build da Imagem**

```bash
# Build local
docker build -f Dockerfile.mcp -t senior-docs-mcp:latest .

# Build via docker-compose
docker-compose build mcp-server

# Com cache limpo
docker-compose build --no-cache mcp-server
```

---

## 📡 Exemplos de Requisições

### Busca Simples

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "como configurar",
    "limit": 10
  }'
```

### Busca com Filtro de Módulo

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "banco de dados",
    "module": "RH",
    "limit": 5
  }'
```

### Listar Módulos

```bash
curl -X GET http://localhost:8000/modules
```

### Obter Documentação de Módulo

```bash
curl -X GET http://localhost:8000/modules/RH
```

### Obter Estatísticas

```bash
curl -X GET http://localhost:8000/stats
```

### Health Check

```bash
curl -X GET http://localhost:8000/health
```

---

## 🔄 Resposta em Python

```python
import httpx

# Cliente HTTP
client = httpx.AsyncClient(base_url="http://localhost:8000")

# Busca
response = await client.post("/search", json={
    "query": "configurar banco",
    "module": "RH",
    "limit": 10
})
results = response.json()

print(f"Total encontrado: {results['total']}")
for doc in results['results']:
    print(f"- {doc['title']} ({doc['module']})")

# Modules
modules = await client.get("/modules")
print(modules.json())

# Stats
stats = await client.get("/stats")
print(stats.json())
```

---

## 🌐 Integração em Aplicações Web

### Exemplo com JavaScript/Node.js

```javascript
// Buscar documentação
async function searchDocs(query, module) {
  const response = await fetch('http://localhost:8000/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, module, limit: 10 })
  });
  
  return await response.json();
}

// Obter módulos
async function getModules() {
  const response = await fetch('http://localhost:8000/modules');
  return await response.json();
}

// Usar
const results = await searchDocs('como configurar', 'RH');
console.log(results.results);
```

### Exemplo com React

```jsx
import { useState, useEffect } from 'react';

function DocSearch() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const search = async (query) => {
    setLoading(true);
    const res = await fetch('http://localhost:8000/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, limit: 10 })
    });
    
    const data = await res.json();
    setResults(data.results);
    setLoading(false);
  };

  return (
    <div>
      <input 
        onChange={(e) => search(e.target.value)}
        placeholder="Buscar documentação..."
      />
      
      {loading && <p>Carregando...</p>}
      
      <ul>
        {results.map(doc => (
          <li key={doc.id}>
            <h3>{doc.title}</h3>
            <p>{doc.content_preview}</p>
            <small>{doc.module}</small>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default DocSearch;
```

---

## 📊 Modelos OpenAPI (Pydantic)

### SearchRequest
```python
{
  "query": "string",           # Obrigatório
  "module": "string",          # Opcional
  "limit": 10,                 # Padrão: 10, Máximo: 100
  "offset": 0                  # Padrão: 0
}
```

### SearchResponse
```python
{
  "success": true,
  "query": "string",
  "total": 42,                 # Total de resultados
  "limit": 10,
  "offset": 0,
  "results": [
    {
      "id": "doc-1",
      "title": "string",
      "module": "RH",
      "breadcrumb": "string",
      "content_preview": "string",
      "content": "string",     # Opcional
      "html": "string",       # Opcional
      "url": "string",
      "score": 0.95,          # Score de relevância
      "metadata": {}
    }
  ],
  "execution_time_ms": 45.2
}
```

### ModulesResponse
```python
{
  "success": true,
  "total_modules": 15,
  "modules": [
    {
      "name": "RH",
      "doc_count": 1234,
      "description": "string"
    }
  ]
}
```

### StatsResponse
```python
{
  "success": true,
  "total_documents": 1866,
  "total_modules": 15,
  "modules": {
    "RH": 234,
    "Fiscal": 456,
    ...
  },
  "index_name": "senior_docs",
  "meilisearch_version": "1.11.0",
  "last_indexed": "2024-02-02T10:30:00Z"
}
```

---

## 🔐 Segurança e CORS

### Configuração Atual

```python
# Em openapi_adapter.py
CORSMiddleware(
    allow_origins=["*"],  # Em produção, restringir!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Para Produção

```python
# Restringir origens
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://seu-dominio.com",
        "https://app.seu-dominio.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

### Autenticação (Futuro)

```python
# Adicionar autenticação via bearer token
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/search")
async def search_documents(
    request: SearchRequest,
    credentials: HTTPAuthCredentials = Depends(security)
):
    # Validar token
    if not validate_token(credentials.credentials):
        raise HTTPException(status_code=401)
    
    # Executar busca...
```

---

## 📝 Variáveis de Ambiente

```bash
# Modo de operação
MCP_MODE=openapi              # openapi|mcp|both

# Configuração OpenAPI
OPENAPI_HOST=0.0.0.0          # Host para escutar
OPENAPI_PORT=8000             # Porta HTTP

# Meilisearch
MEILISEARCH_URL=http://meilisearch:7700
MEILISEARCH_KEY=your_api_key

# Python
PYTHONUNBUFFERED=1
LOG_LEVEL=info                 # debug|info|warning|error
```

---

## 🧪 Testes

### Health Check

```bash
docker-compose run --rm mcp-server \
  curl -f http://meilisearch:7700/health
```

### Teste de Busca

```bash
docker-compose exec mcp-server \
  curl -X POST http://localhost:8000/search \
    -H "Content-Type: application/json" \
    -d '{"query":"test"}'
```

### Teste de Performance

```python
import asyncio
import time
from httpx import AsyncClient

async def test_search_performance():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        start = time.time()
        
        for i in range(100):
            await client.post("/search", json={"query": "teste"})
        
        elapsed = time.time() - start
        print(f"100 requests em {elapsed:.2f}s ({elapsed/100*1000:.1f}ms por request)")

asyncio.run(test_search_performance())
```

---

## 🔧 Troubleshooting

### Erro: Connection refused

```bash
# Verificar se container está rodando
docker-compose ps

# Verificar logs
docker-compose logs mcp-server

# Testar conectividade
docker-compose exec mcp-server curl -f http://meilisearch:7700/health
```

### Erro: Module not found

```bash
# Atualizar imports
export PYTHONPATH=/app:$PYTHONPATH

# Verificar estrutura
docker-compose exec mcp-server ls -la apps/mcp-server/
```

### Erro: Meilisearch unreachable

```bash
# Verificar Meilisearch
docker-compose exec meilisearch curl -f http://localhost:7700/health

# Reiniciar
docker-compose down
docker-compose up -d
```

### Performance lenta

```bash
# Verificar índices
docker-compose logs meilisearch | grep "indexing"

# Reindexar
docker-compose exec scraper python scripts/indexing/reindex_all_docs.py

# Monitorar recursos
docker stats senior-docs-mcp-server
```

---

## 📚 Documentação Adicional

- **MCP Spec**: https://modelcontextprotocol.io/
- **FastAPI**: https://fastapi.tiangolo.com/
- **OpenAPI**: https://swagger.io/specification/
- **Meilisearch**: https://docs.meilisearch.com/

---

## 🎯 Próximos Passos

- [ ] Adicionar autenticação via JWT
- [ ] Implementar rate limiting
- [ ] Adicionar cache de resultados
- [ ] Suportar filtros avançados (AND, OR, NOT)
- [ ] Implementar webhooks para índice atualizado
- [ ] Adicionar GraphQL endpoint

---

## 💬 Suporte

Para dúvidas ou problemas, verifique:

1. `docker-compose logs mcp-server`
2. `docker-compose logs meilisearch`
3. `http://localhost:8000/docs` - Documentação Swagger
4. `MCP_ARCHITECTURE_CORRECTED.md` - Decisões arquiteturais

---

**Versão**: 2.0.0 (Dual-Mode)  
**Atualizado**: 2024-02-02  
**Status**: ✅ Production-Ready
