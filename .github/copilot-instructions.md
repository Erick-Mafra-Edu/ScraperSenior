# Copilot Instructions - Senior Documentation Scraper

## Estrutura do Projeto (Monorepo v2.0)

Este projeto segue uma arquitetura **monorepo** com separação clara de responsabilidades:

### 📁 Diretórios Principais

#### `apps/` - Aplicações Executáveis
Aplicações standalone que podem ser executadas diretamente:
- **`apps/scraper/`** - Scrapers principais (scraper_unificado.py, scraper_modular.py)
  - `config/` - Configurações específicas do scraper
- **`apps/mcp-server/`** - MCP Server para busca em documentação
- **`apps/zendesk/`** - Integração com Zendesk e Suporte Senior

**Regra**: Apps devem ser autocontidos e importar apenas de `libs/`.

#### `libs/` - Bibliotecas Compartilhadas
Código reutilizável entre diferentes apps:
- **`libs/scrapers/`** - Scrapers base e funções de scraping
- **`libs/indexers/`** - Indexadores (JSONL local + Meilisearch)
- **`libs/pipelines/`** - Data pipelines e transformações
- **`libs/utils/`** - Funções utilitárias compartilhadas

**Regra**: Libs não devem importar de `apps/`, apenas de outras `libs/`.

#### `scripts/` - Utilitários e Ferramentas
Scripts auxiliares organizados por categoria:
- **`scripts/analysis/`** - Análise de dados e estruturas
- **`scripts/indexing/`** - Indexação manual e reindexação
- **`scripts/fixes/`** - Debug e correções
- **`scripts/queries/`** - Consultas e verificações

**Regra**: Scripts podem importar de `apps/` e `libs/` conforme necessário.

#### `data/` - Dados e Outputs
Dados separados do código para facilitar backup/deploy:
- **`data/scraped/`** - Dados extraídos
  - `estruturado/` - Docs estruturados por módulo (~1866 arquivos)
  - `unified/` - Docs unificados
  - `zendesk/` - Dados do Zendesk
- **`data/indexes/`** - Índices JSONL para busca
- **`data/metadata/`** - Metadados e configurações geradas

**Regra**: Nunca commitar dados grandes. Usar .gitignore apropriado.

#### `docs/` - Documentação
Documentação consolidada e organizada:
- **`docs/guides/`** - Guias de uso (Quick Start, MCP Server, etc.)
- **`docs/architecture/`** - Decisões técnicas e arquitetura
- **`docs/api/`** - Documentação de API (futura)

**Regra**: Manter docs atualizados ao fazer mudanças significativas.

#### `tests/` - Testes
Testes organizados por tipo:
- **`tests/unit/`** - Testes unitários
- **`tests/integration/`** - Testes de integração
- **`tests/e2e/`** - Testes end-to-end
- **`tests/fixtures/`** - Dados de teste

**Regra**: Novos features devem incluir testes.

#### `infra/` - Infraestrutura
Configurações de infraestrutura:
- **`infra/docker/`** - Dockerfiles e docker-compose
- **`infra/ci/`** - CI/CD pipelines

**Regra**: Testar mudanças de Docker localmente antes de commitar.

---

## Melhores Práticas

### 1. Imports
```python
# ✅ CORRETO - Imports absolutos da nova estrutura
from apps.scraper.scraper_unificado import ScraperUnificado
from libs.indexers.index_local import LocalIndexer
from libs.utils.logger import setup_logger

# ❌ ERRADO - Imports antigos (pré-refatoração)
from src.scraper_unificado import ScraperUnificado
from src.indexers.index_local import LocalIndexer
```

### 2. Paths de Arquivos
```python
# ✅ CORRETO - Paths relativos à nova estrutura
config_path = "apps/scraper/config/scraper_config.json"
data_path = "data/scraped/estruturado/"
index_path = "data/indexes/docs_indexacao.jsonl"

# ❌ ERRADO - Paths antigos
config_path = "scraper_config.json"
data_path = "docs_estruturado/"
index_path = "docs_indexacao.jsonl"
```

### 3. Criação de Novos Módulos

**App novo**:
```bash
mkdir -p apps/novo-app/config
touch apps/novo-app/__init__.py
touch apps/novo-app/main.py
touch apps/novo-app/config/config.json
```

**Lib nova**:
```bash
mkdir -p libs/nova-lib
touch libs/nova-lib/__init__.py
touch libs/nova-lib/module.py
```

**Script novo**:
```bash
# Identificar categoria: analysis, indexing, fixes, ou queries
touch scripts/analysis/novo_script.py
```

### 4. Documentação

Ao adicionar features ou fazer mudanças:
1. Atualizar `CHANGELOG.md` com entrada datada
2. Criar/atualizar guia em `docs/guides/` se necessário
3. Documentar breaking changes
4. Atualizar `README.md` se mudar interface pública

### 5. Testes

```bash
# Executar todos os testes
pytest tests/

# Executar categoria específica
pytest tests/integration/
pytest tests/unit/

# Executar arquivo específico
pytest tests/integration/test_mcp_server.py
```

### 6. Docker

```bash
# Build e run local (de dentro de infra/docker/)
cd infra/docker
docker-compose up -d meilisearch
docker-compose up mcp-server

# Verificar logs
docker-compose logs -f mcp-server
```

### 7. Dados

- **Scraping**: Output vai para `data/scraped/`
- **Indexação**: Índices vão para `data/indexes/`
- **Metadados**: JSON files vão para `data/metadata/`
- **Backups**: Usar `backups/` na raiz

---

## Referências Rápidas

### Comandos Principais

```bash
# Scraper
python apps/scraper/scraper_unificado.py

# MCP Server
python apps/mcp-server/mcp_server.py

# Indexação
python scripts/indexing/reindex_all_docs.py

# Testes
pytest tests/

# CI/CD
powershell infra/ci/ci_pipeline.ps1
```

### Estrutura de Imports

```
apps/
  └─ scraper/  ─┐
  └─ mcp-server/ ├──> libs/
  └─ zendesk/   ─┘      └─ scrapers/
                        └─ indexers/
scripts/              └─ utils/
  └─ pode importar de apps/ e libs/
```

### Arquivos de Configuração

- `apps/scraper/config/scraper_config.json` - Config do scraper
- `apps/scraper/config/release_notes_config.json` - Config de release notes
- `apps/mcp-server/mcp_config.json` - Config do MCP server
- `infra/docker/docker-compose.yml` - Orquestração Docker

---

## Breaking Changes (v2.0)

Se estiver migrando código antigo:

1. **Atualizar imports**: `src.*` → `apps.*` ou `libs.*`
2. **Atualizar paths de config**: Mover configs para `apps/*/config/`
3. **Atualizar paths de dados**: Referenciar `data/` ao invés da raiz
4. **Atualizar Docker volumes**: Apontar para novos paths

Ver `REFACTORING_NOTES.md` para detalhes completos da migração.

---

## Suporte

- **Documentação**: Ver `docs/` para guias completos
- **Changelog**: Ver `CHANGELOG.md` para histórico
- **Issues**: Documentar problemas e soluções no projeto
- **Refactoring Notes**: Ver `REFACTORING_NOTES.md` para contexto da migração