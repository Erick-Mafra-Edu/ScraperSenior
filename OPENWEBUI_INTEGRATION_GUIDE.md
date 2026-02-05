# Como Integrar as Tools ao Open WebUI

## 1. Preparação

### Verificar que o servidor MCP está rodando:
```bash
curl http://localhost:8000/health
```

Deve retornar:
```json
{
  "status": "ok",
  "timestamp": "..."
}
```

---

## 2. Adicionar as Tools no Open WebUI

### Opção A: Via Python (Recomendado)

1. **Copie o arquivo `openwebui_senior_tools.py` para o container/servidor do Open WebUI**

2. **No Open WebUI, vá para: Settings → Tools**

3. **Crie uma nova ferramenta Python com o seguinte código:**

```python
# Importe do arquivo que você copiou
from openwebui_senior_tools import Tools

# Instancie as tools
tools = Tools()

# Defina as funções que o OpenWebUI pode chamar:

async def search_documentation(query: str, module: str = None, strategy: str = "auto", limit: int = 5) -> str:
    """Busca na documentação Senior"""
    return await tools.consultar_documentacao_senior(query, module, strategy, limit)

async def list_modules() -> str:
    """Lista todos os módulos de documentação"""
    return await tools.listar_todos_modulos()

async def get_module_docs(module_name: str, limit: int = 20) -> str:
    """Obtém documentos de um módulo específico"""
    return await tools.consultar_modulo_especifico(module_name, limit)

async def get_stats() -> str:
    """Obtém estatísticas da base de documentação"""
    return await tools.obter_estatisticas_base()

async def get_full_document(document_id: str) -> str:
    """Recupera o conteúdo completo de um documento"""
    return await tools.recuperar_documento_completo(document_id)
```

### Opção B: Via REST/OpenAPI

1. **No Open WebUI, vá para: Settings → Tools**

2. **Crie uma ferramenta customizada com os endpoints:**

```
Base URL: http://host.docker.internal:8000/api
```

**Endpoints:**
- `GET /search?query=...&limit=5&strategy=auto` - Buscar
- `GET /modules` - Listar módulos
- `GET /modules/{module_name}?limit=20` - Docs do módulo
- `GET /stats` - Estatísticas

---

## 3. Usar as Tools em Conversas

### Exemplo 1: Perguntar sobre LSP
```
Usuário: "Como configurar LSP no Senior?"
LLM: Usa tool `search_documentation` com query="configurar LSP"
Resposta: Retorna documentos sobre LSP
```

### Exemplo 2: Explorar módulos
```
Usuário: "Quais módulos de documentação você tem?"
LLM: Usa tool `list_modules`
Resposta: Lista todos os módulos disponíveis
```

### Exemplo 3: Busca com contexto
```
Usuário: "Sobre implantação no RH"
LLM: Usa tool `search_documentation` com query="implantação", module="RH"
Resposta: Documentos específicos do RH
```

---

## 4. Configuração do Host

### Se O Open WebUI está no Docker:
```python
# openwebui_senior_tools.py
self.base_url = "http://host.docker.internal:8000"
```

### Se Open WebUI está local (sem Docker):
```python
# openwebui_senior_tools.py
self.base_url = "http://localhost:8000"
```

### Se está em rede remota:
```python
# openwebui_senior_tools.py
self.base_url = "http://people-fy.com:8000"
```

---

## 5. System Prompt Recomendado

Use este system prompt para direcionar o LLM a usar as tools:

```
Você é um assistente que responde perguntas sobre a documentação técnica da Senior.

Quando o usuário fizer uma pergunta:
1. Use a ferramenta `search_documentation` para buscar informações relevantes
2. Se precisar explorar módulos, use `list_modules` ou `get_module_docs`
3. Se a resposta inicial for insuficiente, use `get_full_document` para mais detalhes
4. Sintetize as informações e responda ao usuário em português

Lembre-se:
- "LSP" = Linguagem Senior de Programação
- Sempre cite a fonte (módulo e documento)
- Se não encontrar, sugira buscar em outro módulo
- Use `get_stats` para informar sobre a base quando perguntado
```

---

## 6. Teste Local (Sem Open WebUI)

Execute o script de teste:
```bash
python openwebui_senior_tools.py
```

Deve mostrar:
```
1️⃣ Buscando 'LSP'...
### 📚 Resultados para: 'LSP'
...

2️⃣ Listando módulos...
### 📚 Módulos de Documentação Disponíveis
...
```

---

## 7. Resolução de Problemas

### "Connection refused" ou "timeout"
- Verifique se o servidor MCP está rodando na porta 8000
- Teste: `curl http://localhost:8000/health`

### "Module not found" ou erro de import
- Certifique-se que `openwebui_senior_tools.py` está no PYTHONPATH
- Se em Docker, copie o arquivo para dentro do container

### Respostas genéricas demais
- Tente usar a estratégia `"quoted"` para buscas de frases exatas
- Use `strategy="and"` para garantir que todos os termos estejam presentes

### Documento não encontrado com `get_full_document`
- Verifique se o `document_id` vem dos resultados de busca
- Alguns documentos podem ter apenas resumo disponível

---

## 8. Estrutura de Resposta (Para Referência)

### /api/search
```json
{
  "status": "success",
  "query": "LSP",
  "parsed_query": "\"LSP\"",
  "strategy": "auto",
  "count": 5,
  "results": [
    {
      "title": "...",
      "url": "...",
      "module": "...",
      "content": "..."
    }
  ]
}
```

### /api/modules
```json
{
  "status": "success",
  "total_modules": 12,
  "modules": ["Help Center", "Release Notes", ...]
}
```

### /api/stats
```json
{
  "status": "success",
  "data": {
    "total_documents": 10456,
    "total_modules": 12,
    "indexed_date": "2026-02-05",
    "index_size": "45.3 MB"
  }
}
```

---

## 9. Dicas para Melhor Performance

1. **Cache**: Open WebUI faz cache de respostas. Respostas iguais são devolvidas mais rápido
2. **Limite**: Use `limit=5` para buscas rápidas, `limit=20+` para listagens completas
3. **Estratégia**: 
   - Use `"auto"` por padrão (inteligente)
   - Use `"quoted"` para frases exatas
   - Use `"and"` para garantir múltiplos termos
4. **Contexto**: Sempre passe `module` quando souber em qual módulo buscar

---

## 10. Próximos Passos

- Monitore os logs do servidor MCP para ver quais queries estão sendo feitas
- Refine o system prompt baseado no comportamento do LLM
- Considere adicionar mecanismos de feedback (thumbs up/down) para melhorar o ranking
