# Senior Documentation Scraper

Scraper automatizado de documentação técnica Senior Sistemas com MCP Server para busca e suporte a notas de versão.

## 🚀 Quick Start

```bash
# Setup
pip install -r requirements.txt
playwright install chromium

# Executar scraper
python apps/scraper/scraper_unificado.py

# MCP Server (busca)
python apps/mcp-server/mcp_server.py

# Testes
pytest tests/
```

## 📁 Estrutura do Projeto (v2.0 - Monorepo)

```
scrapyTest/
├── apps/                    # Aplicações executáveis
│   ├── scraper/            # Scraper principal (MadCap + Astro + Release Notes)
│   ├── mcp-server/         # MCP Server para busca
│   └── zendesk/            # Integração Zendesk
├── libs/                    # Bibliotecas compartilhadas
│   ├── scrapers/           # Scrapers base
│   ├── indexers/           # Indexadores (JSONL + Meilisearch)
│   ├── pipelines/          # Data pipelines
│   └── utils/              # Utilidades
├── scripts/                 # Scripts de utilidades
│   ├── analysis/           # Análise de dados
│   ├── indexing/           # Indexação manual
│   ├── fixes/              # Debug e correções
│   └── queries/            # Consultas
├── data/                    # Dados e outputs
│   ├── scraped/            # Dados extraídos
│   ├── indexes/            # Índices JSONL
│   └── metadata/           # Metadados
├── docs/                    # Documentação
│   ├── guides/             # Guias de uso
│   ├── architecture/       # Decisões técnicas
│   └── api/                # Docs de API
├── tests/                   # Testes
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── infra/                   # Infraestrutura
│   ├── docker/             # Docker configs
│   └── ci/                 # CI/CD pipelines
└── backups/                 # Backups automáticos
```

## 📖 Documentação

- **[Guia Rápido](docs/guides/QUICK_START.md)** - Primeiros passos
- **[MCP Server](docs/guides/MCP_SERVER.md)** - Busca e integração
- **[Release Notes](docs/guides/RELEASE_NOTES_GUIDE.md)** - Scraping de notas de versão
- **[Docker Setup](docs/guides/DOCKER.md)** - Containers e produção
- **[Debug Guide](docs/guides/DEBUG_GUIA_COMPLETO.md)** - Troubleshooting
- **[Arquitetura](docs/architecture/)** - Decisões técnicas

## ✨ Features

### Scraping
- **MadCap Flare** (15 módulos) - Extração hierárquica com expansão de menu
- **Astro** (1 módulo) - Navegação direta via sidebar
- **Release Notes** - Notas de versão com âncoras (#versão.htm)
- Retry com backoff exponencial
- Validação de conteúdo
- Organização hierárquica com breadcrumb

### MCP Server
4 ferramentas para busca em documentação:
1. **search_docs** - Busca full-text com filtro por módulo
2. **list_modules** - Lista módulos disponíveis
3. **get_module_docs** - Documentos de um módulo
4. **get_stats** - Estatísticas do índice

### Indexação
- **JSONL local** - Sem dependência de servidor
- **Meilisearch** - Para produção
- Metadados completos
- Estatísticas detalhadas

## 🐳 Docker

```bash
# Iniciar Meilisearch
cd infra/docker
docker-compose up -d meilisearch

# Indexar documentos
python scripts/indexing/index_to_meilisearch.py
```

## 🧪 Testes

```bash
# Todos os testes
pytest tests/

# Testes específicos
pytest tests/integration/test_mcp_server.py
pytest tests/integration/test_scraper.py
```

## 📊 Outputs

- `data/scraped/estruturado/` - Documentação estruturada por módulo
- `data/indexes/docs_indexacao_detailed.jsonl` - Índice de busca (933+ documentos)
- `data/metadata/docs_metadata.json` - Metadados

## 🔄 Changelog

Ver [CHANGELOG.md](CHANGELOG.md) para histórico completo de mudanças.

**Versão atual: 2.0.0** - Refatoração completa para monorepo

## 📝 License

Propriedade da Senior Sistemas

---

Para mais detalhes, consulte a [documentação completa](docs/).
