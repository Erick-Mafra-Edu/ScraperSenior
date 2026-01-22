# 🔍 DIAGNÓSTICO: Ausência de Conteúdo no Scraping

## 📋 O QUE FOI FEITO

### 1. **Reindexação Completa (855 documentos)**
- ✅ Docker-compose buildado com sucesso
- ✅ Arquivo `docs_indexacao_detailed.jsonl` gerado (3 MB)
- ✅ Meilisearch indexando documentos
- ✅ MCP Server respondendo às ferramentas de busca

### 2. **Ferramentas do MCP Funcionando**
```
✅ search_docs        - Busca por palavras-chave
✅ get_module_docs    - Retorna docs de um módulo
✅ list_modules       - Lista 16 módulos disponíveis
✅ get_stats          - Retorna estatísticas
✅ (6/6 ferramentas)  - Bug fix completo
```

### 3. **Resultados Encontrados**
- **Consultas SQL**: 10 resultados (funcionando!)
- **Gerador de Relatórios**: 6 documentos encontrados
- **Específicas do Gerador**: Encontrado, mas **TRUNCADO**

---

## ⚠️ O PROBLEMA IDENTIFICADO

### **Conteúdo Truncado em 5000 caracteres**

**Arquivo**: [scraper_unificado.py](src/scraper_unificado.py#L549)

```python
# LINHA 549 - TRUNCAMENTO
'content': doc['text_content'][:5000],  # ← AQUI! Primeiros 5k chars apenas
```

### **Impacto**

O documento "Específicas do Gerador de Relatórios" contém:
- **Tamanho real**: ~50-100 KB (tabela completa de funções)
- **Tamanho indexado**: ~1 KB (truncado para 5000 caracteres)
- **Resultado**: Funções específicas não aparecem nos resultados de busca

### **Por que não encontramos:**
- `AdicionaCondicao()` ❌ Truncada
- `AdicionaCaminho()` ❌ Truncada
- `GetSQLError()` ❌ Truncada
- `StatusCode()` ❌ Truncada

---

## 🛠️ COMO DEBUGAR

### **Etapa 1: Verificar Arquivo Fonte**

```powershell
# Procurar documento truncado
cd c:\Users\Digisys\scrapyTest
$doc = Get-Content docs_indexacao_detailed.jsonl | ConvertFrom-Json | `
  Where-Object { $_.title -like "*Específicas*" } | Select-Object -First 1

# Ver tamanho real vs indexado
Write-Host "Conteúdo: $($doc.content.Length) caracteres (deve ser 5000 ou menos)"
Write-Host "Content_Length field: $($doc.content_length) caracteres (real antes de truncar)"
```

### **Etapa 2: Verificar Arquivo Estruturado**

```powershell
# Procurar arquivo original na pasta
dir docs_estruturado -Recurse -Filter "*Gerador*" | ForEach-Object {
  Write-Host "Arquivo: $($_.FullName)"
  $size = (Get-Item $_).Length
  Write-Host "Tamanho: $size bytes"
}
```

### **Etapa 3: Rastrear o Scraper**

```python
# Adicionar logging ao scraper_unificado.py (linha 545-550)
print(f"[DEBUG] Conteúdo original: {len(doc['text_content'])} chars")
print(f"[DEBUG] Conteúdo indexado: {len(doc['text_content'][:5000])} chars")
print(f"[DEBUG] Primeiras 100 chars: {doc['text_content'][:100]}")
print(f"[DEBUG] Chars 4900-5000: {doc['text_content'][4900:5000]}")
```

### **Etapa 4: Verificar no MCP Server**

```powershell
# Consultar o servidor com debug
$body = @{
  jsonrpc="2.0"
  id=1
  method="tools/call"
  params=@{
    name="search_docs"
    arguments=@{
      query="AdicionaCondicao"
      limit=10
    }
  }
} | ConvertTo-Json

$response = (Invoke-WebRequest -Uri "http://localhost:8000/v1/messages" `
  -Method Post -Body $body -ContentType "application/json" `
  -UseBasicParsing).Content | ConvertFrom-Json

# Analisar resultado
$response.content[0].text | ConvertFrom-Json | Select-Object -Property query, count
```

---

## 🔧 SOLUÇÕES RECOMENDADAS

### **Opção 1: Aumentar Limite de Truncamento** (Rápido)

```python
# scraper_unificado.py, linha 549
# DE:
'content': doc['text_content'][:5000],  # 5KB

# PARA:
'content': doc['text_content'][:20000],  # 20KB (para tabelas de funções)
# OU:
'content': doc['text_content'][:50000],  # 50KB (completo para docs técnicos)
```

**Impacto**: 
- ✅ Recupera conteúdo completo
- ❌ Aumenta tamanho do índice (~10-15 MB)

### **Opção 2: Indexação Seletiva** (Melhor)

```python
# Aumentar apenas para documentos técnicos
if 'LSP' in doc['breadcrumb'] or 'Funções' in doc['breadcrumb']:
    content_limit = 50000  # Docs técnicos: completo
else:
    content_limit = 5000   # Docs normais: 5KB

'content': doc['text_content'][:content_limit],
```

### **Opção 3: Campo Separado para Funções** (Profissional)

```python
# Adicionar campo especial para tabelas
index_doc = {
    'content': doc['text_content'][:5000],
    'technical_reference': doc.get('tables', [])[:10],  # Novo campo
    'function_names': extract_function_names(doc['text_content'])
}
```

---

## 📊 ANÁLISE DO ÍNDICE ATUAL

```
Estatísticas:
├── Total de documentos: 855
├── Tamanho do arquivo: 3 MB
├── Documento truncado em: 5000 caracteres
├── Função original: ~50-100 KB
└── Perda de conteúdo: 95-99% 😞
```

### **Estrutura Atual do Documento**
```json
{
  "id": "TECNOLOGIA_652",
  "title": "Específicas do Gerador de Relatórios",
  "module": "TECNOLOGIA",
  "breadcrumb": "TECNOLOGIA > Gerador de Relatórios > Funções",
  "content": "# Funções SQL... [TRUNCADO EM 5000 CHARS]",
  "content_length": 52840,  // ← Campo indica tamanho REAL
  "headers": ["Funções SQL em Regra"],
  "language": "pt-BR"
}
```

---

## 🎯 PRÓXIMOS PASSOS

### **1. Aumentar limite de indexação**
```bash
cd c:\Users\Digisys\scrapyTest
# Editar scraper_unificado.py linha 549
# Aumentar de 5000 para 20000 ou 50000
```

### **2. Reindexar documentos**
```bash
python reindex_all_docs.py
```

### **3. Reiniciar Docker**
```bash
docker-compose down
docker-compose up -d
```

### **4. Testar novamente**
```powershell
# Buscar por função específica
$response = (Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing).Content
if ($response -contains 'healthy') {
  Write-Host "✅ Servidor pronto para testes"
}
```

---

## 📝 RESUMO

| Aspecto | Status | Problema |
|--------|--------|----------|
| Scraping | ✅ Funcionando | Conteúdo truncado |
| Indexação | ✅ 855 docs | Limite 5000 chars |
| MCP Server | ✅ Respondendo | Dados incompletos |
| Busca SQL | ✅ 10 resultados | Funções não encontradas |
| Gerador Relatórios | ⚠️ Encontrado | 95% do conteúdo perdido |

---

## 🚀 AÇÃO IMEDIATA

Para recuperar as funções do Gerador de Relatórios:

1. **Editar** [scraper_unificado.py](src/scraper_unificado.py#L549)
   - Linha 549: mudar `[:5000]` para `[:50000]`

2. **Executar**:
   ```bash
   python reindex_all_docs.py
   docker-compose restart mcp-server
   ```

3. **Verificar**:
   ```powershell
   # Buscar por função
   mcp_senior-docs-d_search_docs -query "AdicionaCondicao" -limit 10
   ```

4. **Resultado esperado**: ✅ Funções aparecerão nos resultados!
