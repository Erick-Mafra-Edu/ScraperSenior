# MCP Server - Test Suite para Validação via IA

## Formato de Teste
Cada teste segue este formato:
```
TEST #N: [NOME DO TESTE]
├─ Descrição: [O que está sendo testado]
├─ Comando: [Requisição HTTP/JSON-RPC]
├─ Validações: [O que verificar]
├─ Resposta Esperada: [Exemplo de resposta válida]
└─ Status: [✓ PASS / ✗ FAIL]
```

---

## TEST 1: Initialize - Handshake Protocolo MCP

**Descrição:** Verificar se o servidor responde corretamente ao método initialize

**Comando:**
```powershell
$body = @{
  jsonrpc = "2.0"
  id = 1
  method = "initialize"
  params = @{ protocolVersion = "2024-11-05" }
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/" `
  -Method Post -ContentType "application/json" -Body $body -UseBasicParsing

$result = $response.Content | ConvertFrom-Json
```

**Validações:**
- ✓ HTTP Status Code = 200
- ✓ `$result.jsonrpc` = "2.0"
- ✓ `$result.id` = 1
- ✓ `$result.result.serverInfo.name` = "Senior Documentation MCP"
- ✓ `$result.result.protocolVersion` = "2024-11-05"
- ✓ `$result.result.capabilities` é um objeto

**Resposta Esperada:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "resources": {},
      "tools": {},
      "prompts": {}
    },
    "serverInfo": {
      "name": "Senior Documentation MCP",
      "version": "1.0.0"
    }
  }
}
```

---

## TEST 2: Tools List - Listar Ferramentas Disponíveis

**Descrição:** Verificar se o servidor retorna a lista de ferramentas com inputSchema correto

**Comando:**
```powershell
$body = @{
  jsonrpc = "2.0"
  id = 2
  method = "tools/list"
  params = @{}
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/" `
  -Method Post -ContentType "application/json" -Body $body -UseBasicParsing

$result = $response.Content | ConvertFrom-Json
```

**Validações:**
- ✓ HTTP Status Code = 200
- ✓ `$result.result.tools.Count` >= 4
- ✓ Existe ferramenta "search_docs" com `inputSchema.required` contendo "query"
- ✓ Existe ferramenta "list_modules"
- ✓ Existe ferramenta "get_module_docs" com `inputSchema.required` contendo "module"
- ✓ Existe ferramenta "get_stats"

**Resposta Esperada (trecho):**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "search_docs",
        "description": "Busca documentos por palavras-chave",
        "inputSchema": {
          "type": "object",
          "properties": {
            "query": {
              "type": "string",
              "description": "Palavras-chave para busca (obrigatório)"
            },
            "module": {
              "type": "string",
              "description": "Módulo específico para filtrar (opcional)"
            },
            "limit": {
              "type": "integer",
              "description": "Número máximo de resultados (padrão: 5)"
            }
          },
          "required": ["query"]
        }
      },
      {
        "name": "list_modules",
        "description": "Lista todos os módulos disponíveis com contagem de documentos",
        "inputSchema": {
          "type": "object",
          "properties": {},
          "required": []
        }
      }
    ]
  }
}
```

---

## TEST 3: Search Docs - Buscar por "BPM"

**Descrição:** Verificar se search_docs retorna resultados validos para query "BPM"

**Comando:**
```powershell
$body = @{
  jsonrpc = "2.0"
  id = 3
  method = "tools/call"
  params = @{
    name = "search_docs"
    arguments = @{ query = "BPM"; limit = 5 }
  }
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/" `
  -Method Post -ContentType "application/json" -Body $body -UseBasicParsing

$result = $response.Content | ConvertFrom-Json
$data = $result.result.content[0].text | ConvertFrom-Json
```

**Validações:**
- ✓ HTTP Status Code = 200
- ✓ `$data.count` > 0 (encontrou resultados)
- ✓ `$data.query` = "BPM"
- ✓ `$data.results` é um array
- ✓ Cada resultado tem: `id`, `title`, `module`, `url`, `breadcrumb`
- ✓ Todos os módulos são "BPM"

**Resposta Esperada (estrutura):**
```json
{
  "query": "BPM",
  "module_filter": null,
  "count": 5,
  "results": [
    {
      "id": "BPM_Abas_Customizadas",
      "title": "Abas Customizadas",
      "url": "https://documentacao.senior.com.br/bpm/7.0.0/#abas-customizadas.htm",
      "module": "BPM",
      "breadcrumb": "BPM > Customizações",
      "content": "...",
      "type": "documentation"
    }
  ]
}
```

---

## TEST 4: Search Docs - Buscar por "folha" (Genérico)

**Descrição:** Verificar se search_docs encontra resultados para "folha" em qualquer módulo

**Comando:**
```powershell
$body = @{
  jsonrpc = "2.0"
  id = 4
  method = "tools/call"
  params = @{
    name = "search_docs"
    arguments = @{ query = "folha"; limit = 3 }
  }
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/" `
  -Method Post -ContentType "application/json" -Body $body -UseBasicParsing

$result = $response.Content | ConvertFrom-Json
$data = $result.result.content[0].text | ConvertFrom-Json
```

**Validações:**
- ✓ HTTP Status Code = 200
- ✓ `$data.count` >= 0 (pode ou não ter resultados)
- ✓ `$data.query` = "folha"
- ✓ Se `count > 0`, verificar estrutura de resultados

**Resposta Esperada (com resultados):**
```json
{
  "query": "folha",
  "module_filter": null,
  "count": 3,
  "results": [
    {
      "id": "GESTAO_DE_PESSOAS_HCM_...",
      "title": "Folha de Pagamento",
      "module": "GESTAO_DE_PESSOAS_HCM",
      "url": "https://...",
      "type": "documentation"
    }
  ]
}
```

---

## TEST 5: Search Docs Filtrado - "folha" em HCM

**Descrição:** Verificar se search_docs com module filter funciona corretamente

**Comando:**
```powershell
$body = @{
  jsonrpc = "2.0"
  id = 5
  method = "tools/call"
  params = @{
    name = "search_docs"
    arguments = @{
      query = "folha"
      module = "GESTAO_DE_PESSOAS_HCM"
      limit = 3
    }
  }
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/" `
  -Method Post -ContentType "application/json" -Body $body -UseBasicParsing

$result = $response.Content | ConvertFrom-Json
$data = $result.result.content[0].text | ConvertFrom-Json
```

**Validações:**
- ✓ HTTP Status Code = 200
- ✓ `$data.query` = "folha"
- ✓ `$data.module_filter` = "GESTAO_DE_PESSOAS_HCM"
- ✓ Se `count > 0`, todos os resultados devem ter `module` = "GESTAO_DE_PESSOAS_HCM"

**Resposta Esperada:**
```json
{
  "query": "folha",
  "module_filter": "GESTAO_DE_PESSOAS_HCM",
  "count": 3,
  "results": [
    {
      "module": "GESTAO_DE_PESSOAS_HCM",
      "title": "..."
    }
  ]
}
```

---

## TEST 6: List Modules - Listar Todos os Módulos

**Descrição:** Verificar se list_modules retorna exatamente 17 módulos

**Comando:**
```powershell
$body = @{
  jsonrpc = "2.0"
  id = 6
  method = "tools/call"
  params = @{
    name = "list_modules"
    arguments = @{}
  }
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/" `
  -Method Post -ContentType "application/json" -Body $body -UseBasicParsing

$result = $response.Content | ConvertFrom-Json
$data = $result.result.content[0].text | ConvertFrom-Json
```

**Validações:**
- ✓ HTTP Status Code = 200
- ✓ `$data.total_modules` = 17
- ✓ `$data.modules` é um array com 17 elementos
- ✓ Array contém: "BPM", "GESTAO_DE_PESSOAS_HCM", "GESTAO_DE_RELACIONAMENTO_CRM", etc.
- ✓ Nenhum módulo é vazio ou null

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

## TEST 7: Get Module Docs - Documentos do BPM

**Descrição:** Verificar se get_module_docs retorna documentos de um módulo específico

**Comando:**
```powershell
$body = @{
  jsonrpc = "2.0"
  id = 7
  method = "tools/call"
  params = @{
    name = "get_module_docs"
    arguments = @{
      module = "BPM"
      limit = 2
    }
  }
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/" `
  -Method Post -ContentType "application/json" -Body $body -UseBasicParsing

$result = $response.Content | ConvertFrom-Json
$data = $result.result.content[0].text | ConvertFrom-Json
```

**Validações:**
- ✓ HTTP Status Code = 200
- ✓ `$data.count` > 0
- ✓ `$data.module` = "BPM"
- ✓ `$data.results.Length` <= 2 (respeitou limit)
- ✓ Todos os resultados têm `module` = "BPM"

**Resposta Esperada:**
```json
{
  "module": "BPM",
  "count": 10,
  "limit": 2,
  "results": [
    {
      "id": "BPM_...",
      "title": "...",
      "module": "BPM",
      "url": "https://..."
    }
  ]
}
```

---

## TEST 8: Get Stats - Estatísticas do Índice

**Descrição:** Verificar se get_stats retorna informações válidas

**Comando:**
```powershell
$body = @{
  jsonrpc = "2.0"
  id = 8
  method = "tools/call"
  params = @{
    name = "get_stats"
    arguments = @{}
  }
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/" `
  -Method Post -ContentType "application/json" -Body $body -UseBasicParsing

$result = $response.Content | ConvertFrom-Json
$data = $result.result.content[0].text | ConvertFrom-Json
```

**Validações:**
- ✓ HTTP Status Code = 200
- ✓ `$data.total_documents` > 0
- ✓ `$data.total_modules` = 17
- ✓ `$data.total_documents` >= 933 (mínimo esperado)
- ✓ `$data.indexed_at` não é null

**Resposta Esperada:**
```json
{
  "total_documents": 933,
  "total_modules": 17,
  "modules_distribution": {
    "BPM": 50,
    "GESTAO_DE_PESSOAS_HCM": 120
  },
  "indexed_at": "2026-01-21T16:00:00Z"
}
```

---

## TEST 9: Error Handling - Query Vazia

**Descrição:** Verificar se search_docs retorna erro quando query está vazia

**Comando:**
```powershell
$body = @{
  jsonrpc = "2.0"
  id = 9
  method = "tools/call"
  params = @{
    name = "search_docs"
    arguments = @{ query = "" }
  }
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/" `
  -Method Post -ContentType "application/json" -Body $body -UseBasicParsing

$result = $response.Content | ConvertFrom-Json
```

**Validações:**
- ✓ HTTP Status Code = 200
- ✓ `$result.error` existe OU `$result.result.count` = 0
- ✓ Se erro: `$result.error.code` = -32600 (invalid params)

**Resposta Esperada:**
```json
{
  "jsonrpc": "2.0",
  "id": 9,
  "error": {
    "code": -32600,
    "message": "query é obrigatório"
  }
}
```

---

## TEST 10: Error Handling - Módulo Inexistente

**Descrição:** Verificar comportamento com módulo que não existe

**Comando:**
```powershell
$body = @{
  jsonrpc = "2.0"
  id = 10
  method = "tools/call"
  params = @{
    name = "get_module_docs"
    arguments = @{ module = "MODULO_INEXISTENTE" }
  }
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/" `
  -Method Post -ContentType "application/json" -Body $body -UseBasicParsing

$result = $response.Content | ConvertFrom-Json
$data = $result.result.content[0].text | ConvertFrom-Json
```

**Validações:**
- ✓ HTTP Status Code = 200
- ✓ `$data.count` = 0 (nenhum resultado encontrado)
- ✓ `$data.results` é um array vazio

**Resposta Esperada:**
```json
{
  "module": "MODULO_INEXISTENTE",
  "count": 0,
  "limit": 20,
  "results": []
}
```

---

## Resumo de Testes

| # | Teste | Status | Validação |
|---|-------|--------|-----------|
| 1 | Initialize | ? | Handshake correto |
| 2 | Tools List | ? | 4+ ferramentas com inputSchema |
| 3 | Search BPM | ? | Encontra resultados |
| 4 | Search Folha | ? | Query genérica |
| 5 | Search HCM Folha | ? | Filtro por módulo |
| 6 | List Modules | ? | 17 módulos |
| 7 | Get Module Docs | ? | Documentos de BPM |
| 8 | Get Stats | ? | Estatísticas |
| 9 | Error Query Vazia | ? | Trata erro |
| 10 | Error Módulo Inválido | ? | Retorna vazio |

---

## Como Executar Todos os Testes

```powershell
# Script para executar todos os 10 testes
for ($i = 1; $i -le 10; $i++) {
  Write-Host "Executando TEST #$i..." -ForegroundColor Cyan
  # [Executar teste correspondente]
  Write-Host ""
}
```

## Para a IA Validar

A IA pode usar este arquivo para:
1. ✅ Executar cada teste sequencialmente
2. ✅ Comparar respostas com os valores esperados
3. ✅ Relatar quais testes passaram/falharam
4. ✅ Sugerir correções se algum teste falhar

**Modelo de Resposta:**
```
TEST #X: [NOME]
├─ Status: ✓ PASS / ✗ FAIL
├─ Validações Passadas: 5/5
├─ Tempo de Resposta: 234ms
└─ Observações: [Detalhes adicionais]
```
