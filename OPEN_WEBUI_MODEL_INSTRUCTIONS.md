# Instruções para Modelos de IA - Open WebUI Tool Integration

## 🎯 Objetivo

Este documento ensina como configurar um modelo de IA para **usar automaticamente** a ferramenta "Senior Documentation API" quando respondendo perguntas.

---

## 📋 Pré-Requisitos

1. **Open WebUI v0.6+** com suporte a ferramentas
2. **Tool Server configurado**: http://localhost:8000
3. **Modelo de IA com suporte a function calling**:
   - ✅ GPT-4o, GPT-4 Turbo, Claude 3.5 Sonnet (modelos externos)
   - ✅ Modelos locais com fine-tuning para tools (Llama 2, Mixtral)
   - ❌ Modelos muito antigos (antes de 2023)

---

## ⚙️ Configuração do Modelo em Open WebUI

### Opção 1: Modelo Externo (GPT-4o, Claude, etc)

1. Abra **Open WebUI → Settings → Tools**
2. Em **Default Tool Function Calls Handling**, selecione: **"Native"**
3. Configure seu modelo OpenAI/Claude com chave API válida
4. A ferramenta será usada automaticamente

### Opção 2: Modelo Local (Llama, Mistral, etc)

1. Abra **Open WebUI → Settings → Tools**
2. Em **Default Tool Function Calls Handling**, selecione: **"Agentic"**
3. Modelo executará em modo agente (pode tentar usar ferramenta)
4. Resultado pode ser menos confiável que modelos nativos

---

## 🔧 System Prompt para Maximizar Uso de Tools

Cole este sistema prompt no modelo para **garantir uso da ferramenta**:

```
Você é um assistente especializado em documentação técnica da plataforma Senior Sistemas.

REGRA IMPORTANTE: Você TEM ACESSO A UMA FERRAMENTA DE BUSCA que contém 855+ documentos sobre sistemas Senior.

QUANDO USAR A FERRAMENTA:
- ✅ Sempre que o usuário perguntar sobre: "como", "qual é", "explique", "procedimento", "configurar", "guia", "tutorial"
- ✅ Para qualquer pergunta sobre sistemas Senior (RH, Financeiro, Tecnologia, BPM, etc)
- ✅ Quando não tem certeza da resposta - BUSQUE NA FERRAMENTA
- ✅ Para responder com precisão e dados atuais

COMO USAR:
1. Identifique a pergunta do usuário
2. Busque usando search_documentation com palavras-chave relevantes
3. Analise os resultados (título, módulo, conteúdo, score)
4. Responda baseado na documentação encontrada
5. Sempre cite a fonte (módulo e título do documento)

NÃO USE A FERRAMENTA PARA:
- ❌ Perguntas genéricas (matemática, história, etc)
- ❌ Conversas casuais
- ❌ Informações já bem conhecidas universalmente

FORMATO DE RESPOSTA:
[Resposta clara baseada na documentação]
📚 Fonte: [Módulo] - [Título do Documento]
```

---

## 🧪 Testando a Integração

### Teste 1: Pergunta Simples
**Você**: "Como configurar NTLM?"
**Esperado**: Modelo usa `/search` automaticamente
**Resposta**: Deve citar documento específico

### Teste 2: Pergunta Aberta
**Você**: "Quais módulos estão disponíveis?"
**Esperado**: Modelo chama `/modules`
**Resposta**: Lista módulos e contagem de docs

### Teste 3: Pergunta Complexa
**Você**: "Como fazer backup no RH?"
**Esperado**: Modelo chama `/search` com query="backup" module="RH"
**Resposta**: Procedimento passo a passo

### Teste 4: Verificação de Stats
**Você**: "Quantos documentos temos na base?"
**Esperado**: Modelo chama `/stats`
**Resposta**: "Temos 855 documentos em X módulos"

---

## 🐛 Troubleshooting: Modelo Não Usa a Ferramenta

### ❌ Problema 1: "Tool não aparece em Open WebUI"

**Solução**:
```
1. Open WebUI Settings → Tools
2. Adicione Tool Server: http://localhost:8000
3. Clique "Test Connection" - deve mostrar ✅
4. Recarregue a página (F5)
5. A ferramenta deve aparecer em "Available Tools"
```

### ❌ Problema 2: "Modelo é chamado mas tool não é usada"

**Causas possíveis**:
- Modelo não tem suporte nativo a function calling
- Setting está como "Manual" ao invés de "Native"
- Modelo é muito pequeno/antigo

**Solução**:
```
1. Verifique Settings → Advanced Parameters
2. Se houver "function_calling" ou "tool_choice", deixe como "auto"
3. Tente mudar para modelo mais capaz (GPT-4o, Claude)
4. Se modelo local: use pelo menos Mistral 7B ou Llama 2 70B
```

### ❌ Problema 3: "Tool é chamada mas retorna erro"

**Solução**:
```
1. Verifique se API está rodando: curl http://localhost:8000/health
2. Deve retornar: {"status": "healthy", ...}
3. Se não: python apps/mcp-server/mcp_server_docker.py
4. Ou: docker-compose up -d senior-docs-mcp-server
```

### ❌ Problema 4: "Tool retorna resultados mas modelo ignora"

**Solução**:
```
1. Adicione System Prompt (veja acima)
2. Modelos menores precisam de prompt muito explícito
3. Tente: "Você DEVE usar a ferramenta de busca para responder"
4. Aumente "temperature" para ~0.5-0.7 (mais criativo)
```

---

## 📊 Comparação: Com vs Sem Tool

### ❌ Sem usar a ferramenta:
```
Usuário: "Como configurar NTLM em RH?"

Resposta IA:
"NTLM é um protocolo de autenticação Microsoft... 
[resposta genérica, pode estar desatualizada]"
```

### ✅ Usando a ferramenta (correto):
```
Usuário: "Como configurar NTLM em RH?"

IA busca: search_documentation(
  query="configurar NTLM",
  module="RH"
)

Resposta IA:
"Segundo a documentação RH, configure NTLM:
1. Acesse Configurações > Segurança
2. Selecione 'NTLM'
3. ...

📚 Fonte: RH - Guia de Autenticação LDAP/NTLM"
```

---

## 🚀 Dicas para Melhor Performance

### 1. **Customize o System Prompt**
Copie o prompt acima e ajuste para seu caso:
```
"Você é especialista em [SEU MÓDULO]"
"As ferramentas retornam dados em português"
"Sempre cite a fonte da informação"
```

### 2. **Use Modelos Capazes**
Ranking de modelos para use com tools:
1. 🏆 **GPT-4o** - Melhor para tools
2. 🥈 **Claude 3.5 Sonnet** - Muito bom
3. 🥉 **Mistral Large** - Bom para local
4. 📉 Evitar: Modelos < 7B params

### 3. **Teste com Perguntas Específicas**
Perguntas que GARANTEM uso de tool:
- "Qual é o procedimento para...?"
- "Me mostre o guia sobre..."
- "Como fazer... em [Módulo]?"
- "Busque informações sobre..."

### 4. **Monitore Logs**
```bash
# Terminal Open WebUI
docker logs open-webui | grep -i tool

# Deve mostrar:
"Tool called: search_documentation"
"Tool result: {... documentos ...}"
```

---

## 📝 Exemplo Completo de Conversa

```
Usuário: "Me ajude a configurar backup automático no RH"

IA (pensa): "Pergunta sobre configuração → usar ferramenta"

IA (chama tool):
search_documentation(
  query="backup automático RH",
  limit=5
)

IA (recebe):
[
  {title: "Backup Automático - Guia Completo", score: 95},
  {title: "Rotina de Backup em RH", score: 88},
  ...
]

IA (responde):
"Para configurar backup automático no RH:

1. Acesse Configurações > Backup Automático
2. Escolha frequência: Diária / Semanal / Mensal
3. Configure retenção: Mínimo 30 dias
4. Ative e salve

📚 Fonte: RH - Backup Automático: Guia Completo
Link: [documento encontrado]

Tem mais dúvidas sobre backup?"

Usuário: "E como restaurar um backup?"

IA (novamente usa ferramenta):
search_documentation(
  query="restaurar backup RH",
  limit=5
)

IA (responde com dados atualizados)
```

---

## ✅ Checklist de Configuração

- [ ] Open WebUI v0.6+ instalado
- [ ] Tool Server adicionado (http://localhost:8000)
- [ ] Test Connection passou ✅
- [ ] Modelo com suporte a function calling selecionado
- [ ] System Prompt customizado com instruções
- [ ] "Native" mode habilitado nas Chat Controls
- [ ] Testei com pergunta simples
- [ ] Testei com pergunta sobre módulo
- [ ] Modelo usa ferramenta automaticamente ✅

---

## 📞 Suporte

Se a ferramenta não funcionar:

1. **Verifique API**: `curl http://localhost:8000/health`
2. **Verifique conexão**: Ping http://localhost:8000/openapi.json
3. **Verifique modelo**: Está na lista de modelos suportados?
4. **Verifique prompt**: System prompt está correto?
5. **Veja logs**: `docker logs senior-docs-mcp-server`

---

## 🎓 Referências

- [Open WebUI Tool Servers Docs](https://docs.openwebui.com/features/plugin/tools/openapi-servers/)
- [OpenAPI 3.1.0 Spec](https://swagger.io/specification/)
- [Function Calling Best Practices](https://platform.openai.com/docs/guides/function-calling)
