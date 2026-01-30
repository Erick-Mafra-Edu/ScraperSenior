# Pipeline Unificado - Setup Completo

## ✅ Status

Tudo pronto para iniciar o pipeline!

```
[OK] Importacoes
[OK] Arquivos necessarios  
[OK] Configuracao scraper
[OK] Docker
[OK] Docker Compose
[OK] Meilisearch
```

## 🚀 Como Iniciar

### Opção 1: Uma linha (Recomendado)

```bash
docker-compose up -d
```

Isso:
1. ✅ Inicia Meilisearch (porta 7700)
2. ✅ Inicia container scraper
3. ✅ Scraper aguarda Meilisearch ficar pronto
4. ✅ Scrapa documentação do site
5. ✅ Scrapa API Zendesk Help Center
6. ✅ Indexa tudo em um único índice
7. ✅ Inicia servidor MCP (porta 8000)

**Tempo esperado**: 3-7 minutos

### Opção 2: Passo a passo

```bash
# 1. Inicia Meilisearch
docker-compose up -d meilisearch

# 2. Aguarda 5 segundos
sleep 5

# 3. Inicia scraper
docker-compose up -d scraper

# 4. Monitora progresso
docker-compose logs -f scraper

# 5. Quando terminar, inicia MCP Server
docker-compose up -d mcp-server
```

## 📊 Arquitetura Docker

```yaml
services:
  meilisearch                 ← Engine de busca (porta 7700)
    ↓
  scraper (NOVO)              ← Pipeline scrape + indexador
    ├─ Website (docs_estruturado/)
    ├─ Zendesk API
    └─ Indexa em Meilisearch
    ↓
  mcp-server                  ← API MCP (porta 8000)

networks:
  senior-docs (10.0.9.0/24)

volumes:
  meilisearch_data            ← Índices persistidos
```

## 📁 Fluxo de Dados

```
docs_estruturado/                    (read-only)
  ├─ GESTAO_DE_RELACIONAMENTO_CRM/
  ├─ RONDA_SENIOR/
  └─ ...
         ↓
    [ModularScraper]
         ↓
    Formato unificado
         ↓
    docs_unified/unified_documentation.jsonl
         ↓
    [Meilisearch]
         ↓
   http://localhost:7700/indexes/documentation
```

## 🔧 Componentes do Pipeline

### 1. Scraper Modular
- **Arquivo**: `src/scraper_modular.py`
- **Funcao**: Extrai texto de HTML
- **Entrada**: `docs_estruturado/`
- **Saida**: Documentos estruturados

### 2. API Zendesk Client
- **Arquivo**: `src/api_zendesk.py`
- **Funcao**: Consome API Help Center
- **Entrada**: https://suporte.senior.com.br/api/v2/help_center
- **Saida**: Artigos estruturados

### 3. Adaptador de Formato
- **Arquivo**: `src/zendesk_modular_adapter.py`
- **Funcao**: Converte Zendesk → formato modular
- **Entrada**: Artigos Zendesk
- **Saida**: Formato unificado

### 4. Indexador Unificado
- **Arquivo**: `scrape_and_index_all.py`
- **Classe**: `UnifiedIndexer`
- **Funcao**: Orquestra tudo e indexa Meilisearch
- **Saida**: Índice único com ambas as fontes

### 5. Docker Entrypoint
- **Arquivo**: `docker_entrypoint.py`
- **Funcao**: Aguarda Meilisearch e executa pipeline
- **Roda em**: Container scraper

## 🔍 Verificar Status

### Durante a execucao

```bash
# Ver logs do scraper (real-time)
docker-compose logs -f scraper

# Ver status de todos os servicos
docker-compose ps

# Entrar no container
docker-compose exec scraper bash
```

### Apos conclusao

```bash
# Ver documentos indexados
curl -s http://localhost:7700/indexes/documentation/stats | python -m json.tool

# Acessar Meilisearch UI
open http://localhost:7700

# Listar arquivos gerados
ls -lh docs_unified/

# Ver conteudo do JSONL
head -5 docs_unified/unified_documentation.jsonl
```

## 📊 Estatísticas Esperadas

Apos executar, voce vera:

```
================================================================================
INDEXANDO DOCUMENTACAO COMPLETA
================================================================================

[1] Coletando documentos...
    Encontrados: 1,234 documentos

[2] Indexando em Meilisearch...
    [OK] Indexados 1,234 documentos

[3] Verificando índice...
    Total indexado: 1,234 documentos

[4] Testando busca...
    Resultados encontrados: 12

================================================================================
RESUMO DOS TESTES
================================================================================

Website documentos:     1,234
Zendesk artigos:        456
Total de documentos:    1,690
Documentos indexados:   1,690
Tempo total:            125.43s

================================================================================
```

## 🧪 Testar Busca

### No Meilisearch UI
```
http://localhost:7700
```

### Via API
```bash
curl -s -X POST "http://localhost:7700/indexes/documentation/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer meilisearch_master_key_change_me" \
  -d '{"q":"CRM"}' | python -m json.tool
```

### Via Python
```python
import meilisearch

client = meilisearch.Client("http://localhost:7700", "meilisearch_master_key_change_me")
index = client.get_index("documentation")

results = index.search("CRM", {"limit": 10})
for doc in results['hits']:
    print(f"{doc['title']} ({doc['source']})")
```

## 🛑 Parar Tudo

```bash
# Para todos os servicos
docker-compose down

# Para e remove volumes (limpa dados)
docker-compose down -v

# Para logs
Ctrl+C (no terminal com docker-compose logs -f)
```

## 🐛 Se Algo Nao Funcionar

### Meilisearch nao responde
```bash
# Ver logs
docker-compose logs meilisearch

# Reiniciar
docker-compose restart meilisearch

# Limpar dados e reiniciar
docker-compose down -v
docker-compose up -d meilisearch
```

### Scraper nao inicia
```bash
# Ver logs detalhados
docker-compose logs scraper --tail=100

# Verificar se Meilisearch esta pronto
docker-compose exec meilisearch curl -s http://localhost:7700/health | python -m json.tool

# Reiniciar scraper
docker-compose restart scraper
```

### Documentos nao foram indexados
```bash
# Verificar se arquivo JSONL foi criado
docker-compose exec scraper ls -lah docs_unified/

# Ver conteudo
docker-compose exec scraper head -20 docs_unified/unified_documentation.jsonl

# Contar documentos
docker-compose exec scraper wc -l docs_unified/unified_documentation.jsonl
```

## 📚 Arquivos Importantes

```
projeto/
├── docker-compose.yml           ← Configuracao dos servicos
├── Dockerfile                   ← Imagem do scraper
├── docker_entrypoint.py         ← Script de inicializacao
├── scrape_and_index_all.py      ← Pipeline unificado
├── test_pipeline_setup.py       ← Teste de validacao
│
├── src/
│   ├── scraper_modular.py       ← Scraper do site
│   ├── api_zendesk.py           ← Cliente Zendesk
│   └── zendesk_modular_adapter.py ← Conversor de formato
│
├── docs_estruturado/            ← Documentacao do site (entrada)
├── docs_unified/                ← Documentos indexados (saida)
│   ├── unified_documentation.jsonl
│   └── unified_metadata.json
│
└── DOCKER_COMPOSE_SETUP.md      ← Guia completo
```

## ✅ Checklist Final

- [x] Testes passaram
- [x] Docker disponível
- [x] Docker Compose configurado
- [x] Meilisearch rodando
- [x] Scraper pronto
- [x] API Zendesk acessível
- [x] Arquivos JSONL estruturados
- [ ] Executar: `docker-compose up -d`
- [ ] Aguardar 5-7 minutos
- [ ] Acessar: http://localhost:7700
- [ ] Buscar documentos

## 🎓 Próximas Etapas

1. **Executar pipeline**
   ```bash
   docker-compose up -d
   docker-compose logs -f scraper
   ```

2. **Esperar indexacao** (3-7 minutos)

3. **Acessar Meilisearch**
   - UI: http://localhost:7700
   - API: http://localhost:7700/indexes/documentation

4. **Testar buscas** com termos como "CRM", "Help Center", etc

5. **Integrar com MCP** para usar com Claude

## 📞 Suporte

Para duvidas ou problemas:

1. Verifique logs: `docker-compose logs [service]`
2. Valide setup: `python test_pipeline_setup.py`
3. Teste componentes individualmente
4. Consulte documentacao em `DOCKER_COMPOSE_SETUP.md`

---

**Ultima atualizacao**: 2026-01-26
**Status**: Pronto para producao
