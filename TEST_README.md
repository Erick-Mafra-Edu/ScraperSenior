# Teste Automatizado de MCP Server

## Visão Geral

Este repositório inclui dois arquivos de teste para validar o MCP Server:

### 1. **MCP_TESTS.md** - Manual de Testes (Legível para Humanos)
- 10 testes com comandos PowerShell exatos
- Respostas esperadas em JSON
- Critérios de validação detalhados
- **Uso**: Para entender e executar manualmente cada teste

### 2. **MCP_TESTS.ps1** - Suite Automatizada (Executável via Script)
- Script PowerShell completo com 10 testes
- Executado com: `.\MCP_TESTS.ps1`
- Validações automáticas
- Relatório de resultados (verde = sucesso, vermelho = falha)
- **Uso**: Para CI/CD, automação, e validação contínua

## Início Rápido

### Pré-requisitos
- Docker rodando com MCP Server (`docker-compose up -d`)
- PowerShell 5.1+ (ou PowerShell Core)
- Meilisearch acessível em `localhost:7700`
- MCP Server acessível em `localhost:8000`

### Executar Testes Automatizados

```powershell
# Na pasta do projeto
cd c:\Users\Digisys\scrapyTest

# Executar suite de testes
.\MCP_TESTS.ps1

# Resultado esperado: "✓ TODOS OS TESTES PASSARAM!"
```

### Verificar Status dos Containers

```powershell
# Verificar se containers estão saudáveis
docker-compose ps

# Ver logs do MCP Server
docker-compose logs mcp-server

# Ver logs do Meilisearch
docker-compose logs meilisearch
```

## Testes Inclusos

| # | Teste | Valida | Status Esperado |
|---|-------|--------|---|
| 1 | Initialize | Handshake MCP | ✓ serverInfo presente |
| 2 | Tools List | 4 ferramentas | ✓ inputSchema válido |
| 3 | Search BPM | Busca genérica | ✓ 5+ resultados |
| 4 | Search folha | Query ampla | ✓ resultados encontrados |
| 5 | Search Filtrado | Filtro por módulo | ✓ apenas HCM |
| 6 | List Modules | 17 módulos | ✓ all present |
| 7 | Get Module Docs | Docs de BPM | ✓ array com docs |
| 8 | Get Stats | Estatísticas | ✓ 933+ docs |
| 9 | Error - Query Vazia | Rejeição | ✓ count=0 |
| 10 | Error - Módulo Invalido | Retorno Vazio | ✓ results=[] |

## Como Funcionam os Testes

### Estrutura de Cada Teste

```powershell
Test-MCP -TestNumber N -TestName "Nome" `
    -RequestBody @{
        jsonrpc = "2.0"
        id = N
        method = "tools/call"
        params = @{ ... }
    } `
    -Validation {
        param($Result)
        # Verificações lógicas
        if ($Result.success) {
            @{ Success = $true; Message = "..."; Details = "..." }
        } else {
            @{ Success = $false; Message = "..."; Details = "..." }
        }
    }
```

### Ciclo de Execução

1. **Preparação**: Monta corpo JSON-RPC 2.0
2. **Envio**: POST para `http://localhost:8000/`
3. **Resposta**: Recebe JSON
4. **Validação**: Verifica campos esperados
5. **Resultado**: ✓ PASS ou ✗ FAIL com detalhes
6. **Relatório**: Resumo final com % sucesso

## Resultados Esperados

### Sucesso Completo (100%)
```
================================================================================
RESUMO DE TESTES
================================================================================
Total de Testes: 10
Passados: 10
Falhados: 0
Taxa de Sucesso: 100%

================================================================================
✓ TODOS OS TESTES PASSARAM!
```

### Com Falhas
```
✗ TESTE #3 falhou: Search BPM
  Details: count <= 0

RESUMO: 9 passados, 1 falhado (90%)
```

## Troubleshooting

### "Conexão recusada" (Connection Refused)
```powershell
# Verificar se container está rodando
docker-compose ps

# Se não está, iniciar
docker-compose up -d

# Aguardar alguns segundos para ficar healthy
Start-Sleep -Seconds 5
.\MCP_TESTS.ps1
```

### "Query vazia não foi rejeitada" (Teste 9)
```powershell
# Verificar logs do servidor
docker-compose logs mcp-server | tail -20

# Reconstruir imagem
docker-compose build
docker-compose up -d
```

### Timeout
```powershell
# Aumentar timeout (default 30s)
.\MCP_TESTS.ps1 -TimeoutSeconds 60

# Ou URL customizada
.\MCP_TESTS.ps1 -Url "http://seu-servidor:8000/"
```

## Extensibilidade

### Adicionar Novo Teste

```powershell
# Dupliçar estrutura e adaptar
Test-MCP -TestNumber 11 -TestName "Novo Teste" `
    -RequestBody @{
        jsonrpc = "2.0"
        id = 11
        method = "tools/call"
        params = @{ name = "sua_ferramenta"; arguments = @{ ... } }
    } `
    -Validation {
        param($Result)
        # Suas validações aqui
    }
```

### Modificar Validações

Editar a função `Test-MCP` ou adicionar checks customizados na seção `-Validation`.

## Integração com CI/CD

### GitHub Actions

```yaml
name: MCP Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Start Docker
        run: docker-compose up -d
      - name: Wait for server
        run: sleep 10
      - name: Run tests
        run: pwsh ./MCP_TESTS.ps1
```

### GitLab CI

```yaml
test:mcp:
  script:
    - docker-compose up -d
    - sleep 10
    - pwsh ./MCP_TESTS.ps1
```

## Detalhes Técnicos

### JSON-RPC 2.0 Specification
- Cada teste segue formato JSON-RPC 2.0
- `jsonrpc`: "2.0"
- `id`: número único (1-10)
- `method`: nome do método MCP
- `params`: argumentos

### Validações

Cada teste valida:
- ✓ Status HTTP 200
- ✓ Resposta JSON válida
- ✓ Campos obrigatórios presentes
- ✓ Tipos de dados corretos
- ✓ Valores dentro de intervalos esperados

### Performance

- Tempo típico: 2-5 segundos por teste
- Total com 10 testes: 20-50 segundos
- Timeout padrão: 30 segundos por requisição

## Métricas

```
Testes Totais:         10
Cobertura Funcional:  100%
  - Inicialização:     1 teste
  - Tools:             2 testes
  - Search:            3 testes (genérica, filtrada, múltipla)
  - Listagem:          2 testes (modules, docs)
  - Estatísticas:      1 teste
  - Erros:             2 testes (input, module)
```

## Contato e Suporte

Para problemas:
1. Verificar logs: `docker-compose logs`
2. Testar endpoint manualmente: POST `http://localhost:8000/`
3. Verificar configuração: `mcp_config.json`
4. Revisar `MCP_TESTS.md` para comandos manuais

---

**Última Atualização**: Janeiro 2025
**Versão MCP**: 2024-11-05
**Status**: ✓ Completo e Testado
