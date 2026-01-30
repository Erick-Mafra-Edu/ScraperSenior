#!/usr/bin/env python3
"""
Exemplo de uso do Scraper Modular com configurações customizadas
"""

import json
from pathlib import Path
from src.scraper_modular import ModularScraper
import asyncio


def create_custom_config(output_file: str = "scraper_config_custom.json"):
    """Cria uma configuração customizada para demonstração"""
    
    custom_config = {
        "scraper": {
            "base_url": "https://documentacao.senior.com.br",
            "max_pages": 50,
            "timeout_ms": 45000,
            "headless": True,
            "viewport": {"width": 1920, "height": 1080}
        },
        "extraction": {
            "max_content_length": 100000,
            "min_content_length": 50,
            "max_title_length": 300,
            "max_breadcrumb_depth": 6,
            "extract_images": True,
            "extract_links": True,
            "extract_tables": True
        },
        "cleanup": {
            "remove_empty_lines": True,
            "normalize_whitespace": True,
            "remove_trailing_spaces": True,
            "garbage_patterns": [
                r'\n{3,}',
                r'<!--.*?-->',
                r'\x00|\ufffd',
                r'\s{2,}(?=\n)'
            ],
            "garbage_sequences": [
                {
                    "pattern": r'^[\s]*$',
                    "action": "remove",
                    "description": "Remove linhas vazio"
                },
                {
                    "pattern": r'javascript:void\(0\)',
                    "action": "skip_element",
                    "description": "Ignora links javascript vazios"
                },
                {
                    "pattern": r'(anúncio|advertisement|publicidade|ad)',
                    "action": "remove",
                    "description": "Remove referências a anúncios"
                },
                {
                    "pattern": r'(cookie|rastreamento|tracking|analytics)',
                    "action": "remove",
                    "description": "Remove referências a cookies e rastreamento"
                },
                {
                    "pattern": r'(clique aqui|ver mais|carregando|loading)',
                    "action": "remove",
                    "description": "Remove CTAs e textos genéricos"
                }
            ]
        },
        "javascript_handling": {
            "enable_js_interaction": True,
            "wait_for_selectors": [
                ".content-loaded",
                "[data-loaded='true']",
                "#main-content",
                ".document-content"
            ],
            "click_and_wait": [
                {
                    "selector": "a[href*='#']",
                    "wait_ms": 1500,
                    "description": "Clica em links com âncoras e aguarda carregamento",
                    "detect_change": {
                        "monitor_selector": ".dynamic-content, .content",
                        "check_attribute": "data-timestamp",
                        "max_retries": 3
                    }
                },
                {
                    "selector": "[data-expandable='true'], .expandable, [class*='collapse']",
                    "wait_ms": 800,
                    "description": "Expande elementos colapsáveis",
                    "detect_change": {
                        "monitor_selector": "[data-expanded='true'], .expanded",
                        "check_visibility": True
                    }
                },
                {
                    "selector": ".toc-item, .menu-item, [role='tab']",
                    "wait_ms": 1000,
                    "description": "Clica em itens do TOC e abas",
                    "detect_change": {
                        "monitor_selector": ".content-frame, .tab-content, [aria-selected='true']",
                        "check_content_change": True
                    }
                }
            ],
            "execute_scripts": [
                {
                    "name": "remove_modals",
                    "description": "Remove modais e diálogos",
                    "script": "document.querySelectorAll('.modal, [role=\"dialog\"], .overlay, .popup').forEach(el => el.remove())"
                },
                {
                    "name": "remove_ads",
                    "description": "Remove banners e anúncios",
                    "script": "document.querySelectorAll('[class*=\"ad\"], [class*=\"banner\"], .advertisement, .promo').forEach(el => el.remove())"
                },
                {
                    "name": "remove_sticky_headers",
                    "description": "Remove headers fixos que cobrem conteúdo",
                    "script": "document.querySelectorAll('.sticky, [position=\"sticky\"], .fixed-header, .navbar-fixed').forEach(el => el.style.position = 'relative')"
                },
                {
                    "name": "expand_dynamic_content",
                    "description": "Expande conteúdo dinâmico",
                    "script": "document.querySelectorAll('[data-expandable], .collapsed, .accordion-item[aria-expanded=\"false\"]').forEach(el => el.click && el.click())"
                }
            ]
        },
        "selectors": {
            "title": [
                "h1",
                "[data-role='title']",
                ".page-title",
                ".document-title",
                ".entry-title",
                "[class*='main-title']"
            ],
            "content": [
                "#main-content",
                ".content",
                "[data-role='content']",
                "article",
                "main",
                ".document-content",
                ".post-content",
                "[class*='article-content']"
            ],
            "breadcrumb": [
                ".breadcrumb",
                "[data-role='navigation']",
                ".toc-path",
                "[class*='breadcrumb']",
                ".breadcrumb-nav",
                "[aria-label*='breadcrumb']"
            ],
            "navigation": [
                ".toc",
                ".sidebar",
                "[data-role='toc']",
                ".navigation-menu",
                ".main-nav"
            ],
            "skip": [
                "script",
                "style",
                ".hidden",
                "[aria-hidden='true']",
                ".advertisement",
                "[class*='cookie']",
                "iframe[src*='ads']",
                ".sidebar-ad",
                ".footer-ad",
                "[data-ad-unit-path]"
            ]
        },
        "links": {
            "follow_patterns": [
                "documentacao.senior.com.br",
                "help.senior.com.br",
                "suporte.senior.com.br"
            ],
            "ignore_patterns": [
                "javascript:",
                "#$",
                "mailto:",
                "tel:",
                "data:",
                "file://",
                ".pdf",
                ".zip",
                "logout",
                "signin"
            ],
            "internal_only": True,
            "max_depth": 5
        },
        "output": {
            "format": "jsonl",
            "save_directory": "docs_scraped",
            "include_metadata": True,
            "include_timestamp": True,
            "include_scrape_duration": True,
            "compression": None
        },
        "retry": {
            "max_retries": 3,
            "retry_delay_ms": 2000,
            "timeout_on_retry_ms": 60000
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(custom_config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Configuração customizada salva em: {output_file}")
    return output_file


def print_config_info(config_path: str):
    """Exibe informações sobre a configuração"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("\n" + "="*80)
    print("INFORMAÇÕES DE CONFIGURAÇÃO DO SCRAPER")
    print("="*80 + "\n")
    
    print("📊 SCRAPER:")
    print(f"  • Base URL: {config['scraper']['base_url']}")
    print(f"  • Máx. páginas: {config['scraper']['max_pages']}")
    print(f"  • Timeout: {config['scraper']['timeout_ms']}ms")
    
    print("\n📄 EXTRAÇÃO:")
    print(f"  • Comprimento máx. conteúdo: {config['extraction']['max_content_length']:,} caracteres")
    print(f"  • Comprimento mín. conteúdo: {config['extraction']['min_content_length']} caracteres")
    print(f"  • Comprimento máx. título: {config['extraction']['max_title_length']} caracteres")
    
    print("\n🧹 LIMPEZA:")
    print(f"  • Padrões de lixo: {len(config['cleanup']['garbage_patterns'])}")
    print(f"  • Sequências customizadas: {len(config['cleanup']['garbage_sequences'])}")
    
    print("\n⚙️  JAVASCRIPT:")
    print(f"  • JS ativado: {config['javascript_handling']['enable_js_interaction']}")
    print(f"  • Cliques customizados: {len(config['javascript_handling']['click_and_wait'])}")
    print(f"  • Scripts de limpeza: {len(config['javascript_handling']['execute_scripts'])}")
    
    print("\n🔗 LINKS:")
    print(f"  • Domínios permitidos: {len(config['links']['follow_patterns'])}")
    print(f"  • Padrões ignorados: {len(config['links']['ignore_patterns'])}")
    print(f"  • Apenas interno: {config['links']['internal_only']}")
    
    print("\n" + "="*80 + "\n")


async def main():
    """Função principal"""
    import sys
    
    # Cria configuração customizada
    config_file = "scraper_config_custom.json"
    print("\n🔨 Criando configuração customizada...\n")
    create_custom_config(config_file)
    
    # Mostra informações
    print_config_info(config_file)
    
    # Executa scraper
    print("🚀 Iniciando scraper modular...\n")
    scraper = ModularScraper(config_file)
    await scraper.scrape()


if __name__ == "__main__":
    asyncio.run(main())
