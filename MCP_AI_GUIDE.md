# Guia: Usando MCP Server com Modelos de IA

Este guia explica como integrar o Senior Documentation MCP Server com modelos de IA e como executar o projeto.

## 🚀 Como Executar o Projeto

### Opção 1: MCP Server Local (Mais Rápido)

```bash
# Setup inicial (primeira vez)
pip install -r requirements.txt
playwright install chromium

# Executar MCP Server
python src/mcp_server.py
```

**Características:**
- Usa índice JSONL local (docs_indexacao_detailed.jsonl)
- Sem dependências externas
- Performance: ~1ms por query
- Porta: Comunica via stdin/stdout (padrão MCP)

### Opção 2: MCP Server com Docker (Recomendado para Produção)

```bash
# Build e execute
docker-compose up -d

# Verificar status
curl http://localhost:8000/health
```

**Características:**
- Stack completo: Meilisearch + MCP Server
- Busca em múltiplas máquinas
- Health checks em /health, /ready, /stats
- Container seguro (non-root user)

### Opção 3: Ambiente de Desenvolvimento

```bash
# Executar testes
python src/test_mcp_server.py

# Testar busca manualmente
python -c "
import json
from src.mcp_server import SeniorDocumentationMCP
mcp = SeniorDocumentationMCP()
results = mcp.search_docs('CRM')
print(json.dumps(results, indent=2))
"
```

---

## 🤖 Integrando com Modelos de IA

### Claude (com MCP)

1. **Configurar VS Code ou Claude Desktop**

Adicione no `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "senior-docs": {
      "command": "python",
      "args": ["src/mcp_server.py"],
      "cwd": "/caminho/para/scrapyTest"
    }
  }
}
```

2. **Usar no Claude**

```
Você pode buscar documentação do Senior usando @senior-docs

"@senior-docs: Como configurar CRM?"
→ O Claude terá acesso às 4 ferramentas MCP
```

### OpenAI Assistant API

```python
from openai import OpenAI
import json

client = OpenAI(api_key="seu-api-key")

# 1. Definir as ferramentas MCP
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "Busca documentação do Senior",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Termo de busca"},
                    "module": {"type": "string", "description": "Módulo específico (opcional)"},
                    "limit": {"type": "integer", "description": "Limite de resultados"}
                },
                "required": ["query"]
            }
        }
    }
]

# 2. Criar assistente
assistant = client.beta.assistants.create(
    name="Senior Documentation Expert",
    instructions="Você é um especialista em documentação Senior. Use a ferramenta search_docs para responder perguntas sobre CRM, RH, Financeiro, etc.",
    tools=tools,
    model="gpt-4"
)

# 3. Usar assistente
thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Como configuro um contato no CRM?"
)

# 4. Executar e processar ferramentas
run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id)
# ... (processar responses com tool_calls)
```

### LangChain

```python
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
import json

# 1. Criar ferramentas
from src.mcp_server import SeniorDocumentationMCP
mcp = SeniorDocumentationMCP()

@tool
def search_senior_docs(query: str, module: str = None, limit: int = 5) -> str:
    """Busca documentação do Senior"""
    results = mcp.search_docs(query, module, limit)
    return json.dumps(results, ensure_ascii=False)

@tool
def list_senior_modules() -> str:
    """Lista módulos disponíveis"""
    modules = mcp.list_modules()
    return json.dumps(modules, ensure_ascii=False)

# 2. Criar agente
tools = [search_senior_docs, list_senior_modules]
llm = ChatOpenAI(model="gpt-4", temperature=0)
agent = create_openai_tools_agent(llm, tools, prompt)
executor = AgentExecutor.from_agent_and_tools(agent, tools)

# 3. Usar
response = executor.invoke({
    "input": "Como faço para criar um novo usuário no CRM?"
})
print(response["output"])
```

### Anthropic SDK (Python)

```python
import anthropic
import json
from src.mcp_server import SeniorDocumentationMCP

mcp = SeniorDocumentationMCP()
client = anthropic.Anthropic(api_key="seu-api-key")

# 1. Definir ferramentas
tools = [
    {
        "name": "search_docs",
        "description": "Busca documentação técnica do Senior",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "module": {"type": "string"},
                "limit": {"type": "integer"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "list_modules",
        "description": "Lista todos os módulos disponíveis",
        "input_schema": {"type": "object", "properties": {}}
    }
]

# 2. Processador de ferramentas
def process_tool(name, input_data):
    if name == "search_docs":
        return mcp.search_docs(
            input_data.get("query"),
            input_data.get("module"),
            input_data.get("limit", 5)
        )
    elif name == "list_modules":
        return mcp.list_modules()

# 3. Loop de processamento
messages = [
    {
        "role": "user",
        "content": "Como configurar acesso para um novo usuário no módulo Gestão de Relacionamento CRM?"
    }
]

while True:
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )
    
    if response.stop_reason == "end_turn":
        # Resposta final
        for block in response.content:
            if hasattr(block, "text"):
                print(block.text)
        break
    
    if response.stop_reason == "tool_use":
        # Processar ferramentas
        for block in response.content:
            if block.type == "tool_use":
                result = process_tool(block.name, block.input)
                messages.append({"role": "assistant", "content": response.content})
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, ensure_ascii=False)
                        }
                    ]
                })
```

---

## 📊 As 4 Ferramentas MCP Disponíveis

### 1. `search_docs`
Busca full-text na documentação com filtro por módulo.

```python
# Busca simples
results = mcp.search_docs("como criar usuário")

# Com filtro
results = mcp.search_docs("contato", module="GESTAO_DE_RELACIONAMENTO_CRM", limit=10)
```

**Response:**
```json
{
  "status": "success",
  "total": 3,
  "results": [
    {
      "title": "Criando um novo contato",
      "url": "https://...",
      "module": "GESTAO_DE_RELACIONAMENTO_CRM",
      "excerpt": "Para criar um novo contato..."
    }
  ]
}
```

### 2. `list_modules`
Lista todos os módulos disponíveis.

```python
modules = mcp.list_modules()
```

**Response:**
```json
{
  "status": "success",
  "count": 17,
  "modules": [
    "GESTAO_DE_RELACIONAMENTO_CRM",
    "RONDA_SENIOR",
    "RECURSOS_HUMANOS",
    "FINANCEIRO",
    ...
  ]
}
```

### 3. `get_module_docs`
Retorna documentação completa de um módulo.

```python
docs = mcp.get_module_docs("GESTAO_DE_RELACIONAMENTO_CRM", limit=5)
```

### 4. `get_stats`
Retorna estatísticas do índice.

```python
stats = mcp.get_stats()
```

**Response:**
```json
{
  "status": "success",
  "stats": {
    "total_documents": 933,
    "modules_count": 17,
    "index_type": "local",
    "source": "JSONL"
  }
}
```

---

## 🔧 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'playwright'"
```bash
pip install -r requirements.txt
playwright install chromium
```

### MCP Server não responde
```bash
# Verificar se está rodando
python src/mcp_server.py

# Em outro terminal
python src/test_mcp_server.py
```

### Índice desatualizado
```bash
# Recriar índice
python -m src.indexers.index_local
```

### Docker compose com erro
```bash
# Ver logs
docker-compose logs mcp-server

# Reconstruir
docker-compose down
docker-compose up --build
```

---

## 💡 Boas Práticas

1. **Cache de Resultados**: Armazene resultados frequentes
2. **Timeout**: Configure timeout de 30s para queries
3. **Rate Limiting**: Limite a 100 queries/min
4. **Logs**: Ative logging para debug em produção
5. **Atualização**: Recriar índice mensalmente com novos dados

---

## 📚 Referências

- [MCP_SERVER.md](MCP_SERVER.md) - Documentação técnica completa
- [DOCKER.md](DOCKER.md) - Guia Docker
- [README.md](README.md) - Instruções gerais

---

## 📝 Próximos Passos

1. **Executar localmente**: `python src/mcp_server.py`
2. **Testar**: `python src/test_mcp_server.py`
3. **Integrar com seu modelo**: Use um dos exemplos acima
4. **Deploy em produção**: `docker-compose up -d`
