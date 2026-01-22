#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo: Usando o scraper melhorado para capturar notas de versão

Este script demonstra como usar o novo recurso de detecção automática
de notas de versão e suas âncoras.
"""

import json
from pathlib import Path
import asyncio


async def example_1_descobrir_notas():
    """Exemplo 1: Descobrir URLs de notas de versão"""
    print("\n" + "="*80)
    print("EXEMPLO 1: Descobrir URLs de Notas de Versão")
    print("="*80 + "\n")
    
    # Carregar arquivo gerado
    release_notes_config = Path("release_notes_config.json")
    
    if not release_notes_config.exists():
        print("[INFO] Gerando configuração...")
        import subprocess
        subprocess.run(["python", "src/adicionar_notas_versao.py"])
    
    with open(release_notes_config) as f:
        config = json.load(f)
    
    print(f"[INFO] Total de módulos: {len(config)}\n")
    
    # Mostrar URLs de cada módulo (apenas notas-da-versao)
    for module_name, notes_list in list(config.items())[:3]:
        print(f"\n[MÓDULO] {module_name}")
        for note_info in notes_list:
            if 'notas-da-versao' in note_info['url']:
                print(f"  URL: {note_info['url']}")


async def example_2_verificar_url_release_notes():
    """Exemplo 2: Verificar se URL é de notas de versão"""
    print("\n" + "="*80)
    print("EXEMPLO 2: Detectar Páginas de Notas de Versão")
    print("="*80 + "\n")
    
    from src.scraper_unificado import SeniorDocScraper
    
    scraper = SeniorDocScraper()
    
    # URLs de exemplo
    urls = [
        "https://documentacao.senior.com.br/gestao-de-pessoas-hcm/6.10.4/",
        "https://documentacao.senior.com.br/gestao-de-pessoas-hcm/notas-da-versao/",
        "https://documentacao.senior.com.br/gestaoempresarialerp/notas-de-versao/",
    ]
    
    for url in urls:
        is_release = (
            'notas-da-versao' in url or 
            'notas-de-versao' in url or 
            'release-notes' in url
        )
        
        print(f"\nURL: {url}")
        print(f"  Tipo: {'NOTAS DE VERSÃO' if is_release else 'Documentação'}")


async def example_3_estrutura_saida():
    """Exemplo 3: Estrutura de saída esperada"""
    print("\n" + "="*80)
    print("EXEMPLO 3: Estrutura de Saída das Notas de Versão")
    print("="*80 + "\n")
    
    structure = """
Após scraping de notas de versão, a estrutura será:

docs_estruturado/
├── GESTAO_DE_PESSOAS_HCM/
│   └── NOTAS_DE_VERSAO/
│       ├── 6-10-4/
│       │   ├── content.txt (conteúdo da versão)
│       │   ├── metadata.json (metadados)
│       │   └── page.html (HTML original, se --save-html)
│       ├── 6-10-3/
│       ├── 6-10-2/
│       └── ...
│
└── GESTAOEMPRESARIALERP/
    └── NOTAS_DE_VERSAO/
        ├── 5-10-4/
        ├── 5-10-3/
        └── ...

metadata.json de exemplo:
{
  "title": "Versão 6.10.4",
  "url": "https://documentacao.senior.com.br/gestao-de-pessoas-hcm/notas-da-versao/#6-10-4.htm",
  "breadcrumb": ["GESTAO_DE_PESSOAS_HCM", "NOTAS_DE_VERSAO", "6-10-4"],
  "module": "GESTAO_DE_PESSOAS_HCM",
  "version": "6.10.4",
  "total_chars": 2048,
  "has_html": true,
  "scraped_at": "2026-01-22T10:30:00"
}
"""
    print(structure)


async def example_4_usando_no_mcp():
    """Exemplo 4: Buscando notas de versão no MCP Server"""
    print("\n" + "="*80)
    print("EXEMPLO 4: Buscando Notas de Versão no MCP Server")
    print("="*80 + "\n")
    
    code_example = """
from src.mcp_server import SeniorDocumentationMCP

mcp = SeniorDocumentationMCP()

# Buscar por versão específica
results = mcp.search_docs("6.10.4", module="GESTAO DE PESSOAS HCM")
print(f"Encontradas {len(results['results'])} referências à versão 6.10.4")

# Buscar por mudança em notas de versão
results = mcp.search_docs("novo recurso", module="GESTAO DE PESSOAS HCM")

# Filtrar apenas notas de versão
release_notes = [
    r for r in results['results'] 
    if 'NOTAS_DE_VERSAO' in r.get('breadcrumb', [])
]
print(f"Encontradas {len(release_notes)} mudanças em notas de versão")

# Listar todas as versões de um módulo
from src.indexers.index_local import load_jsonl_index

index = load_jsonl_index()
versions = [
    d for d in index 
    if d.get('module') == 'GESTAO_DE_PESSOAS_HCM' and 
       'NOTAS_DE_VERSÃO' in d.get('breadcrumb', [])
]

# Ordenar por versão (mais recente primeiro)
versions_sorted = sorted(
    versions, 
    key=lambda x: x['subcategory'].replace('-', '.'), 
    reverse=True
)

print("\\nÚltimas versões:")
for v in versions_sorted[:5]:
    print(f"  - {v['subcategory']}: {v['content'][:100]}...")
"""
    print(code_example)


async def example_5_workflow_completo():
    """Exemplo 5: Workflow completo de captura e busca"""
    print("\n" + "="*80)
    print("EXEMPLO 5: Workflow Completo")
    print("="*80 + "\n")
    
    workflow = """
1. DESCOBERTA
   $ python src/adicionar_notas_versao.py
   
   Saída: release_notes_config.json com todas as URLs possíveis

2. SCRAPING
   $ python src/scraper_unificado.py
   
   • Detecta automaticamente páginas de notas de versão
   • Extrai âncoras de versão (#6-10-4.htm, etc)
   • Cria documento separado por versão
   • Gera docs_indexacao_detailed.jsonl

3. INDEXAÇÃO (Automática)
   • JSONL gerado com todas as versões
   • Metadados incluem breadcrumb e versão
   • Pronto para Meilisearch ou busca local

4. BUSCA
   $ python src/mcp_server.py
   
   # Buscar versões
   mcp.search_docs("6.10.4")
   
   # Buscar mudanças
   mcp.search_docs("bug fix CRM", module="GESTAO_DE_PESSOAS_HCM")

5. ANÁLISE
   # Comparar versões
   v1 = mcp.search_docs("6-10-4")
   v2 = mcp.search_docs("6-10-3")
   
   # Ver histórico
   versions = mcp.get_module_docs("GESTAO_DE_PESSOAS_HCM")
"""
    print(workflow)


async def main():
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "Exemplos: Usando o Scraper com Notas de Versão".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    await example_1_descobrir_notas()
    await example_2_verificar_url_release_notes()
    await example_3_estrutura_saida()
    await example_4_usando_no_mcp()
    await example_5_workflow_completo()
    
    print("\n" + "="*80)
    print("✅ PRÓXIMO PASSO: Executar o scraper")
    print("="*80)
    print("""
Para começar a capturar notas de versão:

1. Descobrir URLs:
   python src/adicionar_notas_versao.py

2. Scraping:
   python src/scraper_unificado.py

3. Buscar:
   python src/mcp_server.py

Veja RELEASE_NOTES_GUIDE.md para documentação completa.
""")
    print()


if __name__ == "__main__":
    asyncio.run(main())
