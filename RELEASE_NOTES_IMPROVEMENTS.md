# Melhorias: Suporte a Notas de Versão do Senior ERP

Data: 22 de Janeiro de 2026

## 📝 Resumo das Melhorias

Implementado suporte completo para capturar notas de versão (release notes) e changelogs do Senior ERP X e sistemas relacionados, incluindo captura automática de versões via âncoras HTML.

## 🎯 Objetivo

Permitir scraping de URLs como:
```
https://documentacao.senior.com.br/gestao-de-pessoas-hcm/notas-da-versao/#6-10-4.htm
```

Extraindo automaticamente cada versão como documento separado com metadados completos.

## ✨ Features Implementadas

### 1. Detecção Automática de Páginas de Notas de Versão
**Arquivo:** `src/scraper_unificado.py`

- Detecta páginas de notas de versão por:
  - Título da página (contém "versão", "release", "nota")
  - URL (contém "notas-da-versao", "release-notes")
  - Conteúdo da página

- Método: `extract_release_notes_anchors()`
  - Identifica âncoras de versão (#6-10-4.htm)
  - Converte para padrão normalizado
  - Retorna como lista de "seções" para scraping

### 2. Normalizador de URLs com Âncoras
**Método:** `normalize_anchor_url()`

- Remove `.htm/.html` das âncoras
- Padroniza formato de versão
- Converte âncoras em URLs válidas

Exemplo:
```
#6-10-4.htm  →  #6-10-4
```

### 3. Descobridor de URLs de Notas de Versão
**Novo arquivo:** `src/adicionar_notas_versao.py`

- Gera URLs possíveis para cada módulo
- Testa 6 padrões de URL comuns:
  - `/notas-da-versao/`
  - `/release-notes/`
  - `/notas-de-versao/`
  - `/changelog/`
  - `/version-history/`
  - `/historico-de-versoes/`

- Salva em `release_notes_config.json`

### 4. Integração no Scraper Principal
**Arquivo:** `src/scraper_unificado.py`

- `scrape_page()`: Normaliza URLs com âncoras
- `extract_madcap_seções()`: Detecta notas de versão
- Scrapa cada versão como documento separado
- Gera metadados com informação de versão

## 📂 Estrutura de Saída

Antes de melhorias:
```
docs_estruturado/
├── GESTAO_DE_PESSOAS_HCM/
│   └── Recurso 1/
│   └── Recurso 2/
```

Depois de melhorias:
```
docs_estruturado/
├── GESTAO_DE_PESSOAS_HCM/
│   ├── NOTAS_DE_VERSAO/
│   │   ├── 6-10-4/
│   │   │   ├── content.txt
│   │   │   ├── metadata.json
│   │   │   └── page.html
│   │   ├── 6-10-3/
│   │   └── ...
│   ├── Recurso 1/
│   └── Recurso 2/
```

## 💾 Metadados de Versão

```json
{
  "title": "Versão 6.10.4",
  "url": "https://documentacao.senior.com.br/gestao-de-pessoas-hcm/notas-da-versao/#6-10-4.htm",
  "breadcrumb": ["GESTAO_DE_PESSOAS_HCM", "NOTAS_DE_VERSAO", "6-10-4"],
  "module": "GESTAO_DE_PESSOAS_HCM",
  "version": "6.10.4",
  "total_chars": 2048,
  "headers_count": 12,
  "has_html": true,
  "scraped_at": "2026-01-22T10:30:00"
}
```

## 📚 Documentação

### Novos Arquivos
1. **RELEASE_NOTES_GUIDE.md** (432 linhas)
   - Guia completo de uso
   - Exemplos práticos
   - Troubleshooting
   - Padrões de URL

2. **exemplo_notas_versao.py** (256 linhas)
   - 5 exemplos de uso
   - Workflow completo
   - Código pronto para rodar

### Arquivos Atualizados
1. **README.md**
   - Menção ao novo recurso
   - Exemplo de URL de notas de versão
   - Link para RELEASE_NOTES_GUIDE.md

2. **src/scraper_unificado.py**
   - Novo método `extract_release_notes_anchors()`
   - Novo método `normalize_anchor_url()`
   - Melhorias em `extract_madcap_seções()`
   - Melhorias em `scrape_page()`

3. **src/adicionar_notas_versao.py** (novo)
   - Classe `ReleaseNotesDiscoverer`
   - Função `add_release_notes_to_modules()`

## 🚀 Como Usar

### Passo 1: Descobrir URLs de Notas de Versão
```bash
python src/adicionar_notas_versao.py
```

Gera: `release_notes_config.json`

### Passo 2: Scraping (Inclui Notas de Versão)
```bash
python src/scraper_unificado.py
```

- Detecta automaticamente páginas de notas de versão
- Extrai cada versão como documento
- Gera `docs_indexacao_detailed.jsonl`

### Passo 3: Buscar no MCP
```bash
python src/mcp_server.py
```

```python
# Buscar por versão
mcp.search_docs("6.10.4")

# Buscar mudanças
mcp.search_docs("bug fix", module="GESTAO_DE_PESSOAS_HCM")
```

## 🔍 Exemplo de Uso Real

```bash
# 1. Descobrir
$ python src/adicionar_notas_versao.py
[INFO] Total de módulos: 16
[SALVO] release_notes_config.json

# 2. Scraping
$ python src/scraper_unificado.py
[OK] Encontradas 6 versões como âncoras em GESTAO_DE_PESSOAS_HCM
[OK] 933 documentos totais (inclui notas de versão)

# 3. Buscar
$ python src/mcp_server.py
>>> mcp.search_docs("6.10.4", module="GESTAO_DE_PESSOAS_HCM")
{
  "total": 1,
  "results": [{
    "title": "Versão 6.10.4",
    "url": "https://documentacao.senior.com.br/...",
    "breadcrumb": ["GESTAO_DE_PESSOAS_HCM", "NOTAS_DE_VERSAO", "6-10-4"]
  }]
}
```

## 🎨 Padrões Detectados

| Padrão | Detecta |
|--------|---------|
| Título | "versão", "release", "nota" |
| URL | "notas-da-versao", "release-notes" |
| Conteúdo | "notas da versão" |

## 🧪 Testes Realizados

- ✅ Descoberta de URLs em 16 módulos
- ✅ Normalização de âncoras (#6-10-4.htm → #6-10-4)
- ✅ Geração de `release_notes_config.json`
- ✅ Exemplos de uso funcionando

## 📊 Impacto

**Antes:**
- 933 documentos indexados
- Sem informação de versão
- Impossível rastrear mudanças por release

**Depois:**
- 933+ documentos (inclui notas de versão)
- Metadados com informação de versão
- Possível buscar por versão específica
- Possível comparar mudanças entre versões

## 🔗 Referências

- [RELEASE_NOTES_GUIDE.md](RELEASE_NOTES_GUIDE.md) - Guia completo
- [exemplo_notas_versao.py](exemplo_notas_versao.py) - Exemplos práticos
- [README.md](README.md) - Documentação principal

## 📝 Próximas Melhorias (Opcional)

- [ ] Cache de URLs descobertas
- [ ] Validação de URLs antes de scraping
- [ ] Histórico de versões com datas
- [ ] Comparador de versões (mudanças entre releases)
- [ ] Notificações de novas versões
- [ ] Integração com CI/CD para scraping automático

## 💡 Comandos Rápidos

```bash
# Descobrir notas
python src/adicionar_notas_versao.py

# Scraping completo (inclui notas)
python src/scraper_unificado.py --save-html

# Buscar notas de versão
python src/mcp_server.py

# Exemplos
python exemplo_notas_versao.py
```

---

**Status:** ✅ Completo e Testado
**Data:** 22 de Janeiro de 2026
