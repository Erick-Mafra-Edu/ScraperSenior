# 🔍 Guia Completo de Buscas para LSP (Language of Senior Platform)

## 📌 Regra de Ouro

> **QUALQUER pergunta sobre LSP ou módulos Senior DEVE COMEÇAR COM UMA BUSCA NA DOCUMENTAÇÃO**

Não use seu conhecimento prévio - SEMPRE busque primeiro!

---

## 🎯 Termos de Busca Eficientes

### ✅ Termos que SEMPRE retornam resultados:

#### LSP e Regras
```
Buscar por:           Melhor resultado:
"LSP"                 ✅ 13+ artigos
"regras LSP"          ✅ Vários procedimentos
"compilação regras"   ✅ Guias técnicos
"função LSP"          ✅ Referência de funções
"variável"            ✅ Definições
```

#### Módulos e Componentes
```
Buscar por:                    Melhor resultado:
"ERP"                          ✅ Múltiplos artigos
"RH"                           ✅ Gestão de pessoal
"Financeiro"                   ✅ Contabilidade
"Gerador de Relatórios"        ✅ 10+ artigos
"Gestão Empresarial"           ✅ Módulo principal
```

#### Operações Comuns
```
Buscar por:               Melhor resultado:
"implantação"             ✅ Processos de setup
"backup"                  ✅ Procedimentos
"erro"                    ✅ Troubleshooting
"performance"             ✅ Otimização
"configuração"            ✅ Setup
```

#### Termos Específicos de Senior
```
Buscar por:               Melhor resultado:
"Nexxera"                 ✅ Integração bancária
"DARF"                    ✅ Impostos
"Nota Fiscal"             ✅ NF-e
"Office Banking"          ✅ Transações
```

---

## ❌ Termos que NÃO FUNCIONAM bem

### Buscas muito específicas retornam 0 resultados:

```
❌ Não busque:                          ✅ Busque em vez disso:
"módulo de tecnologia LSP e relatório"  "Gerador de Relatórios"
"LSP implantação"                       "implantação" OU "LSP"
"relatórios LSP"                        "relatório"
"procedimento completo de X"            "X" (simples)
"como fazer X passo a passo"            "X" (evite "como fazer")
```

---

## 🔍 Estratégia de Busca Recomendada

### Nível 1: Tentativa Inicial
**Use 1-2 palavras-chave principais**

```
Pergunta do usuário: "Como funciona a compilação de regras LSP?"
├─ Palavra-chave principal: "compilação"
├─ Palavra-chave secundária: "regras" OU "LSP"
└─ Buscar por: "compilação regras"  ✅ Retorna resultados
```

### Nível 2: Se Não Encontrar
**Use termos mais genéricos**

```
Se "compilação regras" retornar 0:
├─ Tentar: "compilação"
├─ Tentar: "regras LSP"
└─ Tentar: "LSP"
```

### Nível 3: Última Tentativa
**Use um termo único e simples**

```
Se ainda não encontrar:
├─ Tentar: "LSP" (amplo)
├─ Tentar: "procedimento"
└─ Tentar: "configuração"
```

---

## 📊 Tabela de Resultados Testados

| Termo de Busca | Total de Resultados | Qualidade | Recomendação |
|---|---|---|---|
| "LSP" | 13+ | ⭐⭐⭐⭐⭐ | Excelente - use como fallback |
| "implantação" | 5+ | ⭐⭐⭐⭐⭐ | Excelente |
| "relatório" | 10+ | ⭐⭐⭐⭐⭐ | Excelente |
| "Gerador de Relatórios" | 10 | ⭐⭐⭐⭐⭐ | Muito bom |
| "regras" | 10+ | ⭐⭐⭐⭐ | Bom, resultados variados |
| "compilação" | Vários | ⭐⭐⭐⭐ | Bom |
| "ERP" | Múltiplos | ⭐⭐⭐⭐ | Bom |
| "LSP implantação" | 0 | ❌ | Não funciona |
| "módulo de tecnologia LSP e relatório" | 0 | ❌ | Não funciona |
| "LSP relatório" | 0 | ❌ | Não funciona |

---

## 🎓 Exemplos de Buscas Reais

### Exemplo 1: Pergunta sobre Compilação
```
👤 Usuário: "Como funciona a compilação de regras LSP em prod?"

🤖 Assistente pensa:
- Tema: LSP
- Ação: Compilação
- Contexto: Produção
- Estratégia: Buscar "compilação regras"

🔍 Busca realizada:
search_documentation(query="compilação regras", limit=5)

✅ Resultado: 5 artigos encontrados
Documento principal: "TECNOLOGIA - Regras LSP - Como funciona o processo de compilação de regras dos sistemas de Tecnologia G5/G6 (XTended)"

💬 Resposta clara com procedimentos técnicos
```

### Exemplo 2: Pergunta sobre Implantação
```
👤 Usuário: "Quais são os passos para implantar o sistema?"

🤖 Assistente pensa:
- Tema: Implantação
- Estratégia: Buscar "implantação"

🔍 Busca realizada:
search_documentation(query="implantação", limit=10)

✅ Resultado: 5+ artigos encontrados
- "ERP MEGA - Nexxera - Fluxo de Implantação"
- "ERP MEGA - Como inserir arquivos para serem exibidos na aba Implantação"
- "ERP MEGA - Conciliação Bancária - A data de implantação não pode ser alterada"
- etc

💬 Resposta consolidada dos melhores resultados
```

### Exemplo 3: Pergunta sobre Relatórios
```
👤 Usuário: "Como criar um relatório customizado?"

🤖 Assistente pensa:
- Tema: Relatórios
- Ação: Criar/Customizar
- Estratégia: Buscar "Gerador de Relatórios"

🔍 Busca realizada:
search_documentation(query="Gerador de Relatórios", limit=5)

✅ Resultado: 10 artigos encontrados
- "TECNOLOGIA - Gerador de Relatórios - Informações sobrepostas"
- "ERP - Gerador de Relatórios - Como é o comportamento do preenchimento"
- etc

💬 Resposta com procedimento passo a passo
```

### Exemplo 4: Falha de Busca - Recuperação
```
👤 Usuário: "Como fazer implantação de relatório LSP com tecnologia avançada?"

🤖 Assistente pensa:
- Termo composto muito longo
- Estratégia: Tentar busca específica primeiro

🔍 Tentativa 1:
search_documentation(query="implantação relatório LSP", limit=5)
❌ Resultado: 0 artigos

🔍 Tentativa 2:
search_documentation(query="implantação", limit=5)
✅ Resultado: 5 artigos encontrados!

💬 Resposta:
"Não encontrei a combinação exata 'implantação de relatório LSP'.
Mas encontrei documentos sobre 'implantação' em geral:
[Artigos relevantes]

Se você procura especificamente por Gerador de Relatórios, recomendo:
search_documentation(query="Gerador de Relatórios", limit=5)"
```

---

## 🛠️ Dicas para Assistentes usando MCP

### Quando usar search_docs tool:

```python
# ✅ SEMPRE USE QUANDO:
search_docs(query="LSP", limit=10)                    # Pergunta sobre LSP
search_docs(query="compilação", limit=5)              # Técnico
search_docs(query="implantação", limit=10)            # Procedimento
search_docs(query="configuração", limit=5)            # Setup
search_docs(query="erro", limit=5)                    # Troubleshooting
search_docs(query="módulo RH", limit=5)               # Módulo específico

# ❌ NÃO USE (retorna 0):
search_docs(query="como funciona LSP implantação com relatórios")  # Muito específico
search_docs(query="qual é a melhor forma de fazer X")             # Amplo demais
```

### Parâmetros Recomendados:

```python
# Para busca simples:
search_docs(query="termo", limit=5)

# Para busca mais abrangente:
search_docs(query="termo", limit=10)

# Para busca em módulo específico:
search_docs(query="termo", module="RH", limit=5)

# EVITE:
limit=50  # Muito resultado, difícil analisar
limit=1   # Pode perder informações
```

---

## 📋 Checklist para Perguntas sobre LSP

- [ ] Usuário perguntou sobre LSP ou módulo Senior?
- [ ] Realizei uma busca antes de responder?
- [ ] Busca retornou resultados (count > 0)?
  - [ ] Sim → Responder com documentação
  - [ ] Não → Tentar termos alternativos
- [ ] Citei a fonte do documento?
- [ ] Resposta baseada APENAS na documentação?
- [ ] Ofereci próximas perguntas úteis?

---

## 🚀 Fluxo de Busca Otimizado

```
┌─────────────────────┐
│ Usuário faz pergunta│
└──────────┬──────────┘
           │
           ▼
    ┌──────────────────────┐
    │ Contém LSP/módulo?   │
    └──────────┬───────────┘
               │
         ┌─────┴─────┐
         │           │
        SIM         NÃO
         │           │
         │    ┌──────▼──────┐
         │    │ Conversação │
         │    │ genérica    │
         │    └─────────────┘
         │
         ▼
    ┌─────────────────────┐
    │ Extrair palavras    │
    │ -chave (1-2 termos) │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ search_documentation│
    │ (query, limit=5-10) │
    └──────────┬──────────┘
               │
         ┌─────┴─────┐
         │           │
      COUNT>0       COUNT=0
         │           │
         │    ┌──────▼───────┐
         │    │ Tentar termos│
         │    │ alternativos │
         │    └──────┬───────┘
         │           │
         │           ▼
         │    ┌──────────────┐
         │    │ COUNT>0?     │
         │    └──────┬───────┘
         │           │
         │      SIM  │  NÃO
         │      ┌────┘
         │      │
         ▼      ▼
    ┌──────────────────────┐
    │ Análise de resultados│
    │ (usar score > 0.6)   │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │ Responder com docs   │
    │ + Citar fonte        │
    │ + Próximas perguntas │
    └──────────────────────┘
```

---

## 💡 Otimizações para Diferentes Modelos

### Para Llama/Mistral (Locais)
- Use termos bem específicos (não ambíguos)
- Limite a 5 resultados
- Inclua contexto na busca

### Para GPT-4o/Claude
- Pode usar termos mais genéricos
- Limite a 10 resultados
- Modelo faz análise melhor dos resultados

### Para Pequenos Modelos
- Use 1-2 palavras-chave máximo
- Limite a 3-5 resultados
- Evite termos compostos

---

## 📞 Quando Encaminhar para Suporte

Se após 3 tentativas de busca com termos alternativos:
- Ainda retorna 0 resultados
- Os resultados não são relevantes
- A informação parece estar faltando

**Responda:**
```
Desculpe, não encontrei essa informação específica na base de documentação disponível.

Recomendo contatar o suporte técnico Senior:
📞 Telefone: [número]
📧 Email: suporte@senior.com.br
🔗 Portal: https://suporte.senior.com.br

Você pode me ajudar com:
✅ Documentação de outros módulos?
✅ Configurações gerais do sistema?
✅ Outros procedimentos técnicos?
```

---

## ✅ Resumo das Melhores Práticas

1. **SEMPRE busque para LSP** - Não negocie
2. **Use termos simples** - 1-2 palavras principais
3. **Se 0 resultados** - Tente novamente com palavra-chave única
4. **Cite a fonte** - Sempre indique o documento
5. **Respeite a documentação** - Não complemente com seu conhecimento
6. **Ofereça continuidade** - Próximas perguntas úteis

---

## 🎯 Próximos Passos

1. Copie o **PROMPT 8 (LSP)** de `OPEN_WEBUI_SYSTEM_PROMPTS.md`
2. Cole em Open WebUI → Chat Settings → System Prompt
3. Configure Tool: Senior Documentation API
4. Teste com perguntas sobre LSP
5. Verifique se está chamando a ferramenta automaticamente

**Resultado esperado:** Assistente SEMPRE busca antes de responder perguntas sobre LSP! 🎉
