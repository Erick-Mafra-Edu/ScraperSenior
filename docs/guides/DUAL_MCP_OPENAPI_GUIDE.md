# Servidor Dual - MCP + OpenAPI

## 📋 Visão Geral

Este projeto agora suporta **AMBOS os protocolos** usando a ferramenta pronta [mcp-openapi-server](https://github.com/ivo-toby/mcp-openapi-server):

1. **MCP (Model Context Protocol)** - Para Claude, Cursor IDE, etc
2. **OpenAPI/REST** - Para Open WebUI, HTTP clients, integração genérica

O servidor `mcp-openapi-server` converte automaticamente a especificação OpenAPI da API do Meilisearch em ferramentas MCP disponíveis no Claude/Cursor e simultaneamente expõe endpoints HTTP REST para Open WebUI.

### O que é mcp-openapi-server?

Uma ferramenta pronta que:
- ✅ Converte qualquer OpenAPI spec em ferramentas MCP
- ✅ Suporta múltiplos transportes (stdio para Claude, HTTP para web)
- ✅ Autenticação Bearer token automática
- ✅ Sem necessidade de escrever código customizado
- ✅ Documentação interativa via Swagger/ReDoc

---

## 🚀 Como Usar

### Quick Start - OpenAPI via HTTP (30 segundos)

```bash
# Instalar a ferramenta (uma única vez)
npm install -g @ivotoby/openapi-mcp-server

# Rodar com Meilisearch local
npx @ivotoby/openapi-mcp-server \
  --api-base-url http://localhost:7700 \
  --openapi-spec http://localhost:7700/openapi.json \
  --headers "Authorization:Bearer 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa" \
  --transport http \
  --port 3000

# Ou em Docker
docker run -p 3000:3000 -e API_BASE_URL=http://meilisearch:7700 \
  -e OPENAPI_SPEC_PATH=http://meilisearch:7700/openapi.json \
  -e API_HEADERS="Authorization:Bearer 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa" \
  ivo-toby/mcp-openapi-server
```

### Quick Start - MCP via Stdio (Para Claude Desktop)

```bash
# Instalar
npm install -g @ivotoby/openapi-mcp-server

# Configurar Claude Desktop (macOS: ~/Library/Application\ Support/Claude/claude_desktop_config.json)
# Windows: %APPDATA%\Claude\claude_desktop_config.json
{
  "mcpServers": {
    "meilisearch-openapi": {
      "command": "npx",
      "args": ["-y", "@ivotoby/openapi-mcp-server"],
      "env": {
        "API_BASE_URL": "http://localhost:7700",
        "OPENAPI_SPEC_PATH": "http://localhost:7700/openapi.json",
        "API_HEADERS": "Authorization:Bearer 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa"
      }
    }
  }
}

# Restart Claude Desktop e a ferramenta estará disponível!
```

---

## 📡 Usando OpenAPI

### GET - Busca Simples

```bash
# Exemplo: Listar índices
curl -X GET http://localhost:3000/indexes \
  -H "Authorization: Bearer 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa"

# Exemplo: Pesquisar em índice
curl -X POST http://localhost:3000/indexes/documentation/search \
  -H "Authorization: Bearer 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa" \
  -H "Content-Type: application/json" \
  -d '{"q": "CRM"}'
```

Os endpoints disponíveis dependem do OpenAPI spec do Meilisearch. A ferramenta automaticamente converte para MCP tools quando rodando em modo stdio.

### OpenAPI Specification

A ferramenta automaticamente gera documentação Swagger/ReDoc. Acesse em:

```
http://localhost:3000/swagger  (Swagger UI)
http://localhost:3000/redoc    (ReDoc)
```

Ou use a documentação do Meilisearch diretamente:
```
http://localhost:7700/openapi.json
```

Resposta exemplo:
```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Meilisearch",
    "version": "1.11.0"
  },
  "paths": {
    "/indexes/{uid}/search": {
      "post": {
        "summary": "Search in index",
        "parameters": [...],
        "requestBody": {...}
      }
    }
  }
}
```

---

## 🔗 Documentação Interativa

Quando rodando em HTTP mode, acesse:

- **Swagger UI**: http://localhost:3000/swagger
- **ReDoc**: http://localhost:3000/redoc
- **OpenAPI JSON**: http://localhost:3000/api/openapi.json
- **Health Check**: http://localhost:3000/health

---

## 📦 Integração com Open WebUI

Open WebUI suporta integração nativa com APIs OpenAPI/HTTP. Adicione manualmente ou via UI:

1. **Via Open WebUI Settings**:
   - Vá para **Settings** > **Models**
   - Adicione novo backend com URL `http://localhost:3000`

2. **Via API HTTP customizada**:
   ```bash
   # Open WebUI pode chamar endpoints diretamente
   curl -X GET http://localhost:3000/indexes \
     -H "Authorization: Bearer SEU_TOKEN"
   ```

3. **Via MCP (melhor opção)**:
   - Configure `claude_desktop_config.json` (veja Quick Start acima)
   - Use em agentes que suportam MCP

---

## 🐳 Com Docker

### Docker Compose com mcp-openapi-server

```yaml
# docker-compose.yml
services:
  meilisearch:
    image: getmeili/meilisearch:v1.11.0
    ports:
      - "7700:7700"
    environment:
      MEILI_MASTER_KEY: ${MEILISEARCH_KEY}
  
  mcp-openapi-server:
    image: ivo-toby/mcp-openapi-server:latest
    ports:
      - "3000:3000"
    environment:
      API_BASE_URL: http://meilisearch:7700
      OPENAPI_SPEC_PATH: http://meilisearch:7700/openapi.json
      API_HEADERS: "Authorization:Bearer ${MEILISEARCH_KEY}"
      TRANSPORT_TYPE: http
      HTTP_PORT: 3000
    depends_on:
      - meilisearch
```

Rodar:

```bash
export MEILISEARCH_KEY=5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa
docker-compose up meilisearch mcp-openapi-server

# Acesso
curl http://localhost:3000/health
```

### Build customizado

Se precisar customizar, clone o repositório:

```bash
git clone https://github.com/ivo-toby/mcp-openapi-server.git
cd mcp-openapi-server
npm install
npm run build

# Usar localmente
npx bin/mcp-server.js \
  --api-base-url http://localhost:7700 \
  --openapi-spec http://localhost:7700/openapi.json \
  --headers "Authorization:Bearer SEU_TOKEN" \
  --transport http \
  --port 3000
```

---

## 🔧 Configuração

### Variáveis de Ambiente

Para **CLI** ou **Docker**:

```bash
# URL do servidor (Meilisearch)
export API_BASE_URL=http://localhost:7700

# Especificação OpenAPI
export OPENAPI_SPEC_PATH=http://localhost:7700/openapi.json
# OU ler do stdin:
export OPENAPI_SPEC_FROM_STDIN=true

# Headers de autenticação
export API_HEADERS="Authorization:Bearer 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa"

# Modo de transporte
export TRANSPORT_TYPE=http  # ou: stdio

# Configurações HTTP
export HTTP_PORT=3000
export HTTP_HOST=0.0.0.0
export ENDPOINT_PATH=/mcp

# Nomes customizados
export SERVER_NAME="Meilisearch MCP"
export SERVER_VERSION="1.0.0"

# Modo de carregamento de tools
export TOOLS_MODE=all  # ou: dynamic, explicit
```

### Argumentos CLI

```bash
npx @ivotoby/openapi-mcp-server \
  --api-base-url http://localhost:7700 \
  --openapi-spec http://localhost:7700/openapi.json \
  --headers "Authorization:Bearer TOKEN" \
  --name "Meilisearch MCP" \
  --transport http \
  --port 3000 \
  --host 0.0.0.0 \
  --path /mcp \
  --tools all  # all, dynamic, explicit
```

### Filtrar Endpoints Específicos

```bash
# Apenas endpoints de pesquisa
npx @ivotoby/openapi-mcp-server \
  --api-base-url http://localhost:7700 \
  --openapi-spec http://localhost:7700/openapi.json \
  --headers "Authorization:Bearer TOKEN" \
  --tool POST::indexes::uid::search \
  --tools explicit

# Apenas GET requests
npx @ivotoby/openapi-mcp-server \
  --api-base-url http://localhost:7700 \
  --openapi-spec http://localhost:7700/openapi.json \
  --operation get
```

---

## 🧪 Testando

### Teste via HTTP

```bash
# Health check
curl http://localhost:3000/health

# Listar índices
curl http://localhost:3000/indexes \
  -H "Authorization: Bearer 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa"

# Pesquisar
curl -X POST http://localhost:3000/indexes/documentation/search \
  -H "Authorization: Bearer 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa" \
  -H "Content-Type: application/json" \
  -d '{"q": "CRM", "limit": 5}'
```

### Teste em Python

```python
import requests
import json

BASE_URL = "http://localhost:3000"
TOKEN = "5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa"

headers = {"Authorization": f"Bearer {TOKEN}"}

# Health
r = requests.get(f"{BASE_URL}/health")
print("Health:", r.json())

# Listar índices
r = requests.get(f"{BASE_URL}/indexes", headers=headers)
print("Índices:", r.json())

# Pesquisar
payload = {"q": "CRM", "limit": 5}
r = requests.post(
    f"{BASE_URL}/indexes/documentation/search",
    json=payload,
    headers=headers
)
print("Resultados:", r.json())
```

### Teste via MCP (Claude Desktop)

Depois de configurar `claude_desktop_config.json`:

1. Restart Claude Desktop
2. Abra uma conversa
3. Procure pela ferramenta "Meilisearch" na lista de tools disponíveis
4. Use naturalmente: "Buscar documentação sobre CRM"

---

## 🔄 Fluxo de Funcionamento

### Modo MCP (Stdio) - Claude Desktop

```
Claude Desktop
    ↓ (MCP Protocol via stdio)
mcp-openapi-server
    ↓ (converte OpenAPI em MCP tools)
Meilisearch
    ↓
Resultados da busca
```

### Modo HTTP - Open WebUI / API Clients

```
Open WebUI / HTTP Client
    ↓ (HTTP REST com Bearer token)
mcp-openapi-server
    ↓ (expõe endpoints do Meilisearch)
Meilisearch
    ↓
JSON Response
```

### Modo DUAL - Ambos

```
Claude Desktop (stdio)
    ↓                    ↓
    |            Open WebUI (HTTP)
    |                   ↓
    └─────────────────┬─┘
                      ↓
            mcp-openapi-server
                      ↓
                Meilisearch
                      ↓
               Mesmos resultados
```

---

## ✅ Checklist de Verificação

- [ ] Node.js 18+ instalado: `node --version`
- [ ] npm instalado: `npm --version`
- [ ] Meilisearch rodando: `curl http://localhost:7700/health`
- [ ] API Key do Meilisearch disponível: `5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa`
- [ ] Instalar ferramenta: `npm install -g @ivotoby/openapi-mcp-server`
- [ ] Testar HTTP mode: `curl http://localhost:3000/health`
- [ ] Configurar Claude Desktop (macOS/Windows)
- [ ] Restart Claude Desktop
- [ ] Verificar ferramentas disponíveis em Claude
- [ ] Integração com Open WebUI funcionando

---

## 🚨 Troubleshooting

### Ferramenta não aparece em Claude Desktop

**Erro**: Ferramenta não listada após restart

**Solução**:
```bash
# Verificar se o servidor está rodando
curl http://localhost:3000/health

# Verificar path do config
echo $HOME  # macOS/Linux
echo $APPDATA  # Windows

# Checar se o path está correto:
# macOS: ~/Library/Application\ Support/Claude/claude_desktop_config.json
# Windows: %APPDATA%\Claude\claude_desktop_config.json
# Linux: ~/.config/Claude/claude_desktop_config.json

# Restartar Claude completamente (fechar todos os processos)
ps aux | grep Claude  # ou tasklist | findstr Claude (Windows)
```

### Erro de autenticação (401)

**Erro**: `{"error": "invalid_api_key"}`

**Solução**:
```bash
# Verificar formato do token
curl -H "Authorization: Bearer 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa" \
  http://localhost:7700/health

# Usar tipo de header correto
# MCP: API_HEADERS="Authorization:Bearer TOKEN"
# Não: "X-Meili-API-Key:TOKEN" (deprecated)
```

### Porta 3000 em uso

**Erro**: `Address already in use`

**Solução**:
```bash
# Usar outra porta
npx @ivotoby/openapi-mcp-server \
  --api-base-url http://localhost:7700 \
  --openapi-spec http://localhost:7700/openapi.json \
  --port 3001

# Ou matar processo atual
lsof -i :3000  # ou: netstat -ano | findstr :3000 (Windows)
kill -9 <PID>
```

### Meilisearch não encontrado

**Erro**: `ECONNREFUSED 127.0.0.1:7700`

**Solução**:
```bash
# Iniciar Meilisearch
docker-compose up meilisearch

# Ou em outro host
export API_BASE_URL=http://people-fy.com:7700
npx @ivotoby/openapi-mcp-server --api-base-url http://people-fy.com:7700 ...
```

### OpenAPI spec inválido

**Erro**: `Failed to parse OpenAPI spec`

**Solução**:
```bash
# Testar spec diretamente
curl http://localhost:7700/openapi.json

# Validar com ferramenta online
# https://editor.swagger.io

# Se estiver usando arquivo local:
npx @ivotoby/openapi-mcp-server --openapi-spec ./spec.json
```

---

## 🔐 Segurança

### Produção

Para ambiente de produção:

```bash
# Não exposer em 0.0.0.0 sem SSL
# Use nginx/reverse proxy com HTTPS

# Gerar nova API key no Meilisearch se necessário
curl -X POST http://meilisearch:7700/keys \
  -H "Authorization: Bearer master-key" \
  -d '{"name": "mcp-server", "actions": ["*"]}'

# Usar em docker-compose
export MEILISEARCH_KEY=nova-chave
docker-compose up
```

### Variáveis Sensíveis

Nunca commitar credenciais:

```bash
# .gitignore
.env
claude_desktop_config.json
api-keys.txt
```

Use `.env` files:

```bash
# .env
API_HEADERS=Authorization:Bearer SEU_TOKEN_SEGURO

# Carregar
export $(cat .env | xargs)
npx @ivotoby/openapi-mcp-server --headers "$API_HEADERS" ...
```

---

## 📚 Referências

- [Model Context Protocol](https://modelcontextprotocol.io)
- [mcp-openapi-server GitHub](https://github.com/ivo-toby/mcp-openapi-server)
- [mcp-openapi-server Docs](https://github.com/ivo-toby/mcp-openapi-server#readme)
- [Meilisearch](https://www.meilisearch.com)
- [Meilisearch OpenAPI](https://docs.meilisearch.com/reference/api/overview.html)
- [Claude Desktop MCP Setup](https://modelcontextprotocol.io/docs/tools/claude)
- [Open WebUI](https://github.com/open-webui/open-webui)

---

## 🎯 Próximos Passos

1. ✅ Usar ferramenta pronta `mcp-openapi-server`
2. ⏳ Testar integração com Claude Desktop
3. ⏳ Testar integração com Open WebUI
4. ⏳ Configurar para ambiente de produção
5. ⏳ Adicionar documentação customizada
6. ⏳ Monitorar performance

---

## 📝 Exemplo Completo - Produção

### 1. Docker Compose (Production)

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  meilisearch:
    image: getmeili/meilisearch:v1.11.0
    volumes:
      - meilisearch_data:/meili_data
    environment:
      MEILI_MASTER_KEY: ${MEILISEARCH_MASTER_KEY}
      MEILI_ENV: production
    restart: unless-stopped

  mcp-server:
    image: ivo-toby/mcp-openapi-server:latest
    ports:
      - "3000:3000"
    environment:
      API_BASE_URL: http://meilisearch:7700
      OPENAPI_SPEC_PATH: http://meilisearch:7700/openapi.json
      API_HEADERS: "Authorization:Bearer ${MEILISEARCH_API_KEY}"
      TRANSPORT_TYPE: http
      HTTP_PORT: 3000
      HTTP_HOST: 0.0.0.0
      NODE_ENV: production
    depends_on:
      - meilisearch
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Nginx reverse proxy (opcional, mas recomendado)
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - mcp-server
    restart: unless-stopped

volumes:
  meilisearch_data:
```

### 2. Nginx Config (SSL/HTTPS)

```nginx
# nginx.conf
upstream mcp {
    server mcp-server:3000;
}

server {
    listen 80;
    server_name api.senior-docs.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.senior-docs.com;

    ssl_certificate /etc/nginx/certs/cert.pem;
    ssl_certificate_key /etc/nginx/certs/key.pem;

    location / {
        proxy_pass http://mcp;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS
        add_header 'Access-Control-Allow-Origin' '*';
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type';
    }
}
```

### 3. Deploy

```bash
# Carregar variáveis
export MEILISEARCH_MASTER_KEY=seu-master-key
export MEILISEARCH_API_KEY=seu-api-key

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Verificar
docker-compose logs -f mcp-server

# Backup
docker-compose exec meilisearch curl \
  -X POST http://localhost:7700/dumps \
  -H "Authorization: Bearer ${MEILISEARCH_MASTER_KEY}"
```

---

**Última atualização**: 2026-02-02
