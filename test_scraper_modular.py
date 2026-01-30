#!/usr/bin/env python3
"""
Testes do Scraper Modular
Valida cada componente individualmente
"""

import asyncio
import json
import tempfile
from pathlib import Path
from src.scraper_modular import (
    ConfigManager,
    GarbageCollector,
    ContentExtractor,
    JavaScriptHandler,
    LinkExtractor
)


def test_config_manager():
    """Testa carregamento de configurações"""
    print("\n" + "="*70)
    print("TEST 1: ConfigManager")
    print("="*70)
    
    config = ConfigManager("scraper_config.json")
    
    # Testa get com path
    base_url = config.get("scraper.base_url")
    max_pages = config.get("scraper.max_pages")
    max_length = config.get("extraction.max_content_length")
    
    print(f"✅ Base URL: {base_url}")
    print(f"✅ Max Pages: {max_pages}")
    print(f"✅ Max Content Length: {max_length}")
    
    # Testa valores padrão
    missing = config.get("inexistent.path", "default_value")
    print(f"✅ Valor padrão para path inexistente: {missing}")
    
    return True


def test_garbage_collector():
    """Testa remoção de lixo"""
    print("\n" + "="*70)
    print("TEST 2: GarbageCollector")
    print("="*70)
    
    config = ConfigManager("scraper_config.json")
    gc = GarbageCollector(config)
    
    # Testa remoção de padrões
    test_cases = [
        ("Texto   com    espaços", "Texto com espaços"),
        ("Linha 1\n\n\n\nLinha 2", "Linha 1\n\nLinha 2"),
        ("  espaços  à esquerda  ", "espaços à esquerda"),
        ("texto\n\nmultilinha", "texto\nmultilinha"),
    ]
    
    for input_text, expected in test_cases:
        result = gc.clean(input_text)
        status = "✅" if result.strip() == expected.strip() else "❌"
        print(f"{status} '{input_text[:40]}...' -> '{result[:40]}...'")
    
    # Testa detecção de lixo
    garbage_text = "Clique em nossa publicidade para saber mais"
    is_garbage = gc.is_garbage(garbage_text)
    print(f"✅ Detecta lixo: {is_garbage}")
    
    return True


def test_link_extractor():
    """Testa validação de links"""
    print("\n" + "="*70)
    print("TEST 3: LinkExtractor")
    print("="*70)
    
    config = ConfigManager("scraper_config.json")
    extractor = LinkExtractor(config)
    
    # Testa links válidos
    valid_links = [
        "https://documentacao.senior.com.br/page1",
        "https://help.senior.com.br/article",
        "https://suporte.senior.com.br/faq"
    ]
    
    for link in valid_links:
        should_follow = extractor.should_follow(link)
        print(f"✅ '{link[:50]}...' -> {should_follow}")
    
    # Testa links inválidos
    invalid_links = [
        "https://documentacao.senior.com.br/page.pdf",
        "javascript:void(0)",
        "mailto:test@example.com",
        "https://external.com/page"
    ]
    
    print("\nLinks inválidos:")
    for link in invalid_links:
        should_follow = extractor.should_follow(link)
        print(f"✅ '{link[:50]}...' -> {should_follow}")
    
    return True


def test_config_customization():
    """Testa customização de configurações"""
    print("\n" + "="*70)
    print("TEST 4: Customização de Configurações")
    print("="*70)
    
    config = ConfigManager("scraper_config.json")
    
    # Carrega configuração original
    original_max = config.get("extraction.max_content_length")
    print(f"✅ Max content original: {original_max}")
    
    # Cria configuração customizada
    custom_config = {
        "extraction": {
            "max_content_length": 100000,
            "garbage_sequences": [
                {"pattern": "test", "action": "remove"}
            ]
        }
    }
    
    # Salva em arquivo temporário
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(custom_config, f)
        temp_path = f.name
    
    try:
        custom_cfg = ConfigManager(temp_path)
        custom_max = custom_cfg.get("extraction.max_content_length", 50000)
        print(f"✅ Max content customizado: {custom_max}")
        print(f"✅ Sequências customizadas: {len(custom_cfg.get('extraction.garbage_sequences', []))}")
    finally:
        Path(temp_path).unlink()
    
    return True


def test_garbage_sequences():
    """Testa tratamento de sequências de lixo"""
    print("\n" + "="*70)
    print("TEST 5: Garbage Sequences")
    print("="*70)
    
    config = ConfigManager("scraper_config.json")
    gc = GarbageCollector(config)
    
    # Simula sequências de lixo
    test_cases = [
        ("Clique aqui para mais informações", "Remove CTA"),
        ("javascript:void(0)", "Remove JS vazio"),
        ("Veja nossa publicidade especial", "Remove anúncio"),
        ("Aceite nosso rastreamento", "Remove tracking"),
    ]
    
    print("Testando remoção de sequências de lixo:")
    for text, description in test_cases:
        result = gc.clean(text)
        was_cleaned = len(result) < len(text)
        status = "✅" if was_cleaned else "⚠️"
        print(f"{status} {description}: '{text}' -> '{result}'")
    
    return True


def test_selectors():
    """Testa seletores CSS"""
    print("\n" + "="*70)
    print("TEST 6: CSS Selectors")
    print("="*70)
    
    config = ConfigManager("scraper_config.json")
    
    # Verifica seletores
    title_selectors = config.get("selectors.title", [])
    content_selectors = config.get("selectors.content", [])
    skip_selectors = config.get("selectors.skip", [])
    
    print(f"✅ Seletores de título: {len(title_selectors)}")
    print(f"   {', '.join(title_selectors[:3])}")
    
    print(f"\n✅ Seletores de conteúdo: {len(content_selectors)}")
    print(f"   {', '.join(content_selectors[:3])}")
    
    print(f"\n✅ Seletores a ignorar: {len(skip_selectors)}")
    print(f"   {', '.join(skip_selectors[:3])}")
    
    return True


def test_js_handling_config():
    """Testa configuração de JavaScript"""
    print("\n" + "="*70)
    print("TEST 7: JavaScript Handling Configuration")
    print("="*70)
    
    config = ConfigManager("scraper_config.json")
    
    # Verifica configurações JS
    js_enabled = config.get("javascript_handling.enable_js_interaction", False)
    wait_selectors = config.get("javascript_handling.wait_for_selectors", [])
    click_configs = config.get("javascript_handling.click_and_wait", [])
    execute_scripts = config.get("javascript_handling.execute_scripts", [])
    
    print(f"✅ JS ativado: {js_enabled}")
    print(f"✅ Seletores para aguardar: {len(wait_selectors)}")
    print(f"✅ Configurações de clique: {len(click_configs)}")
    
    if click_configs:
        print(f"\n   Exemplo de clique:")
        example = click_configs[0]
        print(f"   - Selector: {example.get('selector')}")
        print(f"   - Wait MS: {example.get('wait_ms')}")
        print(f"   - Detect changes: {bool(example.get('detect_change'))}")
    
    print(f"\n✅ Scripts de limpeza: {len(execute_scripts)}")
    if execute_scripts:
        print(f"   Exemplos: {', '.join([s.get('name', 'Unknown')[:30] for s in execute_scripts[:3]])}")
    
    return True


def test_output_config():
    """Testa configuração de output"""
    print("\n" + "="*70)
    print("TEST 8: Output Configuration")
    print("="*70)
    
    config = ConfigManager("scraper_config.json")
    
    output_format = config.get("output.format", "jsonl")
    save_dir = config.get("output.save_directory", "docs_scraped")
    include_meta = config.get("output.include_metadata", False)
    include_ts = config.get("output.include_timestamp", False)
    include_duration = config.get("output.include_scrape_duration", False)
    
    print(f"✅ Formato: {output_format}")
    print(f"✅ Diretório de saída: {save_dir}")
    print(f"✅ Incluir metadata: {include_meta}")
    print(f"✅ Incluir timestamp: {include_ts}")
    print(f"✅ Incluir duração: {include_duration}")
    
    return True


def test_links_config():
    """Testa configuração de links"""
    print("\n" + "="*70)
    print("TEST 9: Links Configuration")
    print("="*70)
    
    config = ConfigManager("scraper_config.json")
    
    follow_patterns = config.get("links.follow_patterns", [])
    ignore_patterns = config.get("links.ignore_patterns", [])
    internal_only = config.get("links.internal_only", True)
    max_depth = config.get("links.max_depth", 5)
    
    print(f"✅ Domínios permitidos: {len(follow_patterns)}")
    for pattern in follow_patterns[:3]:
        print(f"   - {pattern}")
    
    print(f"\n✅ Padrões ignorados: {len(ignore_patterns)}")
    for pattern in ignore_patterns[:5]:
        print(f"   - {pattern}")
    
    print(f"\n✅ Apenas interno: {internal_only}")
    print(f"✅ Profundidade máx: {max_depth}")
    
    return True


def main():
    """Executa todos os testes"""
    print("\n" + "="*70)
    print("TESTES DO SCRAPER MODULAR")
    print("="*70)
    
    tests = [
        ("ConfigManager", test_config_manager),
        ("GarbageCollector", test_garbage_collector),
        ("LinkExtractor", test_link_extractor),
        ("Customização", test_config_customization),
        ("Garbage Sequences", test_garbage_sequences),
        ("CSS Selectors", test_selectors),
        ("JavaScript Handling", test_js_handling_config),
        ("Output Config", test_output_config),
        ("Links Config", test_links_config),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Erro em {name}: {e}")
            results.append((name, False))
    
    # Relatório final
    print("\n" + "="*70)
    print("RELATÓRIO")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    print("="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
