# Senior Documentation Scraper

Scraper automatizado de documentação técnica Senior Sistemas com MCP Server para busca e suporte a notas de versão.

## Quickstart

```bash
# Setup
pip install -r requirements.txt
playwright install chromium

# Executar scraper (inclui documentação e notas de versão)
python src/scraper_unificado.py

# Descobrir notas de versão por módulo
python src/adicionar_notas_versao.py

# MCP Server (busca)
python src/mcp_server.py

# Testes
python src/test_mcp_server.py
```

**Output**:
- `docs_estruturado/` - Documentação estruturada por módulo (inclui notas de versão)
- `docs_indexacao_detailed.jsonl` - Índice de busca (933+ documentos)
- `docs_metadata.json` - Metadados
- `release_notes_config.json` - Configuração de notas de versão

## Estrutura do Projeto

```
src/
 scraper_unificado.py      # Scraper principal (MadCap + Astro + Release Notes)
 adicionar_notas_versao.py # Descobridor de URLs de notas de versão
 mcp_server.py             # MCP Server para busca
 test_mcp_server.py        # Testes MCP
 indexers/                 # Indexação
    index_local.py        # Indexador JSONL
    index_meilisearch.py  # Indexador Meilisearch

docs_estruturado/              # Documentação estruturada por módulo
docs_indexacao_detailed.jsonl  # Índice para busca
release_notes_config.json      # Configuração de notas de versão
MCP_SERVER.md                  # Documentação MCP
RELEASE_NOTES_GUIDE.md         # Guia de scraping de notas de versão
```

## Formatos Suportados

- **MadCap Flare** (15 módulos) - Extração hierárquica com expansão de menu
- **Astro** (1 módulo) - Navegação direta via sidebar
- **Release Notes** (Múltiplos módulos) - Notas de versão com âncoras (#versão.htm)

## ✨ Novo: Notas de Versão

Agora suporta scraping automático de notas de versão do Senior ERP X:

```bash
# Descobrir URLs de notas de versão
python src/adicionar_notas_versao.py

# Scraping (inclui documentação + notas de versão)
python src/scraper_unificado.py
```

Veja [RELEASE_NOTES_GUIDE.md](RELEASE_NOTES_GUIDE.md) para detalhes completos.

Exemplo de URL:
```
https://documentacao.senior.com.br/gestao-de-pessoas-hcm/notas-da-versao/#6-10-4.htm
```

O scraper detecta automaticamente páginas de notas de versão e extrai cada versão (âncora) como documento separado.

## MCP Server (NEW)

Servidor Model Context Protocol para busca em documenta��o com 4 ferramentas:

1. **search_docs** - Busca full-text com filtro por m�dulo
2. **list_modules** - Lista m�dulos dispon�veis
3. **get_module_docs** - Documentos de um m�dulo
4. **get_stats** - Estat�sticas do �ndice

### Uso

``````bash
# Iniciar servidor
python src/mcp_server.py

# Usar (Python)
from src.mcp_server import MCPServer
server = MCPServer()
result = server.handle_tool_call("search_docs", {"query": "CRM"})
``````

Ver [MCP_SERVER.md](MCP_SERVER.md) para documenta��o completa.

## Melhorias Implementadas

-  Detec��o autom�tica de formato
-  Expans�o agressiva de menus (at� 5 rounds)
-  Retry com backoff exponencial
-  CSS seletores m�ltiplos
-  Valida��o de conte�do
-  Organiza��o hier�rquica com breadcrumb
-  **Op��o --save-html para preservar HTML original**
-  **Indexa��o local (JSONL) sem depend�ncia de servidor**
-  **Meilisearch integration para produ��o**
-  **MCP Server para AI integration**

## Docker (Meilisearch)

``````bash
# Iniciar Meilisearch
docker-compose up -d meilisearch

# Indexar documentos
python src/indexers/index_meilisearch.py
``````

## Configura��o

Copiar `.env.example` para `.env` se necess�rio.

---

Ver [CHANGELOG.md](CHANGELOG.md) para hist�rico e [MCP_SERVER.md](MCP_SERVER.md) para guia completo do MCP Server.
