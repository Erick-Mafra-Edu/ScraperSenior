# 🚀 CI/CD Pipeline - Senior Documentation

Pipeline automático de testes e validação para o Scraper e MCP Server.

## 📋 Visão Geral

Este pipeline garante que:
- ✅ Dados do scraper estão estruturados corretamente
- ✅ Títulos são capturados com sucesso (≥90%)
- ✅ URLs são válidas
- ✅ Meilisearch está indexando documentos
- ✅ MCP Server está respondendo corretamente
- ✅ Busca está funcionando

## 🚀 Quick Start

### Opção 1: Pipeline Completo (Python)
```bash
python run_ci_pipeline.py
```

### Opção 2: PowerShell (Windows)
```powershell
.\ci_pipeline.ps1 -Action Full
```

### Opção 3: Watch Mode (Monitora mudanças)
```bash
python tools/watch_tests.py
```

## 📂 Estrutura

```
CI/CD Pipeline
├── run_ci_pipeline.py          # Orquestrador principal
├── ci_pipeline.ps1             # Script PowerShell
├── CICD_PIPELINE.md            # Documentação completa
├── pytest.ini                  # Configuração pytest
├── tests/
│   ├── test_scraper.py        # Validação de dados
│   ├── test_meilisearch.py    # Testes de busca
│   └── test_mcp_server.py     # Testes HTTP
├── tools/
│   ├── pre_commit.py          # Hook pre-commit
│   └── watch_tests.py         # Monitor de mudanças
└── test_report.json           # Relatório gerado
```

## 🧪 Testes Disponíveis

### 1. Validação de Dados do Scraper
```python
python -m pytest tests/test_scraper.py -v
```
Valida:
- ✅ Estrutura JSONL
- ✅ Títulos (≥90% capturados)
- ✅ URLs válidas
- ✅ Módulos consistentes
- ✅ Breadcrumbs estruturados
- ✅ Encoding UTF-8

### 2. Testes Meilisearch
```python
python -m pytest tests/test_meilisearch.py -v
```
Valida:
- ✅ Conexão com servidor
- ✅ Índice existe
- ✅ Documentos indexados
- ✅ Busca funcionando
- ✅ Campos corretos
- ✅ Filtros por módulo

### 3. Testes MCP Server
```python
python -m pytest tests/test_mcp_server.py -v
```
Valida:
- ✅ Server healthy
- ✅ Endpoints acessíveis
- ✅ Stats corretos
- ✅ Ferramentas disponíveis
- ✅ Busca funcionando
- ✅ Integração Meilisearch

## 🎯 Executar Testes Individuais

### Apenas dados do scraper
```powershell
.\ci_pipeline.ps1 -Action ValidateData
```

### Apenas Meilisearch
```bash
python tests/test_meilisearch.py
```

### Apenas MCP Server
```bash
python tests/test_mcp_server.py
```

### Ver último relatório
```powershell
.\ci_pipeline.ps1 -Action Report
```

## 🔄 Fluxo Automático

### Pre-commit Hook
Valida antes de cada commit Git:
```bash
cp tools/pre_commit.py .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Watch Mode
Monitora arquivos e roda testes ao detectar mudanças:
```bash
python tools/watch_tests.py

# Monitora:
# - Alterações em src/
# - Mudanças no JSONL
# - Roda testes automaticamente
```

## 📊 Interpretando Relatórios

### Saída no Console
```
================================================================================
📊 RESUMO DOS TESTES
================================================================================
✅ PASS: Scraper Data Validation
✅ PASS: Meilisearch Tests
✅ PASS: MCP Server Tests

Total: 3/3 testes passaram (100.0%)
================================================================================
```

### Arquivo JSON
```json
{
  "timestamp": "2024-01-22T10:30:45",
  "tests": {
    "Scraper Data Validation": {"passed": true},
    "Meilisearch Tests": {"passed": true},
    "MCP Server Tests": {"passed": true}
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

## 🛠️ Troubleshooting

### Erro: "Meilisearch conectado"
```bash
# Reiniciar Docker
docker-compose down -v
docker-compose up -d --build

# Reindexar
python index_meilisearch.py

# Rodar testes novamente
python run_ci_pipeline.py
```

### Erro: "MCP Server não responde"
```bash
# Verificar logs
docker-compose logs mcp-server

# Reiniciar container
docker-compose restart mcp-server

# Rodar testes
python tests/test_mcp_server.py
```

### Erro: "JSONL inválido"
```bash
# Recriar JSONL
python prepare_documents.py

# Validar
python tests/test_scraper.py
```

### Erro: "0 documentos indexados"
```bash
# Reindexar com debug
python index_meilisearch.py

# Verificar Meilisearch stats
curl -H "Authorization: Bearer meilisearch_master_key_change_me" \
  http://localhost:7700/indexes/senior_docs/stats
```

## 📈 Métricas

O pipeline rastreia:
- 📊 Taxa de sucesso de testes (%)
- ⏱️ Tempo de execução (s)
- 📦 Documentos indexados
- 🔍 Títulos capturados (%)
- 🌍 URLs validadas
- 📋 Módulos encontrados
- 🔗 Status da integração

## 🔗 Integração com CI/CD Externo

### GitHub Actions
```yaml
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      meilisearch:
        image: getmeili/meilisearch:v1.11.0
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python run_ci_pipeline.py
```

### GitLab CI
```yaml
test:
  image: python:3.11
  services:
    - getmeili/meilisearch:v1.11.0
  script:
    - pip install -r requirements.txt
    - python run_ci_pipeline.py
```

## 📚 Documentação Adicional

- [CICD_PIPELINE.md](CICD_PIPELINE.md) - Documentação completa
- [README.md](README.md) - Visão geral do projeto
- [MCP_SERVER.md](MCP_SERVER.md) - Documentação MCP
- [RELATORIO_TESTES.md](RELATORIO_TESTES.md) - Testes anteriores

## ✅ Checklist de Setup

- [ ] Docker instalado e rodando
- [ ] Docker Compose funcionando
- [ ] Python 3.11+ instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `docs_indexacao_detailed.jsonl` presente
- [ ] Meilisearch container saudável
- [ ] MCP Server container saudável
- [ ] Testes locais passando
- [ ] Pre-commit hook configurado (opcional)
- [ ] Watch mode testado (opcional)

## 🎓 Exemplos de Uso

### Desenvolver com validação automática
```bash
# Terminal 1: Watch mode
python tools/watch_tests.py

# Terminal 2: Fazer alterações e committar
git add src/scraper_unificado.py
git commit -m "Fix title extraction"  # Pre-commit validates
```

### Deploy com confiança
```bash
# Rodar pipeline completo
.\ci_pipeline.ps1 -Action Full

# Se passar, fazer deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Debugging de falhas
```bash
# Rodar teste específico com verbose
python -m pytest tests/test_scraper.py -v -s

# Ver relatório detalhado
python -m pytest tests/ --html=report.html --self-contained-html

# Check específico
python tests/test_meilisearch.py
```

## 💡 Dicas

1. **Rápido**: Use `ValidateData` para validação rápida de dados
2. **Desenvolvimento**: Use `watch_tests.py` para feedback instantâneo
3. **CI/CD**: Integre `run_ci_pipeline.py` em seu pipeline
4. **Debug**: Use testes individuais com `-v` (verbose)

## 🤝 Suporte

Problemas? Verifique:
1. Status do Docker: `docker-compose ps`
2. Logs: `docker-compose logs mcp-server`
3. Conectividade: `curl http://localhost:8000/health`
4. Dados: `wc -l docs_indexacao_detailed.jsonl`

---

**Última atualização**: Janeiro 2024
**Versão do Pipeline**: 1.0.0
