#!/usr/bin/env python3
"""
Cliente para API Pública do Suporte Senior
https://suporte.senior.com.br/api/v2/help_center/pt-br/

Módulo para consultar e indexar artigos de conhecimento do Suporte Senior
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from urllib.parse import urljoin


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SupportArticle:
    """Modelo de artigo do Suporte Senior"""
    id: str
    title: str
    body: str
    category: str
    locale: str = "pt-br"
    url: str = ""
    created_at: str = ""
    updated_at: str = ""
    views: int = 0
    helpful_count: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return asdict(self)


class SupportSeniorAPI:
    """Cliente para API do Suporte Senior"""
    
    BASE_URL = "https://suporte.senior.com.br/api/v2/help_center"
    LOCALE = "pt-br"
    
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self.session = session
        self._own_session = session is None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém ou cria uma sessão HTTP"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Fecha a sessão HTTP"""
        if self.session and self._own_session:
            await self.session.close()
    
    async def __aenter__(self):
        """Context manager - enter"""
        await self._get_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager - exit"""
        await self.close()
    
    def _build_url(self, endpoint: str) -> str:
        """Constrói URL completa"""
        return urljoin(f"{self.BASE_URL}/{self.LOCALE}/", endpoint)
    
    async def get_articles(self, page: int = 1, per_page: int = 100) -> Dict[str, Any]:
        """
        Obtém lista de artigos com paginação
        
        Args:
            page: Número da página (começa em 1)
            per_page: Artigos por página (máx 100)
        
        Returns:
            Dicionário com dados da resposta
        """
        url = self._build_url("articles.json")
        
        params = {
            "page": page,
            "per_page": min(per_page, 100)
        }
        
        try:
            session = await self._get_session()
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                logger.info(f"GET {url} (página {page}) - Status: {response.status}")
                
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Erro na API: Status {response.status}")
                    return {}
        except asyncio.TimeoutError:
            logger.error(f"Timeout ao acessar {url}")
            return {}
        except Exception as e:
            logger.error(f"Erro ao acessar {url}: {e}")
            return {}
    
    async def get_article_details(self, article_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes completos de um artigo
        
        Args:
            article_id: ID do artigo
        
        Returns:
            Dicionário com dados do artigo
        """
        url = self._build_url(f"articles/{article_id}.json")
        
        try:
            session = await self._get_session()
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                logger.info(f"GET {url} - Status: {response.status}")
                
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Erro na API: Status {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Erro ao acessar {url}: {e}")
            return {}
    
    async def get_categories(self) -> Dict[str, Any]:
        """
        Obtém lista de categorias
        
        Returns:
            Dicionário com categorias
        """
        url = self._build_url("categories.json")
        
        try:
            session = await self._get_session()
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                logger.info(f"GET {url} - Status: {response.status}")
                
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Erro na API: Status {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Erro ao acessar {url}: {e}")
            return {}
    
    async def get_all_articles(self, per_page: int = 100) -> List[SupportArticle]:
        """
        Obtém TODOS os artigos (com paginação automática)
        
        Args:
            per_page: Artigos por página
        
        Returns:
            Lista de artigos
        """
        articles = []
        page = 1
        
        while True:
            logger.info(f"Buscando página {page}...")
            
            response = await self.get_articles(page=page, per_page=per_page)
            
            if not response or 'articles' not in response:
                logger.warning(f"Fim da paginação na página {page}")
                break
            
            articles_data = response.get('articles', [])
            
            if not articles_data:
                logger.info(f"Nenhum artigo na página {page}")
                break
            
            for article_data in articles_data:
                try:
                    article = self._parse_article(article_data)
                    articles.append(article)
                except Exception as e:
                    logger.error(f"Erro ao parsear artigo: {e}")
            
            # Verifica se tem próxima página
            pagination = response.get('page_count', page)
            if page >= pagination:
                logger.info(f"Total de páginas: {pagination}")
                break
            
            page += 1
        
        logger.info(f"Total de artigos obtidos: {len(articles)}")
        return articles
    
    def _parse_article(self, data: Dict[str, Any]) -> SupportArticle:
        """Parseia dados brutos para SupportArticle"""
        return SupportArticle(
            id=str(data.get('id', '')),
            title=data.get('title', ''),
            body=data.get('body', ''),
            category=data.get('section_id', data.get('category', '')),
            locale=data.get('locale', 'pt-br'),
            url=data.get('html_url', ''),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', ''),
            views=int(data.get('views', 0)),
            helpful_count=int(data.get('helpful_count', 0)),
            metadata={
                'source_id': data.get('id'),
                'section_id': data.get('section_id'),
                'source': 'suporte.senior.com.br',
                'api_version': 'v2'
            }
        )
    
    async def search_articles(self, query: str) -> List[SupportArticle]:
        """
        Busca artigos por termo
        
        Args:
            query: Termo de busca
        
        Returns:
            Lista de artigos encontrados
        """
        url = self._build_url("articles/search.json")
        
        params = {
            "query": query
        }
        
        try:
            session = await self._get_session()
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                logger.info(f"GET {url} com query={query} - Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    articles = []
                    
                    for article_data in data.get('articles', []):
                        try:
                            article = self._parse_article(article_data)
                            articles.append(article)
                        except Exception as e:
                            logger.error(f"Erro ao parsear artigo: {e}")
                    
                    return articles
                else:
                    logger.error(f"Erro na API: Status {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Erro ao buscar: {e}")
            return []


class SupportArticleIndexer:
    """Indexa artigos do Suporte Senior para JSONL"""
    
    def __init__(self, output_dir: str = "docs_suporte_senior"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def index_all_articles(self, client: SupportSeniorAPI) -> Dict[str, Any]:
        """
        Indexa todos os artigos
        
        Args:
            client: Cliente da API
        
        Returns:
            Estatísticas de indexação
        """
        logger.info("Iniciando indexação de artigos...")
        
        articles = await client.get_all_articles()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"suporte_senior_{timestamp}.jsonl"
        
        # Salva em JSONL
        with open(output_file, 'w', encoding='utf-8') as f:
            for article in articles:
                # Converte para formato de indexação
                doc = {
                    'id': f"suporte_{article.id}",
                    'url': article.url,
                    'title': article.title,
                    'content': article.body,
                    'module': article.category,
                    'source': 'suporte.senior.com.br',
                    'metadata': {
                        **article.metadata,
                        'views': article.views,
                        'helpful_count': article.helpful_count,
                        'created_at': article.created_at,
                        'updated_at': article.updated_at
                    }
                }
                f.write(json.dumps(doc, ensure_ascii=False) + '\n')
        
        logger.info(f"✅ Artigos indexados em: {output_file}")
        
        # Estatísticas
        stats = {
            'timestamp': datetime.now().isoformat(),
            'total_articles': len(articles),
            'output_file': str(output_file),
            'by_category': {}
        }
        
        # Agrupa por categoria
        for article in articles:
            cat = article.category or 'Sem categoria'
            stats['by_category'][cat] = stats['by_category'].get(cat, 0) + 1
        
        # Salva metadados
        metadata_file = self.output_dir / f"metadata_{timestamp}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Metadados salvos em: {metadata_file}")
        
        return stats


async def main():
    """Exemplo de uso"""
    
    print("\n" + "="*80)
    print("CLIENTE API SUPORTE SENIOR")
    print("="*80 + "\n")
    
    # Exemplo 1: Obter artigos com paginação
    async with SupportSeniorAPI() as client:
        print("📄 Obtendo primeira página de artigos...\n")
        
        response = await client.get_articles(page=1, per_page=10)
        
        if 'articles' in response:
            print(f"Total de páginas: {response.get('page_count', 'N/A')}")
            print(f"Artigos nesta página: {len(response['articles'])}\n")
            
            for article in response['articles'][:3]:
                print(f"  📌 {article.get('title', 'Sem título')[:60]}")
                print(f"     ID: {article.get('id')}")
                print(f"     Views: {article.get('views', 0)}")
                print()
    
    # Exemplo 2: Obter todas as categorias
    async with SupportSeniorAPI() as client:
        print("\n📂 Obtendo categorias...\n")
        
        response = await client.get_categories()
        
        if 'categories' in response:
            print(f"Total de categorias: {len(response['categories'])}\n")
            
            for category in response['categories'][:5]:
                print(f"  📁 {category.get('name', 'Sem nome')}")
                print(f"     ID: {category.get('id')}")
                print()
    
    # Exemplo 3: Indexar todos os artigos
    print("\n" + "="*80)
    print("INDEXANDO TODOS OS ARTIGOS")
    print("="*80 + "\n")
    
    async with SupportSeniorAPI() as client:
        indexer = SupportArticleIndexer()
        stats = await indexer.index_all_articles(client)
        
        print(f"\n✅ Indexação completa!")
        print(f"   Total de artigos: {stats['total_articles']}")
        print(f"   Arquivo: {stats['output_file']}")
        print(f"\n📊 Artigos por categoria:")
        
        for category, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {category}: {count}")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
