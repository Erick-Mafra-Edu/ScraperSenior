# Guia de Scraping: Notas de Versão do Senior ERP

Este guia explica como usar o scraper melhorado para capturar notas de versão e changelogs do Senior ERP X e sistemas relacionados.

## 🎯 Objetivo

Capturar automaticamente todas as notas de versão (release notes) das diferentes versões do Senior ERP, permitindo:
- Busca de mudanças por versão
- Histórico de melhorias e correções
- Rastreamento de features por release

## 📝 Exemplo de URL

```
https://documentacao.senior.com.br/gestao-de-pessoas-hcm/notas-da-versao/#6-10-4.htm
                                                        ^^^^^^^^^^^^^^^^^^
                                                        seção de notas de versão
                                                                         
                                                                         ^^^^^^^^^
                                                                         âncora da versão específica
```

## 🚀 Como Usar

### Opção 1: Descobrir Notas de Versão Automaticamente

```bash
# Gerar configuração de notas de versão
python src/adicionar_notas_versao.py

# Isso cria: release_notes_config.json
```

**Output:**
```json
{
  "GESTAO DE PESSOAS HCM": [
    {
      "url": "https://documentacao.senior.com.br/gestao-de-pessoas-hcm/notas-da-versao/",
      "pattern": "notas-da-versao/"
    }
  ],
  "GESTAOEMPRESARIALERP": [
    {
      "url": "https://documentacao.senior.com.br/gestaoempresarialerp/notas-da-versao/",
      "pattern": "notas-da-versao/"
    }
  ]
}
```

### Opção 2: Scraping de Notas de Versão Manualmente

Adicione URLs de notas de versão diretamente ao `modulos_descobertos.json`:

```json
{
  "GESTAO DE PESSOAS HCM - NOTAS DE VERSÃO": {
    "url": "https://documentacao.senior.com.br/gestao-de-pessoas-hcm/notas-da-versao/",
    "version": "6.10.4",
    "slug": "gestao-de-pessoas-hcm"
  },
  "GESTAOEMPRESARIALERP - NOTAS DE VERSÃO": {
    "url": "https://documentacao.senior.com.br/gestaoempresarialerp/notas-da-versao/",
    "version": "5.10.4",
    "slug": "gestaoempresarialerp"
  }
}
```

Então execute:
```bash
python src/scraper_unificado.py
```

## 🔍 O que o Scraper Faz com Notas de Versão

### Detecção Automática

O scraper identifica automaticamente quando está em uma página de notas de versão:
- Verifica o título da página (contém "versão", "release", "nota")
- Verifica a URL (contém "notas-da-versao", "release-notes")
- Verifica o conteúdo da página

### Extração de Âncoras

Para páginas de notas de versão, o scraper:
1. **Identifica âncoras de versão** (ex: `#6-10-4.htm`, `#5-8-16.htm`)
2. **Converte âncoras em URLs** (ex: `URL#6-10-4.htm`)
3. **Scrapa cada âncora como documento separado**

### Exemplo de Extração

```
Input:  https://documentacao.senior.com.br/gestao-de-pessoas-hcm/notas-da-versao/
        
Âncoras detectadas:
  - #6-10-4.htm
  - #6-10-3.htm
  - #6-10-2.htm
  - #6-10-1.htm
  - #6-9-0.htm

Output: 5 documentos (um por versão)
  - docs_estruturado/GESTAO_DE_PESSOAS_HCM/.../6-10-4/...
  - docs_estruturado/GESTAO_DE_PESSOAS_HCM/.../6-10-3/...
  - etc...
```

## 💾 Estrutura de Saída

Cada versão é salva como documento separado:

```
docs_estruturado/
├── GESTAO_DE_PESSOAS_HCM/
│   └── NOTAS_DE_VERSÃO/
│       ├── 6-10-4/
│       │   ├── content.txt
│       │   ├── metadata.json
│       │   └── page.html (se --save-html)
│       ├── 6-10-3/
│       │   ├── content.txt
│       │   ├── metadata.json
│       │   └── page.html
│       └── ...
└── ...
```

### Metadados de Versão

```json
{
  "title": "Versão 6.10.4",
  "url": "https://documentacao.senior.com.br/gestao-de-pessoas-hcm/notas-da-versao/#6-10-4.htm",
  "breadcrumb": ["GESTAO DE PESSOAS HCM", "NOTAS DE VERSÃO", "6-10-4"],
  "version": "6.10.4",
  "module": "GESTAO_DE_PESSOAS_HCM",
  "has_html": true,
  "total_chars": 2048
}
```

## 🎨 Padrões de URL Suportados

O scraper busca automaticamente por estes padrões:

| Padrão | Exemplo |
|--------|---------|
| `{slug}/notas-da-versao/` | `/gestao-de-pessoas-hcm/notas-da-versao/` |
| `{slug}/release-notes/` | `/gestao-de-pessoas-hcm/release-notes/` |
| `{slug}/notas-de-versao/` | `/gestao-de-pessoas-hcm/notas-de-versao/` |
| `{slug}/changelog/` | `/gestao-de-pessoas-hcm/changelog/` |
| `{slug}/version-history/` | `/gestao-de-pessoas-hcm/version-history/` |
| `{slug}/historico-de-versoes/` | `/gestao-de-pessoas-hcm/historico-de-versoes/` |

## 🔧 Configuração Avançada

### Adicionar Padrão Customizado

Edite `src/adicionar_notas_versao.py` e adicione à lista `RELEASE_NOTES_PATTERNS`:

```python
RELEASE_NOTES_PATTERNS = [
    "{slug}/notas-da-versao/",
    "{slug}/seu-padrao-customizado/",  # Adicione aqui
]
```

### Filtrar por Versão Específica

Se quiser scraping de apenas uma versão:

```python
# No scraper_unificado.py
# Filtrar âncoras por padrão
release_anchors = [a for a in release_anchors if '6-10' in a['href']]
```

## 📊 Buscando Notas de Versão no MCP

Depois do scraping, as notas de versão ficam disponíveis no MCP Server:

### Busca por Versão
```python
# Buscar por versão específica
results = mcp.search_docs("6.10.4", module="GESTAO_DE_PESSOAS_HCM")

# Todos os resultados terão breadcrumb com a versão
# Ex: ["GESTAO_DE_PESSOAS_HCM", "NOTAS_DE_VERSÃO", "6-10-4"]
```

### Busca por Mudança
```python
# Buscar mudanças
results = mcp.search_docs("bug fix", module="GESTAO_DE_PESSOAS_HCM")

# Retorna apenas notas de versão que mencionam "bug fix"
```

### Busca com Filtro de Versão
```python
# Usando breadcrumb
results = [d for d in all_docs if "NOTAS_DE_VERSÃO" in d.get("breadcrumb", [])]
```

## 🚨 Troubleshooting

### "Nenhuma âncora de versão encontrada"

**Causa:** A página de notas de versão usa estrutura diferente

**Solução:**
1. Verifique a URL manualmente: https://documentacao.senior.com.br/gestao-de-pessoas-hcm/notas-da-versao/
2. Se o padrão for diferente, atualize `RELEASE_NOTES_PATTERNS` em `adicionar_notas_versao.py`
3. Se usar navegação em menu, adicione manualmente ao `modulos_descobertos.json`

### Timeout ao carregar notas de versão

**Causa:** Página pesada com muitas âncoras

**Solução:**
```bash
# Aumentar timeout
# Edite scraper_unificado.py, linha 210:
await page.goto(url, wait_until="domcontentloaded", timeout=30000)  # 30s
```

### URLs de âncoras não sendo encontradas

**Causa:** Scraper não detectou como página de versão

**Solução:**
1. Adicione debug:
```python
is_release_notes_page = await page.evaluate("""
    () => {
        console.log('Título:', document.title);
        console.log('URL:', window.location.href);
        // ... resto do código
    }
""")
```

2. Se o padrão for diferente, customize em `extract_release_notes_anchors`

## 📚 Próximos Passos

1. **Execute descobridor:** `python src/adicionar_notas_versao.py`
2. **Scrape:** `python src/scraper_unificado.py`
3. **Teste no MCP:** `python src/mcp_server.py` + busque por versões
4. **Indexe:** O JSONL será gerado automaticamente

## 🎓 Exemplos de Uso

### Exemplo 1: Comparar Mudanças Entre Versões

```python
from src.mcp_server import SeniorDocumentationMCP

mcp = SeniorDocumentationMCP()

# Notas da versão 6.10.4
v6_10_4 = mcp.search_docs("6-10-4", module="GESTAO_DE_PESSOAS_HCM")

# Notas da versão 6.10.3
v6_10_3 = mcp.search_docs("6-10-3", module="GESTAO_DE_PESSOAS_HCM")

# Comparar mudanças
for doc in v6_10_4['results']:
    print(f"v6.10.4: {doc['title']}")
```

### Exemplo 2: Rastrear Features por Release

```python
# Buscar quando feature X foi adicionada
results = mcp.search_docs("nova funcionalidade de relatório")

for doc in results['results']:
    if "NOTAS_DE_VERSÃO" in doc['breadcrumb']:
        version = doc['breadcrumb'][-1]
        print(f"Adicionado em: {version}")
```

## 📖 Referências

- [Scraper Unificado Documentação](../MCP_SERVER.md)
- [Guia de IA e MCP](../MCP_AI_GUIDE.md)
- [README Principal](../README.md)
