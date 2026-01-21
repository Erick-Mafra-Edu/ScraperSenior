# Docker - MCP Server

Imagem Docker para o MCP Server com integração completa do Meilisearch.

## Build da Imagem

```bash
# Build local
docker build -f Dockerfile.mcp -t senior-docs-mcp:latest .

# Build com tag versionada
docker build -f Dockerfile.mcp -t senior-docs-mcp:1.0.0 .
```

## Executar com Docker Compose

```bash
# Iniciar ambos os serviços (Meilisearch + MCP Server)
docker-compose up -d

# Verificar logs
docker-compose logs -f mcp-server

# Parar serviços
docker-compose down
```

## Executar Manualmente

```bash
# Build
docker build -f Dockerfile.mcp -t senior-docs-mcp .

# Run com modo local (JSONL)
docker run -d \
  --name senior-docs-mcp \
  -p 8000:8000 \
  senior-docs-mcp

# Run com Meilisearch externo
docker run -d \
  --name senior-docs-mcp \
  -p 8000:8000 \
  -e MEILISEARCH_URL=http://meilisearch:7700 \
  -e MEILISEARCH_KEY=meilisearch_master_key \
  --link meilisearch \
  senior-docs-mcp

# Ver logs
docker logs -f senior-docs-mcp

# Parar
docker stop senior-docs-mcp
docker rm senior-docs-mcp
```

## Health Checks

O MCP Server em Docker expõe 3 endpoints para health checks:

### 1. `/health` - Health Status
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-21T17:30:00.000000",
  "service": "MCP Server - Senior Documentation",
  "mode": "local"
}
```

### 2. `/ready` - Readiness Probe
```bash
curl http://localhost:8000/ready
```

**Response:**
```json
{
  "ready": true,
  "timestamp": "2026-01-21T17:30:00.000000"
}
```

### 3. `/stats` - Statistics
```bash
curl http://localhost:8000/stats
```

**Response:**
```json
{
  "total_documents": 933,
  "modules": 17,
  "has_html": 0,
  "source": "local"
}
```

## Variáveis de Ambiente

```dockerfile
# Meilisearch (opcional)
MEILISEARCH_URL=http://meilisearch:7700
MEILISEARCH_KEY=meilisearch_master_key_change_me

# Health Checks
HEALTH_CHECK_PORT=8000
HEALTH_CHECK_HOST=0.0.0.0

# Python
PYTHONUNBUFFERED=1
```

## Docker Compose - Stack Completo

```yaml
services:
  meilisearch:
    image: getmeili/meilisearch:v1.11.0
    ports:
      - "7700:7700"
    environment:
      MEILI_MASTER_KEY: ${MEILISEARCH_KEY:-change_me}

  mcp-server:
    build:
      context: .
      dockerfile: Dockerfile.mcp
    ports:
      - "8000:8000"
    environment:
      MEILISEARCH_URL: http://meilisearch:7700
      MEILISEARCH_KEY: ${MEILISEARCH_KEY:-change_me}
    depends_on:
      meilisearch:
        condition: service_healthy
```

## Monitoramento em Docker

```bash
# Ver status do container
docker ps | grep senior-docs-mcp

# Ver recursos utilizados
docker stats senior-docs-mcp

# Ver detalhes do container
docker inspect senior-docs-mcp

# Executar comando dentro do container
docker exec -it senior-docs-mcp python -c "from src.mcp_server import MCPServer; s = MCPServer(); print(s.doc_search.get_stats())"
```

## Troubleshooting

### Container não inicia
```bash
# Ver logs detalhados
docker logs senior-docs-mcp

# Verificar se a porta está disponível
lsof -i :8000
```

### Health check falha
```bash
# Testar manualmente
curl -v http://localhost:8000/health

# Ver status do healthcheck
docker inspect senior-docs-mcp | grep -A 5 "Health"
```

### Permissões no container
```bash
# O container usa usuário não-root por segurança
# Se precisar executar com root:
docker run -it --user root senior-docs-mcp bash
```

## Otimizações de Performance

### Caching do Docker
```bash
# Build com cache
docker build -f Dockerfile.mcp -t senior-docs-mcp:latest .

# Build sem cache
docker build --no-cache -f Dockerfile.mcp -t senior-docs-mcp:latest .
```

### Volume para dados persistentes
```bash
docker run -d \
  -v docs_indexacao_detailed.jsonl:/app/docs_indexacao_detailed.jsonl:ro \
  senior-docs-mcp
```

### Limites de recursos
```bash
docker run -d \
  --memory=512m \
  --cpus=1 \
  --name senior-docs-mcp \
  -p 8000:8000 \
  senior-docs-mcp
```

## Image Details

- **Base**: `python:3.11-slim` (150 MB)
- **Tamanho final**: ~200-250 MB (estimado)
- **Usuário**: `appuser` (UID: 1000, não-root)
- **Working Directory**: `/app`
- **Healthcheck**: A cada 30s com 3 tentativas
- **Restart Policy**: `unless-stopped` (em docker-compose)

## Segurança

- Executa com usuário não-root
- Sem acesso a arquivos do host
- Índice JSONL montado como read-only
- Variáveis sensíveis via environment

## Development vs Production

### Development
```bash
docker run -it \
  -v $(pwd)/src:/app/src \
  -p 8000:8000 \
  senior-docs-mcp
```

### Production
```bash
docker run -d \
  --restart unless-stopped \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  -e MEILISEARCH_URL=http://meilisearch:7700 \
  -p 8000:8000 \
  senior-docs-mcp
```

## Scripts Úteis

```bash
# Build, test e push
#!/bin/bash
docker build -f Dockerfile.mcp -t senior-docs-mcp:latest .
docker run -it --rm -p 8000:8000 senior-docs-mcp
# Testar health
curl http://localhost:8000/health
```

## Próximos Passos

- [ ] Registry privado (DockerHub, ECR, etc.)
- [ ] CI/CD pipeline para builds automáticos
- [ ] Multi-stage build para otimizar tamanho
- [ ] Versioning automático
- [ ] Documentação de deployment em Kubernetes
