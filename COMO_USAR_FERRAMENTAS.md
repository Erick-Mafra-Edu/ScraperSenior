# Como Usar as Ferramentas de Documentação Senior ✅

## Status: SERVIDOR 100% FUNCIONAL

O servidor MCP está respondendo corretamente. Todos os parâmetros foram testados e funcionam.

---

## 📋 Ferramentas Disponíveis

### 1️⃣ search_docs (BUSCAR DOCUMENTOS)

**Parâmetros:**
- `query` ⭐ **OBRIGATÓRIO** - Palavra-chave para buscar
- `module` (opcional) - Filtrar por módulo específico
- `limit` (opcional) - Número máximo de resultados (padrão: 5)

**Exemplos de Uso:**

```javascript
// Buscar "BPM" em toda documentação
search_docs({"query": "BPM"})

// Buscar "folha" apenas em GESTAO_DE_PESSOAS_HCM
search_docs({"query": "folha", "module": "GESTAO_DE_PESSOAS_HCM"})

// Buscar "integração" com limite de 10 resultados
search_docs({"query": "integração", "limit": 10})

// Buscar "relatório" em BI com 3 resultados
search_docs({"query": "relatório", "module": "BI", "limit": 3})
```

**Resposta Esperada:**
```json
{
  "query": "BPM",
  "module_filter": null,
  "count": 5,
  "results": [
    {
      "id": "BPM_Abas_Customizadas",
      "title": "Abas Customizadas",
      "url": "https://documentacao.senior.com.br/bpm/7.0.0/#...",
      "module": "BPM",
      "breadcrumb": "BPM",
      "content": "...",
      "content_length": 5395
    },
    // ... mais 4 documentos
  ]
}
```

---

### 2️⃣ get_module_docs (LISTAR DOCS DE UM MÓDULO)

**Parâmetros:**
- `module` ⭐ **OBRIGATÓRIO** - Nome do módulo
- `limit` (opcional) - Número máximo de resultados (padrão: 20)

**Exemplos de Uso:**

```javascript
// Obter todos os documentos de BPM (até 20)
get_module_docs({"module": "BPM"})

// Obter 5 primeiros documentos de BI
get_module_docs({"module": "BI", "limit": 5})

// Obter 10 documentos de GESTAO_DE_PESSOAS_HCM
get_module_docs({"module": "GESTAO_DE_PESSOAS_HCM", "limit": 10})

// Obter 3 documentos de Workflow
get_module_docs({"module": "WORKFLOW", "limit": 3})
```

**Resposta Esperada:**
```json
{
  "module": "BPM",
  "count": 2,
  "docs": [
    {
      "id": "BPM_Abas_Customizadas",
      "title": "Abas Customizadas",
      "url": "https://documentacao.senior.com.br/bpm/7.0.0/#...",
      "module": "BPM",
      "content": "...",
      "content_length": 5395
    },
    {
      "id": "BPM_Analytics",
      "title": "Analytics",
      "url": "https://documentacao.senior.com.br/bpm/7.0.0/#...",
      "module": "BPM",
      "content": "...",
      "content_length": 4407
    }
  ]
}
```

---

### 3️⃣ list_modules (LISTAR MÓDULOS)

**Parâmetros:** Nenhum

**Exemplos de Uso:**

```javascript
// Listar todos os módulos disponíveis
list_modules()
```

**Resposta Esperada:**
```json
{
  "total_modules": 17,
  "modules": [
    "BI",
    "BPM",
    "DOCUMENTOSELETRONICOS",
    "GESTAODEFRETESFIS",
    "GESTAODELOJAS",
    "GESTAODETRANSPORTESTMS",
    "GESTAOEMPRESARIALERP",
    "GESTAO_DE_PESSOAS_HCM",
    "GESTAO_DE_RELACIONAMENTO_CRM",
    "GOUP",
    "PORTAL",
    "RONDA_SENIOR",
    "ROTEIRIZACAOEMONITORAMENTO",
    "SENIOR_AI_LOGISTICS",
    "TECNOLOGIA",
    "WORKFLOW",
    "s"
  ]
}
```

---

### 4️⃣ get_stats (ESTATÍSTICAS)

**Parâmetros:** Nenhum

**Exemplos de Uso:**

```javascript
// Obter estatísticas da base
get_stats()
```

**Resposta Esperada:**
```json
{
  "total_documents": 933,
  "modules": 17,
  "has_html": 0,
  "source": "local"
}
```

---

## 🔍 Casos de Uso Práticos

### Cenário 1: "Preciso aprender sobre BPM"
```javascript
// Passo 1: Buscar documentação geral
search_docs({"query": "BPM", "limit": 5})

// Resultado: 5 documentos sobre BPM da base inteira
```

### Cenário 2: "Preciso de tudo sobre um módulo específico"
```javascript
// Passo 1: Descobrir módulos disponíveis
list_modules()

// Resultado: Lista com 17 módulos

// Passo 2: Obter todos os docs do módulo desejado
get_module_docs({"module": "BPM", "limit": 20})

// Resultado: Até 20 documentos do módulo BPM
```

### Cenário 3: "Preciso buscar um tópico específico em um módulo"
```javascript
// Buscar "folha" apenas em GESTAO_DE_PESSOAS_HCM
search_docs({"query": "folha", "module": "GESTAO_DE_PESSOAS_HCM", "limit": 5})

// Resultado: Documentos com "folha" apenas do módulo HCM
```

### Cenário 4: "Quero explorar tudo o que temos"
```javascript
// Passo 1: Ver estatísticas
get_stats()
// Resultado: 933 documentos, 17 módulos

// Passo 2: Listar todos os módulos
list_modules()
// Resultado: Lista de todos os módulos

// Passo 3: Para cada módulo, pegar primeiros documentos
get_module_docs({"module": "BPM", "limit": 3})
get_module_docs({"module": "BI", "limit": 3})
// etc...
```

---

## ✅ Validação Testada

### Teste 1: search_docs com query
```bash
POST http://localhost:8000/
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search_docs",
    "arguments": {
      "query": "BPM"
    }
  }
}
```
**Resultado:** ✅ **5 documentos retornados**

### Teste 2: get_module_docs com module
```bash
POST http://localhost:8000/
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "get_module_docs",
    "arguments": {
      "module": "BPM",
      "limit": 2
    }
  }
}
```
**Resultado:** ✅ **2 documentos retornados**

### Teste 3: list_modules
```bash
POST http://localhost:8000/
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "list_modules",
    "arguments": {}
  }
}
```
**Resultado:** ✅ **17 módulos listados**

---

## 🐛 Por Que Recebeu Erro?

O erro que você recebeu ocorre quando:

1. **A IA chama `search_docs()` SEM `query`**
   ```javascript
   ❌ search_docs()  // Falta query!
   ❌ search_docs({"limit": 5})  // Falta query!
   ✅ search_docs({"query": "BPM"})  // Correto!
   ```

2. **A IA chama `get_module_docs()` SEM `module`**
   ```javascript
   ❌ get_module_docs()  // Falta module!
   ❌ get_module_docs({"limit": 5})  // Falta module!
   ✅ get_module_docs({"module": "BPM"})  // Correto!
   ```

**O servidor está correto!** Retorna erro apropriado quando parâmetros obrigatórios faltam.

---

## 🚀 Próximos Passos

### Se usando Claude Desktop:
1. Copiar exemplos acima
2. Colar em novo chat
3. Pedir: "Busque documentação sobre X usando essas ferramentas"
4. Claude verá os exemplos e saberá como chamar

### Se usando VS Code:
Verificar se extensão MCP está instalada e configurada corretamente.

---

**Data**: 22 de Janeiro de 2026  
**Status**: ✅ FERRAMENTAS 100% FUNCIONAL  
**Servidor**: Respondendo corretamente - 933 documentos indexados
