# 🚀 GUIA FINAL: Recuperação Completa do Sistema

## 📋 O que foi corrigido

| # | Problema | Solução | Status |
|---|----------|---------|--------|
| 1 | Chave Meilisearch inconsistente | `.env` com chave correta + imports em 6 Python files | ✅ |
| 2 | `os` não importado em Docker entrypoint | Adicionado `import os` em 5 arquivos | ✅ |
| 3 | OpenAPI schema genérico demais para LLMs | Descrições melhoradas + x-openai-isConsequential | ✅ |
| 4 | Modelo IA não usa ferramenta automaticamente | Prompts prontos + instruções completas | ✅ |

---

## 🔧 EXECUÇÃO PASSO A PASSO

### Passo 1: Verificar Arquivos (2 min)
```bash
# Windows PowerShell
cd C:\Users\Digisys\scrapyTest

# Verificar que .env existe
Get-Content .env | Select-String MEILISEARCH_KEY

# Esperado:
# MEILISEARCH_KEY=5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa
```

### Passo 2: Parar Docker Antigo (1 min)
```bash
# Remover containers e volumes antigos
docker-compose down -v

# Ou se usar Podman:
podman-compose down -v
```

### Passo 3: Build Novo (5-10 min)
```bash
# Rebuild sem cache
docker-compose build --no-cache

# Esperado: "Successfully tagged senior-docs-mcp:latest"
#          "Successfully tagged senior-docs-scraper:latest"
```

### Passo 4: Iniciar Services (2 min)
```bash
# Iniciar todos os serviços
docker-compose up -d

# Verificar que estão rodando
docker-compose ps

# Esperado:
# - meilisearch: running
# - mcp-server: running  
# - scraper: running (or exited/0 se completou)
```

### Passo 5: Validar Conectividade (2 min)
```bash
# Script automático (recomendado)
python test_meilisearch_connection.py

# OU verificação manual:

# 1. Meilisearch health
curl http://localhost:7700/health

# 2. API health
curl http://localhost:8000/health

# 3. Search test
curl -X POST http://localhost:8000/search `
  -H "Content-Type: application/json" `
  -d '{\"query\":\"teste\",\"limit\":5}'
```

### Passo 6: Verificar Logs (2 min)
```bash
# Ver logs de todos os serviços
docker-compose logs

# OU específico:
docker-compose logs meilisearch
docker-compose logs senior-docs-mcp-server
docker-compose logs senior-docs-scraper

# Procurar por:
# ✅ "healthy" (no Meilisearch)
# ✅ "855 documents" (no MCP Server)
# ❌ Erros "403" ou "NameError"
```

---

## 📊 VALIDAÇÃO RÁPIDA

Execute este comando para verificar tudo:

```bash
# Windows PowerShell
$tests = @(
    @{Name="Meilisearch"; URL="http://localhost:7700/health"},
    @{Name="API Health"; URL="http://localhost:8000/health"},
    @{Name="API Stats"; URL="http://localhost:8000/stats"},
    @{Name="List Modules"; URL="http://localhost:8000/modules"}
)

foreach ($test in $tests) {
    try {
        $resp = Invoke-WebRequest -Uri $test.URL -UseBasicParsing -TimeoutSec 5
        if ($resp.StatusCode -eq 200) {
            Write-Host "✅ $($test.Name)" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ $($test.Name)" -ForegroundColor Red
    }
}
```

**Esperado**: ✅ em todos os 4 testes

---

## 🎯 ROTEIRO DE RECUPERAÇÃO (TOTAL: ~30 min)

```
┌─────────────────────────────────────────┐
│ FASE 1: PREPARAÇÃO (2 min)              │
│ ✓ Verificar .env                        │
│ ✓ Verificar git status                  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ FASE 2: REBUILD (10 min)                │
│ ✓ docker-compose down -v                │
│ ✓ docker-compose build --no-cache       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ FASE 3: START (2 min)                   │
│ ✓ docker-compose up -d                  │
│ ✓ docker-compose ps (verificar)         │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ FASE 4: VALIDAÇÃO (3 min)               │
│ ✓ Health checks (API + Meilisearch)     │
│ ✓ Test search endpoint                  │
│ ✓ Verificar logs                        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ FASE 5: TESTES (10+ min)                │
│ ✓ python test_meilisearch_connection.py │
│ ✓ Testar 5 exemplos de search           │
│ ✓ Testar Open WebUI (opcional)          │
└─────────────────────────────────────────┘
```

---

## 🧪 EXEMPLOS DE BUSCA PARA TESTAR

### Teste 1: Busca Simples
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"como","limit":3}'

# Esperado: ~100 resultados, retorna 3
```

### Teste 2: Busca com Módulo
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"configurar","module":"RH","limit":5}'

# Esperado: Documentos específicos de RH
```

### Teste 3: Busca Vazia
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"xyz123notfound","limit":5}'

# Esperado: {"success":true,"total":0,"results":[]}
```

### Teste 4: Stats
```bash
curl http://localhost:8000/stats

# Esperado:
# {"success":true,"total_documents":855,"total_modules":7,...}
```

### Teste 5: Módulos
```bash
curl http://localhost:8000/modules

# Esperado:
# {"success":true,"modules":[{"name":"RH","doc_count":XXX},...]}
```

---

## 🔍 TROUBLESHOOTING

### ❌ Erro: "connection refused"
```bash
# Solução: Containers não estão rodando
docker-compose ps
docker-compose up -d

# Se ainda não funcionar:
docker-compose logs
```

### ❌ Erro: "403 invalid_api_key"
```bash
# Solução: Chave não corresponde
# 1. Verificar .env
cat .env

# 2. Rebuild
docker-compose build --no-cache
docker-compose restart

# 3. Testar novamente
python test_meilisearch_connection.py
```

### ❌ Erro: "NameError: name 'os' is not defined"
```bash
# Isso NÃO deve mais acontecer!
# Se acontecer, significa que o rebuild não funcionou
# Tente:

docker-compose build --no-cache scraper
docker-compose restart scraper
docker-compose logs scraper
```

### ❌ Erro: "No documents returned"
```bash
# Verificar se foram indexados:
curl http://localhost:8000/stats

# Se total_documents = 0:
# - Scraper não rodou
# - Ou dados não foram indexados
# - Verificar: docker-compose logs scraper
```

---

## 📚 DOCUMENTAÇÃO CRIADA

| Arquivo | Propósito | Linhas |
|---------|-----------|--------|
| `MEILISEARCH_API_KEY_FIX.md` | Detalhes da correção de API key | 500+ |
| `test_meilisearch_connection.py` | Script automático de validação | 250+ |
| `OPEN_WEBUI_MODEL_INSTRUCTIONS.md` | Como usar com Open WebUI | 400+ |
| `OPEN_WEBUI_SYSTEM_PROMPTS.md` | 7 prompts prontos para LLMs | 500+ |
| `FIX_SUMMARY.md` | Resumo executivo (este arquivo) | 400+ |
| `IMPORT_OS_FIX.md` | Fix de imports | 100+ |

---

## ✅ CHECKLIST FINAL

- [ ] .env criado com chave correta
- [ ] Todos os arquivos Python têm `import os`
- [ ] OpenAPI schema melhorado
- [ ] Docker build completado sem cache
- [ ] Todos os containers estão running
- [ ] Health checks passam (4/4)
- [ ] Search endpoint retorna resultados
- [ ] Stats mostra 855 documentos
- [ ] Modules endpoint lista módulos
- [ ] Logs não têm erros 403 ou NameError
- [ ] Test script passa todos os testes
- [ ] Git commits feitos

---

## 🎉 SUCESSO!

Se chegou aqui:
```
✅ Sistema corrigido
✅ Documentação completa
✅ Tests passando
✅ Pronto para produção

Próximo: Usar em Open WebUI ou sua aplicação!
```

---

## 💡 DICAS

### Performance
- Se search é lento: aumentar `limit` para cachear
- Se Docker lento: Rebuild com `--no-cache` consome tempo

### Desenvolvimento
- Para logs em tempo real: `docker-compose logs -f`
- Para rebuild rápido (com cache): `docker-compose build`
- Para forçar rebuild: `docker-compose build --no-cache`

### Produção
- Mude `MCP_MODE=openapi` se for usar só como API
- Configure HTTPS em produção
- Use variáveis de ambiente para chaves, não .env

---

## 📞 PRECISA DE AJUDA?

1. **Erro de Autenticação**: Ver `MEILISEARCH_API_KEY_FIX.md`
2. **Teste Rápido**: Executar `python test_meilisearch_connection.py`
3. **LLM não usa tool**: Ver `OPEN_WEBUI_MODEL_INSTRUCTIONS.md`
4. **Verificar logs**: `docker-compose logs -f`
5. **Rebuildar tudo**: `docker-compose down -v && docker-compose build --no-cache && docker-compose up -d`
