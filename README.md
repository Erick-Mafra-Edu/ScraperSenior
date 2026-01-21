# Senior Documentation Scraper

Scraper automatizado de documentação técnica Senior Sistemas.

## Quickstart

```bash
# Setup
pip install -r requirements.txt
playwright install chromium

# Executar
python src/scraper_unificado.py
```

**Output**:
- `docs_estruturado/` - Documentação estruturada por módulo
- `docs_indexacao.jsonl` - Índice para busca
- `docs_metadata.json` - Metadados

## Estrutura do Projeto

```
src/
├── scraper_unificado.py  # Scraper principal (MadCap + Astro)
├── scrapers/             # Módulos de scraping
├── indexers/             # Indexação de docs
├── pipelines/            # Pipelines de processamento
└── utils/                # Utilitários comuns

docs_estruturado/        # Documentação extraída (16 módulos)
docker-compose.yml       # Docker com Meilisearch
requirements.txt         # Dependências
```

## Formatos Suportados

- **MadCap Flare** (15 módulos) - Extração hierárquica com expansão de menu
- **Astro** (1 módulo) - Navegação direta via sidebar

## Melhorias Implementadas

- ✅ Detecção automática de formato
- ✅ Expansão agressiva de menus (até 5 rounds)
- ✅ Retry com backoff exponencial
- ✅ CSS seletores múltiplos
- ✅ Validação de conteúdo
- ✅ Organização hierárquica com breadcrumb

## Docker (Meilisearch)

```bash
# Iniciar Meilisearch
docker-compose up -d meilisearch

# Indexar documentos
curl -X POST 'http://localhost:7700/indexes/senior_docs/documents' \
  --data-binary @docs_indexacao.jsonl
```

## Configuração

Copiar `.env.example` para `.env` se necessário.

---

Ver [CHANGELOG.md](CHANGELOG.md) para histórico.
