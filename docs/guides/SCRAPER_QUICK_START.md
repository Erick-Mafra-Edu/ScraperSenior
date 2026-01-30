# Guia Rápido - Scraper Modular

## 🚀 Início Rápido

### 1. Executar com Configuração Padrão

```bash
python exemplo_scraper_modular.py
```

### 2. Customizar Configuração

Edite `scraper_config.json`:

```json
{
  "scraper": {
    "base_url": "https://seu-site.com",
    "max_pages": 50
  },
  "extraction": {
    "max_content_length": 100000
  }
}
```

### 3. Usar em Seu Código

```python
from src.scraper_modular import ModularScraper
import asyncio

async def main():
    scraper = ModularScraper("scraper_config.json")
    await scraper.scrape()

asyncio.run(main())
```

---

## 📌 Configurações Mais Comuns

### Ajustar Limites de Conteúdo

```json
"extraction": {
  "max_content_length": 100000,    // Máximo de caracteres
  "min_content_length": 100,       // Mínimo de caracteres
  "max_title_length": 500          // Máximo de caracteres no título
}
```

### Remover Tipos Específicos de Lixo

Adicione em `garbage_sequences`:

```json
{
  "pattern": "seu_padrão_regex_aqui",
  "action": "remove",
  "description": "Descrição do que é removido"
}
```

**Exemplos de padrões:**

```python
# Remove anúncios
"(ad|advertisement|promotional)"

# Remove elementos de navegação
"(menu|nav|sidebar|toc)"

# Remove caracteres especiais
"[^\x20-\x7E\n]"  # Mantém apenas ASCII imprimível + quebras

# Remove múltiplos espaços
"[ ]{2,}"

# Remove URLs
"https?://[^\s]+"
```

### Tratar Conteúdo Dinâmico (JavaScript)

Para páginas com links em âncoras (#):

```json
"javascript_handling": {
  "enable_js_interaction": true,
  "click_and_wait": [
    {
      "selector": "a[href*='#']",
      "wait_ms": 1500,
      "detect_change": {
        "monitor_selector": ".content",
        "check_content_change": true
      }
    }
  ]
}
```

### Expandir Acordeões/Colapsáveis

```json
{
  "selector": "[data-expandable], .accordion, [role='tab']",
  "wait_ms": 800,
  "detect_change": {
    "monitor_selector": ".expanded, [aria-expanded='true']",
    "check_visibility": true
  }
}
```

### Remover Modais e Sobreposições

```json
"execute_scripts": [
  {
    "name": "remove_modals",
    "script": "document.querySelectorAll('.modal, [role=\"dialog\"]').forEach(e => e.remove())"
  }
]
```

---

## 🔍 Seletores CSS

Personalize onde o scraper procura por conteúdo:

```json
"selectors": {
  "title": [
    "h1",
    ".page-title",
    "[data-title]",
    ".main-heading"
  ],
  "content": [
    "#main-content",
    "article",
    ".post-content",
    "[role='main']"
  ],
  "breadcrumb": [
    ".breadcrumb",
    "[aria-label='breadcrumb']",
    ".toc-path"
  ],
  "skip": [
    "script",
    "style",
    ".advertisement",
    "[aria-hidden='true']"
  ]
}
```

---

## 🔗 Controlar Quais Links Seguir

### Seguir Apenas Domínios Específicos

```json
"links": {
  "follow_patterns": [
    "documentacao.senior.com.br",
    "help.senior.com.br",
    "suporte.example.com"
  ],
  "internal_only": true
}
```

### Ignorar Certos Padrões de URL

```json
"ignore_patterns": [
  "javascript:",
  "#$",
  "mailto:",
  "tel:",
  ".pdf",
  "logout",
  "signin",
  "admin"
]
```

---

## 📊 Entender o Output

Cada documento tem:

```json
{
  "id": "hash_único",
  "url": "https://...",
  "title": "Título da Página",
  "content": "Conteúdo extraído...",
  "breadcrumb": ["Módulo", "Sub", "Página"],
  "module": "Módulo Principal",
  "metadata": {
    "scraped_at": "2026-01-26T...",
    "scrape_duration_ms": 2500,
    "content_length": 15000
  }
}
```

---

## 🧪 Testar Configuração

```bash
python test_scraper_modular.py
```

Isso valida:
- ✅ Carregamento de config
- ✅ Remoção de lixo
- ✅ Validação de links
- ✅ Seletores CSS
- ✅ JavaScript handling
- ✅ Output config

---

## ⚡ Dicas de Performance

1. **Aumente `timeout_ms`** se páginas carregam lentamente
2. **Reduza `max_pages`** para testes rápidos
3. **Limite `wait_ms`** em `click_and_wait` para velocidade
4. **Use seletores específicos** em vez de genéricos
5. **Aumente `max_content_length`** se conteúdo está sendo truncado

---

## 🐛 Troubleshooting Rápido

### Conteúdo vazio?
- [ ] Verifique `selectors.content` tem seletores certos
- [ ] Ative `enable_js_interaction`
- [ ] Aumente `timeout_ms`

### Muita lixo no conteúdo?
- [ ] Adicione padrões em `garbage_patterns`
- [ ] Defina sequências em `garbage_sequences`
- [ ] Use `skip` selectors

### Links não seguindo?
- [ ] Confirme `follow_patterns` tem os domínios
- [ ] Verifique `ignore_patterns` não bloqueia
- [ ] Aumente `max_depth`

### Erro de JavaScript?
- [ ] Confirme `enable_js_interaction` = true
- [ ] Verifique seletores existem
- [ ] Aumente `wait_ms`

---

## 📝 Exemplos de Configuração

### Para Blog/Notícias
```json
{
  "scraper": {"max_pages": 200},
  "extraction": {"max_content_length": 50000},
  "selectors": {
    "title": ["h1.post-title", ".entry-title"],
    "content": ["article", ".post-content", ".entry-content"],
    "breadcrumb": [".breadcrumb", ".posts-breadcrumb"]
  }
}
```

### Para Documentação Técnica
```json
{
  "scraper": {"max_pages": 500},
  "extraction": {"max_content_length": 100000},
  "javascript_handling": {
    "enable_js_interaction": true,
    "click_and_wait": [{
      "selector": "a[href*='#'], .toc-item",
      "wait_ms": 1000
    }]
  },
  "selectors": {
    "title": ["h1", ".doc-title"],
    "content": ["#doc-content", ".documentation"]
  }
}
```

### Para E-commerce
```json
{
  "scraper": {"max_pages": 1000},
  "extraction": {
    "max_content_length": 50000,
    "extract_images": true
  },
  "garbage_sequences": [
    {"pattern": "(anúncio|recomendado|promoted)", "action": "remove"},
    {"pattern": "(cookie|rastreamento)", "action": "remove"}
  ]
}
```

---

## 🎓 Aprender Mais

- [Documentação Completa](SCRAPER_MODULAR_README.md)
- [Exemplos de Código](exemplo_scraper_modular.py)
- [Testes](test_scraper_modular.py)
- [Configuração Padrão](scraper_config.json)
