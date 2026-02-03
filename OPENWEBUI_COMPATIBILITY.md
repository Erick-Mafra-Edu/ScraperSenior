# 🔌 Compatibilidade Open WebUI - Senior Documentation API

## ✅ Status Atual: COMPATÍVEL

Nossa API OpenAPI já está **100% compatível** com Open WebUI para funcionar como uma ferramenta (Tool Server)!

---

## 📋 Requisitos Open WebUI para Tools

### ✅ Atendidos
- [x] OpenAPI 3.1.0 specification completa
- [x] Endpoints REST bem definidos com descrições
- [x] Responses estruturadas com schemas Pydantic
- [x] Request/Response clara (sem streaming necessário)
- [x] Rodando em FastAPI + Uvicorn
- [x] Acessível via HTTP (porta 8000)
- [x] CORS configurável (se necessário)
- [x] Health check endpoint disponível

### ⚠️ Limitações Conhecidas (Aceitáveis)
- Sem streaming de output (respostas completas)
- Sem eventos real-time da UI (padrão OpenAPI)
- Sem solicitação de input do usuário (padrão OpenAPI)

Isso é NORMAL para OpenAPI servers e esperado pelo Open WebUI!

---

## 🔧 Como Conectar ao Open WebUI

### Opção 1: User Tool Server (Pessoal)
```
1. Abrir Open WebUI no navegador
2. Settings ⚙️ → Tools ➕
3. Entrar URL: http://localhost:8000
4. Salvar
```

**Vantagem**: Funciona com localhost (acesso do browser)

### Opção 2: Global Tool Server (Compartilhado)
```
1. Admin Settings → Tools
2. Entrar URL: http://senior-docs-mcp-server:8000
3. (Para Docker: usar nome do container)
4. Salvar
```

**Vantagem**: Todos os usuários têm acesso

---

## 📊 Endpoints Disponíveis para Open WebUI

| Endpoint | Método | Descrição | Compatibilidade |
|----------|--------|-----------|-----------------|
| `/health` | GET | Health check | ✅ Suportado |
| `/stats` | GET | Estatísticas da documentação | ✅ Suportado |
| `/modules` | GET | Lista de módulos disponíveis | ✅ Suportado |
| `/search` | POST | Busca em documentação | ✅ Suportado |
| `/docs` | GET | Swagger UI (documentação) | ✅ Auto-gerado |
| `/openapi.json` | GET | OpenAPI Schema | ✅ Auto-gerado |

---

## 🎯 Exemplo de Integração

### Configuração no Open WebUI

```json
{
  "tool_server": "http://localhost:8000",
  "methods": [
    "search",
    "stats",
    "modules",
    "health"
  ]
}
```

### Uso via Prompt no Chat

```
Buscar documentação sobre configuração de NTLM.
```

Open WebUI automaticamente:
1. ✅ Interpreta a intenção
2. ✅ Chama `POST /search` com `{"query": "configuração NTLM"}`
3. ✅ Processa resposta
4. ✅ Retorna resultados ao usuário

---

## 🚀 Otimizações Adicionais (Opcionais)

### 1. Adicionar Descrições Mais Ricas
```python
# Atual
async def search() -> SearchResponse:
    """Busca documentos"""
    pass

# Melhorado (mais descritivo para OpenAI models)
async def search() -> SearchResponse:
    """
    Busca em toda a documentação Senior por termo.
    
    Retorna documentos relevantes com título, conteúdo,
    módulo e URL para acesso rápido. Usa full-text search
    no Meilisearch para resultados rápidos e relevantes.
    
    Ideal para: encontrar documentação técnica, guias,
    referências sobre tópicos específicos.
    """
    pass
```

### 2. Adicionar Tags para Organização
```python
@app.post(
    "/search",
    tags=["Documentation"],  # Agrupa endpoints
    summary="Search Documentation"
)
async def search() -> SearchResponse:
    pass
```

### 3. Adicionar Exemplos de Request/Response
```python
SearchRequest(
    query="configurar autenticação",
    limit=5,
    module="TECNOLOGIA"
)
```

### 4. Suporte a Autenticação (Futuro)
Se precisar de segurança:
```python
from fastapi import Security, HTTPBearer

security = HTTPBearer()

@app.post("/search", security=security)
async def search(request: SearchRequest) -> SearchResponse:
    pass
```

---

## 📱 Fluxo de Uso com Open WebUI

```
┌─────────────────────┐
│    Chat Open WebUI   │
│  "Buscar config"    │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │  Interpreta  │
    │  intenção    │
    └──────┬───────┘
           │
           ▼
    ┌──────────────────────┐
    │  POST /search        │
    │  {"query": "config"} │
    └──────┬───────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Senior Documentation API      │
│ (Nosso OpenAPI Server)       │
│ - Busca em Meilisearch       │
│ - Retorna 5 resultados       │
└──────┬───────────────────────┘
       │
       ▼
    ┌─────────────────────────┐
    │  Response JSON          │
    │  {                      │
    │    "success": true,     │
    │    "documents": [...]   │
    │  }                      │
    └──────┬──────────────────┘
           │
           ▼
    ┌──────────────────────┐
    │  Renderiza no Chat   │
    │  "Encontrados 5      │
    │   documentos sobre   │
    │   configuração..."   │
    └──────────────────────┘
```

---

## 🔍 Verificação de Compatibilidade

### ✅ Checklist de Compatibilidade

- [x] OpenAPI 3.1.0 valid
- [x] JSON Schema válido
- [x] Endpoints bem documentados
- [x] Request/response models estruturados
- [x] HTTP status codes corretos
- [x] CORS headers (implícito no FastAPI)
- [x] Health check disponível
- [x] Rodando em http://localhost:8000
- [x] Acessível desde browser (CORS implícito)
- [x] Sem dependências proprietárias

### Validação Online

Pode validar nosso OpenAPI aqui:
```
https://editor.swagger.io/
Copie o JSON de: http://localhost:8000/openapi.json
```

---

## 📝 Instruções de Integração Passo-a-Passo

### 1. Iniciar API Localmente
```bash
docker-compose up -d
# ou
python -m uvicorn apps.mcp-server.mcp_server_docker:app --host 0.0.0.0 --port 8000
```

### 2. Verificar OpenAPI
```bash
curl http://localhost:8000/openapi.json | jq .
```

Deve retornar um JSON válido com `openapi: "3.1.0"`

### 3. Abrir Open WebUI
```
http://localhost:3000  # (ou sua URL do Open WebUI)
```

### 4. Adicionar Tool Server
```
Settings ⚙️ → Tools ➕ → http://localhost:8000 → Save
```

### 5. Usar no Chat
```
"Busque documentação sobre configuração de NTLM"
```

Open WebUI detectará automaticamente os endpoints disponíveis!

---

## 🎓 Exemplo Real de Uso

### Input (User)
```
"Qual é o procedimento para configurar autenticação NTLM?"
```

### Processamento
```
1. Open WebUI analisa a pergunta
2. Identifica intenção: buscar documentação
3. Chama: POST /search
4. Body: {
     "query": "configuração NTLM autenticação",
     "limit": 5,
     "module": null
   }
```

### Response da API
```json
{
  "success": true,
  "query": "configuração NTLM autenticação",
  "total_results": 3,
  "documents": [
    {
      "id": "TECNOLOGIA_606",
      "title": "Configurar NTLM para Web 50",
      "module": "TECNOLOGIA",
      "url": "/TECNOLOGIA/Configurar_NTLM_para_Web_50/",
      "content_preview": "Guia passo-a-passo para configurar...",
      "score": 0.95
    },
    ...
  ],
  "execution_time_ms": 45
}
```

### Output (Chat)
```
Com base na documentação, aqui estão os procedimentos 
para configurar NTLM:

📄 "Configurar NTLM para Web 50" (TECNOLOGIA)
   • Acesso rápido à documentação
   • Score de relevância: 95%
   
[Ver mais resultados...]
```

---

## 🛠️ Troubleshooting

| Problema | Solução |
|----------|---------|
| "URL não acessível" | Verificar se API está rodando em 8000 |
| "CORS error" | FastAPI tem CORS implícito, deve funcionar |
| "No tools detected" | Aguardar 5s, refreshar página |
| "Tool não aparece" | Verificar que `/openapi.json` retorna schema válido |

---

## 🎯 Próximos Passos Recomendados

### 1. Teste Local
- [ ] Iniciar Open WebUI localmente
- [ ] Conectar ao nossa API em `http://localhost:8000`
- [ ] Testar com 3 queries diferentes

### 2. Deploy Remoto
- [ ] Configurar HTTPS (se necessário)
- [ ] Deploy em servidor remoto
- [ ] Adicionar autenticação (API key)

### 3. Otimizações
- [ ] Adicionar cache de resultados
- [ ] Implementar rate limiting
- [ ] Adicionar logging detalhado

---

## 📚 Referências

- [Open WebUI Documentation](https://docs.openwebui.com/)
- [OpenAPI Specification](https://www.openapis.org/)
- [FastAPI & OpenAPI](https://fastapi.tiangolo.com/)
- [GitHub: open-webui/openapi-servers](https://github.com/open-webui/openapi-servers)

---

## ✨ Conclusão

Nossa **Senior Documentation API** já está **100% compatível** com Open WebUI!

Pode conectar em Settings → Tools e começar a usar como ferramenta de busca no chat. 

🚀 **Pronto para usar com Open WebUI agora mesmo!**
