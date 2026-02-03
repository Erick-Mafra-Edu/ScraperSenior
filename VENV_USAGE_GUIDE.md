# 🚀 OpenAPI Server - Usando Virtual Environment

## Status: ✅ Servidor em Execução

O servidor FastAPI com OpenAPI está rodando com sucesso!

```
Uvicorn running on http://0.0.0.0:8000
```

## 📍 Como Acessar

### Documentação Interativa (Swagger)
```
http://localhost:8000/docs
```
- UI mais completa para testar endpoints
- Recomendado para desenvolvimento

### Documentação Alternativa (ReDoc)
```
http://localhost:8000/redoc
```
- Visualização mais "limpa" da documentação
- Ótimo para ler a especificação

### Schema OpenAPI (JSON)
Duas formas de acessar:

1. **Auto-gerado pelo FastAPI** (padrão)
   ```
   http://localhost:8000/openapi.json
   ```

2. **Do arquivo openapi.json** (do disco)
   ```
   http://localhost:8000/api/openapi.json
   ```

## 🔧 Usando o Virtual Environment

### Ativar (primeira vez ou depois de fechar terminal)

**PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**CMD/Batch:**
```cmd
venv\Scripts\activate.bat
```

**Git Bash:**
```bash
source venv/Scripts/activate
```

Você verá `(venv)` no prompt quando ativado.

### Desativar

```powershell
deactivate
```

### Iniciar o Servidor

Com venv ativado:
```powershell
python run_openapi_server.py
```

Ou com opções:
```powershell
python run_openapi_server.py --reload --log-level debug
```

## 📊 Endpoints Disponíveis

### Sistema
- **GET** `/` - Info da API
- **GET** `/health` - Health check

### Busca
- **POST** `/search` - Buscar documentos
  ```json
  {
    "query": "configurar banco de dados",
    "module": "RH",
    "limit": 10,
    "offset": 0
  }
  ```

### Módulos
- **GET** `/modules` - Listar todos os módulos
- **GET** `/modules/{module_name}` - Documentação de um módulo

### Informações
- **GET** `/stats` - Estatísticas da documentação

## 🧪 Testando com curl

```bash
# Health check
curl http://localhost:8000/health

# Listar módulos
curl http://localhost:8000/modules

# Buscar documentação
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "banco de dados",
    "limit": 5
  }'

# Estatísticas
curl http://localhost:8000/stats
```

## 🐍 Testando com Python

```python
import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        # Health
        resp = await client.get("http://localhost:8000/health")
        print("Health:", resp.json())
        
        # Modules
        resp = await client.get("http://localhost:8000/modules")
        print("Modules:", resp.json())
        
        # Search
        resp = await client.post(
            "http://localhost:8000/search",
            json={"query": "configurar", "limit": 5}
        )
        print("Search:", resp.json())

asyncio.run(test())
```

## 📝 Testando com Postman

1. Abrir Postman
2. **Import** > **Paste raw text**
3. Colar a URL: `http://localhost:8000/openapi.json`
4. Importar automaticamente
5. Testar endpoints diretamente

## ⚠️ Nota sobre Meilisearch

O servidor está rodando mesmo sem Meilisearch disponível. 

Para usar buscas reais, você precisa:

```bash
# Iniciar Meilisearch via Docker
docker-compose up -d meilisearch

# Depois reindexar documentação
python scripts/indexing/reindex_all_docs.py
```

Ou:

```powershell
# Iniciar servidor com URL customizada
python run_openapi_server.py --meilisearch-url http://seu-server:7700
```

## 📦 Estrutura de Arquivos

```
c:\Users\Digisys\scrapyTest\
├── venv/                           # Virtual environment (já criado)
│   ├── Scripts/
│   │   ├── Activate.ps1           # Ativar (PowerShell)
│   │   ├── activate.bat           # Ativar (CMD)
│   │   └── python.exe             # Python isolado
│   ├── Lib/
│   │   └── site-packages/         # Pacotes instalados
│   └── ...
├── openapi.json                   # ✨ Especificação OpenAPI
├── run_openapi_server.py          # ✨ Script para iniciar
├── apps/
│   └── mcp-server/
│       └── openapi_adapter.py     # FastAPI adapter
├── OPENAPI_QUICKSTART.md
└── ...
```

## 🛑 Parar o Servidor

Pressione **CTRL+C** no terminal onde está rodando.

## 🔄 Reiniciar Servidor com Reload

Para desenvolvimento com reload automático:

```powershell
python run_openapi_server.py --reload
```

O servidor vai reiniciar automaticamente ao salvar arquivos.

## 📚 Documentação Completa

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [OpenAPI 3.1.0](https://spec.openapis.org/oas/v3.1.0)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [ReDoc](https://redoc.ly/)

## ✅ Checklist - Próximos Passos

- [ ] Acessar `http://localhost:8000/docs` e testar endpoints
- [ ] Configurar Meilisearch se quiser buscas reais
- [ ] Integrar API com aplicação cliente
- [ ] Deploy em produção via Docker
- [ ] Customizar openapi.json conforme necessário

---

**Servidor iniciado com sucesso! 🎉**

Próximo passo: Abra http://localhost:8000/docs no navegador
