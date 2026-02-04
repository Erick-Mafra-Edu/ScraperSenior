# Fluxo de Chaves do Meilisearch - Corrigido

## 📋 Configuração Corrigida (Feb 4, 2026)

### Chave Padrão
```
5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa
```

---

## 🔄 Fluxo Completo (Scraping → Indexação)

### 1. **Docker Compose** (Orquestrador Principal)
```yaml
environment:
  MEILISEARCH_KEY: ${MEILISEARCH_KEY:-5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa}
```

**Status**: ✅ CORRETO - Usa variável de ambiente com fallback

---

### 2. **Meilisearch Service** (Banco de Busca)
```yaml
# docker-compose.yml linha 42
MEILI_MASTER_KEY: ${MEILISEARCH_KEY:-5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa}
```

**Status**: ✅ CORRETO - Recebe chave via variável de ambiente

---

### 3. **MCP Server** (Aplicação)
```yaml
# docker-compose.yml linha 107
MEILISEARCH_KEY: ${MEILISEARCH_KEY:-5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa}
```

**Python Code** (`apps/mcp-server/openapi_adapter.py`):
```python
api_key = api_key or os.getenv(
    "MEILISEARCH_KEY",
    "5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa"
)
```

**Status**: ✅ CORRETO - Lê de variável de ambiente

---

### 4. **Scraper Service** (Extração de Dados)
```yaml
# docker-compose.yml linha 165
MEILISEARCH_KEY: ${MEILISEARCH_KEY:-5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa}
```

**Docker Entrypoint** (`docker_entrypoint.py`):
```python
meilisearch_key=os.getenv("MEILISEARCH_KEY", "5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa")
```

**Status**: ✅ CORRETO - Lê de variável de ambiente

---

### 5. **Post-Scraping Indexation** (Indexação Final)
**Arquivo**: `post_scraping_indexation.py` (raiz do projeto)

**Status**: ✅ CORRETO (CORRIGIDO)
```python
MEILISEARCH_KEY = os.getenv("MEILISEARCH_KEY", "5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa")
```

---

## 📊 Resumo das Alterações

### Arquivos Corrigidos ✅
1. ✅ `post_scraping_indexation.py` (raiz) - POST-SCRAPING INDEXATION
2. ✅ `scripts/indexing/post_scraping_indexation.py` - Versão alternativa
3. ✅ `test_search.py`
4. ✅ `test_meilisearch_direct.py`
5. ✅ `tmp/scripts/debug_mcp.py`
6. ✅ `tmp/scripts/setup_meilisearch_index.py`
7. ✅ `tmp/scripts/quick_test.py`

### Arquivos que Já Estavam Corretos ✅
- ✅ `docker-compose.yml` - Todos os serviços (meilisearch, mcp-server, scraper)
- ✅ `docker_entrypoint.py` - Passa chave corretamente
- ✅ `Dockerfile` - Sem hardcoding
- ✅ `apps/mcp-server/openapi_adapter.py` - Lê da env
- ✅ `scrape_and_index_all.py` - Lê da env

---

## 🚀 Como Usar

### Iniciar com Chave Padrão
```bash
docker-compose up -d meilisearch mcp-server scraper
```

### Iniciar com Chave Customizada
```bash
MEILISEARCH_KEY="sua-chave-aqui" docker-compose up -d meilisearch mcp-server scraper
```

### Verificar Variáveis
```bash
docker-compose config | grep MEILISEARCH_KEY
```

---

## ✅ Validação do Fluxo

```
┌─────────────────────────────────────────────────────────────────┐
│                    Docker-Compose (Orquestrador)               │
│        MEILISEARCH_KEY=${MEILISEARCH_KEY:-default}             │
└────────────┬──────────────────────┬──────────────────┬─────────┘
             │                      │                  │
             ▼                      ▼                  ▼
      ┌────────────┐         ┌──────────┐      ┌──────────────┐
      │ Meilisearch│◄────────│MCP Server│      │   Scraper    │
      │ (7700)     │  Query  │ (8000)   │      │  (indexação) │
      └────────────┘         └──────────┘      └──────────────┘
             ▲                                         │
             └─────────────────────────────────────────┘
                    (post_scraping_indexation.py)
                    Indexa documentos no Meilisearch
```

---

## 🔍 Rastreamento de Erros

Se você vir erro:
```
Error code: invalid_api_key
Error message: The provided API key is invalid
```

**Verifique**:
1. A chave no docker-compose está igual em TODOS os serviços
2. O serviço Meilisearch rodou com a mesma chave antes
3. Use: `docker-compose config | grep -i meilisearch_key`

---

**Último Update**: 2026-02-04 | Status: ✅ FULLY RESOLVED
