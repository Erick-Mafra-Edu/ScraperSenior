# Scraper Unificado + Meilisearch

Integração completa de múltiplas fontes de documentação em um único índice Meilisearch.

## 🎯 O que faz

```
┌─────────────────────────────────────────────────────┐
│  SCRAPER UNIFICADO + MEILISEARCH                    │
└─────────────────────────────────────────────────────┘

Website (docs_estruturado/) ─┐
                             ├─→ Scraper Modular
Zendesk API ────────────────┤
                             ├─→ Adaptador
                             │
                             ├─→ Formato Unificado (JSONL)
                             │
                             └─→ Meilisearch
                                 (documentação)
```

## 📦 Fontes de Dados

### 1. Documentação do Site
- **Origem**: `docs_estruturado/`
- **Scraper**: `scraper_modular.py`
- **Formato**: HTML → Texto → JSONL
- **Características**:
  - Suporte a iframes (MadCap Flare)
  - Limpeza de lixo (padrões configuráveis)
  - Normalização de URLs com âncoras

### 2. Zendesk Help Center
- **Origem**: `https://suporte.senior.com.br/api/v2/help_center`
- **Scraper**: `api_zendesk.py`
- **Formato**: JSON API → JSONL
- **Características**:
  - Paginação automática
  - Todas as categorias e seções
  - Metadata completa (datas, IDs)

## 🚀 Uso Rápido

### Opção 1: Pipeline Completo (Recomendado)

```bash
# Inicia Docker + Scrapa + Indexa tudo
python docker_orchestrator.py --action all
```

Este comando:
1. ✅ Inicia Meilisearch em Docker
2. ✅ Scrapa documentação do site
3. ✅ Scrapa artigos Zendesk
4. ✅ Indexa tudo em um único índice
5. ✅ Verifica resultado

**Tempo esperado**: 2-5 minutos (depende do tamanho)

### Opção 2: Etapas Separadas

```bash
# 1. Inicia apenas o Meilisearch
python docker_orchestrator.py --action setup

# 2. Executa scrapers + indexação
python docker_orchestrator.py --action scrape

# 3. Verifica status
python docker_orchestrator.py --action index

# 4. Para quando terminar
python docker_orchestrator.py --action cleanup
```

### Opção 3: Scraper Direto (sem Docker)

```bash
# Requer Meilisearch já rodando em http://localhost:7700
python scrape_and_index_all.py --url http://localhost:7700 --api-key meilisearch_master_key
```

## 📋 Arquivos de Saída

Após executar, você terá:

```
docs_unified/
├── unified_documentation.jsonl  ← Todos os documentos em formato único
└── unified_metadata.json        ← Estatísticas e índice de documentos
```

### Formato Unificado (JSONL)

Cada linha é um documento JSON:

```json
{
  "id": "zendesk_12345",
  "type": "zendesk_article",
  "url": "https://suporte.senior.com.br/...",
  "title": "Como Usar CRM",
  "content": "Lorem ipsum dolor sit amet...",
  "module": "Help Center",
  "breadcrumb": "Help Center > pt-BR",
  "source": "zendesk_api",
  "metadata": {
    "source": "zendesk_help_center",
    "scraped_at": "2026-01-26T10:00:00",
    "category_id": 1,
    "section_id": 2
  }
}
```

## 🔍 Testando a Busca

### Opção 1: Via Meilisearch Web UI

```
http://localhost:7700
```

### Opção 2: Via API

```bash
# Listar todos os documentos
curl -X GET "http://localhost:7700/indexes/documentation/documents" \
  -H "Authorization: Bearer meilisearch_master_key"

# Buscar
curl -X POST "http://localhost:7700/indexes/documentation/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer meilisearch_master_key" \
  -d '{"q":"CRM"}'
```

### Opção 3: Python

```python
import meilisearch

client = meilisearch.Client("http://localhost:7700", "meilisearch_master_key")
index = client.get_index("documentation")

# Buscar
results = index.search("CRM")
for doc in results['hits']:
    print(f"{doc['title']} ({doc['source']})")
```

## ⚙️ Configuração Avançada

### Customizar Meilisearch URL

```bash
python scrape_and_index_all.py --url http://seu-servidor:7700 --api-key sua-chave
```

### Limitar Artigos Zendesk

Edite `scrape_and_index_all.py` linha ~130:

```python
scraper.limit_articles = 100  # Limita a 100 artigos para teste
```

### Customizar Tamanho de Conteúdo

Edite `scrape_and_index_all.py`:

```python
'content': article.body[:5000],  # Muda para o número desejado
```

## 📊 Estatísticas

O script mostra ao final:

```
================================================================================
📊 ESTATÍSTICAS FINAIS
================================================================================
Website documentos:     1,234
Zendesk artigos:        456
Total de documentos:    1,690
Documentos indexados:   1,690
Tempo total:            125.43s
================================================================================
```

## 🐛 Troubleshooting

### Meilisearch não inicia

```bash
# Verifique Docker
docker ps

# Verifique logs
docker-compose logs meilisearch

# Tente reiniciar
docker-compose restart meilisearch
```

### Zendesk API lenta/indisponível

O script tem retry automático. Se continuar:

```bash
# Teste conectividade
curl -I https://suporte.senior.com.br/api/v2/help_center/pt-br/articles.json

# Teste manualmente
python -c "
from src.api_zendesk import ZendeskScraper
import asyncio
asyncio.run(ZendeskScraper().scrape_all())
"
```

### Índice vazio

```bash
# Verifique se os arquivos foram criados
ls -lah docs_unified/

# Verifique o conteúdo
head -5 docs_unified/unified_documentation.jsonl
```

## 📚 Estrutura do Código

```
scrape_and_index_all.py     ← Orquestrador principal
├── UnifiedIndexer          ← Classe que combina tudo
│   ├── scrape_website_docs()    ← Lê docs_estruturado/
│   ├── scrape_zendesk_docs()    ← Chama API Zendesk
│   ├── save_unified_jsonl()     ← Salva em formato único
│   └── index_documents()        ← Indexa no Meilisearch
│
docker_orchestrator.py      ← Gerencia Docker e pipeline
├── docker_compose_up()      ← Inicia Meilisearch
├── run_scraper_and_indexer()   ← Executa scraper
└── verify_index()           ← Verifica resultado

src/
├── scraper_modular.py       ← Scraper do site
├── api_zendesk.py           ← Cliente Zendesk
└── zendesk_modular_adapter.py   ← Conversor de formato
```

## 🎓 Exemplos de Uso

### Exemplo 1: Scrape + Indexação Automática

```bash
python docker_orchestrator.py --action all
```

### Exemplo 2: Apenas Website (sem Zendesk)

```bash
# Edite scrape_and_index_all.py, comente a função scrape_zendesk_docs()
python scrape_and_index_all.py
```

### Exemplo 3: Apenas Zendesk (sem Website)

```bash
# Edite scrape_and_index_all.py, comente a função scrape_website_docs()
python scrape_and_index_all.py
```

### Exemplo 4: Testar com Dados Pequenos

```bash
# Edite scrape_and_index_all.py, linha ~130
scraper.limit_articles = 10  # Apenas 10 artigos

python scrape_and_index_all.py
```

## 🔐 Segurança

- ⚠️ **NÃO** commit a chave Meilisearch em repositório
- ✅ Use variáveis de ambiente para chaves em produção:

```bash
export MEILISEARCH_API_KEY="sua-chave-secreta"
python scrape_and_index_all.py --api-key $MEILISEARCH_API_KEY
```

## 📈 Performance

| Operação | Tempo Esperado |
|----------|---|
| Setup Docker | 10-30s |
| Scrape Website (1000+ docs) | 1-2 min |
| Scrape Zendesk (100+ artigos) | 30-60s |
| Indexação Meilisearch | 20-40s |
| **Total** | **3-5 min** |

## 🚀 Próximas Etapas

1. **Integração MCP**: Use com Claude para consultas inteligentes
2. **Busca Avançada**: Configure filtros por módulo/source
3. **Auto-Sync**: Configure cronjob para atualizar regularmente
4. **Replicação**: Replique índice entre ambientes

## 📞 Suporte

Se tiver problemas:

1. ✅ Verifique logs: `docker-compose logs`
2. ✅ Teste conectividade: `curl http://localhost:7700/health`
3. ✅ Valide JSON: `cat docs_unified/unified_documentation.jsonl | python -m json.tool`
4. ✅ Verifique permissões: `ls -l docs_unified/`

## 📝 Changelog

- **v1.0** (2026-01-26): Lançamento inicial
  - Integração website + Zendesk
  - Indexação Meilisearch
  - Docker orchestration
  - Formato unificado JSONL
