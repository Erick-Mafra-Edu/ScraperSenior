# 🔧 Integração MCP com VS Code - Diagnóstico e Correção

## 🎯 Problema Identificado

A IA no VS Code Chat não consegue usar as ferramentas MCP porque:

1. **Configuração padrão do VS Code não suporta MCP nativo**
2. **MCP precisa ser configurado no Claude Desktop (não no VS Code)**
3. **VS Code usa LM API, não MCP diretamente**

---

## 📋 Diferenças Importantes

### VS Code (Editor)
- ✅ Suporta **Language Model API** (LM Chat)
- ✅ Integração com Copilot/Claude
- ❌ **NÃO suporta MCP nativamente**

### Claude Desktop (Aplicação)
- ✅ Suporta **MCP nativo**
- ✅ Pode conectar a servidores MCP via HTTP/stdio
- ✅ **É onde você configura MCP!**

---

## ✅ Solução: Usar Claude Desktop, não VS Code

### Passo 1: Instalar Claude Desktop
```
Baixar em: https://claude.ai/desktop
```

### Passo 2: Configurar MCP no Claude Desktop

**Arquivo:** `~/.config/Claude/claude_desktop_config.json`

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

### Passo 3: Reiniciar Claude Desktop
- Fechar completamente
- Reabrir

### Passo 4: Usar as Ferramentas
```
User: @senior-docs Search for "BPM" documentation

Claude: [Usa a ferramenta search_docs automaticamente]
```

---

## 🔄 Fluxo de Funcionamento

### Como Funciona no Claude Desktop:

```
Claude Desktop
    ↓
Detecta MCP Server (localhost:8000)
    ↓
Envia: tools/list
    ↓
MCP Server Responde: 4 ferramentas
    ↓
User: @senior-docs search for BPM
    ↓
Claude: tools/call (search_docs)
    ↓
Resultado: Documentação de BPM
```

### Por Que VS Code Chat Não Funciona:

```
VS Code Chat
    ↓
Usa Language Model API (Copilot)
    ↓
NÃO tem suporte para MCP
    ↓
❌ Ferramentas não estão disponíveis
```

---

## 📝 Configuração Completa do Claude Desktop

### 1. Localizar o arquivo de configuração

**Windows:**
```
C:\Users\%USERNAME%\AppData\Local\Claude\claude_desktop_config.json
```

**macOS:**
```
~/.config/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### 2. Criar/Editar o arquivo

```json
{
  "mcpServers": {
    "senior-docs-http": {
      "type": "http",
      "url": "http://localhost:8000",
      "timeout": 30000
    }
  }
}
```

### 3. Reiniciar Claude Desktop
- Fechar completamente (⌘Q / Ctrl+Q)
- Aguardar 5 segundos
- Reabrir

### 4. Verificar se funcionou
```
Mensagem: Check available tools
Resposta deve mencionar @senior-docs
```

---

## 🚀 Testando a Integração

### Teste 1: Verificar Disponibilidade
```
User: What tools are available?

Claude should list: @senior-docs
```

### Teste 2: Usar a Ferramenta
```
User: @senior-docs search for BPM

Claude should:
1. Call search_docs tool
2. Return BPM documentation
3. Show results
```

### Teste 3: Usar com Filtro
```
User: @senior-docs search for "folha" in HCM module

Claude should:
1. Call search_docs with module filter
2. Return only HCM results
3. Show filtered documentation
```

---

## 🔍 Troubleshooting

### Problema 1: "Ferramentas não aparecem"

**Causa:** Claude Desktop não foi reiniciado

**Solução:**
```powershell
# Fechar completamente
taskkill /F /IM Claude.exe

# Aguardar 5 segundos
Start-Sleep -Seconds 5

# Reabrir Claude Desktop
Start-Process "C:\Program Files\Claude\Claude.exe"
```

### Problema 2: "Connection refused"

**Causa:** MCP Server não está rodando

**Solução:**
```powershell
cd c:\Users\Digisys\scrapyTest
docker-compose up -d
Start-Sleep -Seconds 10
docker-compose ps  # Verificar se está "Up"
```

### Problema 3: "Tool not found"

**Causa:** Configuração do arquivo está incorreta

**Solução:**
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

Verificar:
- ✅ Port correto: 8000
- ✅ URL correta: http://localhost:8000
- ✅ JSON válido (sem vírgulas erradas)

### Problema 4: "Timeout"

**Causa:** Server demorando para responder

**Solução:**
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

## 📊 Verificação da Configuração

### Verificar arquivo de config
```powershell
$config = Get-Content "~\.config\Claude\claude_desktop_config.json" | ConvertFrom-Json
$config | ConvertTo-Json -Depth 10
```

### Verificar se MCP Server está rodando
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/health"
```

### Verificar se ferramentas estão expostas
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/tools"
```

---

## 📚 Recursos Oficiais

- **MCP Spec:** https://modelcontextprotocol.io
- **Claude Desktop:** https://claude.ai/desktop
- **MCP Architecture:** https://modelcontextprotocol.io/docs/learn/architecture

---

## ✅ Checklist de Configuração

- [ ] MCP Server rodando em Docker (`docker-compose up -d`)
- [ ] Verificado com `docker-compose ps` (status: Up)
- [ ] Claude Desktop instalado
- [ ] Arquivo `claude_desktop_config.json` criado/editado
- [ ] JSON válido (sem erros de syntax)
- [ ] Porta correta: 8000
- [ ] Claude Desktop reiniciado completamente
- [ ] Testado com: `@senior-docs search for BPM`
- [ ] Ferramentas funcionando com parâmetros

---

## 🎯 Conclusão

**VS Code Chat NÃO suporta MCP.** 

Use **Claude Desktop** para integração MCP completa:

1. Configure `claude_desktop_config.json`
2. Reinicie Claude Desktop
3. Use `@senior-docs` no chat
4. Ferramentas funcionam automaticamente

---

**Documentação Atualizada:** Janeiro 2026  
**Status MCP Server:** ✅ 100% Funcional  
**Cliente Recomendado:** Claude Desktop
