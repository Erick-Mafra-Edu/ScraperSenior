# Senior Documentation Scraper

> **v2.1** - Multi-Worker Support | Monorepo Architecture | Scraper automatizado de documentação técnica Senior Sistemas

## 🚀 Quick Start

```bash
# Setup
pip install -r requirements.txt
playwright install chromium

# Executar scraper
python apps/scraper/scraper_unificado.py

# MCP Server (busca)
python apps/mcp-server/mcp_server.py

# Testes
pytest tests/
```

## 📁 Estrutura

```
apps/       → Aplicações executáveis (scraper, mcp-server, zendesk)
libs/       → Bibliotecas compartilhadas (scrapers, indexers, utils)
scripts/    → Utilitários (analysis, indexing, fixes, queries)
data/       → Dados e outputs (scraped, indexes, metadata)
docs/       → Documentação completa
tests/      → Testes (unit, integration, e2e)
infra/      → Docker e CI/CD
```

## 📖 Documentação

**Ver [docs/](docs/) para documentação completa** ou acesse diretamente:

- **[Guia Rápido](docs/guides/QUICK_START.md)** - Primeiros passos
- **[MCP Server](docs/guides/MCP_SERVER.md)** - Busca e integração
- **[Release Notes](docs/guides/RELEASE_NOTES_GUIDE.md)** - Scraping de notas
- **[Docker](docs/guides/DOCKER.md)** - Setup de containers
- **[Arquitetura](docs/architecture/)** - Decisões técnicas

## ✨ Features

- **Scraping**: MadCap Flare (15 módulos) + Astro (1 módulo) + Release Notes
- **MCP Server**: 4 ferramentas para busca (search_docs, list_modules, etc.)
- **Indexação**: JSONL local + Meilisearch
- **Docker**: Pronto para produção
- **CI/CD**: Pipeline completo
- **Grounding & Validação**: Sistema de validação de respostas para prevenir hallucinations

## 🛡️ Grounding e Verificação de Respostas

Sistema robusto para validar respostas de modelos de linguagem e prevenir hallucinations, garantindo que todas as respostas sejam fundamentadas em documentos reais.

### Recursos

- **Validação Automática**: Verifica se cada sentença da resposta está suportada pelos documentos recuperados
- **System Prompt Rígido**: Template de prompt que força o modelo a citar fontes e evitar extrapolações
- **Pipeline Completo**: Fluxo integrado de retrieval → geração → validação
- **API REST**: Endpoints dedicados para validação no OpenAPI

### Endpoints REST Disponíveis

#### 1. Validar Resposta Existente

```bash
POST /model/validate-response
```

Verifica se uma resposta já gerada está fundamentada nas passagens fornecidas.

**Exemplo:**
```bash
curl -X POST http://localhost:8000/model/validate-response \
  -H "Content-Type: application/json" \
  -d '{
    "response": "O CRM Senior permite configurar notificações automáticas por email.",
    "retrieved_passages": [
      {
        "id": "doc_123",
        "text": "O módulo CRM oferece configuração de notificações automáticas..."
      }
    ],
    "threshold": 0.75
  }'
```

**Resposta:**
```json
{
  "verified": true,
  "evidence": [
    {
      "sentence": "O CRM Senior permite configurar notificações automáticas por email.",
      "doc_id": "doc_123",
      "score": 0.92
    }
  ],
  "issues": [],
  "overall_confidence": 0.95
}
```

#### 2. Gerar e Validar Resposta

```bash
POST /model/generate-and-validate
```

Realiza o fluxo completo: busca documentos, gera resposta com prompt rígido e valida.

**Exemplo:**
```bash
curl -X POST http://localhost:8000/model/generate-and-validate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Como configurar notificações no CRM?",
    "limit": 5,
    "generation_config": {
      "temperature": 0.1,
      "max_tokens": 1000
    },
    "validation_threshold": 0.75
  }'
```

**Resposta (Verificada):**
```json
{
  "success": true,
  "response": "Para configurar notificações no CRM, acesse Configurações > Notificações [doc_123]...",
  "verification": {
    "verified": true,
    "evidence": [...],
    "overall_confidence": 0.95
  },
  "retrieved_docs": [...]
}
```

**Resposta (Sem Evidência):**
```json
{
  "success": false,
  "response": "Não encontrei evidência nos documentos fornecidos.",
  "verification": {
    "verified": false,
    "issues": [...]
  }
}
```

#### 3. Validar via MCP

```bash
POST /mcp/validate-response
```

Endpoint MCP para validação, idêntico ao `/model/validate-response` mas seguindo namespace MCP.

### Configuração Open WebUI

Para usar com Open WebUI:

1. **Configure o System Prompt** - Use o template em `docs/prompt_templates/grounded_system_prompt.txt`

2. **Configure os Endpoints** - Aponte para:
   - Validação: `http://localhost:8000/model/validate-response`
   - Geração: `http://localhost:8000/model/generate-and-validate`

3. **Ajuste Parâmetros do Modelo**:
   - Temperature: 0.1 (baixa para respostas mais determinísticas)
   - Top P: 0.8
   - Max Tokens: 1000

### Uso Programático

#### Python - Validação Direta

```python
from libs.validators.hallucination_guard import verify_response

result = verify_response(
    response="O CRM permite configurar notificações.",
    retrieved_passages=[
        {"id": "doc_123", "text": "CRM oferece notificações..."}
    ],
    threshold=0.75
)

print(f"Verificado: {result['verified']}")
print(f"Confiança: {result['overall_confidence']}")
```

#### Python - Pipeline Completo

```python
import asyncio
from services.model_pipeline import ModelPipeline

async def main():
    pipeline = ModelPipeline(validation_threshold=0.75)
    
    result = await pipeline.generate_and_validate(
        query="Como configurar notificações no CRM?",
        limit=5
    )
    
    if result.success:
        print(f"Resposta: {result.response}")
    else:
        print("Sem evidência encontrada")

asyncio.run(main())
```

### Arquitetura

```
Query do Usuário
       ↓
1. Retrieval (busca documentos relevantes)
       ↓
2. Rerank (ordena por relevância - opcional)
       ↓
3. Format Prompt (aplica system prompt rígido)
       ↓
4. Generate (modelo gera resposta com citações)
       ↓
5. Validate (verifica cada sentença contra documentos)
       ↓
   ┌─── verified=True → Retorna resposta com citações
   └─── verified=False → "Não encontrei evidência..."
```

### Componentes

- **`libs/validators/hallucination_guard.py`**: Verificador de evidências
- **`services/model_pipeline.py`**: Pipeline completo de geração
- **`docs/prompt_templates/grounded_system_prompt.txt`**: Template de prompt rígido
- **`openapi.json`**: Especificação com endpoints de validação

### Testes

```bash
# Testes unitários
pytest tests/unit/test_hallucination_guard.py -v

# Testes de integração
pytest tests/integration/test_grounding.py -v

# Todos os testes
pytest tests/ -v
```

### Integração com Provedores

O sistema está preparado para integração com:

- **Embeddings**: OpenAI, Cohere, modelos locais (Sentence Transformers)
- **LLM**: OpenAI GPT, Claude, modelos locais (Ollama, LM Studio)
- **Retrieval**: Meilisearch (atual), Elasticsearch, Pinecone

Pontos de integração marcados com `# TODO` no código para facilitar implementação.

---

## 🔄 Changelog

**v2.0.0** (2026-01-30) - Refatoração completa para monorepo
- Nova estrutura: apps/, libs/, scripts/, docs/, data/
- Consolidação de 60+ arquivos markdown
- Organização de código por responsabilidade

Ver [CHANGELOG.md](CHANGELOG.md) para histórico completo.

---

�� **[Documentação Completa](docs/)** | 🐳 **[Docker Setup](infra/docker/)** | 🧪 **[Testes](tests/)**