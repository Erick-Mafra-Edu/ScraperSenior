#!/usr/bin/env python3
"""
Integração da API Suporte Senior com o Scraper Modular
Converte dados da API para formato compatível com Meilisearch
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

from src.suporte_senior_api import SupportSeniorAPI, SupportArticleIndexer
from src.scraper_modular import ConfigManager, GarbageCollector


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SuporteSeniorIntegration:
    """Integra API do Suporte Senior com o ecossistema de indexação"""
    
    def __init__(self, config_path: str = "scraper_config.json", output_dir: str = "docs_suporte_senior"):
        self.config = ConfigManager(config_path)
        self.gc = GarbageCollector(self.config)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def fetch_and_index(self) -> Dict[str, Any]:
        """
        Busca artigos da API e indexa em formato padrão
        
        Returns:
            Estatísticas de indexação
        """
        logger.info("Iniciando busca de artigos da API Suporte Senior...")
        
        async with SupportSeniorAPI() as api:
            # Busca todos os artigos
            articles = await api.get_all_articles(per_page=100)
            
            logger.info(f"Total de artigos obtidos: {len(articles)}")
            
            # Converte para formato de indexação
            indexed_docs = []
            
            for article in articles:
                doc = {
                    'id': f"suporte_{article.id}",
                    'url': article.url,
                    'title': self.gc.clean(article.title),
                    'content': self.gc.clean(article.body),
                    'module': article.category,
                    'breadcrumb': [article.category],
                    'source': 'suporte.senior.com.br',
                    'metadata': {
                        'views': article.views,
                        'helpful_count': article.helpful_count,
                        'created_at': article.created_at,
                        'updated_at': article.updated_at,
                        'scraped_at': datetime.now().isoformat(),
                        **article.metadata
                    }
                }
                
                # Respeita limites de conteúdo
                max_length = self.config.get("extraction.max_content_length", 50000)
                if len(doc['content']) > max_length:
                    doc['content'] = doc['content'][:max_length] + '...'
                
                indexed_docs.append(doc)
            
            # Salva em JSONL
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"suporte_senior_{timestamp}.jsonl"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for doc in indexed_docs:
                    f.write(json.dumps(doc, ensure_ascii=False) + '\n')
            
            logger.info(f"✅ Documentos indexados: {output_file}")
            
            # Gera estatísticas
            stats = self._generate_stats(indexed_docs, str(output_file))
            
            return stats
    
    def _generate_stats(self, docs: List[Dict[str, Any]], output_file: str) -> Dict[str, Any]:
        """Gera estatísticas de indexação"""
        
        stats = {
            'timestamp': datetime.now().isoformat(),
            'total_documents': len(docs),
            'output_file': output_file,
            'total_content_length': sum(len(doc.get('content', '')) for doc in docs),
            'by_category': {},
            'top_categories': [],
            'avg_content_length': 0
        }
        
        # Agrupa por categoria
        for doc in docs:
            category = doc.get('module', 'Sem categoria')
            if category not in stats['by_category']:
                stats['by_category'][category] = {
                    'count': 0,
                    'total_content': 0,
                    'avg_content': 0
                }
            
            stats['by_category'][category]['count'] += 1
            stats['by_category'][category]['total_content'] += len(doc.get('content', ''))
        
        # Calcula média de conteúdo por categoria
        for category, data in stats['by_category'].items():
            if data['count'] > 0:
                data['avg_content'] = data['total_content'] // data['count']
        
        # Top 10 categorias
        stats['top_categories'] = sorted(
            stats['by_category'].items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:10]
        
        # Média global
        if stats['total_documents'] > 0:
            stats['avg_content_length'] = stats['total_content_length'] // stats['total_documents']
        
        # Salva estatísticas
        stats_file = self.output_dir / f"stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            # Converte para formato serializable
            serializable_stats = {
                **stats,
                'by_category': {k: {'count': v['count']} for k, v in stats['by_category'].items()},
                'top_categories': [{'category': cat, 'count': data['count']} 
                                   for cat, data in stats['top_categories']]
            }
            json.dump(serializable_stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 Estatísticas salvas: {stats_file}")
        
        return stats
    
    async def sync_with_meilisearch(self, meilisearch_url: str, index_name: str = "suporte_senior") -> bool:
        """
        Sincroniza artigos com Meilisearch
        
        Args:
            meilisearch_url: URL do Meilisearch (ex: http://localhost:7700)
            index_name: Nome do índice
        
        Returns:
            True se sucesso
        """
        logger.info(f"Sincronizando com Meilisearch: {meilisearch_url}/{index_name}")
        
        try:
            import aiohttp
        except ImportError:
            logger.error("aiohttp não instalado. Instale com: pip install aiohttp")
            return False
        
        async with SupportSeniorAPI() as api:
            articles = await api.get_all_articles(per_page=100)
            
            # Prepara documentos para Meilisearch
            docs = []
            for article in articles:
                doc = {
                    'id': f"suporte_{article.id}",
                    'title': article.title,
                    'content': article.body[:5000],  # Limita para performance
                    'category': article.category,
                    'views': article.views,
                    'url': article.url,
                    'source': 'suporte.senior.com.br'
                }
                docs.append(doc)
            
            # Envia para Meilisearch
            async with aiohttp.ClientSession() as session:
                url = f"{meilisearch_url}/indexes/{index_name}/documents"
                
                try:
                    async with session.post(url, json=docs) as response:
                        if response.status in [200, 202]:
                            logger.info(f"✅ {len(docs)} documentos enviados para Meilisearch")
                            return True
                        else:
                            logger.error(f"Erro ao sincronizar: Status {response.status}")
                            return False
                except Exception as e:
                    logger.error(f"Erro ao conectar com Meilisearch: {e}")
                    return False


async def main():
    """Exemplo de uso da integração"""
    
    print("\n" + "="*80)
    print("INTEGRAÇÃO SUPORTE SENIOR - API + SCRAPER MODULAR")
    print("="*80 + "\n")
    
    integration = SuporteSeniorIntegration()
    
    # Busca e indexa
    print("📥 Buscando artigos da API...\n")
    stats = await integration.fetch_and_index()
    
    print(f"\n✅ Indexação completa!")
    print(f"   Total de documentos: {stats['total_documents']}")
    print(f"   Tamanho total: {stats['total_content_length']:,} caracteres")
    print(f"   Média por documento: {stats['avg_content_length']:,} caracteres")
    print(f"   Arquivo: {stats['output_file']}")
    
    print(f"\n📊 Top categorias:")
    for category, data in stats.get('top_categories', [])[:5]:
        print(f"   {category}: {data['count']} artigos")
    
    # Opcional: sincronizar com Meilisearch
    print("\n" + "="*80)
    print("SINCRONIZAÇÃO MEILISEARCH (Opcional)")
    print("="*80)
    
    try:
        meilisearch_url = "http://localhost:7700"
        success = await integration.sync_with_meilisearch(meilisearch_url)
        
        if success:
            print(f"✅ Sincronizado com sucesso em: {meilisearch_url}")
        else:
            print("⚠️  Falha ao sincronizar (Meilisearch pode não estar disponível)")
    except Exception as e:
        print(f"⚠️  Erro ao sincronizar: {e}")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
