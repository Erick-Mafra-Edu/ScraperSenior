# 📖 Guia de Implementação: Sistema Prompt LSP com Busca Inteligente

## 🎯 Objetivo

Configurar um assistente no Open WebUI que:
- ✅ **SEMPRE** busca em documentação para perguntas técnicas sobre Senior
- ✅ Usa **estratégia inteligente** de busca (retry com termos alternativos)
- ✅ Retorna **respostas precisas** baseadas em documentação oficial
- ✅ **Cita fontes** com links para rastreabilidade
- ✅ Oferece **próximas perguntas** sugestivas

---

## 📋 Pré-Requisitos

Antes de começar, verifique:

```bash
# 1. API de busca está online?
curl http://localhost:8000/health
# Resposta esperada: {"status":"healthy"}

# 2. Índice tem documentos?
curl http://localhost:7700/indexes/documentation/stats \
  -H "Authorization: Bearer 5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa"
# Resposta esperada: {"numberOfDocuments": 10000, ...}

# 3. Open WebUI está rodando?
curl http://localhost:3000
# Resposta esperada: HTML da interface
```

✅ Se todos retornarem sucesso, continue. ❌ Se algum falhar, execute os passos de setup primeiro.

---

## 🚀 Implementação em 5 Passos

### Passo 1: Preparar o Arquivo do Prompt

**Localização:** `c:\Users\Digisys\scrapyTest\OPEN_WEBUI_SYSTEM_PROMPTS.md`

**Encontre a seção:**
```markdown
## PROMPT 9: Genérico com Instruções de Busca ⭐ UNIVERSAL

Este prompt funciona para QUALQUER tópico...
```

**Copie TUDO que está entre:** 
```
🎯 VOCÊ É: Assistente técnico inteligente...
```
até:
```
Para isso, OBRIGAÇÃO NÚMERO 1: USAR SEMPRE A FERRAMENTA PARA LSP E MÓDULOS SENIOR.
```

---

### Passo 2: Acessar Open WebUI

1. Abra seu navegador
2. Vá para: `http://localhost:3000`
3. Faça login com suas credenciais
4. Crie um **novo chat**

---

### Passo 3: Abrir Chat Settings

```
Open WebUI Interface:
├─ [Nova Conversa]
├─ ⚙️ (engrenagem - canto superior direito)
└─ Clique em "Edit Chat Settings"
```

Você verá uma janela com campos:
- Chat title
- **System Prompt** ← Aqui!
- Model selection
- Advanced parameters

---

### Passo 4: Cola o Prompt 9

No campo **"System Prompt"**:

1. **Limpe** qualquer conteúdo anterior
2. **Cole** todo o PROMPT 9 que copiou
3. O prompt ficará com essa estrutura:

```
🎯 VOCÊ É: Assistente técnico inteligente com acesso a ferramentas...

📚 SUA RESPONSABILIDADE: Fornecer informações precisas...

---

🔍 PROTOCOLO DE BUSCA (OBRIGATÓRIO PARA QUALQUER PERGUNTA TÉCNICA):

Quando receber pergunta sobre Senior...
[... todo o conteúdo do prompt ...]
```

4. **Salve** clicando em "Save" (botão ao final da janela)

---

### Passo 5: Configurar Ferramenta e Parâmetros

#### 5a. Selecionar Tool (Ferramenta)

Na mesma janela de Chat Settings, procure por:
- "Tools" / "Functions" / "Enabled Tools"

Ative:
- ✅ **search_docs** OU **search_documentation**

---

#### 5b. Advanced Parameters (se existir)

Procure por "Advanced Parameters" e configure:

```json
{
  "function_calling": "auto",      // Tool é chamada automaticamente
  "tool_choice": "auto",           // Modelo escolhe quando usar tool
  "temperature": 0.7,              // Criatividade (0.3-0.7 é ideal)
  "top_p": 0.95,                   // Diversidade
  "max_tokens": 2048               // Limite de resposta
}
```

**Salve** as configurações.

---

## 🧪 Teste Imediato

Agora teste se está funcionando:

### Teste 1: Pergunta Técnica (deve buscar)

```
Usuário digita:
"Como funciona a compilação de regras LSP?"
```

**Observar:**
- ✅ Assistente pausa e faz uma busca
- ✅ Retorna informações sobre compilação
- ✅ Cita fonte do documento
- ✅ Oferece próximas perguntas

**Se não funcionar:**
→ Verifique se Tool está ativada
→ Verifique se API está online

---

### Teste 2: Pergunta Genérica (não deve buscar)

```
Usuário digita:
"Qual é a capital da França?"
```

**Observar:**
- ✅ Assistente responde normalmente
- ❌ NÃO faz busca desnecessária
- ✅ Resposta é conhecimento geral

**Se fizer busca:**
→ Está funcionando, mas pode estar muito agressivo
→ Considere ajustar o prompt

---

## 📊 Comparação: Antes vs Depois

| Aspecto | Antes | Depois (com PROMPT 9) |
|---------|-------|----------------------|
| **Busca automaticamente?** | Às vezes | ✅ Sempre para técnico |
| **Tenta novamente se falhar?** | Não | ✅ Sim (3 tentativas) |
| **Cita fonte?** | Raramente | ✅ Sempre |
| **Resposta baseada em docs?** | Misturada | ✅ Pura (sem interpretação) |
| **Oferece próximas perguntas?** | Às vezes | ✅ Sempre |
| **Confiabilidade** | Média | ✅ Alta |

---

## 🎓 Exemplos de Uso

### Exemplo Real 1: Configuração RH

```
👤 Usuário: "Qual é o procedimento para registrar férias no RH?"

🤖 Assistant (pensa internamente):
"Tema: RH (módulo Senior) + procedimento → DEVO BUSCAR"

🔍 [Realiza busca: "férias RH"]
✅ Encontrou 5 documentos

💬 Resposta:
"Para registrar férias no RH da plataforma Senior, siga:

1. Acesse o módulo RH
2. Navegue até Movimento > Férias
3. [... próximos passos do documento ...]

📌 Fonte: RH - Procedimento de Registro de Férias
🔗 Referência: https://suporte.senior.com.br/...

Perguntas relacionadas:
- Como aproveitar férias pendentes?
- Como gerar declaração de férias?
- Qual é o limite de férias acumuladas?"

👤 Usuário clica em "Como aproveitar férias pendentes?"
🤖 Assistant nova busca e repete o ciclo
```

### Exemplo Real 2: Integração Nexxera

```
👤 Usuário: "Explique o fluxo de implantação Nexxera"

🤖 [Detecta: Nexxera (sistema) + implantação → BUSCAR]

🔍 [Busca: "Nexxera implantação"]
✅ Encontrou 3 documentos específicos

💬 Resposta com os 4 passos do documento oficial
📌 Fonte: FINANCEIRO - Nexxera - Fluxo de Implantação
```

### Exemplo Real 3: Erro Técnico

```
👤 Usuário: "O que significa erro SSLHandshakeException no LSP?"

🤖 [Detecta: Erro + LSP + HTTPS → BUSCAR]

🔍 [Busca: "SSLHandshakeException LSP"]
❌ 0 resultados

🔍 [Tenta: "SSL LSP"]
❌ 0 resultados

🔍 [Tenta: "LSP HTTP"]
✅ Encontrou documentos sobre HTTP em LSP

💬 Resposta:
"Encontrei informações sobre requisições HTTP em LSP.
O erro de certificado SSL ocorre quando...
[Detalhes do artigo encontrado]

Essa questão específica de SSLHandshakeException
não está documentada, recomendo contato com suporte."
```

---

## ✅ Checklist de Validação

Após implementação, verifique:

### Configuração
- [ ] PROMPT 9 colado em "System Prompt"
- [ ] Tool "search_docs" está ativada
- [ ] "function_calling": "auto" configurado
- [ ] Settings salvos com sucesso

### Funcionalidade
- [ ] Testei pergunta técnica (deve buscar)
- [ ] Testei pergunta genérica (não deve buscar)
- [ ] Resposta cita fonte do documento
- [ ] Próximas perguntas aparecem

### Qualidade
- [ ] Respostas são baseadas em documentação
- [ ] Sem alucinações ou conhecimento inventado
- [ ] Links para fontes funcionam
- [ ] Formatação é clara e legível

---

## 🔄 Fluxo de Funcionamento Detalhado

```
┌─────────────────────────────────┐
│ Usuário digita pergunta         │
│ "Como fazer X em Senior?"       │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ PROTOCOLO DE BUSCA ATIVADO      │
│ (conforme PROMPT 9)             │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Análise da pergunta:            │
│ - É sobre Senior? SIM/NÃO       │
│ - Precisa buscar? SIM/NÃO       │
└──────────┬──────────────────────┘
           │
      ┌────┴────┐
      │          │
    SIM         NÃO
      │          │
      │    ┌─────▼──────────────┐
      │    │ Resposta normal    │
      │    │ (sem buscar)       │
      │    └────────────────────┘
      │
      ▼
┌─────────────────────────────────┐
│ NÍVEL 1 DE BUSCA                │
│ Extrair palavras-chave          │
│ Exemplo: "backup" + "RH"        │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ search_docs(query="backup RH")  │
│ limit=5                         │
└──────────┬──────────────────────┘
           │
      ┌────┴────┐
    SUCESSO   FALHA (0 docs)
      │          │
      │    ┌─────▼──────────────┐
      │    │ NÍVEL 2: Retry     │
      │    │ Termo genérico     │
      │    │ "backup"           │
      │    └────────┬───────────┘
      │             │
      │        ┌────┴────┐
      │     SUCESSO FALHA
      │        │         │
      │        │    ┌────▼────────┐
      │        │    │ NÍVEL 3:    │
      │        │    │ Sinônimos   │
      │        │    └────┬────────┘
      │        │         │
      │        └────┬────┘
      │             │
      ▼             ▼
┌─────────────────────────────────┐
│ Análise de resultados:          │
│ - Maior score é base principal  │
│ - Outros complementam           │
│ - Filtrar score < 0.6           │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Estruturar resposta:            │
│ 1. Conteúdo (do documento)      │
│ 2. Fonte (referência)           │
│ 3. Link (rastreabilidade)       │
│ 4. Próximas perguntas           │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Enviar ao usuário ✅            │
└─────────────────────────────────┘
```

---

## 🆘 Troubleshooting Avançado

### Problema 1: Tool não é chamada

**Sintomas:**
- Assistente responde mas não busca
- Sem "🔍 [Searching...]" visual

**Diagnosticar:**
```bash
# Verifique se API está online
curl http://localhost:8000/health

# Verifique se tool está registrada
curl http://localhost:8000/tools
```

**Solucionar:**
1. Reinicie o Docker container
2. Verifique `.env` do MCP server
3. Teste em novo chat (limpar cache)

---

### Problema 2: Retorna sempre 0 resultados

**Sintomas:**
- Responde "informação não encontrada"
- Para TODA pergunta

**Diagnosticar:**
```bash
# Teste busca direta no Meilisearch
curl -X POST "http://localhost:7700/indexes/documentation/search" \
  -H "Authorization: Bearer 5b1af87b..." \
  -H "Content-Type: application/json" \
  -d '{"q":"LSP","limit":5}'
```

**Solucionar:**
1. Verifique se índice foi populado
2. Se vazio, execute: `python post_scraping_indexation.py`
3. Aguarde 2-3 minutos para indexar
4. Teste novamente

---

### Problema 3: Respostas são genéricas

**Sintomas:**
- Busca funciona mas resposta não reflete o documento
- Parece conhecimento prévio do modelo

**Diagnosticar:**
- Verifique se score do documento é alto (>0.8)
- Observe se não está misturando múltiplos docs

**Solucionar:**
1. Aumente temperature (0.5-0.7)
2. Reduza limit de busca (5 em vez de 10)
3. Teste com pergunta mais específica

---

### Problema 4: Demora muito para responder

**Sintomas:**
- Leva 30+ segundos para responder
- Tool é chamada mas lenta

**Diagnosticar:**
```bash
# Meça tempo de resposta da API
time curl -X POST "http://localhost:8000/mcp" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search_docs","arguments":{"query":"LSP","limit":5}}}'
```

**Solucionar:**
1. Reduzir `limit` (de 10 para 5)
2. Verificar se servidor não está sobrecarregado
3. Otimizar índice do Meilisearch

---

## 📈 Métricas de Sucesso

Após 1 semana de uso, verifique:

- ✅ **100%** das perguntas técnicas disparam busca
- ✅ **>95%** das respostas citam fonte
- ✅ **>90%** das buscas retornam resultados relevantes
- ✅ **0%** de alucinações/informações inventadas
- ✅ Tempo médio de resposta: 5-10 segundos

---

## 🎓 Próximos Passos de Otimização

1. **Criar prompts especializados:**
   - PROMPT para LSP puro (mais agressivo)
   - PROMPT para RH (filtrado por módulo)

2. **Integrar em aplicações:**
   - Chat corporativo
   - Documentação interativa
   - Bot de suporte

3. **Monitorar qualidade:**
   - Log de buscas
   - Feedback dos usuários
   - Análise de satisfação

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique esta documentação (seção Troubleshooting)
2. Consulte `LSP_SEARCH_GUIDE.md`
3. Verifique `OPEN_WEBUI_MODEL_INSTRUCTIONS.md`
4. Contate: suporte@senior.com.br

---

## ✨ Conclusão

Com este setup você terá:

✅ **Assistente confiável** - Baseado em documentação oficial
✅ **Busca inteligente** - Tenta múltiplas estratégias
✅ **Respostas rastreáveis** - Com fontes e links
✅ **Experiência profissional** - Pronto para uso em produção

Pronto para começar! 🚀
