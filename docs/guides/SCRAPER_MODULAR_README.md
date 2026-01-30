# Scraper Modular e Extensível

Um scraper Python profissional, modular e altamente configurável para documentação e conteúdo web. Projetado para ser flexível, resistente e fácil de adaptar a diferentes fontes.

## 🎯 Características Principais

### ✅ Modularidade
- **ConfigManager**: Carrega e gerencia configurações JSON
- **GarbageCollector**: Remove caracteres indesejados e "lixo"
- **ContentExtractor**: Extrai títulos, conteúdo e breadcrumbs
- **JavaScriptHandler**: Trata conteúdo dinâmico
- **LinkExtractor**: Valida e segue links
- **ModularScraper**: Orquestra todo o processo

### ✅ Tratamento de Caracteres Indesejados
Define sequências de lixo customizáveis em JSON:
```json
"garbage_sequences": [
  {
    "pattern": "javascript:void(0)",
    "action": "skip_element",
    "description": "Ignora links vazios"
  },
  {
    "pattern": "(cookie|rastreamento|analytics)",
    "action": "remove",
    "description": "Remove referências a tracking"
  }
]
```

### ✅ Limites de Conteúdo
Configure limites de caracteres:
```json
"extraction": {
  "max_content_length": 50000,
  "min_content_length": 100,
  "max_title_length": 500,
  "max_breadcrumb_depth": 8
}
```

### ✅ Manipulação de JavaScript
Trata conteúdo dinâmico automaticamente:

**Clique e aguarda em links com âncoras (#):**
```json
{
  "selector": "a[href*='#']",
  "wait_ms": 1000,
  "detect_change": {
    "monitor_selector": ".dynamic-content",
    "check_attribute": "data-timestamp",
    "max_retries": 3
  }
}
```

**Expande elementos colapsáveis:**
```json
{
  "selector": "[data-expandable='true']",
  "wait_ms": 500,
  "detect_change": {
    "monitor_selector": "[data-expanded='true']",
    "check_visibility": true
  }
}
```

**Scripts de limpeza automática:**
```json
"execute_scripts": [
  {
    "name": "remove_modals",
    "script": "document.querySelectorAll('.modal').forEach(el => el.remove())"
  },
  {
    "name": "remove_ads",
    "script": "document.querySelectorAll('[class*='ad']').forEach(el => el.remove())"
  }
]
```

## 📋 Estrutura de Configuração

### 1. Scraper Settings
```json
"scraper": {
  "base_url": "https://documentacao.senior.com.br",
  "max_pages": 100,
  "timeout_ms": 30000,
  "headless": true,
  "viewport": {
    "width": 1920,
    "height": 1080
  }
}
```

### 2. Extraction Settings
```json
"extraction": {
  "max_content_length": 50000,
  "min_content_length": 100,
  "max_title_length": 500,
  "max_breadcrumb_depth": 8,
  "extract_images": false,
  "extract_links": true,
  "extract_tables": true,
  "extract_code_blocks": true
}
```

### 3. Cleanup/Garbage Collection
```json
"cleanup": {
  "remove_empty_lines": true,
  "normalize_whitespace": true,
  "remove_trailing_spaces": true,
  "garbage_patterns": [
    "\\s+",                    // Múltiplos espaços
    "\\n{3,}",                 // 3+ quebras de linha
    "<!--.*?-->",              // Comentários HTML
    "<script.*?</script>"       // Scripts
  ],
  "garbage_sequences": [
    {
      "pattern": "^\\s*$",
      "action": "remove",
      "description": "Remove linhas vazias"
    },
    {
      "pattern": "(javascript:void|#$)",
      "action": "skip_element",
      "description": "Ignora links vazios"
    }
  ]
}
```

### 4. JavaScript Handling
```json
"javascript_handling": {
  "enable_js_interaction": true,
  "wait_for_selectors": [
    ".content-loaded",
    "[data-loaded='true']",
    "#main-content"
  ],
  "click_and_wait": [
    // Configurações de clique
  ],
  "execute_scripts": [
    // Scripts de limpeza
  ]
}
```

### 5. CSS Selectors
```json
"selectors": {
  "title": ["h1", "[data-role='title']", ".page-title"],
  "content": ["#main-content", ".content", "article"],
  "breadcrumb": [".breadcrumb", "[data-role='navigation']"],
  "navigation": [".toc", ".sidebar"],
  "skip": ["script", "style", ".hidden", "[aria-hidden='true']"]
}
```

### 6. Link Handling
```json
"links": {
  "follow_patterns": [
    "documentacao.senior.com.br",
    "help.senior.com.br"
  ],
  "ignore_patterns": [
    "javascript:",
    "#$",
    "mailto:",
    ".pdf",
    "logout"
  ],
  "internal_only": true,
  "max_depth": 5
}
```

### 7. Output
```json
"output": {
  "format": "jsonl",              // ou "json"
  "save_directory": "docs_scraped",
  "include_metadata": true,
  "include_timestamp": true,
  "include_scrape_duration": true,
  "compression": null             // ou "gzip"
}
```

## 🚀 Uso

### Uso Básico

```python
from src.scraper_modular import ModularScraper
import asyncio

async def main():
    scraper = ModularScraper("scraper_config.json")
    await scraper.scrape()

asyncio.run(main())
```

### Uso com Configuração Customizada

```python
import json
from src.scraper_modular import ModularScraper

# Carrega configuração
with open("scraper_config.json") as f:
    config = json.load(f)

# Customiza
config["scraper"]["max_pages"] = 50
config["extraction"]["max_content_length"] = 100000
config["cleanup"]["garbage_sequences"].append({
    "pattern": "seu_padrão_aqui",
    "action": "remove"
})

# Salva
with open("config_custom.json", "w") as f:
    json.dump(config, f)

# Usa
scraper = ModularScraper("config_custom.json")
await scraper.scrape()
```

## 🧹 Exemplos de Tratamento de Lixo

### Remove Anúncios
```json
{
  "pattern": "(anúncio|advertisement|publicidade)",
  "action": "remove",
  "description": "Remove referências a anúncios"
}
```

### Remove Cookies/Tracking
```json
{
  "pattern": "(cookie|rastreamento|tracking|analytics)",
  "action": "remove",
  "description": "Remove referências de tracking"
}
```

### Remove CTAs Genéricas
```json
{
  "pattern": "(clique aqui|ver mais|carregando|loading)",
  "action": "remove",
  "description": "Remove CTAs genéricas"
}
```

### Remove Caracteres Inválidos
```json
{
  "pattern": "\\x00|\\ufffd",
  "action": "remove",
  "description": "Remove caracteres nulos/inválidos"
}
```

## 🔗 Exemplos de Manipulação de JavaScript

### Clique em Links com Âncoras
```json
{
  "selector": "a[href*='#']",
  "wait_ms": 1000,
  "description": "Clica em links com âncoras e aguarda mudanças",
  "detect_change": {
    "monitor_selector": ".dynamic-content",
    "check_attribute": "data-timestamp",
    "max_retries": 3
  }
}
```

### Expande Acordeões
```json
{
  "selector": "[class*='accordion'] [role='button']",
  "wait_ms": 500,
  "detect_change": {
    "monitor_selector": "[aria-expanded='true']",
    "check_visibility": true
  }
}
```

### Remove Modais e Sobreposições
```json
{
  "name": "remove_modals",
  "script": "document.querySelectorAll('.modal, [role=\"dialog\"], .overlay').forEach(el => el.remove())"
}
```

### Remove Headers Fixos
```json
{
  "name": "remove_sticky_headers",
  "script": "document.querySelectorAll('.sticky, [position=\"sticky\"]').forEach(el => el.style.position = 'relative')"
}
```

## 📊 Output

Cada documento extraído tem a seguinte estrutura:

```json
{
  "id": "abc123def456",
  "url": "https://documentacao.senior.com.br/...",
  "title": "Título da Página",
  "content": "Conteúdo extraído...",
  "breadcrumb": ["Módulo", "Submódulo", "Página"],
  "module": "Módulo Principal",
  "metadata": {
    "url": "...",
    "title": "...",
    "breadcrumb": [...],
    "module": "...",
    "scraped_at": "2026-01-26T10:30:45.123456+00:00",
    "scrape_duration_ms": 2500,
    "content_length": 15000,
    "charset": "utf-8"
  }
}
```

## 🔧 Troubleshooting

### Conteúdo não é extraído
1. Verifique `selectors.content` para os seletores corretos
2. Ative `enable_js_interaction` se o conteúdo é dinâmico
3. Aumente `timeout_ms` se as páginas carregam lentamente

### Links não são seguidos
1. Verifique `links.follow_patterns` contém os domínios
2. Confirme que `links.ignore_patterns` não bloqueia links legítimos
3. Aumente `max_depth` se necessário

### Conteúdo contém lixo
1. Adicione padrões em `garbage_patterns`
2. Defina sequências em `garbage_sequences`
3. Use `skip` selectors para ignorar elementos inteiros

### JavaScript não executa
1. Confirme `javascript_handling.enable_js_interaction` é `true`
2. Verifique seletores em `click_and_wait` existem na página
3. Aumente `wait_ms` se as transições são lentas

## 📈 Performance

- **Limite de caracteres**: Controla uso de memória
- **Máx. páginas**: Limita tempo de execução
- **Timeout**: Evita travamentos em páginas lentas
- **Seletores CSS**: Especifique bem para melhor performance

## 🔐 Segurança

- URLs validadas antes de visitação
- Padrões ignoram `javascript:`, `mailto:`, `tel:`
- `internal_only` previne crawling do site inteiro
- Caracteres inválidos removidos automaticamente

## 📝 Exemplo Completo

Veja `exemplo_scraper_modular.py` para um exemplo funcional com:
- Criação de configuração customizada
- Tratamento de JavaScript complexo
- Limpeza de conteúdo personalizada
- Executando o scraper

```bash
python exemplo_scraper_modular.py
```
