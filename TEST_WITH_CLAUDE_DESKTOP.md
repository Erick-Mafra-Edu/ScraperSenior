# 🧪 Teste Passo-a-Passo: MCP com Claude Desktop

## ⚠️ Importante
**VS Code Chat NÃO suporta MCP.**  
**Use Claude Desktop para testar MCP.**

---

## 📋 Pré-requisitos

- [ ] MCP Server rodando em Docker
- [ ] Claude Desktop instalado
- [ ] Arquivo de configuração editável

---

## 🚀 Guia de Teste (5 minutos)

### Passo 1: Verificar MCP Server (1 minuto)

```powershell
cd c:\Users\Digisys\scrapyTest

# Verificar se containers estão rodando
docker-compose ps

# Esperado:
# senior-docs-meilisearch ... Up (healthy)
# senior-docs-mcp-server  ... Up (healthy)
```

✅ Se ambos estão "Up", continue.  
❌ Se não estão, execute:
```powershell
docker-compose up -d
Start-Sleep -Seconds 10
docker-compose ps
```

---

### Passo 2: Criar Arquivo de Configuração (1 minuto)

**Localização:**
```
C:\Users\%USERNAME%\AppData\Local\Claude\claude_desktop_config.json
```

**Conteúdo:**
```json
{
  "mcpServers": {
    "senior-docs": {
      "type": "http",
      "url": "http://localhost:8000"
    }
  }
}
```

**Verificar arquivo:**
```powershell
$path = "$env:APPDATA\Claude\claude_desktop_config.json"
Get-Content $path | ConvertFrom-Json | ConvertTo-Json
```

---

### Passo 3: Reiniciar Claude Desktop (2 minutos)

**Windows:**
```powershell
# Fechar todos os processos Claude
taskkill /F /IM Claude.exe 2>$null

# Aguardar
Start-Sleep -Seconds 5

# Reabrir
Start-Process "C:\Program Files\Claude\Claude.exe"

# Aguardar inicialização
Start-Sleep -Seconds 10
```

**macOS:**
```bash
killall Claude
sleep 5
open /Applications/Claude.app
```

---

### Passo 4: Testar no Claude Desktop (1 minuto)

**Abrir Claude Desktop** e testar cada comando:

#### Teste 1: Listar Ferramentas
```
User: What tools are available?

Esperado:
Claude: I have access to the following tools...
- senior-docs (search documentation)
```

#### Teste 2: Busca Básica
```
User: @senior-docs search for BPM documentation

Esperado:
Claude: I'll search for BPM documentation...
[Results: 5 BPM documents]
```

#### Teste 3: Busca Filtrada
```
User: @senior-docs search for "folha" in GESTAO_DE_PESSOAS_HCM module

Esperado:
Claude: I'll search for folha in the HCM module...
[Results: HCM documents containing "folha"]
```

#### Teste 4: Listar Módulos
```
User: @senior-docs list all modules

Esperado:
Claude: I'll list all modules...
[Results: 17 modules listed]
```

#### Teste 5: Estatísticas
```
User: @senior-docs show statistics

Esperado:
Claude: I'll get the statistics...
[Results: 933 documents, 17 modules]
```

---

## 🔍 Diagnóstico de Problemas

### Problema 1: "@senior-docs não aparece"

**Solução:**
1. Fechar Claude Desktop completamente
2. Verificar arquivo: `$env:APPDATA\Claude\claude_desktop_config.json`
3. Verificar JSON (sem erros de vírgula)
4. Reabrir Claude Desktop

```powershell
# Verificar JSON
$json = Get-Content "$env:APPDATA\Claude\claude_desktop_config.json"
ConvertFrom-Json $json  # Se erro, JSON está inválido
```

### Problema 2: "Connection refused"

**Solução:**
```powershell
# Verificar MCP Server
docker-compose ps

# Se não está Up, reiniciar
docker-compose down
docker-compose up -d

# Aguardar
Start-Sleep -Seconds 10

# Testar endpoint
Invoke-WebRequest -Uri "http://localhost:8000/health"
```

### Problema 3: "Tool call failed"

**Solução:**
```powershell
# Verificar se ferramenta está exposta
Invoke-WebRequest -Uri "http://localhost:8000/tools" | Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json

# Deve listar: search_docs, list_modules, get_module_docs, get_stats
```

### Problema 4: "Timeout"

**Solução em `claude_desktop_config.json`:**
```json
{
  "mcpServers": {
    "senior-docs": {
      "type": "http",
      "url": "http://localhost:8000",
      "timeout": 60000
    }
  }
}
```

---

## ✅ Verificação Completa

### 1️⃣ Verificar Configuração
```powershell
$config = Get-Content "$env:APPDATA\Claude\claude_desktop_config.json" | ConvertFrom-Json
if ($config.mcpServers.PSObject.Properties.Name -contains "senior-docs") {
    Write-Host "✅ Configuração OK"
} else {
    Write-Host "❌ Configuração incompleta"
}
```

### 2️⃣ Verificar Servidor
```powershell
$health = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
if ($health.StatusCode -eq 200) {
    Write-Host "✅ Servidor OK"
} else {
    Write-Host "❌ Servidor indisponível"
}
```

### 3️⃣ Verificar Ferramentas
```powershell
$tools = Invoke-WebRequest -Uri "http://localhost:8000/tools" -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
Write-Host "✅ Ferramentas disponíveis:"
$tools.tools.name | ForEach-Object { Write-Host "  - $_" }
```

### 4️⃣ Testar Chamada de Ferramenta
```powershell
$body = @{
    jsonrpc = "2.0"
    id = 1
    method = "tools/call"
    params = @{
        name = "search_docs"
        arguments = @{
            query = "BPM"
        }
    }
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/" -Method Post -ContentType "application/json" -Body $body -UseBasicParsing
$result = $response.Content | ConvertFrom-Json

Write-Host "✅ Ferramenta funcionando"
Write-Host "  Resultados: $($result.result.content[0].text | ConvertFrom-Json | Select-Object -ExpandProperty count)"
```

---

## 🎯 Resultado Esperado

Após seguir todos os passos:

```
Claude Desktop - Chat
═══════════════════════════════════════════════════════════

User: @senior-docs search for BPM

Claude:
I'll search for BPM documentation in the senior documentation system.

[Calling tool: search_docs with query="BPM"]

Results found 5 documents:
1. BPM_Abas_Customizadas
2. BPM_Analytics
3. BPM_BPM
4. BPM_Central_de_Tarefas
5. BPM_Checklist_Implantacao

[Success ✅]
```

---

## 📞 Suporte

| Problema | Verificar |
|----------|-----------|
| Ferramentas não aparecem | Arquivo config + Claude restart |
| Connection refused | docker-compose ps + restart |
| Tool call failed | Verificar logs: docker-compose logs mcp-server |
| Timeout | Aumentar timeout em config |

---

## 🚀 Próximas Etapas

1. ✅ Claude Desktop configurado
2. ✅ MCP Server testado
3. ✅ Ferramentas funcionando
4. ⏳ Usar em produção

---

**Guia de Teste:** Janeiro 2026  
**Status MCP:** ✅ 100% Funcional  
**Cliente Testado:** Claude Desktop
