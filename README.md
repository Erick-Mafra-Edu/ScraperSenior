# Senior Documentation Scraper

Scraper automatizado de documentação técnica Senior Sistemas com MCP Server para busca.

## Quickstart

``````bash
# Setup
pip install -r requirements.txt
playwright install chromium

# Executar scraper
python src/scraper_unificado.py

# MCP Server (busca)
python src/mcp_server.py

# Testes
python src/test_mcp_server.py
``````

**Output**:
- `docs_estruturado/` - Documentação estruturada por módulo
- `docs_indexacao_detailed.jsonl` - Índice de busca (933 documentos)
- `docs_metadata.json` - Metadados

## Estrutura do Projeto

``````
src/
 scraper_unificado.py   # Scraper principal (MadCap + Astro)
 mcp_server.py          # MCP Server para busca
 test_mcp_server.py     # Testes MCP
 scrapers/              # Módulos de scraping
 indexers/              # Indexação
    index_local.py     # Indexador JSONL
    index_meilisearch.py # Indexador Meilisearch
 pipelines/             # Pipelines de processamento
 utils/                 # Utilitários comuns

docs_estruturado/              # Documentação extraída
docs_indexacao_detailed.jsonl  # Índice para busca
docker-compose.yml             # Docker com Meilisearch
MCP_SERVER.md                  # Documentação MCP
``````

## Formatos Suportados

- **MadCap Flare** (15 módulos) - Extração hierárquica com expansão de menu
- **Astro** (1 módulo) - Navegação direta via sidebar

## MCP Server (NEW)

Servidor Model Context Protocol para busca em documentação com 4 ferramentas:

1. **search_docs** - Busca full-text com filtro por módulo
2. **list_modules** - Lista módulos disponíveis
3. **get_module_docs** - Documentos de um módulo
4. **get_stats** - Estatísticas do índice

### Uso

``````bash
# Iniciar servidor
python src/mcp_server.py

# Usar (Python)
from src.mcp_server import MCPServer
server = MCPServer()
result = server.handle_tool_call("search_docs", {"query": "CRM"})
``````

Ver [MCP_SERVER.md](MCP_SERVER.md) para documentação completa.

## Melhorias Implementadas

-  Detecção automática de formato
-  Expansão agressiva de menus (até 5 rounds)
-  Retry com backoff exponencial
-  CSS seletores múltiplos
-  Validação de conteúdo
-  Organização hierárquica com breadcrumb
-  **Opção --save-html para preservar HTML original**
-  **Indexação local (JSONL) sem dependência de servidor**
-  **Meilisearch integration para produção**
-  **MCP Server para AI integration**

## Docker (Meilisearch)

``````bash
# Iniciar Meilisearch
docker-compose up -d meilisearch

# Indexar documentos
python src/indexers/index_meilisearch.py
``````

## Configuração

Copiar `.env.example` para `.env` se necessário.

---

Ver [CHANGELOG.md](CHANGELOG.md) para histórico e [MCP_SERVER.md](MCP_SERVER.md) para guia completo do MCP Server.
