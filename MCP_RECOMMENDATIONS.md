# Recomendações Finais: MCP, Docker e Meilisearch

**Baseado em**: Validação completa realizada em 30 de janeiro de 2026

---

## 🎯 Prioridade 1: Crítico (Implementar ANTES de produção)

### 1.1 Segurança - API Key do Meilisearch

**Problema**: A chave `meilisearch_master_key_change_me` é hardcoded

**Solução**:
```yaml
# infra/docker/docker-compose.yml
environment:
  MEILI_MASTER_KEY: ${MEILI_MASTER_KEY}  # Obrigatório via env
```

**Arquivo**: `.env` (não commitar)
```
MEILI_MASTER_KEY=seu_master_key_super_seguro_aleatorio
MEILISEARCH_KEY=seu_master_key_super_seguro_aleatorio
```

**Implementação**:
```bash
# Gerar chave segura
openssl rand -base64 32

# Criar .env
echo "MEILI_MASTER_KEY=$(openssl rand -base64 32)" > .env
echo "MEILISEARCH_KEY=$(openssl rand -base64 32)" >> .env

# Adicionar ao .gitignore
echo ".env" >> .gitignore
```

**Status**: ⚠️ Recomendado

---

### 1.2 Atualizar Path em mcp_config.json

**Problema**: Path ainda referencia estrutura antiga (`src/mcp_server.py`)

**Solução**:
```json
{
    "mcpServers": {
        "senior-docs": {
            "command": "python",
            "args": ["apps/mcp-server/mcp_server.py"],  // ← ATUALIZAR
            "cwd": "c:/Users/Digisys/scrapyTest"
        }
    }
}
```

**Status**: 🔴 Crítico

---

### 1.3 HEALTHCHECK no Dockerfile do Scraper

**Problema**: Dockerfile do Scraper não possui HEALTHCHECK

**Solução**:
```dockerfile
# infra/docker/Dockerfile - Adicionar ao final
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1
```

**Status**: 🟡 Importante

---

## 🎯 Prioridade 2: Alta (Implementar em 2-4 semanas)

### 2.1 Monitoramento e Logging

**Implementação**: Prometheus + Grafana

```yaml
# infra/docker/docker-compose.yml - Adicionar serviço
prometheus:
  image: prom/prometheus:latest
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
  ports:
    - "9090:9090"
  networks:
    - senior-docs

grafana:
  image: grafana/grafana:latest
  ports:
    - "3000:3000"
  volumes:
    - grafana_data:/var/lib/grafana
  networks:
    - senior-docs
```

**Métricas a monitorar**:
- Latência de buscas Meilisearch
- Taxa de erro (5xx)
- Uso de memória
- Uptime dos serviços

**Status**: 🟡 Importante

---

### 2.2 Rate Limiting

**Implementação**: Adicionar middleware ao MCP Server

```python
# apps/mcp-server/middleware.py (novo arquivo)
from functools import wraps
from time import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests_per_second=100):
        self.requests_per_second = requests_per_second
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        now = time()
        # Remover requisições antigas
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < 1
        ]
        
        if len(self.requests[client_id]) < self.requests_per_second:
            self.requests[client_id].append(now)
            return True
        return False
```

**Status**: 🟡 Importante

---

### 2.3 Backup Automático do Índice

**Script**: `scripts/indexing/backup_meilisearch.py`

```python
#!/usr/bin/env python3
import meilisearch
import json
from datetime import datetime
from pathlib import Path

def backup_meilisearch_index():
    client = meilisearch.Client("http://localhost:7700", "api_key")
    index = client.index("documentation")
    
    # Exportar documentos
    documents = []
    for doc in index.get_documents({"limit": 10000})["results"]:
        documents.append(doc)
    
    # Salvar backup
    backup_dir = Path("data/backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().isoformat()
    backup_file = backup_dir / f"meilisearch_backup_{timestamp}.jsonl"
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        for doc in documents:
            f.write(json.dumps(doc, ensure_ascii=False) + '\n')
    
    print(f"✓ Backup criado: {backup_file}")

if __name__ == "__main__":
    backup_meilisearch_index()
```

**Agendamento**: Cron job diário
```bash
# Adicionar a crontab
0 2 * * * cd /path/to/project && python scripts/indexing/backup_meilisearch.py
```

**Status**: 🟡 Importante

---

## 🎯 Prioridade 3: Média (Implementar em 4-8 semanas)

### 3.1 Cache com Redis

**Docker Service**:
```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
  networks:
    - senior-docs
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 5s
    timeout: 3s
    retries: 5
```

**MCP Integration**:
```python
import redis

class CachedSearchMCP:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    
    def search(self, query: str, module: str = None, limit: int = 5):
        # Gerar cache key
        cache_key = f"search:{query}:{module}:{limit}"
        
        # Verificar cache
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Se não estiver em cache, fazer busca
        results = self._do_search(query, module, limit)
        
        # Salvar em cache por 1 hora
        self.redis.setex(cache_key, 3600, json.dumps(results))
        
        return results
```

**Status**: 🟡 Média

---

### 3.2 HTTPS/TLS

**Certificado**: Let's Encrypt via Certbot

```bash
# Instalar Certbot
apt-get install certbot python3-certbot-nginx

# Gerar certificado
certbot certonly --standalone -d seu_dominio.com

# Configurar Nginx como reverse proxy
```

**Nginx Config**:
```nginx
server {
    listen 443 ssl;
    server_name seu_dominio.com;
    
    ssl_certificate /etc/letsencrypt/live/seu_dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu_dominio.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Status**: 🟡 Média

---

### 3.3 Replicação de Índices

**Usar Meilisearch Cloud** para backup e failover automático

Ou **implementar sincronização manual**:

```python
# Script para sincronizar índices entre instâncias
import meilisearch

def sync_indices(master_url, replica_url):
    master = meilisearch.Client(master_url, "api_key_master")
    replica = meilisearch.Client(replica_url, "api_key_replica")
    
    # Exportar índice do master
    index = master.index("documentation")
    documents = index.get_documents({"limit": 10000})["results"]
    
    # Importar no replica
    replica_index = replica.index("documentation")
    replica_index.add_documents(documents)
    
    print(f"✓ {len(documents)} documentos sincronizados")
```

**Status**: 🟡 Média

---

## 🎯 Prioridade 4: Baixa (Nice to have)

### 4.1 Dashboard de Administração

**Implementar**: Web UI para:
- Visualizar estatísticas do índice
- Gerenciar documentos
- Histórico de buscas
- Performance metrics

**Stack**: FastAPI + React

---

### 4.2 Analytics

**Rastrear**:
- Buscas mais frequentes
- Documentos mais acessados
- Tempo de resposta
- Taxa de cliques

```python
# apps/mcp-server/analytics.py
class SearchAnalytics:
    def __init__(self):
        self.searches = []
    
    def log_search(self, query, results_count, response_time_ms):
        self.searches.append({
            "query": query,
            "results": results_count,
            "response_time": response_time_ms,
            "timestamp": datetime.now()
        })
```

---

### 4.3 Machine Learning (Ranking Personalizado)

**Usar**: LLM para re-ranker de resultados

```python
from langchain.llms import OpenAI

def rerank_results(query, results):
    llm = OpenAI(api_key="...")
    
    prompt = f"""
    Dado a query: "{query}"
    E estes resultados:
    {results}
    
    Reordene por relevância. Retorne em JSON.
    """
    
    reranked = llm.predict(prompt)
    return json.loads(reranked)
```

---

## 📋 Checklist de Implementação

### Antes de Produção (1-2 semanas)
- [ ] Atualizar mcp_config.json com novo path
- [ ] Configurar variáveis de ambiente (.env)
- [ ] Adicionar HEALTHCHECK ao Dockerfile do Scraper
- [ ] Testar em staging environment
- [ ] Revisar logs de segurança

### Primeira Semana em Produção
- [ ] Monitorar uptime e performance
- [ ] Verificar backup automático
- [ ] Testar fallback para JSONL
- [ ] Revisar logs de erros

### Próximas 2-4 Semanas
- [ ] Implementar Prometheus/Grafana
- [ ] Adicionar rate limiting
- [ ] Configurar backup automático
- [ ] Documentar runbook de ops

---

## 🔧 Troubleshooting Rápido

### Problema: Meilisearch não conecta
```bash
# Verificar saúde
curl http://localhost:7700/health

# Ver logs
docker logs senior-docs-meilisearch

# Reiniciar
docker-compose restart meilisearch
```

### Problema: MCP Server não responde
```bash
# Verificar saúde
curl http://localhost:8000/health

# Ver logs
docker logs senior-docs-mcp-server

# Reiniciar
docker-compose restart mcp-server
```

### Problema: Buscas lentas
```bash
# Verificar performance
curl http://localhost:8000/stats

# Dados podem estar desatualizados
# Reindexar:
python scripts/indexing/reindex_all_docs.py
```

---

## 📞 Contato e Suporte

- **Documentação**: `docs/guides/`
- **Relatório de Validação**: `MCP_VALIDATION_REPORT.md`
- **Resumo Executivo**: `MCP_VALIDATION_EXECUTIVE_SUMMARY.md`
- **Issues**: GitHub Issues (quando disponível)

---

## ✅ Conclusão

Seguindo estas recomendações, o sistema estará:
1. ✅ Seguro (HTTPS, API keys rotativas)
2. ✅ Confiável (Backups, Fallback, Healthchecks)
3. ✅ Observável (Logs, Métricas, Alertas)
4. ✅ Escalável (Cache, Rate Limiting, Replicação)
5. ✅ Produção-ready (Tudo testado e validado)

**Recomendação**: Implementar Prioridade 1 e 2 antes de ir para produção.
