# Multi-Worker Docker Quick Start

## 🚀 Iniciar Rápido (3 Workers)

```bash
cd infra/docker

# Iniciar com 3 workers (padrão)
docker-compose -f docker-compose.workers.yml up -d

# Verificar status
docker-compose -f docker-compose.workers.yml ps

# Logs em tempo real
docker-compose -f docker-compose.workers.yml logs -f
```

**Output esperado:**
```
scraper-orchestrator    Up (healthy)
scraper-worker-001      Up (healthy)
scraper-worker-002      Up (healthy)
scraper-worker-003      Up (healthy)
meilisearch             Up (healthy)
mcp-server              Up (healthy)
```

---

## 🎯 Exemplos de Uso

### Com 5 Workers

```bash
NUM_WORKERS=5 docker-compose -f docker-compose.workers.yml up -d
```

### Escalar Dinamicamente

```bash
# Aumentar de 3 para 5 workers
docker-compose -f docker-compose.workers.yml up -d --scale scraper-worker=5

# Reduzir de 5 para 2 workers
docker-compose -f docker-compose.workers.yml up -d --scale scraper-worker=2
```

### Parar Sistema

```bash
docker-compose -f docker-compose.workers.yml down
```

---

## 📊 Monitoramento

### Ver Status dos Workers

```bash
docker-compose -f docker-compose.workers.yml ps

# Ver logs com cores
docker-compose -f docker-compose.workers.yml logs --tail=50 -f scraper-orchestrator
```

### Verificar Saúde

```bash
# Orchestrator
curl http://localhost:8001/health

# Meilisearch
curl http://localhost:7700/health

# MCP Server
curl http://localhost:8000/health
```

### Recursos (CPU/Memory)

```bash
docker stats

# Exemplo:
# CONTAINER              CPU %     MEM USAGE / LIMIT
# scraper-worker-001    45%       512MB / 1GB
# scraper-worker-002    38%       480MB / 1GB
# scraper-worker-003    52%       535MB / 1GB
# meilisearch          15%       256MB / 1GB
```

---

## ⚙️ Configuração

### Via Variáveis de Ambiente

```bash
# Com arquivo .env
cat > infra/docker/.env <<EOF
NUM_WORKERS=3
MEILISEARCH_KEY=seu_token_seguro
LOG_LEVEL=info
EOF

# Depois rodar
docker-compose -f docker-compose.workers.yml up -d
```

### Limites de Recursos

Editar `docker-compose.workers.yml`:

```yaml
scraper-worker:
  deploy:
    resources:
      limits:
        cpus: '2'       # 2 CPUs por worker
        memory: 2G      # 2GB por worker
```

---

## 🛠️ Troubleshooting

### Workers não iniciam

```bash
# Ver logs de erro
docker-compose -f docker-compose.workers.yml logs scraper-worker

# Reconstruir imagem
docker-compose -f docker-compose.workers.yml build --no-cache

# Reiniciar
docker-compose -f docker-compose.workers.yml down -v
docker-compose -f docker-compose.workers.yml up -d
```

### Out of Memory

```bash
# Reduzir workers
docker-compose -f docker-compose.workers.yml up -d --scale scraper-worker=2

# Ou aumentar RAM Docker Desktop
# Docker Desktop → Settings → Resources → Memory (4+ GB)
```

### Orchestrator não consegue iniciar workers

```bash
# Verificar docker socket
ls -la /var/run/docker.sock

# Testar acesso
docker ps

# Se erro, adicionar user ao grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

---

## 📈 Performance

**Benchmark (1000 URLs):**

| Workers | Tempo Total | Throughput | vs Sequential |
|---------|------------|-----------|---------------|
| 1 (legacy) | 500s | 2 URLs/s | - |
| 3 | 175s | 5.7 URLs/s | **2.9x mais rápido** |
| 5 | 115s | 8.7 URLs/s | **4.3x mais rápido** |

---

## 🔍 Ver Estatísticas Detalhadas

```bash
# Conectar ao orchestrator e obter stats
docker exec senior-docs-scraper-orchestrator \
  python3 -c "
from libs.scrapers.adapters.docker_worker_orchestrator import DockerWorkerOrchestrator
import asyncio
import json

async def stats():
    orch = DockerWorkerOrchestrator()
    s = await orch.get_worker_stats()
    print(json.dumps(s, indent=2, default=str))

asyncio.run(stats())
"
```

---

## 📚 Documentação Completa

- [Docker Multi-Worker Guide](../../docs/guides/docker_multi_worker.md) - Guia completo
- [In-Process Worker Pool](../../docs/guides/multi_worker_scraping.md) - Worker pool local
- [scraper_config.json](../../apps/scraper/config/scraper_config.json) - Configuração

---

## 🎯 Próximos Passos

1. Ajustar `NUM_WORKERS` baseado na sua máquina
2. Monitorar `docker stats` durante o scraping
3. Coletar estatísticas de performance
4. Escalr/reduzir workers conforme necessário
5. Processar dados com `mcp-server` (porta 8000)
