# Copilot Instructions - Senior Documentation Scraper

## Arquitetura do Projeto

Este projeto utiliza **Hexagonal Architecture (Ports & Adapters)** dentro de uma estrutura **monorepo**.

### Princípios Arquiteturais

1. **Hexagonal Architecture**: Core isolado de frameworks e detalhes técnicos
2. **Dependency Inversion**: Core depende de abstrações (ports), não de implementações
3. **Clean Architecture**: Camadas com dependências unidirecionais
4. **SOLID Principles**: Aplicados em todas as camadas

---

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
Código reutilizável seguindo **Hexagonal Architecture**:

**`libs/scrapers/`** - Core do sistema de scraping (Hexagonal Architecture):
```
libs/scrapers/
├── domain/              # Entidades e Value Objects (núcleo)
│   ├── document.py          # Document entity
│   ├── scraping_result.py   # ScrapingResult value object
│   └── metadata.py          # DocumentMetadata value object
│
├── ports/               # Interfaces (contratos)
│   ├── document_scraper.py      # IDocumentScraper
│   ├── document_repository.py   # IDocumentRepository
│   ├── content_extractor.py     # IContentExtractor
│   └── url_resolver.py          # IUrlResolver
│
├── use_cases/           # Lógica de negócio
│   ├── scrape_documentation.py  # ScrapeDocumentation
│   ├── extract_release_notes.py # ExtractReleaseNotes
│   └── index_documents.py       # IndexDocuments
│
└── adapters/            # Implementações concretas
    ├── senior_doc_adapter.py    # SeniorDocAdapter
    ├── zendesk_adapter.py       # ZendeskAdapter
    ├── filesystem_repository.py # FileSystemRepository
    └── playwright_extractor.py  # PlaywrightExtractor
```

**`libs/indexers/`** - Indexadores (JSONL local + Meilisearch)
**`libs/pipelines/`** - Data pipelines e transformações
**`libs/utils/`** - Funções utilitárias compartilhadas

**Regras**:
- Libs não devem importar de `apps/`, apenas de outras `libs/`
- **Domain** não depende de nada (núcleo puro)
- **Ports** definem contratos (interfaces abstratas)
- **Use Cases** dependem apenas de **Domain** e **Ports**
- **Adapters** implementam **Ports** e podem depender de frameworks

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

## Hexagonal Architecture - Padrões e Convenções

### Fluxo de Dependências

```
┌─────────────────────────────────────────────────────────┐
│                    APPLICATION CORE                      │
│                                                           │
│  Domain (entities) ← Ports (interfaces) ← Use Cases     │
│                                                           │
└─────────────────────────────────────────────────────────┘
                            ▲
                            │ depends on
                            │
┌───────────────────────────┴─────────────────────────────┐
│                     ADAPTERS                             │
│  (implementam ports, conhecem frameworks)                │
└──────────────────────────────────────────────────────────┘
```

**Regra de Ouro**: Dependências sempre apontam para dentro (core).

### Camadas da Arquitetura Hexagonal

#### 1. **Domain Layer** (`libs/scrapers/domain/`)
- **O que é**: Entidades e Value Objects do negócio
- **Depende de**: Nada (núcleo puro)
- **Responsabilidade**: Representar conceitos de negócio
- **Exemplo**: `Document`, `ScrapingResult`, `DocumentMetadata`

```python
# ✅ CORRETO - Domain puro
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Document:
    id: str
    title: str
    content: str
    # Sem dependências externas!
```

#### 2. **Ports Layer** (`libs/scrapers/ports/`)
- **O que é**: Interfaces (contratos) que definem operações
- **Depende de**: Domain apenas
- **Responsabilidade**: Definir contratos entre core e mundo externo
- **Exemplo**: `IDocumentScraper`, `IDocumentRepository`

```python
# ✅ CORRETO - Port (interface)
from abc import ABC, abstractmethod
from libs.scrapers.domain import Document

class IDocumentScraper(ABC):
    @abstractmethod
    async def scrape(self, url: str) -> Document:
        pass
```

#### 3. **Use Cases Layer** (`libs/scrapers/use_cases/`)
- **O que é**: Lógica de negócio que orquestra operações
- **Depende de**: Domain + Ports (apenas interfaces)
- **Responsabilidade**: Coordenar fluxo de trabalho
- **Exemplo**: `ScrapeDocumentation`, `ExtractReleaseNotes`

```python
# ✅ CORRETO - Use Case
from libs.scrapers.domain import Document, ScrapingResult
from libs.scrapers.ports import IDocumentScraper, IDocumentRepository

class ScrapeDocumentation:
    def __init__(
        self,
        scrapers: List[IDocumentScraper],  # Depende de interface!
        repository: IDocumentRepository,   # Não de implementação!
    ):
        self.scrapers = scrapers
        self.repository = repository
    
    async def execute(self, urls: List[str]) -> ScrapingResult:
        # Lógica de negócio aqui
        pass
```

#### 4. **Adapters Layer** (`libs/scrapers/adapters/`)
- **O que é**: Implementações concretas dos ports
- **Depende de**: Ports (implementa) + Frameworks externos
- **Responsabilidade**: Conectar core com tecnologias específicas
- **Exemplo**: `SeniorDocAdapter`, `PlaywrightExtractor`

```python
# ✅ CORRETO - Adapter
from playwright.async_api import async_playwright
from libs.scrapers.ports import IDocumentScraper
from libs.scrapers.domain import Document

class SeniorDocAdapter(IDocumentScraper):
    """Implementa IDocumentScraper para Senior Docs"""
    
    async def scrape(self, url: str) -> Document:
        # Usa Playwright (framework externo)
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            # ... scraping logic
            return Document(...)
```

### Criando Novos Componentes

#### ✅ Criar Nova Entidade (Domain)

```python
# libs/scrapers/domain/nova_entidade.py
from dataclasses import dataclass

@dataclass
class MinhaEntidade:
    """Entidade de negócio pura - sem dependências externas"""
    id: str
    nome: str
    
    def metodo_de_negocio(self) -> str:
        # Lógica de negócio pura
        return self.nome.upper()
```

#### ✅ Criar Novo Port (Interface)

```python
# libs/scrapers/ports/meu_port.py
from abc import ABC, abstractmethod
from typing import List
from libs.scrapers.domain import MinhaEntidade

class IMeuPort(ABC):
    """Define contrato para operação X"""
    
    @abstractmethod
    async def fazer_algo(self, param: str) -> MinhaEntidade:
        """Docstring explicando o contrato"""
        pass
```

#### ✅ Criar Novo Use Case

```python
# libs/scrapers/use_cases/meu_use_case.py
from libs.scrapers.domain import MinhaEntidade
from libs.scrapers.ports import IMeuPort

class MeuUseCase:
    """Orquestra lógica de negócio"""
    
    def __init__(self, port: IMeuPort):
        self.port = port  # Depende de interface!
    
    async def execute(self, param: str) -> MinhaEntidade:
        # Lógica de negócio orquestrando ports
        resultado = await self.port.fazer_algo(param)
        # Processar resultado...
        return resultado
```

#### ✅ Criar Novo Adapter

```python
# libs/scrapers/adapters/meu_adapter.py
from libs.scrapers.ports import IMeuPort
from libs.scrapers.domain import MinhaEntidade

class MeuAdapter(IMeuPort):
    """Implementação concreta de IMeuPort"""
    
    async def fazer_algo(self, param: str) -> MinhaEntidade:
        # Implementação usando tecnologias específicas
        # (banco de dados, APIs, scraping, etc.)
        return MinhaEntidade(id="1", nome=param)
```

### Dependency Injection Pattern

```python
# apps/scraper/main.py (Bootstrap)

# 1. Criar adapters (implementações)
scraper_adapter = SeniorDocAdapter(extractor=PlaywrightExtractor())
zendesk_adapter = ZendeskAdapter(extractor=PlaywrightExtractor())
repository = FileSystemRepository(output_dir="data/scraped/")

# 2. Injetar no use case
use_case = ScrapeDocumentation(
    scrapers=[scraper_adapter, zendesk_adapter],
    repository=repository
)

# 3. Executar
result = await use_case.execute(urls=["https://..."])
```

### Testes com Mocks

```python
# tests/unit/test_use_case.py
from unittest.mock import AsyncMock
from libs.scrapers.use_cases import ScrapeDocumentation

async def test_scrape_documentation():
    # Mock dos ports
    mock_scraper = AsyncMock(IDocumentScraper)
    mock_repository = AsyncMock(IDocumentRepository)
    
    # Use case testável sem adapters reais!
    use_case = ScrapeDocumentation(
        scrapers=[mock_scraper],
        repository=mock_repository
    )
    
    result = await use_case.execute(["https://test.com"])
    
    # Assertions...
```

### Anti-Patterns (❌ Evitar)

```python
# ❌ ERRADO - Domain dependendo de framework
from playwright.async_api import Page

@dataclass
class Document:
    page: Page  # NÃO! Domain não pode depender de Playwright

# ❌ ERRADO - Use Case dependendo de implementação
from libs.scrapers.adapters.senior_doc_adapter import SeniorDocAdapter

class ScrapeDocumentation:
    def __init__(self, scraper: SeniorDocAdapter):  # NÃO! Depende de implementação
        pass

# ❌ ERRADO - Adapter no domain
from libs.scrapers.adapters import FileSystemRepository

@dataclass
class Document:
    def save(self):
        repo = FileSystemRepository()  # NÃO! Domain não chama adapters
        repo.save(self)
```

---

## Melhores Práticas

### 1. Imports (Hexagonal Architecture)

```python
# ✅ CORRETO - Use Case importando apenas abstrações
from libs.scrapers.domain import Document, ScrapingResult
from libs.scrapers.ports import IDocumentScraper, IDocumentRepository

class MeuUseCase:
    def __init__(
        self,
        scraper: IDocumentScraper,      # Interface, não implementação
        repository: IDocumentRepository  # Interface, não implementação
    ):
        pass

# ✅ CORRETO - Adapter implementando interface
from libs.scrapers.ports import IDocumentScraper
from libs.scrapers.domain import Document
import external_framework  # OK em adapters

class MeuAdapter(IDocumentScraper):
    async def scrape(self, url: str) -> Document:
        # Pode usar frameworks externos aqui
        pass

# ❌ ERRADO - Use Case dependendo de adapter
from libs.scrapers.adapters.senior_doc_adapter import SeniorDocAdapter

class MeuUseCase:
    def __init__(self, scraper: SeniorDocAdapter):  # NÃO!
        pass
```

### 2. Imports Gerais
```python
# ✅ CORRETO - Imports absolutos da nova estrutura
from apps.scraper.scraper_unificado import ScraperUnificado
from libs.indexers.index_local import LocalIndexer
from libs.utils.logger import setup_logger

# ❌ ERRADO - Imports antigos (pré-refatoração)
from src.scraper_unificado import ScraperUnificado
from src.indexers.index_local import LocalIndexer
```

### 3. Paths de Arquivos
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

### 4. Criação de Novos Módulos (Hexagonal)

**Domain Entity**:
```bash
# Criar nova entidade de negócio
touch libs/scrapers/domain/nova_entidade.py
# Adicionar em libs/scrapers/domain/__init__.py
```

**Port (Interface)**:
```bash
# Criar nova interface
touch libs/scrapers/ports/novo_port.py
# Adicionar em libs/scrapers/ports/__init__.py
```

**Use Case**:
```bash
# Criar novo caso de uso
touch libs/scrapers/use_cases/novo_use_case.py
# Adicionar em libs/scrapers/use_cases/__init__.py
```

**Adapter**:
```bash
# Criar nova implementação
touch libs/scrapers/adapters/novo_adapter.py
# Não adicionar em __init__.py (injetado via DI)
```

### 5. Criação de Novos Módulos (Geral)

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

### 6. Documentação

Ao adicionar features ou fazer mudanças:
1. Atualizar `CHANGELOG.md` com entrada datada
2. Criar/atualizar guia em `docs/guides/` se necessário
3. Documentar breaking changes
4. Atualizar `README.md` se mudar interface pública

### 7. Testes (Hexagonal)

**Testes Unitários (Domain & Use Cases)**:
```python
# tests/unit/domain/test_document.py
from libs.scrapers.domain import Document

def test_document_word_count():
    doc = Document(
        id="1", url="test", title="Test",
        content="Hello world", module="test"
    )
    assert doc.word_count() == 2

# tests/unit/use_cases/test_scrape_documentation.py
from unittest.mock import AsyncMock
from libs.scrapers.use_cases import ScrapeDocumentation

async def test_execute_with_mocked_scraper():
    mock_scraper = AsyncMock()
    mock_repository = AsyncMock()
    
    use_case = ScrapeDocumentation(
        scrapers=[mock_scraper],
        repository=mock_repository
    )
    # Test sem dependências reais!
```

**Testes de Integração (Adapters)**:
```python
# tests/integration/adapters/test_senior_doc_adapter.py
from libs.scrapers.adapters import SeniorDocAdapter

async def test_senior_doc_adapter_real_scraping():
    adapter = SeniorDocAdapter()
    doc = await adapter.scrape("https://real-url.com")
    assert doc.title
    await adapter.close()
```

### 8. Testes Gerais

```bash
# Executar todos os testes
pytest tests/

# Executar categoria específica
pytest tests/integration/
pytest tests/unit/

# Executar arquivo específico
pytest tests/integration/test_mcp_server.py
```

### 9. Docker

```bash
# Build e run local (de dentro de infra/docker/)
cd infra/docker
docker-compose up -d meilisearch
docker-compose up mcp-server

# Verificar logs
docker-compose logs -f mcp-server
```

### 10. Dados

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

## Checklist para Novos Features (Hexagonal)

Ao adicionar um novo feature de scraping:

- [ ] **Domain**: Criar/atualizar entidades se necessário
- [ ] **Port**: Definir interface se for nova operação
- [ ] **Use Case**: Implementar lógica de negócio
- [ ] **Adapter**: Implementar conexão com tecnologia específica
- [ ] **Tests**: Unit tests (use cases) + Integration tests (adapters)
- [ ] **Bootstrap**: Adicionar DI no main.py
- [ ] **Docs**: Atualizar documentação

## Exemplos Rápidos

### Adicionar Novo Scraper (ex: Confluence)

```python
# 1. Criar Adapter
# libs/scrapers/adapters/confluence_adapter.py
from libs.scrapers.ports import IDocumentScraper
from libs.scrapers.domain import Document, DocumentSource, DocumentType

class ConfluenceAdapter(IDocumentScraper):
    async def scrape(self, url: str) -> Document:
        # Implementação específica
        return Document(
            id=url,
            url=url,
            title="...",
            content="...",
            module="confluence",
            doc_type=DocumentType.TECHNICAL_DOC,
            source=DocumentSource.UNKNOWN  # Adicionar CONFLUENCE no enum
        )
    
    def supports_url(self, url: str) -> bool:
        return "confluence" in url.lower()

# 2. Registrar no Bootstrap
# apps/scraper/main.py
confluence = ConfluenceAdapter(extractor=PlaywrightExtractor())
use_case = ScrapeDocumentation(
    scrapers=[senior_adapter, zendesk_adapter, confluence],  # Adicionar
    repository=repository
)
```

### Adicionar Novo Repositório (ex: MongoDB)

```python
# 1. Criar Adapter
# libs/scrapers/adapters/mongodb_repository.py
from libs.scrapers.ports import IDocumentRepository
from libs.scrapers.domain import Document

class MongoDBRepository(IDocumentRepository):
    def __init__(self, connection_string: str):
        # Setup MongoDB
        pass
    
    async def save(self, document: Document) -> None:
        # Salvar no MongoDB
        pass
    
    # Implementar outros métodos do IDocumentRepository...

# 2. Usar no Bootstrap
repository = MongoDBRepository("mongodb://localhost:27017/docs")
use_case = ScrapeDocumentation(scrapers, repository)
```

## Suporte

- **Documentação**: Ver `docs/` para guias completos
- **Changelog**: Ver `CHANGELOG.md` para histórico
- **Issues**: Documentar problemas e soluções no projeto
- **Refactoring Notes**: Ver `REFACTORING_NOTES.md` para contexto da migração
- **Hexagonal Plan**: Ver session workspace `hexagonal-plan.md` para detalhes da arquitetura