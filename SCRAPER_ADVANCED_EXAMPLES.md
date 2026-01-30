# Exemplos Avançados - Scraper Modular

## 1. Scraper para Site com Abas Dinâmicas

```json
{
  "scraper": {
    "base_url": "https://documentacao.senior.com.br",
    "max_pages": 100
  },
  "javascript_handling": {
    "enable_js_interaction": true,
    "execute_scripts": [
      {
        "name": "remove_modals",
        "script": "document.querySelectorAll('.modal, [role=\"dialog\"]').forEach(el => el.remove())"
      }
    ],
    "click_and_wait": [
      {
        "selector": "[role='tab'], .tab-header, [class*='tab']",
        "wait_ms": 1500,
        "description": "Clica em cada aba e aguarda conteúdo carregar",
        "detect_change": {
          "monitor_selector": ".tab-content, [role='tabpanel'], [aria-selected='true']",
          "check_visibility": true,
          "max_retries": 3
        }
      }
    ]
  }
}
```

## 2. Scraper para Documentação com Navegação em Árvore

```json
{
  "javascript_handling": {
    "enable_js_interaction": true,
    "click_and_wait": [
      {
        "selector": ".toc-item, .tree-node, [class*='expandable']",
        "wait_ms": 800,
        "description": "Expande cada item da árvore de navegação",
        "detect_change": {
          "monitor_selector": ".tree-expanded, [aria-expanded='true'], .visible-children",
          "check_content_change": true
        }
      }
    ],
    "execute_scripts": [
      {
        "name": "expand_all_trees",
        "script": "document.querySelectorAll('[aria-expanded=\"false\"]').forEach(el => el.click())"
      }
    ]
  },
  "cleanup": {
    "garbage_sequences": [
      {
        "pattern": "^(Voltar|Página anterior|Próxima)$",
        "action": "remove"
      }
    ]
  }
}
```

## 3. Scraper para Site com Muitos Anúncios e Rastreamento

```json
{
  "cleanup": {
    "garbage_patterns": [
      "<!--.*?-->",
      "<script.*?</script>",
      "<style.*?</style>",
      "<noscript.*?</noscript>"
    ],
    "garbage_sequences": [
      {
        "pattern": "(google_ad_|adsbygoogle|doubleclick|ads\\.google)",
        "action": "remove",
        "description": "Remove tags de anúncios Google"
      },
      {
        "pattern": "(facebook\\.com/tr|fbq\\(|gtag\\(|ga\\(|_trackPageview)",
        "action": "remove",
        "description": "Remove tracking de Facebook, Google Analytics"
      },
      {
        "pattern": "(cookie.*?consent|gdpr.*?banner|privacy.*?notice)",
        "action": "remove",
        "description": "Remove banners de cookie/GDPR"
      },
      {
        "pattern": "\\[.{0,5}(ad|announcement|promo).*?\\]",
        "action": "remove"
      }
    ]
  },
  "javascript_handling": {
    "execute_scripts": [
      {
        "name": "remove_ads",
        "script": "document.querySelectorAll('[class*=\"ad\"], [class*=\"advertisement\"], [id*=\"ad\"], [id*=\"advertisement\"]').forEach(el => el.remove())"
      },
      {
        "name": "remove_tracking",
        "script": "document.querySelectorAll('img[src*=\"doubleclick\"], img[src*=\"facebook\"], img[src*=\"google\"]').forEach(el => el.remove())"
      },
      {
        "name": "remove_popup",
        "script": "document.querySelectorAll('.popup, .modal, .overlay, [class*=\"modal\"]').forEach(el => el.remove())"
      }
    ]
  }
}
```

## 4. Scraper para Site com Paginação

```json
{
  "scraper": {
    "max_pages": 500
  },
  "javascript_handling": {
    "click_and_wait": [
      {
        "selector": "a[rel='next'], .next-page, [aria-label*='Next'], .pagination a:last-child",
        "wait_ms": 2000,
        "description": "Clica em 'Próxima página' para paginar",
        "detect_change": {
          "monitor_selector": ".post, article, [data-post-id]",
          "check_content_change": true
        }
      }
    ]
  },
  "cleanup": {
    "garbage_sequences": [
      {
        "pattern": "^(Próxima página|Página anterior|Ver mais|Carregando)$",
        "action": "remove"
      }
    ]
  }
}
```

## 5. Scraper para Documentação com Exemplos de Código

```json
{
  "extraction": {
    "extract_code_blocks": true,
    "max_content_length": 200000
  },
  "cleanup": {
    "garbage_sequences": [
      {
        "pattern": "^\\s*Copy\\s*$",
        "action": "remove",
        "description": "Remove botão 'Copy' de blocos de código"
      },
      {
        "pattern": "^\\s*Show lines\\s*$",
        "action": "remove"
      }
    ]
  },
  "selectors": {
    "content": [
      "#main-content",
      ".documentation",
      "article",
      "[data-content-area]"
    ],
    "skip": [
      "script",
      "style",
      ".hidden",
      "[aria-hidden='true']"
    ]
  }
}
```

## 6. Scraper para Wiki/Enciclopédia

```json
{
  "javascript_handling": {
    "enable_js_interaction": true,
    "click_and_wait": [
      {
        "selector": "a[href*='#']",
        "wait_ms": 500,
        "description": "Clica em links âncora para carregar seções"
      }
    ],
    "execute_scripts": [
      {
        "name": "remove_references_popup",
        "script": "document.querySelectorAll('.reference-popup, .citation-popup').forEach(el => el.remove())"
      }
    ]
  },
  "cleanup": {
    "garbage_sequences": [
      {
        "pattern": "\\[\\s*citation needed\\s*\\]",
        "action": "remove"
      },
      {
        "pattern": "\\[edit\\]",
        "action": "remove"
      }
    ]
  },
  "selectors": {
    "content": [
      "#mw-content-text",
      ".mw-parser-output",
      "#page-content",
      "main"
    ]
  }
}
```

## 7. Uso Programático com Customizações Dinâmicas

```python
from src.scraper_modular import ModularScraper, ConfigManager
import json

# Carrega config base
config = ConfigManager("scraper_config.json")

# Customiza dinamicamente
new_config = config.config.copy()
new_config['scraper']['max_pages'] = 200
new_config['extraction']['max_content_length'] = 150000
new_config['cleanup']['garbage_sequences'].append({
    "pattern": r"seu_padrão_customizado",
    "action": "remove"
})

# Salva config customizada
with open("config_temp.json", "w") as f:
    json.dump(new_config, f)

# Executa com config customizada
import asyncio

async def run():
    scraper = ModularScraper("config_temp.json")
    await scraper.scrape()

asyncio.run(run())
```

## 8. Scraper com Logging Detalhado

```python
import logging
from src.scraper_modular import ModularScraper

# Configura logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('scraper')

# Executa com logging
import asyncio

async def run():
    scraper = ModularScraper("scraper_config.json")
    logger.info(f"Iniciando scraper para {scraper.config.get('scraper.base_url')}")
    logger.info(f"Máx páginas: {scraper.config.get('scraper.max_pages')}")
    await scraper.scrape()

asyncio.run(run())
```

## 9. Scraper com Validação Customizada

```python
from src.scraper_modular import ModularScraper, ConfigManager
import json

class ValidatedScraper(ModularScraper):
    """Scraper com validações customizadas"""
    
    async def _scrape_page(self, page, url: str) -> bool:
        """Override para adicionar validações"""
        # Executa scraping normal
        result = await super()._scrape_page(page, url)
        
        if result and self.documents:
            # Valida último documento
            doc = self.documents[-1]
            
            # Verifica se título não é vazio
            if not doc['title'] or len(doc['title']) < 5:
                print(f"⚠️  Título muito curto: {url}")
                self.documents.pop()
                return False
            
            # Verifica se tem conteúdo suficiente
            if len(doc['content']) < 500:
                print(f"⚠️  Conteúdo muito curto: {url}")
                self.documents.pop()
                return False
        
        return result

# Usa scraper customizado
import asyncio

async def run():
    scraper = ValidatedScraper("scraper_config.json")
    await scraper.scrape()

asyncio.run(run())
```

## 10. Extração Seletiva por Tipo de Página

```json
{
  "scraper": {
    "base_url": "https://documentacao.senior.com.br",
    "max_pages": 200
  },
  "selectors": {
    "title": [
      "h1",
      ".page-title",
      "[data-document-title]"
    ],
    "content": [
      "#main-content",
      ".documentation-content"
    ]
  },
  "cleanup": {
    "garbage_sequences": [
      {
        "pattern": "\\b(Deprecated|Obsolete|Legacy)\\b",
        "action": "remove",
        "description": "Remove tags de deprecation"
      },
      {
        "pattern": "^\\s*(Versão|Version):\\s*(\\d+\\.)*\\d+.*$",
        "action": "remove",
        "description": "Remove indicadores de versão específica"
      }
    ]
  },
  "javascript_handling": {
    "enable_js_interaction": true,
    "click_and_wait": [
      {
        "selector": "[data-expandable='true']",
        "wait_ms": 600,
        "detect_change": {
          "monitor_selector": "[data-expanded='true']",
          "check_visibility": true
        }
      }
    ]
  }
}
```

---

## 📊 Monitorar Performance

```python
from src.scraper_modular import ModularScraper
import time

class MonitoredScraper(ModularScraper):
    """Scraper com monitoramento de performance"""
    
    async def _scrape_page(self, page, url: str) -> bool:
        start = time.time()
        result = await super()._scrape_page(page, url)
        duration = time.time() - start
        
        if result:
            doc = self.documents[-1]
            bytes_per_second = doc['metadata']['content_length'] / duration
            print(f"  ⏱️  {duration:.2f}s | {bytes_per_second:.0f} chars/s | {doc['metadata']['content_length']} chars")
        
        return result
```

---

## 🔄 Processamento em Batch

```python
from src.scraper_modular import ModularScraper
import asyncio
import json

async def scrape_multiple_sites():
    """Scrapa múltiplos sites com diferentes configurações"""
    
    sites = [
        ("https://documentacao.senior.com.br", "senior_docs"),
        ("https://help.example.com", "example_help"),
        ("https://docs.example.org", "example_docs")
    ]
    
    for base_url, name in sites:
        config = {
            "scraper": {
                "base_url": base_url,
                "max_pages": 100
            },
            "output": {
                "save_directory": f"docs_{name}"
            }
        }
        
        with open(f"config_{name}.json", "w") as f:
            json.dump(config, f)
        
        scraper = ModularScraper(f"config_{name}.json")
        await scraper.scrape()

asyncio.run(scrape_multiple_sites())
```

---

## 💾 Pós-processamento dos Dados

```python
from src.scraper_modular import ModularScraper
import json
from pathlib import Path

class PostProcessingScraper(ModularScraper):
    """Scraper com pós-processamento"""
    
    def _save_documents(self):
        """Override para adicionar pós-processamento"""
        # Executa salvamento normal
        super()._save_documents()
        
        # Pós-processamento
        print("\n📊 Pós-processamento...")
        
        # Indexa por módulo
        by_module = {}
        for doc in self.documents:
            module = doc.get('module', 'Unknown')
            if module not in by_module:
                by_module[module] = []
            by_module[module].append(doc)
        
        # Salva índice
        with open("docs_by_module.json", "w") as f:
            json.dump({m: len(docs) for m, docs in by_module.items()}, f)
        
        # Estatísticas
        print(f"📈 {len(self.documents)} documentos em {len(by_module)} módulos")
```

---

## 🎯 Casos de Uso Específicos

### Extrair Apenas Headers
```python
async def extract_headers_only():
    config = ConfigManager("scraper_config.json")
    config.config['extraction']['min_content_length'] = 1
    # Remove conteúdo sem headers
```

### Extrair Apenas Links
```python
async def extract_links_only():
    # Configure para não extrair conteúdo
    config = ConfigManager("scraper_config.json")
    config.config['extraction']['extract_links'] = True
```

### Validar Conformidade
```python
def validate_links():
    """Valida se links estão vivos"""
    for doc in scraper.documents:
        url = doc['url']
        # Verificar status code
```
