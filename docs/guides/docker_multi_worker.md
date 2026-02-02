# Docker Multi-Worker Deployment Guide

## 🚀 Overview

Sistema de scraping com múltiplos workers usando Docker e docker-compose, permitindo escalar horizontalmente o processamento de URLs.

**Arquitetura:**
```
docker-compose.workers.yml
├── meilisearch (serviço de busca)
├── scraper-orchestrator (gerencia workers)
├── scraper-worker-001 (process URLs)
├── scraper-worker-002 (process URLs)
├── scraper-worker-003 (process URLs)
└── mcp-server (API de busca)
```

---

## 📋 Pré-requisitos

- Docker 20.10+
- docker-compose 1.29+
- 2+ GB RAM disponível (por worker)
- Acesso a /var/run/docker.sock (para orquestração)

```bash
# Verificar versões
docker --version
docker-compose --version

# Exemplo de saída esperado:
# Docker version 24.0.0
# docker-compose version v2.15.0
```

---

## 🎯 Modos de Execução

### 1. LEGACY (Padrão - Scraper Único)

```bash
# Scraper tradicional sem workers
cd infra/docker
docker-compose up -d scraper meilisearch

# Logs
docker-compose logs -f scraper
```

**Quando usar:**
- Desenvolvimento local
- Scraping leve/rápido
- Debugging

---

### 2. ORCHESTRATOR (Gerenciador de Workers)

```bash
# Iniciar com 3 workers (padrão)
cd infra/docker
docker-compose -f docker-compose.workers.yml up -d

# Com 5 workers (via variável de ambiente)
NUM_WORKERS=5 docker-compose -f docker-compose.workers.yml up -d

# Com 10 workers (máximo recomendado)
NUM_WORKERS=10 docker-compose -f docker-compose.workers.yml up -d
```

**Componentes:**
- `scraper-orchestrator`: Gerencia workers via Docker API
- `scraper-worker-*`: Múltiplos containers processando URLs
- `meilisearch`: Indexação centralizada
- `mcp-server`: API de busca

**Quando usar:**
- Produção com scraping em larga escala
- Processamento de 1000+ URLs
- Paralelismo necessário

---

### 3. WORKER (Processador Individual)

Worker é iniciado automaticamente pelo orchestrator.

```bash
# Iniciar worker manualmente (raro)
SCRAPER_MODE=worker WORKER_ID=1 python infra/docker/docker_entrypoint_workers.py
```

---

## ⚙️ Configuração

### Via Variáveis de Ambiente

```bash
# Variáveis principais
export NUM_WORKERS=3
export MEILISEARCH_KEY=seu_token_seguro
export LOG_LEVEL=info
export PYTHONUNBUFFERED=1

# Iniciar
NUM_WORKERS=3 docker-compose -f docker-compose.workers.yml up -d
```

### Via Arquivo .env

```bash
# infra/docker/.env
NUM_WORKERS=3
MEILISEARCH_KEY=seu_token_seguro
LOG_LEVEL=info
MEILI_LOG_LEVEL=info
```

Depois rodar normalmente:

```bash
docker-compose -f docker-compose.workers.yml up -d
```

### Via docker-compose override

```bash
# docker-compose.override.yml (local, não commitar)
version: '3.9'
services:
  scraper-worker:
    deploy:
      replicas: 5  # Sobrescreve padrão
```

---

## 📊 Escalabilidade Dinâmica

### Scale Workers via docker-compose

```bash
# Iniciar com 3 workers
docker-compose -f docker-compose.workers.yml up -d --scale scraper-worker=3

# Aumentar para 5 workers
docker-compose -f docker-compose.workers.yml up -d --scale scraper-worker=5

# Reduzir para 2 workers
docker-compose -f docker-compose.workers.yml up -d --scale scraper-worker=2

# Visualizar workers
docker ps | grep scraper-worker
```

### Scale via Docker CLI (programático)

```python
from libs.scrapers.adapters.docker_worker_orchestrator import DockerWorkerOrchestrator

async def scale():
    orchestrator = DockerWorkerOrchestrator()
    
    # Escalar para 5 workers
    workers = await orchestrator.scale_workers(5)
    print(f"✅ Escalado para {len(workers)} workers")
    
    # Coletar estatísticas
    stats = await orchestrator.get_worker_stats()
    print(stats)
```

---

## 📈 Monitoramento

### Logs em Tempo Real

```bash
# Logs de todos os serviços
docker-compose -f docker-compose.workers.yml logs -f

# Logs de orchestrator apenas
docker-compose -f docker-compose.workers.yml logs -f scraper-orchestrator

# Logs de um worker específico
docker-compose -f docker-compose.workers.yml logs -f scraper-worker

# Logs com timestamp e 50 linhas
docker-compose -f docker-compose.workers.yml logs -f --timestamps --tail=50 scraper-orchestrator
```

### Status dos Containers

```bash
# Verificar status
docker-compose -f docker-compose.workers.yml ps

# Exemplo de saída:
# NAME                      COMMAND    STATUS
# scraper-orchestrator      python...  Up (healthy)
# scraper-worker-001        python...  Up (healthy)
# scraper-worker-002        python...  Up (healthy)
# scraper-worker-003        python...  Up (healthy)
# meilisearch               ...        Up (healthy)
# mcp-server                ...        Up (healthy)
```

### Healthchecks

```bash
# Verificar saúde do orchestrator
curl http://localhost:8001/health

# Verificar saúde do Meilisearch
curl http://localhost:7700/health

# Verificar saúde do MCP Server
curl http://localhost:8000/health
```

### Métricas e Estatísticas

```bash
# Conectar ao container e verificar stats
docker exec senior-docs-scraper-orchestrator python -c "
from libs.scrapers.adapters.docker_worker_orchestrator import DockerWorkerOrchestrator
import asyncio
import json

orchestrator = DockerWorkerOrchestrator()
stats = asyncio.run(orchestrator.get_worker_stats())
print(json.dumps(stats, indent=2, default=str))
"
```

---

## 🔄 Operações Comuns

### Iniciar Sistema Completo

```bash
cd infra/docker

# Com 3 workers (padrão)
docker-compose -f docker-compose.workers.yml up -d

# Aguardar healthchecks
sleep 30

# Verificar status
docker-compose -f docker-compose.workers.yml ps
```

### Parar Sistema

```bash
docker-compose -f docker-compose.workers.yml down

# Com limpeza de volumes (dados locais)
docker-compose -f docker-compose.workers.yml down -v
```

### Reiniciar Workers

```bash
# Reiniciar todos
docker-compose -f docker-compose.workers.yml restart scraper-worker

# Reiniciar worker específico
docker-compose -f docker-compose.workers.yml restart scraper-worker_1
```

### Verificar Logs de Erro

```bash
# Logs dos últimos 100 linhas com erro
docker-compose -f docker-compose.workers.yml logs --tail=100 scraper-worker | grep -i error

# Logs com contexto (5 linhas antes/depois)
docker-compose -f docker-compose.workers.yml logs scraper-worker | grep -C 5 -i error
```

### Reconstruir Imagem

```bash
# Se mudou código
docker-compose -f docker-compose.workers.yml build

# Force rebuild sem cache
docker-compose -f docker-compose.workers.yml build --no-cache

# Depois rodar
docker-compose -f docker-compose.workers.yml up -d
```

---

## 🛡️ Troubleshooting

### Problema: "Cannot connect to Docker daemon"

**Causa:** Docker não está rodando ou socket inacessível

```bash
# Solução 1: Iniciar Docker
sudo systemctl start docker

# Solução 2: Verificar permissões
ls -la /var/run/docker.sock

# Solução 3: Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

### Problema: "Out of memory"

**Causa:** Muitos workers ou memória insuficiente

```bash
# Ver uso de memória
docker stats

# Reduzir workers
docker-compose -f docker-compose.workers.yml up -d --scale scraper-worker=2

# Ou aumentar recursos Docker
# Docker Desktop → Settings → Resources → Memory (aumentar para 4+ GB)
```

### Problema: "Worker container keeps restarting"

**Causa:** Erro na inicialização do worker

```bash
# Ver logs de erro
docker-compose -f docker-compose.workers.yml logs scraper-worker

# Logs detalhados (últimas 50 linhas)
docker logs -f --tail=50 $(docker ps -q -f status=running -f ancestor=senior-docs-scraper:latest)

# Verificar healthcheck
docker inspect senior-docs-worker-001 | grep -A 20 '"Health"'
```

### Problema: "Orchestrator cannot reach workers"

**Causa:** Rede Docker não configurada corretamente

```bash
# Verificar rede
docker network ls
docker network inspect senior-docs

# Testar conectividade
docker exec senior-docs-scraper-orchestrator ping scraper-worker-001

# Remover e recriар rede
docker-compose -f docker-compose.workers.yml down -v
docker network rm senior-docs
docker-compose -f docker-compose.workers.yml up -d
```

### Problema: "Meilisearch service unhealthy"

**Causa:** Tempo de startup insuficiente ou recurso indisponível

```bash
# Verificar logs do Meilisearch
docker-compose -f docker-compose.workers.yml logs meilisearch

# Aumentar timeout de healthcheck
# Editar docker-compose.workers.yml:
# healthcheck:
#   start_period: 15s  # aumentar de 5s

# Aumentar volume do Meilisearch
docker volume ls
du -sh /var/lib/docker/volumes/*/meilisearch_data
```

---

## 🚀 Otimizações

### Resource Limits

```yaml
# docker-compose.workers.yml
scraper-worker:
  deploy:
    resources:
      limits:
        cpus: '1'          # 1 CPU por worker
        memory: 1G         # 1GB por worker
      reservations:
        cpus: '0.5'        # Reserve pelo menos 0.5 CPU
        memory: 512M       # Reserve pelo menos 512MB
```

### Network Optimization

```yaml
# Use host network (mais rápido, menos isolamento)
scraper-orchestrator:
  network_mode: host

# Ou configure custom driver
networks:
  senior-docs:
    driver: bridge
    driver_opts:
      com.docker.network.driver.mtu: 1500
```

### Storage Optimization

```bash
# Usar tmpfs para dados temporários
# docker-compose.workers.yml
scraper-worker:
  tmpfs:
    - /tmp
    - /var/tmp

# Limpar imagens não usadas
docker image prune -a --filter "until=72h"

# Limpar volumes não usados
docker volume prune --filter "label!=keep"
```

---

## 📚 Arquivos Relacionados

- `infra/docker/docker-compose.workers.yml` - Compose com multi-worker
- `infra/docker/docker_entrypoint_workers.py` - Entrypoint para orchestrator/worker
- `libs/scrapers/adapters/docker_worker_orchestrator.py` - Orquestrador Docker
- `libs/scrapers/adapters/playwright_worker_pool.py` - Pool de workers em-processo

---

## 🎯 Checklist de Deploy

- [ ] Verificar versões de Docker/Compose
- [ ] Configurar variáveis de ambiente (.env)
- [ ] Build das imagens (docker-compose build)
- [ ] Iniciar serviços (docker-compose up -d)
- [ ] Aguardar healthchecks (30-60s)
- [ ] Verificar status (docker-compose ps)
- [ ] Verificar logs (docker-compose logs -f)
- [ ] Testar endpoints (curl http://localhost:8001/health)
- [ ] Monitorar recursos (docker stats)
- [ ] Coletar métricas após conclusão

---

## 🔗 Referências

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Python SDK](https://docker-py.readthedocs.io/)
- [PlaywrightWorkerPool Guide](./multi_worker_scraping.md)
- [Meilisearch Docker Setup](https://docs.meilisearch.com/learn/what_is_meilisearch/overview.html)
