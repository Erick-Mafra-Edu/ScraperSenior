#!/usr/bin/env python3
"""
Integração entre API Zendesk e Scraper Modular
Converte documentos do Zendesk para formato do scraper modular
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from apps.zendesk.api_zendesk import ZendeskScraper


class ZendeskToModularAdapter:
    """Adapta documentos Zendesk para formato do scraper modular"""
    
    @staticmethod
    def convert_article(zendesk_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte artigo Zendesk para formato do scraper modular
        
        Args:
            zendesk_doc: Documento do Zendesk
            
        Returns:
            Documento no formato do scraper modular
        """
        return {
            'id': zendesk_doc['id'],
            'url': zendesk_doc['url'],
            'title': zendesk_doc['title'],
            'content': zendesk_doc['content'],
            'breadcrumb': [
                'Suporte',
                'Help Center',
                f"Categoria {zendesk_doc.get('category_id', 'Unknown')}",
                f"Seção {zendesk_doc.get('section_id', 'Unknown')}"
            ],
            'module': 'Help Center',
            'metadata': {
                'url': zendesk_doc['url'],
                'title': zendesk_doc['title'],
                'breadcrumb': [],
                'module': 'Help Center',
                'scraped_at': zendesk_doc.get('metadata', {}).get('scraped_at', ''),
                'scrape_duration_ms': 0,
                'content_length': len(zendesk_doc['content']),
                'charset': 'utf-8',
                'source': 'zendesk',
                'locale': zendesk_doc.get('locale', 'pt-BR')
            }
        }
    
    @staticmethod
    async def scrape_and_convert(
        zendesk_url: str = "https://suporte.senior.com.br/api/v2/help_center",
        output_file: str = "docs_zendesk/converted.jsonl"
    ) -> Dict[str, Any]:
        """
        Scrapa Zendesk e converte para formato modular
        
        Args:
            zendesk_url: URL da API Zendesk
            output_file: Arquivo de saída JSONL
            
        Returns:
            Estatísticas da conversão
        """
        
        print("\n" + "="*80)
        print("ZENDESK → SCRAPER MODULAR - Conversão de Documentos")
        print("="*80 + "\n")
        
        # 1. Scrapa Zendesk
        print("[1/3] Scrapando Zendesk Help Center...")
        scraper = ZendeskScraper(api_url=zendesk_url)
        report = await scraper.scrape_all()
        
        # 2. Converte
        print("[2/3] Convertendo para formato modular...")
        converted_docs = []
        
        for doc in scraper.documents:
            converted = ZendeskToModularAdapter.convert_article(doc)
            converted_docs.append(converted)
        
        print(f"✅ {len(converted_docs)} documentos convertidos\n")
        
        # 3. Salva
        print("[3/3] Salvando documentos convertidos...")
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for doc in converted_docs:
                f.write(json.dumps(doc, ensure_ascii=False) + '\n')
        
        print(f"✅ Salvos em: {output_path}\n")
        
        print("="*80)
        print("RESUMO DA CONVERSÃO")
        print("="*80)
        print(f"Documentos convertidos:  {len(converted_docs)}")
        print(f"Artigos Zendesk:         {report['statistics']['articles']}")
        print(f"Categorias:              {report['statistics']['categories']}")
        print(f"Seções:                  {report['statistics']['sections']}")
        print(f"Tempo total:             {report['duration_seconds']:.2f}s")
        print(f"Saída:                   {output_path}")
        print("="*80 + "\n")
        
        return {
            'status': 'success',
            'documents_converted': len(converted_docs),
            'output_file': str(output_path),
            'zendesk_report': report
        }


async def main():
    """Exemplo de uso"""
    result = await ZendeskToModularAdapter.scrape_and_convert()
    print(f"Resultado: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
