# MCP Server - Senior Documentation Search

Servidor Model Context Protocol (MCP) para busca vetorial em documentação Senior Sistemas.

## Features

- 🔍 **Busca Full-Text** em 933 documentos de 17 módulos
- 📦 **Integração com Meilisearch** para busca rápida
- 🗂️ **Filtro por Módulo** para resultados específicos
- 📊 **Metadados Completos** (título, URL, breadcrumb, headers)
- 🔌 **Modo Local** sem dependência de servidor externo para desenvolvimento
- 🏗️ **MCP Protocol** pronto para integração com AI tools

## Estrutura

```
src/
├── mcp_server.py              # Servidor MCP principal
├── test_mcp_server.py         # Testes de funcionalidade
└── indexers/
    ├── index_local.py         # Indexador local (JSONL)
    └── index_meilisearch.py   # Indexador Meilisearch (com conexão real)
```

## Dados

- **Total de Documentos**: 933
- **Módulos Disponíveis**: 17
- **Arquivo de Índice**: `docs_indexacao_detailed.jsonl`
- **Tamanho Total**: ~12.9 MB de conteúdo extraído

### Módulos

- BI
- BPM
- DOCUMENTOSELETRONICOS
- GESTAODEFRETESFIS
- GESTAODELOJAS
- GESTAODETRANSPORTESTMS
- GESTAOEMPRESARIALERP
- GESTAO_DE_PESSOAS_HCM
- GESTAO_DE_RELACIONAMENTO_CRM
- GOUP
- PORTAL
- RONDA_SENIOR
- ROTEIRIZACAOEMONITORAMENTO
- SENIOR_AI_LOGISTICS
- TECNOLOGIA (285 docs)
- WORKFLOW

## Uso

### Iniciar MCP Server

```bash
python src/mcp_server.py
```

**Saída esperada:**
```
[MCP SERVER] Senior Documentation Search
[FERRAMENTAS DISPONÍVEIS]
  • search_docs - Busca documentos por palavras-chave
  • list_modules - Lista todos os módulos disponíveis
  • get_module_docs - Retorna documentos de um módulo
  • get_stats - Retorna estatísticas do índice
```

### Executar Testes

```bash
python src/test_mcp_server.py
```

### Modo Interativo

```python
from src.mcp_server import MCPServer

server = MCPServer()

# Buscar por "CRM"
result = server.handle_tool_call("search_docs", {
    "query": "CRM",
    "limit": 5
})
print(result)

# Listar módulos
modules = server.handle_tool_call("list_modules", {})
print(modules)

# Buscar em módulo específico
result = server.handle_tool_call("search_docs", {
    "query": "relatório",
    "module": "TECNOLOGIA",
    "limit": 3
})
print(result)
```

## Ferramentas Disponíveis

### 1. `search_docs`

Busca documentos por palavras-chave com suporte a filtro por módulo.

**Parâmetros:**
- `query` (string, obrigatório): Palavras-chave para busca
- `module` (string, opcional): Nome do módulo para filtro
- `limit` (number, opcional, padrão: 5): Número de resultados

**Exemplo:**
```json
{
  "query": "Gerador de Relatórios",
  "module": "GESTAOEMPRESARIALERP",
  "limit": 3
}
```

### 2. `list_modules`

Retorna lista de todos os módulos disponíveis.

**Parâmetros:** Nenhum

### 3. `get_module_docs`

Retorna documentos de um módulo específico.

**Parâmetros:**
- `module` (string, obrigatório): Nome do módulo
- `limit` (number, opcional, padrão: 20): Número de resultados

### 4. `get_stats`

Retorna estatísticas do índice de busca.

**Parâmetros:** Nenhum

## Respostas

Todos os resultados retornam JSON com estrutura padronizada:

```json
{
  "query": "busca",
  "count": 3,
  "results": [
    {
      "id": "MODULO_Documento",
      "title": "Título do Documento",
      "url": "https://...",
      "module": "MODULO",
      "breadcrumb": "Módulo > Seção > Subseção",
      "headers_count": 5,
      "content_length": 4738,
      "has_html": false
    }
  ]
}
```

## Configuração

### Modo Local (Padrão)

Carrega índice do arquivo `docs_indexacao_detailed.jsonl`. Sem dependências de servidor.

```bash
python src/mcp_server.py
```

### Modo Meilisearch

Conecta a um servidor Meilisearch em execução.

**Pré-requisitos:**
```bash
# Instalar cliente Meilisearch
pip install meilisearch

# Iniciar servidor
docker-compose up -d meilisearch

# Indexar documentos
python src/indexers/index_meilisearch.py
```

**Usar modo Meilisearch:**
```python
from src.mcp_server import SeniorDocumentationMCP

# Conectará automaticamente se Meilisearch estiver disponível
search = SeniorDocumentationMCP(
    meilisearch_url="http://localhost:7700",
    api_key="meilisearch_master_key"
)
```

## Geração de Índice

### Indexar Localmente

```bash
python src/indexers/index_local.py --debug --search "Gerador de Relatórios"
```

Gera: `docs_indexacao_detailed.jsonl`

### Indexar em Meilisearch

```bash
# Iniciar Meilisearch
docker-compose up -d meilisearch

# Indexar
python src/indexers/index_meilisearch.py --debug
```

## Performance

- **Modo Local**: ~1ms por busca (em memória)
- **Modo Meilisearch**: ~50ms por busca (com rede)
- **Indexação Local**: ~5s para 933 documentos
- **Indexação Meilisearch**: ~30s para 933 documentos

## Próximas Melhorias

- [ ] Suporte a busca vetorial (embedding)
- [ ] Filtro por data de atualização
- [ ] Suporte a HTML original (já extraído, pronto para indexar)
- [ ] Paginação de resultados
- [ ] Destaque de trechos relevantes
- [ ] Busca facetada avançada

## Arquivos Gerados pelo Scraper com `--save-html`

```bash
# Executar scraper salvando HTML original
python src/scraper_unificado.py --save-html
```

Gera estrutura:
```
docs_estruturado/
├── MODULO/
│   ├── Documento/
│   │   ├── content.txt       # Conteúdo extraído
│   │   ├── metadata.json     # Metadados
│   │   └── page.html         # HTML original (com --save-html)
```

## Integração com VS Code

O servidor pode ser integrado com extensões de AI/MCP no VS Code:

```json
{
  "mcpServers": {
    "senior-docs": {
      "command": "python",
      "args": ["/path/to/src/mcp_server.py"]
    }
  }
}
```

## Debug e Desenvolvimento

### Verificar Índice

```bash
python src/indexers/index_local.py --debug --search "Tecnologia"
```

### Testar Busca Específica

```bash
python src/test_mcp_server.py
```

### Ver Arquivo JSONL

```bash
# Primeiras 5 linhas
head -n 5 docs_indexacao_detailed.jsonl | jq .

# Contar documentos
wc -l docs_indexacao_detailed.jsonl
```

## Licença

Desenvolvido para Senior Sistemas
