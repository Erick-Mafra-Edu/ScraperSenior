# Changelog

## [2.0.0] - 2026-01-30 - Refatoração Completa (Monorepo)

### 🏗️ Arquitetura
- **BREAKING**: Migração completa para estrutura monorepo
- Nova organização: `apps/`, `libs/`, `scripts/`, `docs/`, `data/`, `infra/`, `tests/`
- Separação clara entre aplicações executáveis e bibliotecas reutilizáveis
- Consolidação de 60+ arquivos markdown em estrutura organizada

### 📁 Estrutura do Projeto
**Apps (Aplicações executáveis)**:
- `apps/scraper/` - Scrapers principal (unificado + modular)
- `apps/mcp-server/` - MCP Server para busca
- `apps/zendesk/` - Integração Zendesk/Suporte Senior

**Libs (Bibliotecas compartilhadas)**:
- `libs/scrapers/` - Scrapers base reutilizáveis
- `libs/indexers/` - Indexadores (local JSONL + Meilisearch)
- `libs/pipelines/` - Data pipelines
- `libs/utils/` - Utilidades compartilhadas

**Scripts (Utilitários)**:
- `scripts/analysis/` - Scripts de análise
- `scripts/indexing/` - Scripts de indexação manual
- `scripts/fixes/` - Debug e correções
- `scripts/queries/` - Consultas e verificações

**Dados**:
- `data/scraped/` - Dados extraídos (estruturado, unified, zendesk)
- `data/indexes/` - Índices JSONL
- `data/metadata/` - Metadados

**Infraestrutura**:
- `infra/docker/` - Dockerfiles e docker-compose
- `infra/ci/` - CI/CD pipelines

**Documentação**:
- `docs/guides/` - Guias de uso
- `docs/architecture/` - Decisões de arquitetura
- `docs/api/` - Documentação de API

### 🧹 Limpeza
- Removidos 60+ arquivos markdown da raiz
- Consolidados relatórios históricos neste CHANGELOG
- Removidas pastas duplicadas (docs_structured/)
- Organizados scripts dispersos em categorias

### 📝 Histórico Consolidado (v1.x)
Abaixo, consolidação dos principais eventos e entregas das versões anteriores:

#### Release Notes & Melhorias (Jan 2026)
- Implementado scraping de notas de versão com âncoras (#versão.htm)
- Suporte a múltiplos módulos Senior ERP X
- Descoberta automática de URLs de release notes

#### MCP Server (Jan 2026)
- MCP Server com 4 ferramentas: search_docs, list_modules, get_module_docs, get_stats
- Integração com Claude Desktop
- Testes automatizados MCP
- Docker support para MCP Server

#### Pipeline & CI/CD (Jan 2026)
- Pipeline CI/CD completo (ci_pipeline.ps1)
- Validação de schemas
- Testes automatizados de scraper e MCP
- Docker orchestration

#### Fixes & Debug (Jan 2026)
- Correção de títulos truncados
- Fix em parâmetros do Copilot
- Debug de scraping com logs detalhados
- Validação de indexação

#### Zendesk Integration (Jan 2026)
- API Zendesk modular
- Suporte Senior API integration
- Adapter pattern para múltiplas fontes

### 🔧 Breaking Changes
- Paths alterados: código movido de `src/` para `apps/` e `libs/`
- Configs movidos para `apps/*/config/`
- Dados movidos para `data/`
- Imports precisam ser atualizados
- Docker volumes precisam apontar para novos paths

### 📚 Migração
Para migrar código existente:
1. Atualizar imports: `from src.X import Y` → `from apps.X import Y` ou `from libs.X import Y`
2. Atualizar paths de config: `./config.json` → `./apps/*/config/*.json`
3. Atualizar paths de dados: `./docs_*` → `./data/scraped/*`
4. Revisar docker-compose.yml volumes

---

## [1.0.0] - 2026-01-20

### ✨ Features
- ✅ Scraper unificado para MadCap Flare e Astro
- ✅ Extração hierárquica com breadcrumb completo
- ✅ Organização automática em estrutura de pastas
- ✅ Geração de JSONL para Meilisearch
- ✅ Metadados completos e estatísticas
- ✅ Docker compose ready
- ✅ Setup automático

### 🧹 Cleanup
- ❌ Removidos 40+ arquivos de teste antigos
- ❌ Removidas 8 pastas de documentação obsoleta
- ❌ Removido código legado (Flask API, Scrapy, etc)
- ❌ Simplificado docker-compose.yml
- ❌ Atualizado requirements.txt (apenas essenciais)

### 📝 Documentation
- ✅ README.md completamente reescrito
- ✅ README_SCRAPER.md com detalhes de uso
- ✅ LIMPEZA_CONCLUIDA.md com sumário
- ✅ .env.example com configurações padrão

### 🛠️ Infrastructure
- ✅ docker-compose.yml simplificado
- ✅ Dockerfile otimizado
- ✅ tools/setup.py para instalação rápida
- ✅ tools/maintenance.py para limpeza

### 📊 Results
- 58 páginas scrapadas
- 558,342 caracteres de conteúdo
- 338.9 KB de JSONL
- 100% de taxa de sucesso
- Tempo de execução: ~3 minutos

---

**Versão Inicial** | Projeto limpo e pronto para produção
