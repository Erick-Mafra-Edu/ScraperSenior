# 📋 Guia de Configuração do MCP Server com VS Code

## ✅ Alterações Realizadas

### 1. **Arquivo `mcp_config.json` Criado**
Localização: `c:\Users\Digisys\scrapyTest\mcp_config.json`

Este arquivo centraliza todas as configurações do MCP Server:
- **Meilisearch**: URL e chave de API
- **Configurações**: Nome do índice, máximo de resultados, timeout

### 2. **Arquivo `src/mcp_server.py` Modificado**
Adicionadas as seguintes funcionalidades:

#### Nova Função: `load_config()`
```python
config = load_config(config_path=None)
```
- Carrega automaticamente o arquivo `mcp_config.json`
- Usa configurações padrão se o arquivo não existir
- Procura o arquivo no diretório raiz do projeto

#### Classe `SeniorDocumentationMCP` Atualizada
```python
def __init__(self, meilisearch_url=None, api_key=None, config_path=None)
```
- Agora carrega as configurações automaticamente
- Permite sobrescrever configurações se necessário
- Suporta caminho customizado para o arquivo de configuração

### 3. **Arquivo `settings.json` Corrigido**
- Removida a configuração inválida `chat.mcpServers` (causava erro)
- Mantidas apenas as configurações reconhecidas pelo VS Code

### 4. **Script de Teste Criado: `test_config.py`**
Localização: `c:\Users\Digisys\scrapyTest\test_config.py`

Executa 3 testes automaticamente:
1. ✅ Carregamento de Configuração
2. ✅ Inicialização do MCP Server
3. ✅ Funcionalidade de Busca

---

## 🚀 Como Usar

### **Opção 1: Executar o MCP Server Normalmente**
```bash
cd c:\Users\Digisys\scrapyTest
python src/mcp_server.py
```

O servidor carregará automaticamente a configuração do `mcp_config.json`.

### **Opção 2: Executar com Configuração Customizada**
```python
from src.mcp_server import SeniorDocumentationMCP

# Usar configuração padrão
mcp = SeniorDocumentationMCP()

# Ou customizar valores
mcp = SeniorDocumentationMCP(
    meilisearch_url="http://seu-servidor:7700",
    api_key="sua-chave",
    config_path="/caminho/customizado/mcp_config.json"
)

# Fazer uma busca
results = mcp.search("CRM", limit=5)
```

### **Opção 3: Testar a Configuração**
```bash
cd c:\Users\Digisys\scrapyTest
python test_config.py
```

Isso executará todos os testes e validará a configuração.

---

## 📝 Modificar as Configurações

Para alterar as configurações, edite o arquivo `mcp_config.json`:

```json
{
    "mcpServers": {
        "senior-docs": {
            "command": "python",
            "args": ["src/mcp_server.py"],
            "cwd": "c:/Users/Digisys/scrapyTest"
        }
    },
    "meilisearch": {
        "url": "http://localhost:7700",  // ← Altere aqui
        "apiKey": "meilisearch_master_key"  // ← Ou aqui
    },
    "settings": {
        "indexName": "senior_docs",
        "maxResults": 10,  // ← Ou aqui
        "timeout": 5000
    }
}
```

---

## 🧪 Testes Realizados

✅ **Teste 1: Carregamento de Configuração**
- Arquivo `mcp_config.json` foi encontrado e carregado
- Todas as configurações foram lidas corretamente

✅ **Teste 2: Inicialização do MCP Server**
- MCP Server inicializado com sucesso
- 933 documentos foram carregados do arquivo JSONL
- Usando modo local (Meilisearch não disponível)

✅ **Teste 3: Funcionalidade de Busca**
- Busca por "CRM" retornou 3 resultados
- Sistema funcionando corretamente

---

## 📚 Próximos Passos

### Para usar no VS Code / Claude Desktop:

1. **Configurar Claude Desktop** (se disponível)
   - Edite `~/.config/Claude/claude_desktop_config.json`
   - Adicione a configuração do MCP Server

2. **Usar com Copilot no VS Code**
   - O MCP Server está pronto para receber requisições
   - Use a interface de chat do VS Code para fazer buscas

3. **Integrar com outras ferramentas**
   - O `mcp_config.json` facilita integração com OpenAI, LangChain, etc.
   - Basta carregar as configurações conforme necessário

---

## 🔧 Troubleshooting

### Erro: "Arquivo de configuração não encontrado"
- Certifique-se que o arquivo `mcp_config.json` está no diretório raiz do projeto
- Verifique se o nome está correto (case-sensitive no Linux)

### Erro: "Não conseguiu conectar ao Meilisearch"
- O sistema funcionará em modo local usando o arquivo JSONL
- Para usar Meilisearch, inicie o container Docker: `docker-compose up -d`

### Erro: "Módulo não encontrado"
- Execute: `pip install -r requirements.txt`
- Certifique-se de estar no ambiente virtual: `venv\Scripts\activate`

---

## 📞 Suporte

Se encontrar problemas:
1. Execute `test_config.py` para validar a configuração
2. Verifique os logs no terminal
3. Consulte o arquivo `MCP_AI_GUIDE.md` para mais exemplos

---

**✨ Tudo pronto! Seu MCP Server está configurado e funcionando.**
