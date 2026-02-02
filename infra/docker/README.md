# Docker Multi-Worker Setup

## 🚀 Quick Start

### 1. Build da imagem

```bash
# Linux/Mac
chmod +x build.sh
./build.sh

# Windows
build.bat

# Ou manual
docker build -t senior-docs-scraper:latest -f Dockerfile ../..
docker build -t senior-docs-scraper:worker -f Dockerfile.worker ../..
docker build -t senior-docs-mcp:latest -f Dockerfile.mcp ../..
```

### 2. Iniciar com workers

```bash
# 3 workers (padrão)
docker-compose -f docker-compose.workers.yml up -d

# 5 workers
NUM_WORKERS=5 docker-compose -f docker-compose.workers.yml up -d

# Ver status
docker-compose -f docker-compose.workers.yml ps

# Logs
docker-compose -f docker-compose.workers.yml logs -f scraper-orchestrator
```

---

## 🔧 Modos de Execução

A imagem Docker suporta **3 modos** via variável `SCRAPER_MODE`:

### LEGACY (Padrão - Compatível)
```bash
# Container scraper único (compatível com versão anterior)
docker-compose up -d scraper meilisearch

# Logs
docker logs senior-docs-scraper
```

### ORCHESTRATOR (Gerenciador)
```bash
# Gerencia múltiplos workers via Docker API
SCRAPER_MODE=orchestrator docker-compose -f docker-compose.workers.yml up -d scraper-orchestrator

# Logs
docker logs senior-docs-scraper-orchestrator
```

### WORKER (Processador)
```bash
# Processa URLs da fila do orchestrator
SCRAPER_MODE=worker docker run -e SCRAPER_MODE=worker senior-docs-scraper:latest

# Ou via docker-compose (automático)
docker-compose -f docker-compose.workers.yml up -d --scale scraper-worker=3
```

---

## 📋 Variáveis de Ambiente

```bash
# Modo de execução
SCRAPER_MODE=legacy|orchestrator|worker

# Número de workers (orchestrator)
NUM_WORKERS=3

# Meilisearch
MEILISEARCH_URL=http://meilisearch:7700
MEILISEARCH_KEY=seu_token_seguro

# Logging
LOG_LEVEL=info|debug|warning|error

# Python
PYTHONUNBUFFERED=1
```

---

## 📊 Comparação dos Modos

| Modo | Uso | Performance | Simplicidade |
|------|-----|-------------|--------------|
| LEGACY | Dev/Prod simples | 1x (sequencial) | ✅ Simples |
| ORCHESTRATOR + WORKERS | Prod com scale | 2-4x paralelo | ⚠️ Complexo |

---

## 🐳 Imagens Disponíveis

### `senior-docs-scraper:latest` (Principal)
- ✅ Suporta 3 modos (legacy/orchestrator/worker)
- ✅ Playwright + todas as dependências
- ✅ ~1.2 GB

### `senior-docs-scraper:worker` (Otimizado)
- ✅ Versão leve apenas para workers
- ✅ Sem Meilisearch, apenas deps de scraping
- ✅ ~900 MB

### `senior-docs-mcp:latest` (Busca)
- ✅ MCP Server
- ✅ Expõe porta 8000
- ✅ ~500 MB

---

## 🔄 Workflow Completo

### 1. Build Local

```bash
cd infra/docker
./build.sh  # ou build.bat no Windows
```

### 2. Iniciar Sistema

```bash
# Com 3 workers
docker-compose -f docker-compose.workers.yml up -d

# Aguardar healthchecks (~30s)
sleep 30

# Verificar
docker-compose -f docker-compose.workers.yml ps
```

### 3. Acompanhar Progresso

```bash
# Logs em tempo real
docker-compose -f docker-compose.workers.yml logs -f scraper-orchestrator

# Recursos usados
docker stats

# Estatísticas
docker exec senior-docs-scraper-orchestrator python -c "
import asyncio
from libs.scrapers.adapters.docker_worker_orchestrator import DockerWorkerOrchestrator
import json

async def stats():
    orch = DockerWorkerOrchestrator()
    s = await orch.get_worker_stats()
    print(json.dumps(s, indent=2, default=str))

asyncio.run(stats())
"
```

### 4. Parar Sistema

```bash
docker-compose -f docker-compose.workers.yml down
```

---

## 🛠️ Troubleshooting

### Workers não iniciam

```bash
# Ver logs de erro
docker-compose -f docker-compose.workers.yml logs scraper-worker

# Reconstruir imagem
docker-compose -f docker-compose.workers.yml build --no-cache scraper-worker

# Reiniciar
docker-compose -f docker-compose.workers.yml restart scraper-worker
```

### Out of Memory

```bash
# Reduzir workers
docker-compose -f docker-compose.workers.yml up -d --scale scraper-worker=2

# Ou aumentar RAM Docker Desktop
# Settings → Resources → Memory (4GB+)
```

### Orchestrator não encontra workers

```bash
# Verificar rede
docker network inspect senior-docs

# Testar conectividade
docker exec senior-docs-scraper-orchestrator ping scraper-worker-001

# Logs do docker daemon
docker logs docker
```

---

## 📦 Build Customizado

### Build com tag personalizada

```bash
docker build -t meu-registry/scraper:v2.1.0 -f Dockerfile ../..
docker push meu-registry/scraper:v2.1.0
```

### Build sem cache

```bash
docker build --no-cache -t senior-docs-scraper:latest -f Dockerfile ../..
```

### Build multi-stage (otimizado)

```bash
# Criar Dockerfile.prod com multi-stage build
docker build -t senior-docs-scraper:prod -f Dockerfile.prod ../..
```

---

## 🔐 Produção

### Checklist

- [ ] Usar secrets manager para tokens
- [ ] Definir resource limits
- [ ] Ativar logging centralizado
- [ ] Configurar monitoring
- [ ] Testar auto-restart
- [ ] Backup de dados

### Docker Stack (Swarm)

```yaml
# docker-stack.yml
version: '3.8'
services:
  scraper:
    image: senior-docs-scraper:latest
    environment:
      SCRAPER_MODE: orchestrator
      NUM_WORKERS: 5
    deploy:
      replicas: 1
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

---

## 📚 Referências

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Multi-Worker Guide](../../docs/guides/docker_multi_worker.md)
- [Quickstart](./MULTI_WORKER_QUICKSTART.md)
