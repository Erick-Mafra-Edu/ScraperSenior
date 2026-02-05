# 🚀 Quick Start - Prompt LSP com Busca Inteligente

## ⚡ 30 Segundos (TL;DR)

Use o **PROMPT 9 (Universal)** do arquivo `OPEN_WEBUI_SYSTEM_PROMPTS.md`.

Ele:
✅ Funciona para qualquer tópico Senior
✅ Busca automaticamente quando apropriado
✅ Tenta múltiplas variações de termo
✅ Sempre cita a fonte
✅ Oferece próximas perguntas

---

## 📋 Como Implementar (3 passos)

### Passo 1: Copiar o Prompt
Abra `OPEN_WEBUI_SYSTEM_PROMPTS.md` e procure por **"PROMPT 9"**.

Copie TODO o texto dentro dos ``` (do `🎯 VOCÊ É:` até `---`).

### Passo 2: Cola no Open WebUI
1. Abra Open WebUI
2. Clique em ⚙️ (engrenagem) → "Edit Chat Settings"
3. Cole o prompt em "System Prompt"
4. Clique "Save"

### Passo 3: Ativar Tool
1. Verifique se "Senior Documentation API" está ativada
2. Advanced Parameters: `function_calling = "auto"`
3. Pronto! ✅

---

## 🎯 Como Funciona

```
┌─────────────────────────────┐
│ Usuário faz pergunta        │
└──────────┬──────────────────┘
           │
           ▼
    ┌──────────────────────┐
    │ É sobre Senior?      │
    └──────────┬───────────┘
           ┌──┴──┐
          SIM   NÃO
           │     │
           │     ▼ (conversa normal)
           │
           ▼
    ┌──────────────────────┐
    │ Extrair palavras-    │
    │ chave da pergunta    │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │ search_documentation │
    │ (termo + limit=5-10) │
    └──────────┬───────────┘
               │
        ┌──────┴──────┐
        │             │
    Encontrou?    Não encontrou?
        │             │
        │      Tentar outro termo
        │             │
        │        Encontrou?
        │      ┌──────┘│└───┐
        │      │    Sim    │
        │      │   Não     │
        │      ▼           ▼
        │   Responder   Avisar usuário
        │   com docs    "não encontrado"
        │   + fonte
        │
        ▼
    Resposta completa
    + Fonte
    + Próximas perguntas
```

---

## 💡 Estratégia de Busca Inteligente

O prompt usa esta lógica:

**Nível 1: Termo Específico**
```
Pergunta: "Como fazer backup no RH?"
→ Tenta buscar: "backup RH" (2 termos)
→ Se encontrar: ✅ Usa esses resultados
```

**Nível 2: Termo Genérico**
```
Se "backup RH" retornar 0:
→ Tenta buscar: "backup" (1 termo)
→ Se encontrar: ✅ Usa esses resultados
```

**Nível 3: Sinônimos**
```
Se "backup" retornar 0:
→ Tenta: "cópia de segurança"
→ Tenta: "restauração"
→ Se encontrar: ✅ Usa esses resultados
```

**Nível 4: Renderizar**
```
Se nada funcionar (raríssimo):
→ Responde: "Desculpe, não encontrei..."
→ Oferece alternativas
→ Recomenda contato com suporte
```

---

## ✅ Checklist de Implementação

- [ ] Encontrei PROMPT 9 em `OPEN_WEBUI_SYSTEM_PROMPTS.md`
- [ ] Copiei todo o conteúdo do prompt
- [ ] Colei em Open WebUI → System Prompt
- [ ] Salvei as configurações
- [ ] Ativei "Senior Documentation API"
- [ ] Testei com pergunta técnica
- [ ] ✅ Assistente fez busca automaticamente?

---

## 🧪 Perguntas de Teste

Use estas para validar se está funcionando:

### Teste 1: LSP
```
Como funciona a compilação de regras LSP?
```
✅ Esperado: Busca e retorna artigos sobre compilação

### Teste 2: Módulo
```
Quais são os procedimentos para configurar o módulo RH?
```
✅ Esperado: Busca e retorna procedimentos do RH

### Teste 3: Erro
```
O que significa erro de "API key inválida"?
```
✅ Esperado: Busca e retorna explicação do erro

### Teste 4: Implantação
```
Como fazer implantação de um novo módulo?
```
✅ Esperado: Busca e retorna guia de implantação

### Teste 5: Negociação (Assistente Não Deve Buscar)
```
Qual é a capital da França?
```
✅ Esperado: Responde normalmente SEM buscar

---

## 🔍 Exemplos Reais de Funcionamento

### Exemplo 1: Busca com Sucesso

```
👤 "Como fazer backup no RH?"

🤖 [Pensa: é sobre RH → buscar]
🔍 [Busca: "backup RH" com limit=5]
✅ [Encontrou 5 resultados]

Resposta:
"Para fazer backup no RH, siga estes passos:
1. [Do documento]
2. [Do documento]
...

📌 Fonte: RH - Procedimentos de Backup
🔗 Referência: https://..."
```

### Exemplo 2: Busca com Retry

```
👤 "Explique a validação de regra LSP completa"

🤖 [Pensa: é sobre LSP → buscar]
🔍 [Tenta: "validação regra LSP completa"]
❌ [Retornou 0]

🔍 [Tenta: "validação regra"]
❌ [Retornou 0]

🔍 [Tenta: "regra LSP"]
✅ [Encontrou 8 resultados!]

Resposta:
"Sobre validação de regras LSP, encontrei:
1. [Do documento com score alto]
2. [Próximo documento]
...

📌 Fonte: TECNOLOGIA - Regras LSP"
```

### Exemplo 3: Não Encontrado

```
👤 "Qual é a melhor pizza para comer?"

🤖 [Pensa: NÃO é sobre Senior → responder normal]

Resposta:
"Que pergunta interessante! Depende de gosto,
mas pizzas margarita são clássicas porque..."
[SEM buscar]
```

---

## 🎓 Diferenças Entre Prompts

| Prompt | Quando Usar | Busca | Especificidade |
|--------|-----------|-------|-----------------|
| PROMPT 1 | Iniciante | Às vezes | Média |
| PROMPT 7 | Experiente | Inteligente | Alta |
| PROMPT 8 | LSP/Tech | Sempre | Ultra Alta |
| **PROMPT 9** | **Universal** | **Inteligente** | **Alta** |

**PROMPT 9 é melhor porque:**
- ✅ Funciona para qualquer tópico
- ✅ Não busca desnecessariamente (economia de API)
- ✅ Mas SEMPRE busca para tópicos técnicos
- ✅ Tenta múltiplas estratégias se não encontrar
- ✅ Padrão de resposta claro e rastreável

---

## 🚀 Próximos Passos

1. **Implementar** em Open WebUI (siga os 3 passos acima)
2. **Testar** com as 5 perguntas de teste
3. **Verificar** se busca está funcionando
4. **Usar** em produção com confiança

---

## 📞 Troubleshooting

### ❌ Problema: Assistente não busca

**Solução:**
1. Verifique se Tool está ativada
2. Cheque se API está online: `curl http://localhost:8000/health`
3. Teste em novo chat (cache pode estar interferindo)
4. Aumente `temperature` em Advanced Parameters para 0.5

### ❌ Problema: Busca retorna 0 sempre

**Solução:**
1. Teste a API manualmente no terminal
2. Verifique se índice tem documentos: `curl http://localhost:7700/indexes/documentation/stats`
3. Teste um termo conhecido: "LSP"

### ❌ Problema: Busca funciona mas resposta é genérica

**Solução:**
1. Verifique se assistente está usando o `search_docs` tool
2. Teste com pergunta mais específica
3. Aumentar `limit` em busca (ex: 10 em vez de 5)

---

## 📚 Referências

- **OPEN_WEBUI_SYSTEM_PROMPTS.md** - Todos os 9 prompts
- **LSP_SEARCH_GUIDE.md** - Guia completo de buscas eficientes
- **OPEN_WEBUI_MODEL_INSTRUCTIONS.md** - Troubleshooting detalhado

---

## ✨ Dica Final

Para máxima confiabilidade, combine:
1. **PROMPT 9** (esse prompt universal)
2. **search_docs tool** (ferramenta de busca)
3. **Índice com 10.000 docs** (documentação completa)

= **Assistente técnico profissional pronto para produção** 🎉

Comece agora! 🚀
