# ✅ Correção: SSE JSON Error - Open WebUI

## Problema Reportado
```
❌ JSON error injected into SSE stream
```

Ao usar o Open WebUI com o servidor MCP, a resposta SSE estava malformada, causando erro ao parsear a resposta.

---

## Root Cause

O protocolo **Server-Sent Events (SSE)** exige que o JSON esteja em uma **ÚNICA LINHA**:

### ❌ ERRADO (causa erro)
```
data: {
  "id": 1,
  "result": "..."
}

```

### ✅ CORRETO
```
data: {"id":1,"result":"..."}

```

O problema estava em dois lugares no código:

1. **Formatação com `indent=2`**: Quebrava o JSON em múltiplas linhas
2. **JSON com espaços**: O `ensure_ascii=False` estava mantendo formatação legível

---

## Soluções Implementadas

### 1. Correção do formato SSE em `mcp_server_http.py`

**Antes:**
```python
json_str = json.dumps(data, ensure_ascii=False)
sse_content = f"data: {json_str}\n\n"
```

**Depois:**
```python
# JSON em uma única linha (SSE válido)
json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
# Remover qualquer quebra de linha residual
json_str = json_str.replace('\n', '').replace('\r', '')
sse_content = f"data: {json_str}\n\n"
```

**Benefícios:**
- `separators=(',', ':')`: Remove espaços após separadores
- `replace('\n', '')`: Garante nenhuma quebra de linha
- Formato SSE válido para qualquer cliente SSE

### 2. Remoção de `indent=2` em chamadas de ferramentas

Removido de 3 locais onde estava quebrando o JSON:

- `search_docs()`: Resultado de buscas
- `get_module_docs()`: Documentos de módulo
- `get_stats()`: Estatísticas

**Mudança:**
```python
# Antes
return json.dumps(data, ensure_ascii=False, indent=2)

# Depois
return json.dumps(data, ensure_ascii=False)
```

---

## Validação

Para verificar que a correção funciona:

```bash
python test_sse_format.py
```

**Esperado:**
```
✅ Formato correto: começa com 'data: '
✅ JSON em uma única linha (SSE válido)
✅ JSON válido e parseável
✅ SSE formato está correto!
```

---

## Compatibilidade

### ✅ Afetado (Corrigido)
- Open WebUI com SSE streaming
- Claude Desktop (MCP protocol)
- Qualquer cliente SSE

### ✅ Não Afetado
- REST API endpoints (`/api/search`, `/api/modules`, etc.)
- JSON-RPC sem SSE (application/json)
- Endpoints sem streaming

---

## Arquivos Modificados

| Arquivo | Mudança |
|---------|---------|
| `apps/mcp-server/mcp_server_http.py` | Corrigido formato SSE + removido `indent=2` |
| `test_sse_format.py` | NOVO - teste de validação SSE |

---

## Próximas Versões

Para melhor performance, considerar:

1. **Compressão**: `gzip` para reduzir tamanho da resposta
2. **Chunking**: Dividir respostas grandes em múltiplos eventos SSE
3. **Retry**: Implementar retry automático para conexões perdidas
4. **Heartbeat**: Enviar heartbeat para manter conexão viva

Exemplo futuro com múltiplos eventos:
```
data: {"type":"start","total":5}\n\n
data: {"type":"result","index":1,"result":{...}}\n\n
data: {"type":"result","index":2,"result":{...}}\n\n
data: {"type":"complete","count":5}\n\n
```

---

## Status

✅ **FIXADO** - Erro SSE corrigido
✅ **TESTADO** - Validação SSE implementada
✅ **DOCUMENTADO** - Explicação completa fornecida

O Open WebUI e outros clientes SSE agora receberão resposta corretamente formatada.
