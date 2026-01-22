# ⚡ Quick Start - Testes do MCP Server

## 30 Segundos para Validação Completa

### 1️⃣ Iniciar (10 segundos)
```powershell
docker-compose up -d
Start-Sleep -Seconds 5
docker-compose ps  # Verificar se ambos estão "Up (healthy)"
```

### 2️⃣ Executar Testes (10-20 segundos)
```powershell
.\run_tests.ps1
```

### 3️⃣ Verificar Resultado
```
>>> ALL TESTS PASSED <<<
Success Rate: 100%
```

---

## Estrutura dos Testes

```
10 Testes | 4 Ferramentas | 933 Docs | 17 Módulos
═══════════════════════════════════════════════════

Protocolo          Funcionalidade      Erros
├─ Initialize      ├─ Search Docs       ├─ Empty Query
└─ Tools List      ├─ Filter Module     └─ Invalid Module
                   ├─ List Modules
                   ├─ Get Docs
                   └─ Get Stats
```

---

## Comandos Essenciais

| Comando | O que faz |
|---------|-----------|
| `docker-compose ps` | Ver status dos containers |
| `.\run_tests.ps1` | Rodar todos os 10 testes |
| `docker-compose logs mcp-server` | Ver logs do MCP |
| `docker-compose down` | Parar containers |
| `docker-compose up -d` | Iniciar containers |

---

## Exemplos de Teste

### Teste 1: Inicialização (Manual)
```powershell
$body = @{jsonrpc="2.0"; id=1; method="initialize"; params=@{protocolVersion="2024-11-05"}} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/" -Method Post -ContentType "application/json" -Body $body -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Teste 3: Busca BPM (Manual)
```powershell
$body = @{jsonrpc="2.0"; id=3; method="tools/call"; params=@{name="search_docs"; arguments=@{query="BPM"}}} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/" -Method Post -ContentType "application/json" -Body $body -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json -Depth 5
```

---

## Documentação Completa

| Documento | Descrição |
|-----------|-----------|
| **QUICK_TEST_SUMMARY.md** | Este arquivo (30s overview) |
| **run_tests.ps1** | Script PowerShell para executar testes |
| **MCP_TESTS.md** | Manual com todos os 10 testes |
| **MCP_TEST_SUITE.json** | Especificação JSON dos testes |
| **TEST_README.md** | Guia completo e troubleshooting |
| **TEST_RESULTS.md** | Resultados detalhados |

---

## Checklist de Validação

- [ ] Docker rodando (`docker-compose ps` mostra "Up (healthy)")
- [ ] MCP Server acessível (`curl http://localhost:8000/ -v`)
- [ ] Testes rodando (`.\run_tests.ps1`)
- [ ] Todos 10 testes passando
- [ ] Taxa de sucesso 100%

---

## Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| Connection Refused | `docker-compose up -d` + aguardar 10s |
| Test Failed | `docker-compose logs mcp-server` |
| Containers não healthy | `docker-compose restart` |
| Quer limpar tudo | `docker-compose down -v` |

---

## Próximo Passo

### Configurar no VS Code
```json
~/.config/Claude/claude_desktop_config.json

{
  "mcpServers": {
    "senior-docs": {
      "type": "http",
      "url": "http://localhost:8000"
    }
  }
}
```

Usar: `@senior-docs` em prompts

---

**Status:** ✅ 100% de Sucesso  
**Tempo:** ~30 segundos  
**Pronto:** Sim
