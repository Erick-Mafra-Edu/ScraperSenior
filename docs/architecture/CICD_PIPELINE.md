# CI/CD Pipeline Configuration

## Visão Geral

Este pipeline automático valida, testa e garante a qualidade do código antes de qualquer deploy.

### Componentes do Pipeline

1. **Teste de Dados do Scraper** (`tests/test_scraper.py`)
   - Validação de estrutura JSONL
   - Verificação de títulos
   - Validação de URLs
   - Consistência de módulos
   - Estrutura de breadcrumbs
   - Encoding UTF-8

2. **Teste de Meilisearch** (`tests/test_meilisearch.py`)
   - Conexão com servidor
   - Existência de índices
   - Contagem de documentos
   - Funcionalidade de busca
   - Validação de campos
   - Busca por módulo com filtros

3. **Teste de MCP Server** (`tests/test_mcp_server.py`)
   - Health check
   - Endpoint de estatísticas
   - Endpoint de ferramentas
   - Conexão com Meilisearch
   - Endpoint de busca
   - Chamada de ferramentas

### Como Executar

#### Python (Multiplataforma)
```bash
python run_ci_pipeline.py
```

#### PowerShell (Windows)
```powershell
# Executar pipeline completo
.\ci_pipeline.ps1 -Action Full

# Apenas testes
.\ci_pipeline.ps1 -Action RunTests

# Apenas Docker
.\ci_pipeline.ps1 -Action Docker

# Apenas validação de dados
.\ci_pipeline.ps1 -Action ValidateData

# Ver relatório
.\ci_pipeline.ps1 -Action Report
```

#### Bash (Linux/Mac)
```bash
python3 run_ci_pipeline.py
```

### Fluxo de Execução

```
INÍCIO
  ↓
[1] Infraestrutura OK?
    ├─ Sim → Continuar
    └─ Não → Aviso (continua mesmo assim)
  ↓
[2] Validar Dados do Scraper
    ├─ JSONL válido?
    ├─ Títulos OK?
    ├─ URLs OK?
    └─ Encoding OK?
  ↓
[3] Testar Meilisearch
    ├─ Conexão OK?
    ├─ Índice existe?
    ├─ Documentos carregados?
    └─ Busca funciona?
  ↓
[4] Testar MCP Server
    ├─ Server healthy?
    ├─ Stats OK?
    ├─ Busca funciona?
    └─ Ferramentas acessíveis?
  ↓
[5] Gerar Relatório
    ├─ JSON com resultados
    └─ Sumário visual
  ↓
FIM
```

### Critérios de Sucesso

| Teste | Critério | Ação se Falhar |
|-------|----------|---|
| Títulos | ≥ 90% sucesso | Reexecutar scraper |
| URLs | 100% válidas | Validar origem dos dados |
| Módulos | ≥ 1 encontrado | Verificar scraped docs |
| Meilisearch | Conectado e índice existe | Reiniciar Docker |
| MCP Health | Status = healthy | Verificar logs |
| Busca | ≥ 1 resultado | Reindexar dados |

### Integração com Alterações de Código

#### Pre-commit Hook (Git)
```bash
#!/bin/bash
# .git/hooks/pre-commit

python run_ci_pipeline.py
if [ $? -ne 0 ]; then
    echo "❌ Testes falharam. Commit bloqueado."
    exit 1
fi
```

#### GitHub Actions (Opcional)
```yaml
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      meilisearch:
        image: getmeili/meilisearch:v1.11.0
      mcp-server:
        build: .
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: python run_ci_pipeline.py
```

### Relatório de Saída

O pipeline gera um arquivo `test_report.json` com:

```json
{
  "timestamp": "2024-01-22T10:30:45.123456",
  "tests": {
    "Scraper Data Validation": {
      "passed": true,
      "returncode": 0
    },
    "Meilisearch Tests": {
      "passed": true,
      "returncode": 0
    },
    "MCP Server Tests": {
      "passed": true,
      "returncode": 0
    }
  },
  "summary": {
    "total_tests": 3,
    "passed": 3,
    "failed": 0,
    "success_rate": "100.0%",
    "status": "SUCCESS ✅"
  }
}
```

### Troubleshooting

#### Testes falhando após alterações

1. **Verificar logs completos**
   ```bash
   docker-compose logs meilisearch | tail -50
   docker-compose logs mcp-server | tail -50
   ```

2. **Limpar cache e reconstruir**
   ```bash
   docker-compose down -v
   docker-compose up -d --build
   python run_ci_pipeline.py
   ```

3. **Reindexar dados**
   ```bash
   python index_meilisearch.py
   python run_ci_pipeline.py
   ```

### Métricas Rastreadas

- ✅ Taxa de sucesso dos testes
- ⏱️ Tempo de execução do pipeline
- 📊 Documentos indexados
- 🔍 Títulos capturados com sucesso
- 🌍 URLs validadas
- 📦 Módulos descobertos
- 🔗 Integridade de links

### Próximos Passos

1. [ ] Implementar pre-commit hooks
2. [ ] Configurar GitHub Actions
3. [ ] Adicionar análise de cobertura
4. [ ] Implementar performance benchmarks
5. [ ] Alertas automáticos para falhas
6. [ ] Dashboard de métricas

