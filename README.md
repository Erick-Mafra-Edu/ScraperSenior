# Senior Documentation Scraper

> **v2.0** - Monorepo Architecture | Scraper automatizado de documentação técnica Senior Sistemas

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

## 📁 Estrutura

```
apps/       → Aplicações executáveis (scraper, mcp-server, zendesk)
libs/       → Bibliotecas compartilhadas (scrapers, indexers, utils)
scripts/    → Utilitários (analysis, indexing, fixes, queries)
data/       → Dados e outputs (scraped, indexes, metadata)
docs/       → Documentação completa
tests/      → Testes (unit, integration, e2e)
infra/      → Docker e CI/CD
```

## 📖 Documentação

**Ver [docs/](docs/) para documentação completa** ou acesse diretamente:

- **[Guia Rápido](docs/guides/QUICK_START.md)** - Primeiros passos
- **[MCP Server](docs/guides/MCP_SERVER.md)** - Busca e integração
- **[Release Notes](docs/guides/RELEASE_NOTES_GUIDE.md)** - Scraping de notas
- **[Docker](docs/guides/DOCKER.md)** - Setup de containers
- **[Arquitetura](docs/architecture/)** - Decisões técnicas

## ✨ Features

- **Scraping**: MadCap Flare (15 módulos) + Astro (1 módulo) + Release Notes
- **MCP Server**: 4 ferramentas para busca (search_docs, list_modules, etc.)
- **Indexação**: JSONL local + Meilisearch
- **Docker**: Pronto para produção
- **CI/CD**: Pipeline completo

## 🔄 Changelog

**v2.0.0** (2026-01-30) - Refatoração completa para monorepo
- Nova estrutura: apps/, libs/, scripts/, docs/, data/
- Consolidação de 60+ arquivos markdown
- Organização de código por responsabilidade

Ver [CHANGELOG.md](CHANGELOG.md) para histórico completo.

---

�� **[Documentação Completa](docs/)** | 🐳 **[Docker Setup](infra/docker/)** | 🧪 **[Testes](tests/)**