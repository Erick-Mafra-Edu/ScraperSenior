# 🚀 OpenAPI Server - Quick Start Guide

## Overview

O projeto agora possui:
- ✅ `openapi.json` - Especificação OpenAPI completa
- ✅ Integração com FastAPI para hostagem
- ✅ Endpoints que servem o schema OpenAPI
- ✅ Documentação Swagger e ReDoc automáticas

## Installation

```bash
# Instalar dependências (se ainda não estiverem)
pip install fastapi uvicorn pydantic

# Ou via requirements.txt
pip install -r requirements.txt
```

## Running the Server

### Option 1: Using the startup script (Recomendado)

```bash
# Desenvolvimento com reload automático
python run_openapi_server.py --reload

# Produção
python run_openapi_server.py --host 0.0.0.0 --port 8000

# Com logging detalhado
python run_openapi_server.py --log-level debug
```

### Option 2: Direct FastAPI adapter

```bash
python apps/mcp-server/openapi_adapter.py
```

### Option 3: Docker

```bash
docker-compose up openapi-server
# ou
docker build -f Dockerfile.mcp -t mcp-server .
docker run -p 8000:8000 mcp-server
```

## Available Endpoints

### 📊 API Documentation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Info da API |
| `/health` | GET | Health check |
| `/search` | POST | Buscar documentos |
| `/modules` | GET | Listar módulos |
| `/modules/{module_name}` | GET | Docs de um módulo |
| `/stats` | GET | Estatísticas |

### 📖 Interactive Documentation

| URL | Tool |
|-----|------|
| `http://localhost:8000/docs` | **Swagger UI** (recomendado) |
| `http://localhost:8000/redoc` | **ReDoc** (visual alternativo) |

### 📋 OpenAPI Schema

| URL | Source |
|-----|--------|
| `http://localhost:8000/openapi.json` | FastAPI auto-gerado |
| `http://localhost:8000/api/openapi.json` | Arquivo `openapi.json` (disco) |

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# List modules
curl http://localhost:8000/modules

# Search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "banco de dados",
    "module": "RH",
    "limit": 10
  }'

# Get stats
curl http://localhost:8000/stats
```

### Using Python

```python
import httpx
import asyncio

async def test_api():
    async with httpx.AsyncClient() as client:
        # Health check
        response = await client.get("http://localhost:8000/health")
        print("Health:", response.json())
        
        # Search
        response = await client.post(
            "http://localhost:8000/search",
            json={
                "query": "configurar",
                "limit": 5
            }
        )
        print("Search results:", response.json())

asyncio.run(test_api())
```

### Using Postman

1. Abrir Postman
2. Importar a URL: `http://localhost:8000/openapi.json`
3. Automáticamente importa todos os endpoints
4. Testar diretamente da interface

## Environment Variables

```bash
# Server
export HOST=0.0.0.0
export PORT=8000
export LOG_LEVEL=info
export RELOAD=false

# Meilisearch
export MEILISEARCH_URL=http://localhost:7700
export MEILISEARCH_KEY=meilisearch_master_key
```

## Project Structure

```
.
├── openapi.json                          # ✨ Especificação OpenAPI (NOVO)
├── run_openapi_server.py                 # ✨ Script para iniciar servidor
├── apps/
│   └── mcp-server/
│       ├── mcp_server.py                 # MCP Server (stdio)
│       ├── openapi_adapter.py            # ✨ FastAPI adapter (atualizado)
│       └── mcp_config.json
├── docs/
│   └── guides/
│       └── OPENAPI_QUICKSTART.txt        # Este arquivo
└── ...
```

## Arquitetura

```
┌─────────────────────────────────────────┐
│         FastAPI Server (8000)           │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │  OpenAPI Adapter                  │  │
│  │  - Swagger UI (/docs)             │  │
│  │  - ReDoc (/redoc)                 │  │
│  │  - OpenAPI schema endpoints       │  │
│  └───────────────────────────────────┘  │
│           ▼                              │
│  ┌───────────────────────────────────┐  │
│  │  MCP Server (Core)                │  │
│  │  - Search logic                   │  │
│  │  - Module retrieval               │  │
│  │  - Stats & health                 │  │
│  └───────────────────────────────────┘  │
│           ▼                              │
│  ┌───────────────────────────────────┐  │
│  │  Meilisearch (7700)               │  │
│  │  - Index search                   │  │
│  │  - Full-text search               │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Troubleshooting

### Error: "Arquivo openapi.json não encontrado"

- Verificar se `openapi.json` existe na raiz do projeto
- Alternativa: o servidor usará o schema auto-gerado pelo FastAPI
- Ambos funcionam igualmente

### Error: "Meilisearch indisponível"

```bash
# Verificar se Meilisearch está rodando
curl http://localhost:7700/health

# Se não estiver, iniciar via Docker
docker-compose up -d meilisearch
```

### Porta já em uso

```bash
# Mudar porta
python run_openapi_server.py --port 8001

# Ou liberar porta (Linux/Mac)
lsof -ti:8000 | xargs kill -9
```

## Next Steps

1. ✅ Servidor rodando e hostando openapi.json
2. 📝 Teste endpoints via Swagger UI
3. 🔍 Customize o schema conforme necessário
4. 🐳 Deploy em produção via Docker
5. 🔌 Integre com suas aplicações clientes

## Documentação Adicional

- [OpenAPI 3.1.0 Spec](https://spec.openapis.org/oas/v3.1.0)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Meilisearch Docs](https://docs.meilisearch.com/)
- [MCP Protocol](https://modelcontextprotocol.io/)

---

**Última atualização**: 2026-02-03
