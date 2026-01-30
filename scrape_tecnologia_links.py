#!/usr/bin/env python3
"""
Script para scrape de TECNOLOGIA com extração de links ativada
Foco: Capturar funções LSP e documentos relacionados via links em artigos
"""

import asyncio
import json
from pathlib import Path
from src.scraper_unificado import DocumentationScraper
import logging
from datetime import datetime

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'scrape_tecnologia_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    logger.info("=" * 80)
    logger.info("INICIANDO SCRAPE DE TECNOLOGIA COM LINKS ATIVADOS")
    logger.info("=" * 80)
    
    scraper = DocumentationScraper()
    
    try:
        # Conectar ao Playwright
        logger.info("Inicializando Playwright...")
        await scraper.setup()
        
        # Módulo TECNOLOGIA
        module_name = "TECNOLOGIA"
        base_url = "https://documentacao.senior.com.br/tecnologia/5.10.4"
        
        logger.info(f"Iniciando scrape do módulo: {module_name}")
        logger.info(f"URL Base: {base_url}")
        
        # Executar scrape
        logger.info("Executando scrape_module()...")
        await scraper.scrape_module(module_name, base_url, scraper.page)
        
        # Análise de resultados
        logger.info("=" * 80)
        logger.info("ANÁLISE DE RESULTADOS")
        logger.info("=" * 80)
        
        if scraper.all_documents:
            logger.info(f"✅ Total de documentos extraídos: {len(scraper.all_documents)}")
            
            # Contar documentos por tipo
            breadcrumb_counts = {}
            link_extracted_count = 0
            lsp_function_count = 0
            
            for doc in scraper.all_documents:
                breadcrumb = doc.get('breadcrumb', 'N/A')
                if breadcrumb:
                    breadcrumb_counts[breadcrumb] = breadcrumb_counts.get(breadcrumb, 0) + 1
                
                # Detectar documentos extraídos de links
                if 'extracted_from_link' in doc and doc['extracted_from_link']:
                    link_extracted_count += 1
                
                # Detectar funções LSP
                content = doc.get('content', '').lower()
                if 'funcao' in content or 'parametro' in content or 'retorno' in content:
                    if any(func in content for func in ['adicionacondicao', 'getsqlerror', 'arquexiste', 'alfaparaint']):
                        lsp_function_count += 1
            
            logger.info(f"📊 Documentos extraídos de links: {link_extracted_count}")
            logger.info(f"🔧 Documentos de funções LSP: {lsp_function_count}")
            logger.info(f"\n📍 Distribuição por breadcrumb:")
            for breadcrumb, count in sorted(breadcrumb_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
                logger.info(f"  - {breadcrumb}: {count} docs")
            
            # Salvar primeiro documento como amostra
            if scraper.all_documents:
                logger.info("\n📄 Amostra do primeiro documento:")
                first_doc = scraper.all_documents[0]
                logger.info(f"  Título: {first_doc.get('title', 'N/A')}")
                logger.info(f"  Breadcrumb: {first_doc.get('breadcrumb', 'N/A')}")
                logger.info(f"  Comprimento do conteúdo: {len(first_doc.get('content', ''))} caracteres")
                logger.info(f"  URL: {first_doc.get('url', 'N/A')}")
                
                # Salvar amostra
                with open('amostra_tecnologia.json', 'w', encoding='utf-8') as f:
                    json.dump(first_doc, f, indent=2, ensure_ascii=False)
                logger.info(f"  ✅ Amostra salva em: amostra_tecnologia.json")
            
            # Buscar funções LSP específicas
            logger.info("\n🔍 Buscando funções LSP conhecidas...")
            lsp_functions = ['AdicionaCondicao', 'GetSQLError', 'ArqExiste', 'AlfaParaInt']
            for func_name in lsp_functions:
                found = False
                for doc in scraper.all_documents:
                    if func_name.lower() in doc.get('content', '').lower():
                        logger.info(f"  ✅ {func_name} encontrada em: {doc.get('title', 'N/A')}")
                        found = True
                        break
                if not found:
                    logger.info(f"  ❌ {func_name} não encontrada")
            
            # Salvar todos os documentos para reindexação
            jsonl_path = 'docs_tecnologia_com_links.jsonl'
            logger.info(f"\n💾 Salvando documentos em JSONL: {jsonl_path}")
            
            with open(jsonl_path, 'w', encoding='utf-8') as f:
                for i, doc in enumerate(scraper.all_documents):
                    # Adicionar ID único
                    doc['id'] = f"TECNOLOGIA_{i}"
                    f.write(json.dumps(doc, ensure_ascii=False) + '\n')
            
            logger.info(f"✅ {len(scraper.all_documents)} documentos salvos em JSONL")
            
        else:
            logger.warning("⚠️ Nenhum documento foi extraído!")
        
        logger.info("=" * 80)
        logger.info("SCRAPE CONCLUÍDO COM SUCESSO")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Erro durante scrape: {str(e)}", exc_info=True)
        
    finally:
        # Fechar Playwright
        await scraper.cleanup()
        logger.info("Playwright fechado")

if __name__ == "__main__":
    asyncio.run(main())
