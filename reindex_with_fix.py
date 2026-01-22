#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Re-indexar todos os documentos com a correção de títulos
Scrapa os módulos novamente com o código corrigido
"""

import asyncio
import json
import sys
from pathlib import Path
from src.scraper_unificado import SeniorDocScraper


async def reindex_all_modules():
    """Re-indexar todos os módulos"""
    
    print("\n" + "="*80)
    print("[REINDEXAÇÃO] Scraping com Correção de Títulos")
    print("="*80 + "\n")
    
    # Carregar módulos
    modulos_file = Path("modulos_descobertos.json")
    with open(modulos_file) as f:
        modulos = json.load(f)
    
    total_modules = len(modulos)
    print(f"📦 {total_modules} módulos encontrados\n")
    
    scraper = SeniorDocScraper()
    
    # Módulos para testar (começar com os principais)
    test_modules = [
        "GESTAO DE PESSOAS HCM",
        "GESTAO_DE_RELACIONAMENTO_CRM",
        "RONDA_SENIOR"
    ]
    
    for module_name in test_modules:
        if module_name not in modulos:
            print(f"⏭️  Pulando: {module_name} (não encontrado)")
            continue
        
        base_url = modulos[module_name]['url']
        
        print(f"\n🔄 Scraping: {module_name}")
        print(f"   URL: {base_url[:60]}...")
        print("   Status: ...", end="", flush=True)
        
        try:
            docs = await scraper.scrape_module(module_name, base_url)
            
            # Contar documentos com títulos não-vazios
            with_titles = sum(1 for doc in docs if doc.get('title', '').strip())
            
            print(f"\r   ✓ {len(docs)} documentos | {with_titles} com títulos")
            
            # Mostrar alguns títulos como validação
            for doc in docs[:3]:
                title = doc.get('title', 'SEM TÍTULO')[:50]
                print(f"     - {title}")
            
        except Exception as e:
            print(f"\r   ✗ Erro: {e}")
    
    print("\n" + "="*80)
    print("[✓] REINDEXAÇÃO CONCLUÍDA")
    print("="*80 + "\n")
    
    print("📝 Próximos passos:")
    print("   1. Validar títulos acima")
    print("   2. Se OK, executar: python src/indexers/index_all_docs.py")
    print("   3. Reiniciar Docker: docker-compose restart mcp-server")


if __name__ == "__main__":
    asyncio.run(reindex_all_modules())
