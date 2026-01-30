#!/usr/bin/env python3
"""
Módulo de Integração com API Zendesk Help Center
Suporte Senior: https://suporte.senior.com.br/api/v2/help_center/pt-br/

Compatível com Zendesk Help Center API v2
Extrai artigos, categorias e seções
"""

import asyncio
import json
import aiohttp
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class ZendeskArticle:
    """Artigo do Zendesk"""
    id: int
    url: str
    title: str
    body: str
    category_id: int
    section_id: int
    created_at: str
    updated_at: str
    author_id: int
    locale: str = "pt-BR"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ZendeskCategory:
    """Categoria do Zendesk"""
    id: int
    url: str
    name: str
    description: str = ""
    locale: str = "pt-BR"
    position: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ZendeskSection:
    """Seção do Zendesk"""
    id: int
    url: str
    name: str
    description: str = ""
    category_id: int = 0
    locale: str = "pt-BR"
    position: int = 0
    article_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ZendeskAPIClient:
    """Cliente para API Zendesk Help Center"""
    
    def __init__(self, base_url: str = "https://suporte.senior.com.br/api/v2/help_center"):
        """
        Inicializa cliente Zendesk
        
        Args:
            base_url: URL base da API (sem barra final)
        """
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.default_locale = "pt-br"
        self.stats = {
            'articles_fetched': 0,
            'categories_fetched': 0,
            'sections_fetched': 0,
            'api_calls': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
    
    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Faz requisição GET na API
        
        Args:
            endpoint: Caminho do endpoint (ex: /articles)
            params: Parâmetros da query
            
        Returns:
            Resposta JSON
        """
        if not self.session:
            raise RuntimeError("Session não inicializada. Use 'async with' para inicializar.")
        
        url = f"{self.base_url}/{self.default_locale}{endpoint}"
        self.stats['api_calls'] += 1
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.stats['errors'] += 1
                    return {'error': f"Status {response.status}", 'url': url}
        except Exception as e:
            self.stats['errors'] += 1
            print(f"❌ Erro ao fazer request para {url}: {e}")
            return {'error': str(e)}
    
    async def get_categories(self) -> List[ZendeskCategory]:
        """
        Obtém todas as categorias
        
        Returns:
            Lista de categorias
        """
        categories = []
        page = 1
        
        while True:
            print(f"📑 Obtendo categorias (página {page})...", end=" ", flush=True)
            
            data = await self._get("/categories.json", params={"page": page, "per_page": 100})
            
            if 'error' in data:
                print(f"❌")
                break
            
            if 'categories' not in data:
                print(f"❌")
                break
            
            page_categories = data['categories']
            if not page_categories:
                print(f"✅ Fim")
                break
            
            for cat_data in page_categories:
                cat = ZendeskCategory(
                    id=cat_data['id'],
                    url=cat_data['url'],
                    name=cat_data['name'],
                    description=cat_data.get('description', ''),
                    locale=cat_data.get('locale', 'pt-BR'),
                    position=cat_data.get('position', 0)
                )
                categories.append(cat)
                self.stats['categories_fetched'] += 1
            
            print(f"✅ {len(page_categories)} categorias")
            
            # Continua se tiver mais
            if len(page_categories) < 100:
                break
            
            page += 1
        
        return categories
    
    async def get_sections(self, category_id: Optional[int] = None) -> List[ZendeskSection]:
        """
        Obtém seções (opcionalmente de uma categoria específica)
        
        Args:
            category_id: ID da categoria (opcional)
            
        Returns:
            Lista de seções
        """
        sections = []
        page = 1
        
        while True:
            if category_id:
                endpoint = f"/categories/{category_id}/sections.json"
                print(f"📂 Obtendo seções da categoria {category_id} (página {page})...", end=" ", flush=True)
            else:
                endpoint = "/sections.json"
                print(f"📂 Obtendo seções (página {page})...", end=" ", flush=True)
            
            data = await self._get(endpoint, params={"page": page, "per_page": 100})
            
            if 'error' in data:
                print(f"❌")
                break
            
            if 'sections' not in data:
                print(f"❌")
                break
            
            page_sections = data['sections']
            if not page_sections:
                print(f"✅ Fim")
                break
            
            for sec_data in page_sections:
                sec = ZendeskSection(
                    id=sec_data['id'],
                    url=sec_data['url'],
                    name=sec_data['name'],
                    description=sec_data.get('description', ''),
                    category_id=sec_data.get('category_id', category_id or 0),
                    locale=sec_data.get('locale', 'pt-BR'),
                    position=sec_data.get('position', 0),
                    article_count=sec_data.get('article_count', 0)
                )
                sections.append(sec)
                self.stats['sections_fetched'] += 1
            
            print(f"✅ {len(page_sections)} seções")
            
            if len(page_sections) < 100:
                break
            
            page += 1
        
        return sections
    
    async def get_articles(self, 
                          section_id: Optional[int] = None,
                          category_id: Optional[int] = None,
                          locale: str = "pt-br") -> AsyncIterator[ZendeskArticle]:
        """
        Obtém artigos (com paginação automática)
        
        Args:
            section_id: ID da seção (opcional)
            category_id: ID da categoria (opcional)
            locale: Locale dos artigos
            
        Yields:
            Artigos um por um
        """
        page = 1
        self.default_locale = locale
        
        while True:
            if section_id:
                endpoint = f"/sections/{section_id}/articles.json"
                print(f"📄 Obtendo artigos da seção {section_id} (página {page})...", end=" ", flush=True)
            elif category_id:
                endpoint = f"/categories/{category_id}/articles.json"
                print(f"📄 Obtendo artigos da categoria {category_id} (página {page})...", end=" ", flush=True)
            else:
                endpoint = "/articles.json"
                print(f"📄 Obtendo artigos (página {page})...", end=" ", flush=True)
            
            data = await self._get(endpoint, params={"page": page, "per_page": 100})
            
            if 'error' in data:
                print(f"❌")
                break
            
            if 'articles' not in data:
                print(f"❌")
                break
            
            articles = data['articles']
            if not articles:
                print(f"✅ Fim")
                break
            
            for art_data in articles:
                article = ZendeskArticle(
                    id=art_data['id'],
                    url=art_data['html_url'],
                    title=art_data['title'],
                    body=art_data.get('body', ''),
                    category_id=art_data.get('category_id', category_id or 0),
                    section_id=art_data.get('section_id', section_id or 0),
                    created_at=art_data.get('created_at', ''),
                    updated_at=art_data.get('updated_at', ''),
                    author_id=art_data.get('author_id', 0),
                    locale=locale
                )
                self.stats['articles_fetched'] += 1
                yield article
            
            print(f"✅ {len(articles)} artigos")
            
            if len(articles) < 100:
                break
            
            page += 1


class ZendeskScraper:
    """Scraper para Zendesk Help Center com integração ao scraper modular"""
    
    def __init__(self, 
                 api_url: str = "https://suporte.senior.com.br/api/v2/help_center",
                 output_dir: str = "docs_zendesk"):
        self.client = ZendeskAPIClient(api_url)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.documents: List[Dict[str, Any]] = []
        self.categories: List[ZendeskCategory] = []
        self.sections: List[ZendeskSection] = []
    
    async def scrape_all(self) -> Dict[str, Any]:
        """Scrapa tudo: categorias, seções e artigos"""
        
        print("\n" + "="*80)
        print("ZENDESK HELP CENTER SCRAPER - Suporte Senior")
        print("="*80 + "\n")
        
        self.client.stats['start_time'] = datetime.now(timezone.utc)
        
        async with self.client:
            # 1. Categorias
            print("[1/4] Obtendo categorias...")
            self.categories = await self.client.get_categories()
            print(f"✅ {len(self.categories)} categorias encontradas\n")
            
            # 2. Seções
            print("[2/4] Obtendo seções...")
            self.sections = await self.client.get_sections()
            print(f"✅ {len(self.sections)} seções encontradas\n")
            
            # 3. Artigos
            print("[3/4] Obtendo artigos...")
            article_count = 0
            
            async for article in self.client.get_articles():
                doc = {
                    'id': f"zendesk_{article.id}",
                    'type': 'zendesk_article',
                    'url': article.url,
                    'title': article.title,
                    'content': article.body,
                    'category_id': article.category_id,
                    'section_id': article.section_id,
                    'locale': article.locale,
                    'metadata': {
                        'source': 'zendesk',
                        'created_at': article.created_at,
                        'updated_at': article.updated_at,
                        'author_id': article.author_id,
                        'scraped_at': datetime.now(timezone.utc).isoformat()
                    }
                }
                self.documents.append(doc)
                article_count += 1
            
            print(f"✅ {article_count} artigos obtidos\n")
            
            # 4. Salvar
            print("[4/4] Salvando documentos...")
            await self._save_documents()
            print(f"✅ Documentos salvos\n")
        
        self.client.stats['end_time'] = datetime.now(timezone.utc)
        
        return self._generate_report()
    
    async def _save_documents(self):
        """Salva documentos em JSONL"""
        
        # Salva JSONL
        jsonl_path = self.output_dir / "articles.jsonl"
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for doc in self.documents:
                f.write(json.dumps(doc, ensure_ascii=False) + '\n')
        
        # Salva metadados
        metadata = {
            'total_documents': len(self.documents),
            'total_categories': len(self.categories),
            'total_sections': len(self.sections),
            'scraped_at': datetime.now(timezone.utc).isoformat(),
            'categories': [cat.to_dict() for cat in self.categories],
            'sections': [sec.to_dict() for sec in self.sections]
        }
        
        metadata_path = self.output_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"  📄 JSONL: {jsonl_path}")
        print(f"  📋 Metadata: {metadata_path}")
    
    def _generate_report(self) -> Dict[str, Any]:
        """Gera relatório de scraping"""
        
        duration = (self.client.stats['end_time'] - self.client.stats['start_time']).total_seconds()
        
        report = {
            'status': 'success',
            'duration_seconds': duration,
            'statistics': {
                'articles': self.client.stats['articles_fetched'],
                'categories': self.client.stats['categories_fetched'],
                'sections': self.client.stats['sections_fetched'],
                'api_calls': self.client.stats['api_calls'],
                'errors': self.client.stats['errors']
            },
            'output_directory': str(self.output_dir),
            'files': {
                'articles': str(self.output_dir / 'articles.jsonl'),
                'metadata': str(self.output_dir / 'metadata.json')
            }
        }
        
        print("="*80)
        print("RELATÓRIO")
        print("="*80)
        print(f"Artigos:        {report['statistics']['articles']}")
        print(f"Categorias:     {report['statistics']['categories']}")
        print(f"Seções:         {report['statistics']['sections']}")
        print(f"Chamadas API:   {report['statistics']['api_calls']}")
        print(f"Erros:          {report['statistics']['errors']}")
        print(f"Tempo total:    {duration:.2f}s")
        print("="*80 + "\n")
        
        return report


async def main():
    """Exemplo de uso"""
    scraper = ZendeskScraper()
    await scraper.scrape_all()


if __name__ == "__main__":
    asyncio.run(main())
