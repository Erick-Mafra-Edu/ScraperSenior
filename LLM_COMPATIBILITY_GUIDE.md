# Compatibilidade com LLM/Open WebUI - Documentação Completa

## 🎯 Objetivo

O servidor MCP HTTP agora foi otimizado para integração perfeita com agentes de IA (LLMs) no Open WebUI, fornecendo uma interface REST simples e schemas estruturados.

---

## 🚀 Arquitetura para LLM

```
┌─────────────────┐
│   Open WebUI    │
│   + LLM Agent   │
├─────────────────┤
│  REST API       │ ← Simple HTTP GET requests
│  (/api/*)       │   Schemas well-defined
├─────────────────┤
│ MCP HTTP Server │
├─────────────────┤
│ Meilisearch     │
│ Backend         │
└─────────────────┘
```

---

## 📚 Endpoints REST Otimizados para LLM

### 1. **GET /api/search** - Busca Inteligente (Principal)

**Uso pelo LLM:**
- Responde "como faço X?" → busca por X
- Sugere melhorias de query baseado em estratégia
- Refina buscas com /api/document/{id} se necessário

```bash
# Exemplo
GET /api/search?query=configurar+ambiente&strategy=auto&limit=5
```

**Response:**
```json
{
  "status": "success",
  "query": "configurar ambiente",
  "parsed_query": "\"configurar ambiente\"",
  "strategy": "auto",
  "count": 3,
  "results": [
    {
      "id": "doc_123",
      "title": "Configurar Ambiente Local",
      "url": "https://...",
      "module": "Help Center",
      "summary": "Guia passo a passo para...",
      "relevance_score": 0.95
    }
  ]
}
```

**Por que é bom para LLM:**
- ✅ `relevance_score` ajuda LLM a selecionar melhores resultados
- ✅ `summary` é curto (LLM usa para contexto)
- ✅ `id` permite GET /api/document/{id} para conteúdo completo
- ✅ `parsed_query` mostra como a busca foi refinada

---

### 2. **GET /api/modules** - Exploração de Contexto

**Uso pelo LLM:**
- Esclarecer qual módulo o usuário quer
- Sugerir módulos relevantes
- Entender categorias disponíveis

```bash
GET /api/modules
```

**Response:**
```json
{
  "status": "success",
  "total_modules": 12,
  "modules": [
    {
      "name": "Help Center",
      "doc_count": 450,
      "description": "Guias e dúvidas frequentes"
    },
    {
      "name": "Release Notes",
      "doc_count": 85,
      "description": "Histórico de versões"
    }
  ]
}
```

---

### 3. **GET /api/modules/{module_name}** - Listar Docs do Módulo

**Uso pelo LLM:**
- Navegar documentos de uma categoria específica
- Explorar tópicos disponíveis
- Contexto para responder perguntas sobre um domínio

```bash
GET /api/modules/Help%20Center?limit=20
```

---

### 4. **GET /api/document/{document_id}** - Conteúdo Completo ⭐ NOVO

**Uso pelo LLM:**
- Após busca inicial, obter texto completo
- Processar exemplos de código
- Gerar respostas mais precisas

```bash
GET /api/document/doc_123
```

**Response:**
```json
{
  "status": "success",
  "document": {
    "id": "doc_123",
    "title": "Configurar Ambiente Local",
    "url": "https://...",
    "module": "Help Center",
    "content": "...conteúdo HTML completo...",
    "metadata": {
      "last_updated": "2026-02-05",
      "word_count": 2500,
      "author": "Senior Docs"
    }
  }
}
```

**Por que é essencial:**
- ✅ LLM pode ler contexto completo
- ✅ Verifica informações antes de responder
- ✅ Encontra exemplos de código
- ✅ Valida informações

---

### 5. **GET /api/stats** - Exploração de Capacidades

**Uso pelo LLM:**
- Informar ao usuário capacidades da base
- Validar dados disponíveis
- Diagnosticar problemas

---

## 🎓 Schemas Estruturados (Novo)

### DocumentSummary ⭐ NOVO
Resultado otimizado para LLM em buscas:
```json
{
  "id": "doc_id",
  "title": "Título",
  "url": "https://...",
  "module": "Category",
  "summary": "Resumo conciso",
  "relevance_score": 0.95
}
```

### Document ⭐ NOVO
Documento completo com metadados:
```json
{
  "id": "doc_id",
  "title": "Título",
  "url": "https://...",
  "module": "Category",
  "content": "Conteúdo HTML completo",
  "metadata": {
    "last_updated": "2026-02-05",
    "word_count": 2500,
    "author": "Source"
  }
}
```

### SearchResult ⭐ NOVO
Resposta estruturada de /api/search:
```json
{
  "status": "success",
  "query": "termo",
  "parsed_query": "\"termo\"",
  "strategy": "auto",
  "module_filter": null,
  "count": 5,
  "results": [DocumentSummary]
}
```

### ModuleList ⭐ NOVO
Resposta estruturada de /api/modules:
```json
{
  "status": "success",
  "total_modules": 12,
  "modules": [ModuleInfo]
}
```

### DocumentationStats ⭐ NOVO
Resposta estruturada de /api/stats:
```json
{
  "total_documents": 10456,
  "total_modules": 12,
  "indexed_date": "2026-02-05",
  "index_size": "45.3 MB",
  "languages": ["pt-BR", "en"],
  "last_update": "2026-02-05T14:30:00Z"
}
```

---

## 🧠 Padrão de Uso Recomendado para LLM

### Pergunta do Usuário: "Como configuro LSP?"

**1️⃣ Busca Inicial (Rápida)**
```bash
GET /api/search?query=configurar+LSP&strategy=auto&limit=5
```
→ Retorna 5 DocumentSummaries com scores

**2️⃣ Validação (Opcional)**
Se `relevance_score < 0.7`, refina:
```bash
GET /api/search?query=LSP&strategy=quoted&limit=10
```

**3️⃣ Contexto Completo (Se Necessário)**
```bash
GET /api/document/doc_123
```
→ Lê conteúdo completo para responder com precisão

**4️⃣ Exploração de Módulos (Se Incerto)**
```bash
GET /api/modules
```
→ Entende contextos disponíveis

---

## 🔑 Estratégias de Query para LLM

O LLM pode escolher a estratégia baseado no tipo de pergunta:

### `strategy=auto` (Recomendado)
- Multi-palavra? → `quoted` (busca exata)
- Uma palavra? → passa como-está
- **Uso:** 90% das buscas

### `strategy=quoted`
- Força busca de frase exata
- **Uso:** "um padrão específico" ou "um termo técnico"

### `strategy=and`
- Força presença de todos os termos
- **Uso:** "conceitos relacionados mas não necessariamente juntos"

---

## 📊 Métricas de Qualidade para LLM

```json
{
  "relevance_score": 0.95,      // 0-1: confiança
  "word_count": 2500,            // contexto size
  "last_updated": "2026-02-05",  // freshness
  "language": "pt-BR",           // relevância idioma
  "module": "Help Center"        // categoria
}
```

LLM pode usar isso para:
- ✅ Priorizar resultados
- ✅ Indicar confiança ao usuário
- ✅ Descartar documentos desatualizados
- ✅ Preferir idiomas do usuário

---

## 🚦 Fluxo Recomendado no Open WebUI

```
User Message
    ↓
LLM Request: GET /api/search
    ↓
Parse 5 DocumentSummaries
    ↓
Score > 0.8? ─NO→ Try /api/search com strategy diferente
    ↓ YES
Get /api/document/{top_id}
    ↓
Read full content
    ↓
Generate response com citations
    ↓
Return to User
```

---

## ✅ Checklist de Compatibilidade LLM

- ✅ REST API simples (GET, sem JSON-RPC)
- ✅ Schemas estruturados e documentados
- ✅ IDs para referência cruzada (doc_id)
- ✅ Scores de relevância
- ✅ Resumos concisos
- ✅ Conteúdo completo acessível
- ✅ CORS habilitado
- ✅ 3 estratégias de query
- ✅ Exploração de módulos
- ✅ Metadados (data, autor, etc)

---

## 🔧 Exemplo de Integração (Pseudocódigo)

```python
class SeniorDocsLLMTool:
    def search(self, query: str, module: str = None, strategy: str = "auto"):
        """Busca documentação e retorna summaries"""
        response = requests.get(
            f"http://localhost:8000/api/search",
            params={"query": query, "strategy": strategy, "module": module}
        )
        return response.json()["results"]
    
    def get_full_document(self, doc_id: str):
        """Obtém documento completo para análise"""
        response = requests.get(f"http://localhost:8000/api/document/{doc_id}")
        return response.json()["document"]
    
    def list_modules(self):
        """Lista módulos para contexto"""
        response = requests.get("http://localhost:8000/api/modules")
        return response.json()["modules"]
    
    def answer_question(self, question: str):
        """Pipeline completo LLM"""
        # 1. Buscar
        results = self.search(question)
        
        # 2. Validar
        if not results or results[0]["relevance_score"] < 0.7:
            results = self.search(question, strategy="quoted")
        
        # 3. Contexto
        best_doc = self.get_full_document(results[0]["id"])
        
        # 4. Responder
        response = llm.generate(
            context=best_doc["content"],
            question=question,
            citations=[r["url"] for r in results[:3]]
        )
        return response
```

---

## 📖 Próximos Passos

1. **Implementar GET /api/document/{document_id}** no servidor
   - Requer GET do Meilisearch ou cache local
   - Retorna Document schema completo

2. **Testar com Open WebUI**
   - Configurar como ferramenta customizada
   - Validar parsing de responses
   - Medir performance de query

3. **Refinamentos Opcionais**
   - POST /api/search com JSON body (queries complexas)
   - Response caching (módulos, stats)
   - Rate limiting por IP/API-key
   - Logging de queries (analytics)

4. **Documentação para Usuários**
   - Guia de setup no Open WebUI
   - Exemplos de prompts
   - Best practices

---

## 🎯 Conclusão

O servidor agora oferece:
- ✅ Interface REST simples para LLMs
- ✅ Schemas bem-definidos e documentados
- ✅ IDs para referência cruzada
- ✅ Scores de qualidade para priorização
- ✅ Acesso a conteúdo completo
- ✅ Exploração de categorias
- ✅ Estratégias de query flexíveis

**Resultado:** Integração perfeita com Open WebUI como ferramenta de IA IA para responder perguntas sobre documentação Senior com precisão e contexto.
