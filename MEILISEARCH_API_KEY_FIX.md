# 🔧 Recuperação de Erro de API Key do Meilisearch

## 📋 Problema Identificado

**Erro**: `403 - invalid_api_key` ao tentar conectar Docker Scraper com Meilisearch

**Causa**: Inconsistência entre a chave de API configurada no Meilisearch e as chaves usadas pelos serviços Python

---

## 🔑 Chaves Envolvidas

### Antes (❌ Incorreto):
```
docker-compose.yml:
  - MEILI_MASTER_KEY: 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa ✅
  - MEILISEARCH_KEY (default): meilisearch_master_key ❌ (INVÁLIDA!)

Python fallbacks:
  - mcp_server_docker.py: "meilisearch_master_key" ❌
  - docker_entrypoint.py: "meilisearch_master_key" ❌
  - docker_orchestrator.py: "meilisearch_master_key" ❌
  - manual_indexing.py: "meilisearch_master_key_change_me" ❌
  - analyze_indexation.py: "meilisearch_master_key" ❌
```

### Depois (✅ Correto):
```
Arquivo .env (NOVO):
  MEILISEARCH_KEY=5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa

docker-compose.yml:
  - MEILI_MASTER_KEY: ${MEILISEARCH_KEY:-5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa} ✅
  - MEILISEARCH_KEY (todos os serviços): ${MEILISEARCH_KEY:-...} ✅

Python fallbacks (TODOS CORRIGIDOS):
  - Usam fallback: 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa ✅
  - Leem de $MEILISEARCH_KEY se disponível ✅
```

---

## ✅ Arquivos Corrigidos

| Arquivo | Alteração |
|---------|-----------|
| `.env` | CRIADO com chave correta |
| `mcp_server_docker.py` | Fallback corrigido |
| `docker_entrypoint.py` | Usa env var com fallback correto |
| `infra/docker/docker_entrypoint.py` | Usa env var com fallback correto |
| `docker_orchestrator.py` | Usa env var com fallback correto |
| `manual_indexing.py` | Usa env var com fallback correto |
| `analyze_indexation.py` | Usa env var com fallback correto |

---

## 🚀 Como Recuperar Agora

### Passo 1: Garantir que `.env` está presente
```bash
# Windows PowerShell
type .env

# Linux/Mac
cat .env
```

Deve conter:
```
MEILISEARCH_KEY=5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa
```

### Passo 2: Derrubar containers antigos
```bash
# Remove containers e volumes antigos
docker-compose down -v

# Ou se usar podman
podman-compose down -v
```

### Passo 3: Reconstruir e iniciar
```bash
# Build fresh without cache
docker-compose build --no-cache

# Iniciar todos os serviços
docker-compose up -d

# Verificar logs
docker-compose logs -f senior-docs-mcp-server
```

### Passo 4: Verificar Meilisearch conectou
```bash
# Verifique se Meilisearch está saudável
curl http://localhost:7700/health

# Esperado: {"status":"available"}
```

### Passo 5: Testar a API
```bash
# Health check da API
curl http://localhost:8000/health

# Esperado: {"status":"healthy",...}

# Listar módulos
curl http://localhost:8000/modules

# Esperado: {"success":true,"modules":[...]}
```

---

## 🔍 Verificação de Status

### Logs do MCP Server
```bash
docker logs senior-docs-mcp-server | grep -i "meilisearch\|error\|healthy"
```

✅ Esperado:
```
[INFO] Meilisearch saudável
[INFO] 855 documentos indexados
[INFO] Health check: OK
```

❌ Se ainda vir erro 403:
```
1. Verifique se .env foi carregado: docker inspect senior-docs-mcp-server | grep MEILISEARCH_KEY
2. Reconstrua: docker-compose build --no-cache
3. Reinicie: docker-compose restart
```

### Logs do Scraper
```bash
docker logs senior-docs-scraper | tail -50
```

✅ Esperado: Sem erros de autenticação

---

## 📊 Diagnóstico: O que mudou

### Cenário Anterior (Quebrado):

```
User request → MCP Server
                    ↓
            Reads: MEILISEARCH_KEY env var
                    ↓
            Not found → Uses fallback: "meilisearch_master_key" ❌
                    ↓
            Tenta GET http://meilisearch:7700/indexes
            Headers: Authorization: Bearer meilisearch_master_key ❌
                    ↓
            Meilisearch verifica:
            - Minha MASTER_KEY é: 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa
            - Recebida: "meilisearch_master_key"
            - Não combinam! ❌
                    ↓
            403 Unauthorized - invalid_api_key
```

### Cenário Correto (Agora):

```
User request → MCP Server
                    ↓
            Reads: MEILISEARCH_KEY env var
                    ↓
            Found in .env: 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa ✅
                    ↓
            Tenta GET http://meilisearch:7700/indexes
            Headers: Authorization: Bearer 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa ✅
                    ↓
            Meilisearch verifica:
            - Minha MASTER_KEY é: 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa
            - Recebida: 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa
            - Combinam! ✅
                    ↓
            200 OK - Procede com requisição
```

---

## 🎯 Próximos Passos

### Imediato (Agora):
1. ✅ Arquivos corrigidos
2. ⏳ Docker rebuild necessário
3. ⏳ Teste de conectividade

### Verificação:
```bash
# 1. Verifique que Meilisearch tem 855 docs indexados
curl -H "Authorization: Bearer 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa" \
     http://localhost:7700/indexes/documentation/stats

# 2. Verifique que a API consegue buscar
curl -X POST http://localhost:8000/search \
     -H "Content-Type: application/json" \
     -d '{"query":"como configurar"}'
```

---

## 💾 Backup de Configuração

Se precisar revert:
```bash
# A chave pode ser customizada no .env
# Mas DEVE ser a mesma em:
# 1. docker-compose.yml (MEILI_MASTER_KEY)
# 2. .env (MEILISEARCH_KEY)
# 3. Todos os serviços (lerem de MEILISEARCH_KEY ou usarem fallback)

# Nunca use:
# - "meilisearch_master_key" (inválido)
# - "meilisearch_master_key_change_me" (inválido)
# - Strings aleatórias (não combinam com Meilisearch)
```

---

## ✨ Validação Final

Execute este script para verificar tudo:

```bash
#!/bin/bash

echo "=== Meilisearch Health ==="
curl -s http://localhost:7700/health | jq .

echo -e "\n=== API Health ==="
curl -s http://localhost:8000/health | jq .

echo -e "\n=== API Stats ==="
curl -s http://localhost:8000/stats | jq .

echo -e "\n=== Docker Env ==="
docker exec senior-docs-mcp-server env | grep MEILISEARCH

echo -e "\n✅ Se todos retornaram dados, está funcionando!"
```

---

## 📚 Referências

- **Meilisearch Docs**: https://docs.meilisearch.com/learn/security/master_key.html
- **Docker Compose Env**: https://docs.docker.com/compose/environment-variables/
- **OpenAPI Config**: `openapi.json` - 855 documentos, 7 endpoints
