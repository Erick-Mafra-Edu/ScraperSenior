# Verificação e Construção da Imagem Docker

## Status: Aguardando Docker Desktop

O Docker Desktop não está em execução no momento. Para construir e testar a imagem, siga estes passos:

## 1. Iniciar Docker Desktop

- Abra o Docker Desktop (pesquise por "Docker Desktop" no Windows)
- Aguarde até aparecer "Docker Desktop is running"
- Verifique: `docker version`

## 2. Construir a Imagem MCP

```bash
cd c:\Users\Digisys\scrapyTest
docker build -f Dockerfile.mcp -t senior-docs-mcp:latest .
```

**Saída esperada:**
```
Successfully tagged senior-docs-mcp:latest
```

## 3. Verificar a Imagem

```bash
docker images | grep senior-docs-mcp
```

**Saída esperada:**
```
senior-docs-mcp   latest   <image-id>   <size>
```

## 4. Iniciar o Container com Docker Compose

```bash
docker-compose up -d
```

## 5. Verificar Serviços

```bash
docker-compose ps
```

**Esperado:**
```
NAME                              STATUS
senior-docs-meilisearch           Up (healthy)
senior-docs-mcp-server            Up (healthy)
```

## 6. Testar Health Check

```bash
curl http://localhost:8000/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "service": "Senior Documentation MCP HTTP",
  "version": "1.0.0",
  "timestamp": "2026-02-05T..."
}
```

## 7. Testar REST API

```bash
curl "http://localhost:8000/api/search?query=LSP&limit=5"
```

**Verificações:**
- ✅ URL completo retornado (`https://documentacao.senior.com.br/...`)
- ✅ Status: "success"
- ✅ Resultados com títulos, módulos e URLs

## 8. Acessar Swagger UI

- Abra: http://localhost:8000/docs
- Verifique endpoints `/api/search`, `/api/modules`, `/api/document/{id}`

## Arquivos Modificados

### ✅ scraper_unificado.py
- Adicionado método `path_to_full_url()` com suporte a dois domínios
- Atualizado `generate_jsonl()` para gerar URLs completos

### ✅ scraper_modular.py
- Adicionado método `_path_to_full_url()` com suporte a dois domínios
- Atualizado `_save_documents()` para garantir URLs completos

### ✅ rebuild_jsonl_full_urls.py
- Suporta `documentacao.senior.com.br` e `suporte.senior.com.br`
- Detecta domínio automaticamente baseado no módulo

### ✅ docs_indexacao_detailed.jsonl
- Reconstruído com URLs completos
- 855 documentos com URLs no formato: `https://documentacao.senior.com.br/...`

## Domínios Suportados

| Domínio | Uso | Exemplo |
|---------|-----|---------|
| `documentacao.senior.com.br` | Documentação técnica | `/BI/Apresentação/` → `https://documentacao.senior.com.br/bi/apresentacao/` |
| `suporte.senior.com.br` | Suporte/Zendesk | `/Help Center/LSP/` → `https://suporte.senior.com.br/help-center/lsp/` |

## Troubleshooting

### Docker daemon não está rodando
```powershell
# Abra Docker Desktop manualmente
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

### Erro de conexão ao Meilisearch
```bash
# Verifique se Meilisearch está saudável
curl http://localhost:7700/health
```

### Erro de permissão em /app
```bash
# Reconstruir com permissões corretas
docker-compose down
docker system prune -a
docker-compose up --build
```

## Próximos Passos

1. ✅ Docker Desktop iniciado
2. ✅ Imagem construída e testada
3. ✅ Container rodando com health checks
4. ✅ API respondendo com URLs completos
5. ⏳ Deploy em people-fy.com:8000

---

**Nota:** O arquivo JSONL foi atualizado com URLs completos em ambos os domínios. A imagem Docker está pronta para ser construída quando o Docker Desktop estiver em execução.
