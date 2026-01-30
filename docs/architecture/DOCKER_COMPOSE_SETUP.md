# Docker Compose - Pipeline Unificado

Configuração completa do Docker Compose para rodar o pipeline de scraping + Meilisearch.

## 📦 Serviços

```yaml
services:
  meilisearch          ← Mecanismo de busca
  scraper              ← Scraper + indexador (NOVO)
  mcp-server           ← Servidor MCP
```

## 🚀 Iniciar Pipeline Completo

```bash
# Inicia todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver status
docker-compose ps

# Parar tudo
docker-compose down
```

## 📊 Fluxo de Execução

```
1. docker-compose up -d
   ↓
2. Meilisearch inicia (porta 7700)
   ↓
3. Healthcheck do Meilisearch passa
   ↓
4. Serviço 'scraper' inicia
   ├── Aguarda Meilisearch ficar disponível
   ├── Scrapa documentação do site
   ├── Scrapa API Zendesk
   ├── Indexa tudo no Meilisearch
   └── Container continua rodando
   ↓
5. MCP Server inicia (porta 8000)
```

## 🔍 Verificar Status

### Meilisearch (porta 7700)
```bash
# Web UI
http://localhost:7700

# API Health
curl http://localhost:7700/health

# Índice
curl -X GET "http://localhost:7700/indexes/documentation/stats" \
  -H "Authorization: Bearer meilisearch_master_key_change_me"
```

### Scraper
```bash
# Logs
docker-compose logs scraper

# Entrar no container
docker-compose exec scraper bash

# Ver documentos coletados
docker-compose exec scraper ls -lah docs_unified/
```

### MCP Server (porta 8000)
```bash
# Health
curl http://localhost:8000/health

# Logs
docker-compose logs mcp-server
```

## 📁 Volumes

| Serviço | Volume | Tipo | Descrição |
|---------|--------|------|-----------|
| meilisearch | meilisearch_data | docker | Dados do índice |
| scraper | docs_structured | ro | Docs do site (read-only) |
| scraper | docs_unified | rw | Documentos indexados (saída) |
| mcp-server | docs_indexacao_detailed.jsonl | ro | Arquivo de docs |

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# .env (opcional)
MEILISEARCH_KEY=sua_chave_secreta
LOG_LEVEL=info
CONTAINER_USER=1000:1000
```

### Customize

Edite `docker-compose.yml`:

```yaml
# Mudar porta Meilisearch
ports:
  - "7777:7700"  # Alterado de 7700

# Mudar restart policy
restart: always  # Em vez de unless-stopped

# Adicionar variáveis customizadas
environment:
  CUSTOM_VAR: value
```

## 🐛 Troubleshooting

### Meilisearch não inicia

```bash
# Verificar logs
docker-compose logs meilisearch

# Limpar volumes
docker volume rm scrapytest_meilisearch_data

# Reiniciar
docker-compose down && docker-compose up -d
```

### Scraper não roda

```bash
# Ver logs
docker-compose logs scraper

# Verificar se Meilisearch está pronto
docker-compose exec meilisearch curl http://localhost:7700/health

# Verificar conectividade entre containers
docker-compose exec scraper ping meilisearch
```

### Permissões em volumes

```bash
# Ajustar permissões
docker-compose exec scraper chmod -R 777 docs_unified/

# Ou descomente 'user' no compose para usar uid:gid específico
```

## 📈 Performance

| Operação | Tempo |
|----------|-------|
| Start Meilisearch | ~5s |
| Scraper inicia | ~2s |
| Scraper (website + Zendesk) | 2-5 min |
| Indexação Meilisearch | 30-60s |
| **Total** | **~5-7 min** |

## 🔐 Segurança

⚠️ **Valores padrão inseguros:**
- `MEILISEARCH_KEY=meilisearch_master_key_change_me`

✅ **Para produção:**

```bash
# Gerar chave segura
openssl rand -base64 32

# Usar em .env
MEILISEARCH_KEY=sua_chave_gerada_acima

# Docker lê do .env automaticamente
docker-compose up -d
```

## 📝 Dockerfile (scraper)

Principais etapas:

1. **Python 3.14 slim** - Base mínima
2. **Sistema deps** - curl, etc
3. **pip install** - Dependências Python
4. **Playwright install** - Chromium para JS
5. **Copy código** - Aplicação
6. **Non-root user** - appuser (uid 1000)
7. **Entrypoint** - docker_entrypoint.py

## 🚀 Comandos Úteis

```bash
# Build imagens manualmente
docker-compose build

# Build sem cache
docker-compose build --no-cache

# Pull imagens (Meilisearch)
docker-compose pull

# Listar imagens
docker images | grep senior-docs

# Remover imagens
docker rmi senior-docs-scraper:latest

# Inspecionar container
docker inspect senior-docs-scraper

# Executar comando no container
docker-compose exec scraper python -c "import sys; print(sys.version)"

# Copiar arquivo do container
docker cp senior-docs-scraper:/app/docs_unified/unified_documentation.jsonl .

# Ver tamanho de imagens
docker images --format "table {{.Repository}}\t{{.Size}}"
```

## 🔗 Links

- **Meilisearch UI**: http://localhost:7700
- **MCP Server**: http://localhost:8000
- **Health Checks**:
  - Meilisearch: http://localhost:7700/health
  - MCP: http://localhost:8000/health

## 📚 Estrutura Completa

```
docker-compose.yml
├── services
│   ├── meilisearch
│   │   ├── image: getmeili/meilisearch:v1.11.0
│   │   ├── ports: 7700:7700
│   │   ├── volumes: meilisearch_data
│   │   └── healthcheck: /health
│   │
│   ├── scraper (NOVO)
│   │   ├── build: ./Dockerfile
│   │   ├── depends_on: meilisearch
│   │   ├── volumes: docs_structured, docs_unified
│   │   └── entrypoint: docker_entrypoint.py
│   │
│   └── mcp-server
│       ├── build: ./Dockerfile.mcp
│       ├── depends_on: meilisearch
│       ├── ports: 8000:8000
│       └── volumes: docs_indexacao_detailed.jsonl
│
├── networks
│   └── senior-docs (bridge, 10.0.9.0/24)
│
└── volumes
    └── meilisearch_data
```

## ✅ Checklist de Deployment

- [ ] Editar `MEILISEARCH_KEY` no docker-compose.yml
- [ ] Criar arquivo `.env` com variáveis sensíveis
- [ ] Verificar permissões de `docs_structured/`
- [ ] Verificar espaço em disco
- [ ] Testar `docker-compose config` para validar YAML
- [ ] Executar `docker-compose up -d`
- [ ] Verificar logs: `docker-compose logs -f`
- [ ] Acessar Meilisearch em http://localhost:7700
- [ ] Confirmar documentos foram indexados

## 🎓 Exemplo de Uso Completo

```bash
# 1. Clone/prepare o projeto
cd /seu/projeto

# 2. Configure variáveis de ambiente (opcional)
echo "MEILISEARCH_KEY=sua_chave_segura" > .env

# 3. Inicie tudo
docker-compose up -d

# 4. Monitore o progresso
docker-compose logs -f scraper

# 5. Quando terminar, acesse
open http://localhost:7700

# 6. Para quando terminar
docker-compose down
```

## 📞 Suporte

Se tiver problemas:

1. ✅ Verifique logs: `docker-compose logs [service]`
2. ✅ Valide YAML: `docker-compose config`
3. ✅ Teste conectividade: `docker-compose exec scraper ping meilisearch`
4. ✅ Verifique espaço: `docker system df`
5. ✅ Limpe resources: `docker system prune`
